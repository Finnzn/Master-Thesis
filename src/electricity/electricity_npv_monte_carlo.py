"""Monte Carlo input provider for the shared electricity NPV model.

For each technology, this module samples uncertain techno-economic inputs and
passes the aligned arrays to :mod:`electricity.electricity_npv_model`, which
owns plant sizing, sector costs, and financial-result assembly.

Hard coal CCS and CCGT CCS are modelled as retrofits of their unabated parent
technologies. `retrofit_bau_mode` controls whether their BAU inputs are sampled
for each run ID or held at deterministic expected values while the
incremental retrofit inputs remain sampled.

The output intentionally includes both sampled inputs and derived financial
outputs. That makes each Monte Carlo result traceable from assumptions to NPV
when exported to CSV.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from electricity.electricity_npv_model import (
    FUEL_PRICE_KEY_BY_TECHNOLOGY,
    calculate_result,
    resolve_technology_values,
)
from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
    sample_scaled_beta,
    sample_triangular,
    sample_uniform,
)
from electricity.electricity_parameters import (
    BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION,
    ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES,
    ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
)
from general_parameters import (
    BIOMASS_PRICE_DISTRIBUTION,
    BIOGAS_PRICE_EUR_PER_MWH_TH,
    COAL_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
)
from npv_summary import representative_value


DEFAULT_SAMPLE_SIZE = 100_000
DEFAULT_RANDOM_SEED = 42
DEFAULT_RETROFIT_BAU_MODE = "sampled"
RETROFIT_BAU_MODES = ("sampled", "deterministic")

ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def _validate_size(size: int) -> None:
    """Validate a positive Monte Carlo sample size."""

    if size <= 0:
        raise ValueError("size must be positive.")


def _validate_retrofit_bau_mode(retrofit_bau_mode: str) -> None:
    """Validate the BAU baseline mode used for retrofit technologies."""

    if retrofit_bau_mode not in RETROFIT_BAU_MODES:
        allowed = ", ".join(repr(mode) for mode in RETROFIT_BAU_MODES)
        raise ValueError(
            f"retrofit_bau_mode must be one of {allowed}; "
            f"got {retrofit_bau_mode!r}."
        )


def _sample_distribution(
    distribution: (
        ScaledBetaDistribution | TriangularDistribution | UniformDistribution
    ),
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Dispatch one supported stochastic parameter to its sampler.

    Parameter modules store distributions as dataclasses. This helper translates
    each dataclass into the corresponding NumPy random draw while preserving the
    shared random generator.
    """

    if isinstance(distribution, ScaledBetaDistribution):
        return sample_scaled_beta(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, TriangularDistribution):
        return sample_triangular(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, UniformDistribution):
        return sample_uniform(distribution=distribution, size=size, rng=rng)

    raise TypeError(f"Unsupported distribution type: {type(distribution)!r}")


def _sample_parameter(
    parameter: ParameterSpec,
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample stochastic parameters and broadcast fixed parameters.

    Fixed values are expanded to arrays with the same length as sampled values.
    This keeps the later cash-flow formulas vectorized and identical for fixed
    and uncertain inputs.
    """

    if isinstance(parameter, FixedParameter):
        return np.full(size, parameter.value)

    return _sample_distribution(distribution=parameter, size=size, rng=rng)


def _representative_parameter_array(
    parameter: ParameterSpec,
    size: int,
) -> np.ndarray:
    """Broadcast one deterministic expected input value to a sample array."""

    return np.full(size, representative_value(parameter))


def _sample_absolute_technology_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample absolute values for one non-retrofit electricity technology."""

    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute electricity technology: {technology!r}.")

    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _deterministic_bau_values(
    technology: str,
    size: int,
) -> dict[str, np.ndarray]:
    """Return expected parent-technology inputs as BAU arrays."""

    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity BAU technology: {technology!r}.")

    return {
        parameter_name: _representative_parameter_array(parameter, size=size)
        for parameter_name, parameter in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _sample_retrofit_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample BAU-relative changes for one electricity retrofit technology."""

    if technology not in ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity retrofit technology: {technology!r}.")

    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _fuel_price_parameter(technology: str) -> ParameterSpec:
    parameters = {
        "hard_coal": COAL_PRICE_DISTRIBUTION,
        "hard_coal_ccs": COAL_PRICE_DISTRIBUTION,
        "ccgt": GAS_PRICE_DISTRIBUTION,
        "ccgt_ccs": GAS_PRICE_DISTRIBUTION,
        "nuclear": NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_offshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_onshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "pv": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "biogas": BIOGAS_PRICE_EUR_PER_MWH_TH,
        "beccs": BIOMASS_PRICE_DISTRIBUTION,
    }
    try:
        return parameters[technology]
    except KeyError as error:
        raise ValueError(
            f"No fuel-price distribution configured for {technology!r}."
        ) from error


def simulate_electricity_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Sample electricity inputs and delegate resolved arrays to the model."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    all_technologies = (
        set(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
        | set(ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    generator = rng if rng is not None else np.random.default_rng()
    baseline_values: Mapping[str, np.ndarray] | None = None
    retrofit_values: Mapping[str, np.ndarray] | None = None
    if technology in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        parent_technologies = set(ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES.values())
        values = (
            dict(bau_values)
            if technology in parent_technologies and bau_values is not None
            else _sample_absolute_technology_values(technology, size, generator)
        )
        technology_type = "absolute"
        bau_mode = "not_applicable"
    else:
        parent = ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES[technology]
        baseline_values = (
            dict(bau_values)
            if retrofit_bau_mode == "sampled" and bau_values is not None
            else (
                _sample_absolute_technology_values(parent, size, generator)
                if retrofit_bau_mode == "sampled"
                else _deterministic_bau_values(parent, size)
            )
        )
        retrofit_values = _sample_retrofit_values(technology, size, generator)
        values = resolve_technology_values(baseline_values, retrofit_values)
        technology_type = "retrofit"
        bau_mode = retrofit_bau_mode

    fixed = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]
    full_load_hours = _sample_parameter(
        fixed["full_load_hours_per_year"], size=size, rng=generator
    )
    lifetime_years = fixed["lifetime_years"].value
    value_factor_parameter = fixed.get("value_factor")
    value_factor = (
        _sample_parameter(value_factor_parameter, size=size, rng=generator)
        if value_factor_parameter is not None
        else np.ones(size)
    )
    fuel_price_key = FUEL_PRICE_KEY_BY_TECHNOLOGY[technology]
    fuel_price = (
        _sample_parameter(_fuel_price_parameter(technology), size, generator)
        if market_values is None
        else market_values[fuel_price_key]
    )
    beccs_storage_cost = (
        _sample_parameter(
            BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION,
            size=size,
            rng=generator,
        )
        if technology == "beccs"
        else None
    )
    return calculate_result(
        technology=technology,
        technology_type=technology_type,
        bau_mode=bau_mode,
        values=values,
        size=size,
        full_load_hours=full_load_hours,
        lifetime_years=lifetime_years,
        value_factor=value_factor,
        fuel_price_eur_per_mwh_th=fuel_price,
        baseline_values=baseline_values,
        retrofit_values=retrofit_values,
        beccs_transport_and_storage_cost_eur_per_mwh=beccs_storage_cost,
    )


def simulate_hard_coal_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for the hard coal electricity plant."""

    return simulate_electricity_technology_npv(
        technology="hard_coal",
        size=size,
        rng=rng,
    )


def simulate_hard_coal_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a hard coal with CCS electricity plant."""

    return simulate_electricity_technology_npv(
        technology="hard_coal_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ccgt_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a CCGT electricity plant."""

    return simulate_electricity_technology_npv(
        technology="ccgt",
        size=size,
        rng=rng,
    )


def simulate_ccgt_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a CCGT with CCS electricity plant."""

    return simulate_electricity_technology_npv(
        technology="ccgt_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_nuclear_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a nuclear electricity plant."""

    return simulate_electricity_technology_npv(
        technology="nuclear",
        size=size,
        rng=rng,
    )


def simulate_wind_offshore_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for an offshore wind electricity plant."""

    return simulate_electricity_technology_npv(
        technology="wind_offshore",
        size=size,
        rng=rng,
    )


def simulate_wind_onshore_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for an onshore wind electricity plant."""

    return simulate_electricity_technology_npv(
        technology="wind_onshore",
        size=size,
        rng=rng,
    )


def simulate_pv_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a PV electricity plant."""

    return simulate_electricity_technology_npv(
        technology="pv",
        size=size,
        rng=rng,
    )


def simulate_biogas_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a biogas electricity plant."""

    return simulate_electricity_technology_npv(
        technology="biogas",
        size=size,
        rng=rng,
    )


def simulate_beccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a BECCS electricity plant."""

    return simulate_electricity_technology_npv(
        technology="beccs",
        size=size,
        rng=rng,
    )


def simulate_electricity_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run NPV simulations for multiple technologies with aligned run IDs.

    The same generator is passed through all technologies, and each technology
    receives run IDs from 0 to size-1. The rank calculation later uses those IDs
    to compare technologies within each Monte Carlo iteration.
    """

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)

    selected_technologies = technologies or tuple(
        ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS
    )
    # Reusing one generator keeps the random sequence reproducible across technologies
    # for a given top-level seed. Fuel prices are sampled once per run ID so
    # technologies sharing a fuel type are compared under the same market draw.
    generator = rng if rng is not None else np.random.default_rng()
    market_values = {
        "coal_price_eur_per_mwh_th": _sample_parameter(
            parameter=COAL_PRICE_DISTRIBUTION,
            size=size,
            rng=generator,
        ),
        "gas_price_eur_per_mwh_th": _sample_parameter(
            parameter=GAS_PRICE_DISTRIBUTION,
            size=size,
            rng=generator,
        ),
        "uranium_price_eur_per_mwh_th": _sample_parameter(
            parameter=NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=generator,
        ),
        "no_fuel_price_eur_per_mwh_th": _sample_parameter(
            parameter=NO_FUEL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=generator,
        ),
        "biogas_price_eur_per_mwh_th": _sample_parameter(
            parameter=BIOGAS_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=generator,
        ),
    }
    results: dict[str, Mapping[str, np.ndarray]] = {}
    sampled_bau_values: dict[str, Mapping[str, np.ndarray]] = {}
    retrofit_parent_technologies = {
        ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES[technology]
        for technology in selected_technologies
        if technology in ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES
    }
    for technology in selected_technologies:
        if (
            technology == "beccs"
            and "biomass_price_eur_per_mwh_th" not in market_values
        ):
            # BECCS is appended to the default registry. Sampling its shared
            # biomass price only when BECCS is reached preserves the seeded
            # draws of all pre-existing technologies.
            market_values["biomass_price_eur_per_mwh_th"] = _sample_parameter(
                parameter=BIOMASS_PRICE_DISTRIBUTION,
                size=size,
                rng=generator,
            )

        technology_bau_values = None
        if retrofit_bau_mode == "sampled":
            if technology in ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES:
                bau_technology = ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES[technology]
                if bau_technology not in sampled_bau_values:
                    sampled_bau_values[bau_technology] = (
                        _sample_absolute_technology_values(
                            technology=bau_technology,
                            size=size,
                            rng=generator,
                        )
                    )
                technology_bau_values = sampled_bau_values[bau_technology]
            elif technology in retrofit_parent_technologies:
                if technology not in sampled_bau_values:
                    sampled_bau_values[technology] = _sample_absolute_technology_values(
                        technology=technology,
                        size=size,
                        rng=generator,
                    )
                technology_bau_values = sampled_bau_values[technology]

        results[technology] = simulate_electricity_technology_npv(
            technology=technology,
            size=size,
            rng=generator,
            market_values=market_values,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=technology_bau_values,
        )
    return results


def simulate_electricity_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run electricity NPV simulations for all selected technologies.

    This is the public entry point used by notebooks and output scripts. Use the
    same sample size and seed to reproduce a previous electricity Monte Carlo run.
    """

    # The seed is applied once at the top-level simulation entry point.
    rng = np.random.default_rng(random_seed)
    return simulate_electricity_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )
