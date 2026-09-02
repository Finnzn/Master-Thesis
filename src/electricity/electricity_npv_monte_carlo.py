"""Monte Carlo NPV calculations for electricity technologies.

This module is the main electricity-sector simulation engine. For each
technology, it samples uncertain techno-economic inputs, sizes the plant to
produce the same annual electricity output, calculates annual costs and revenue,
and converts the resulting annual net cash flow into NPV.

Hard coal CCS and CCGT CCS are modelled as retrofits of their unabated parent
technologies. `retrofit_bau_mode` controls whether their BAU inputs are sampled
for each run ID or held at deterministic representative values while the
incremental retrofit inputs remain sampled.

The output intentionally includes both sampled inputs and derived financial
outputs. That makes each Monte Carlo result traceable from assumptions to NPV
when exported to CSV.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

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
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION,
    ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES,
    ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
    RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
)
from general_parameters import (
    BIOMASS_PRICE_DISTRIBUTION,
    BIOGAS_PRICE_EUR_PER_MWH_TH,
    CARBON_PRICE_EUR_PER_T,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    COAL_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
)
from npv_finance import (
    calculate_ccs_transport_and_storage_cost_per_output,
    calculate_discounted_lifetime_output,
    calculate_levelized_cost,
    calculate_levelized_net_margin,
    calculate_npv,
    calculate_total_cost_present_value,
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
    """Broadcast one deterministic representative value to a sample array."""

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
    """Return representative parent-technology values as BAU arrays."""

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


def _resolve_retrofit_values(
    bau_values: Mapping[str, np.ndarray],
    retrofit_values: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve absolute retrofit inputs from BAU arrays and sampled changes."""

    return {
        "capex_eur_per_kw": (
            bau_values["capex_eur_per_kw"]
            + retrofit_values["capex_change_eur_per_kw"]
        ),
        "fixed_opex_eur_per_kw_year": (
            bau_values["fixed_opex_eur_per_kw_year"]
            + retrofit_values["fixed_opex_change_eur_per_kw_year"]
        ),
        "variable_opex_eur_per_mwh": (
            bau_values["variable_opex_eur_per_mwh"]
            + retrofit_values["variable_opex_change_eur_per_mwh"]
        ),
        "fuel_consumption_mwh_th_per_mwh_e": (
            bau_values["fuel_consumption_mwh_th_per_mwh_e"]
            * (1.0 - retrofit_values["fuel_consumption_reduction_fraction"])
        ),
        "emissions_tco2_per_mwh_e": (
            bau_values["emissions_tco2_per_mwh_e"]
            * (1.0 - retrofit_values["emissions_reduction_fraction"])
        ),
    }


def simulate_electricity_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for one electricity technology.

    Absolute technologies are sampled directly. Retrofit technologies sample
    incremental inputs and resolve them against either sampled or deterministic
    parent-technology BAU values. Each returned array has length `size`.
    """

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    all_technologies = (
        set(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
        | set(ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    generator = rng if rng is not None else np.random.default_rng()
    technology_fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]

    baseline_values: Mapping[str, np.ndarray] | None = None
    retrofit_values: Mapping[str, np.ndarray] | None = None
    if technology in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        parent_technologies = set(ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES.values())
        values = (
            dict(bau_values)
            if technology in parent_technologies and bau_values is not None
            else _sample_absolute_technology_values(
                technology=technology,
                size=size,
                rng=generator,
            )
        )
        technology_type = "absolute"
        bau_mode = "not_applicable"
    else:
        bau_technology = ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES[technology]
        if retrofit_bau_mode == "sampled":
            baseline_values = (
                dict(bau_values)
                if bau_values is not None
                else _sample_absolute_technology_values(
                    technology=bau_technology,
                    size=size,
                    rng=generator,
                )
            )
        else:
            baseline_values = _deterministic_bau_values(
                technology=bau_technology,
                size=size,
            )
        retrofit_values = _sample_retrofit_values(
            technology=technology,
            size=size,
            rng=generator,
        )
        values = _resolve_retrofit_values(
            bau_values=baseline_values,
            retrofit_values=retrofit_values,
        )
        technology_type = "retrofit"
        bau_mode = retrofit_bau_mode

    # All technologies are normalized to the same annual electricity output. The
    # model therefore compares the economic value of supplying the same amount of
    # electricity, not the economics of arbitrary plant sizes.
    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = _sample_parameter(
        technology_fixed_parameters["full_load_hours_per_year"],
        size=size,
        rng=generator,
    )
    lifetime_years = technology_fixed_parameters["lifetime_years"].value
    value_factor_parameter = technology_fixed_parameters.get("value_factor")
    value_factor = (
        _sample_parameter(value_factor_parameter, size=size, rng=generator)
        if value_factor_parameter is not None
        else np.ones(size)
    )
    capacity_mw = annual_output_mwh / full_load_hours
    capacity_kw = capacity_mw * 1_000.0

    # Absolute and resolved retrofit values use one shared key schema, so the
    # capacity, cash-flow, and NPV formulas below remain technology-agnostic.
    capex_eur_per_kw = values["capex_eur_per_kw"]
    fixed_opex_eur_per_kw_year = values["fixed_opex_eur_per_kw_year"]
    variable_opex_eur_per_mwh = values["variable_opex_eur_per_mwh"]
    fuel_consumption_mwh_th_per_mwh_e = values[
        "fuel_consumption_mwh_th_per_mwh_e"
    ]
    emissions_tco2_per_mwh_e = values["emissions_tco2_per_mwh_e"]
    # Fuel prices are shared by fuel type, while renewable technologies use zero
    # fuel cost. This avoids duplicating the same gas or coal price assumption in
    # every technology definition.
    fuel_price_distribution_by_technology = {
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
    fuel_price_key_by_technology = {
        "hard_coal": "coal_price_eur_per_mwh_th",
        "hard_coal_ccs": "coal_price_eur_per_mwh_th",
        "ccgt": "gas_price_eur_per_mwh_th",
        "ccgt_ccs": "gas_price_eur_per_mwh_th",
        "nuclear": "uranium_price_eur_per_mwh_th",
        "wind_offshore": "no_fuel_price_eur_per_mwh_th",
        "wind_onshore": "no_fuel_price_eur_per_mwh_th",
        "pv": "no_fuel_price_eur_per_mwh_th",
        "biogas": "biogas_price_eur_per_mwh_th",
        "beccs": "biomass_price_eur_per_mwh_th",
    }
    if technology not in fuel_price_distribution_by_technology:
        raise ValueError(f"No fuel-price distribution configured for {technology!r}.")

    fuel_price_key = fuel_price_key_by_technology[technology]
    if market_values is None:
        fuel_price_eur_per_mwh_th = _sample_parameter(
            parameter=fuel_price_distribution_by_technology[technology],
            size=size,
            rng=generator,
        )
    else:
        fuel_price_eur_per_mwh_th = market_values[fuel_price_key]
    electricity_price_eur_per_mwh = RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value
    captured_electricity_price_eur_per_mwh = (
        electricity_price_eur_per_mwh * value_factor
    )

    # Renewable value factors scale the common sales-price proxy to the captured
    # price. Annual cash flow is revenue minus operating, fuel, and carbon-cost
    # terms; CAPEX is handled separately in the NPV formula.
    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = (
        annual_output_mwh * captured_electricity_price_eur_per_mwh
    )
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * fuel_price_eur_per_mwh_th
    )
    capture_cost_excluding_transport_and_storage_eur_per_mwh = np.full(
        size, np.nan
    )
    transport_and_storage_cost_eur_per_mwh = np.zeros(size)
    transport_and_storage_share_of_capture_cost = np.full(size, np.nan)
    if baseline_values is not None:
        transport_and_storage_share_of_capture_cost = np.full(
            size,
            CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value,
        )
        bau_initial_capex_eur = capacity_kw * baseline_values["capex_eur_per_kw"]
        bau_annual_cost_excluding_carbon_eur = (
            capacity_kw * baseline_values["fixed_opex_eur_per_kw_year"]
            + annual_output_mwh * baseline_values["variable_opex_eur_per_mwh"]
            + annual_output_mwh
            * baseline_values["fuel_consumption_mwh_th_per_mwh_e"]
            * fuel_price_eur_per_mwh_th
        )
        annual_cost_excluding_carbon_eur = (
            annual_fixed_opex_eur
            + annual_variable_opex_eur
            + annual_fuel_cost_eur
        )
        (
            capture_cost_excluding_transport_and_storage_eur_per_mwh,
            transport_and_storage_cost_eur_per_mwh,
        ) = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=initial_capex_eur,
            bau_initial_capex_eur=bau_initial_capex_eur,
            ccs_annual_cost_excluding_carbon_eur=(
                annual_cost_excluding_carbon_eur
            ),
            bau_annual_cost_excluding_carbon_eur=(
                bau_annual_cost_excluding_carbon_eur
            ),
            annual_output=annual_output_mwh,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
            ),
        )
    elif technology == "beccs":
        transport_and_storage_cost_eur_per_mwh = _sample_parameter(
            BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION,
            size=size,
            rng=generator,
        )
    annual_transport_and_storage_cost_eur = (
        annual_output_mwh * transport_and_storage_cost_eur_per_mwh
    )
    # For BECCS, sampled emissions are negative. The resulting negative
    # carbon-cost value is subtracted from cash flow and therefore acts as
    # carbon-removal revenue while retaining one shared formula.
    annual_emissions_cost_eur = (
        annual_output_mwh * emissions_tco2_per_mwh_e * CARBON_PRICE_EUR_PER_T.value
    )
    annual_net_cash_flow_eur = (
        annual_revenue_eur
        - annual_fixed_opex_eur
        - annual_variable_opex_eur
        - annual_fuel_cost_eur
        - annual_transport_and_storage_cost_eur
        - annual_emissions_cost_eur
    )
    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_transport_and_storage_cost_eur
        + annual_emissions_cost_eur
    )
    npv_eur = calculate_npv(
        initial_capex_eur=initial_capex_eur,
        annual_net_cash_flow_eur=annual_net_cash_flow_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    discounted_lifetime_output_mwh = calculate_discounted_lifetime_output(
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    levelized_net_margin_eur_per_mwh = calculate_levelized_net_margin(
        npv_eur=npv_eur,
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    present_value_total_cost_eur = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    lcoe_eur_per_mwh = calculate_levelized_cost(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )

    # Return both sampled inputs and derived outputs so CSV exports are traceable.
    # `run_id` links technologies when they are ranked within the same simulation.
    result = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, technology_type),
        "retrofit_bau_mode": np.full(size, bau_mode),
        "annual_output_mwh": np.full(size, annual_output_mwh),
        "full_load_hours_per_year": full_load_hours,
        "lifetime_years": np.full(size, lifetime_years),
        "capacity_mw": capacity_mw,
        "capacity_kw": capacity_kw,
        "capex_eur_per_kw": capex_eur_per_kw,
        "fixed_opex_eur_per_kw_year": fixed_opex_eur_per_kw_year,
        "variable_opex_eur_per_mwh": variable_opex_eur_per_mwh,
        "fuel_consumption_mwh_th_per_mwh_e": fuel_consumption_mwh_th_per_mwh_e,
        "emissions_tco2_per_mwh_e": emissions_tco2_per_mwh_e,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        fuel_price_key: fuel_price_eur_per_mwh_th,
        "electricity_price_eur_per_mwh": np.full(size, electricity_price_eur_per_mwh),
        "value_factor": value_factor,
        "captured_electricity_price_eur_per_mwh": (
            captured_electricity_price_eur_per_mwh
        ),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "capture_cost_excluding_transport_and_storage_eur_per_mwh": (
            capture_cost_excluding_transport_and_storage_eur_per_mwh
        ),
        "transport_and_storage_cost_eur_per_mwh": (
            transport_and_storage_cost_eur_per_mwh
        ),
        "transport_and_storage_share_of_capture_cost": (
            transport_and_storage_share_of_capture_cost
        ),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output_mwh": np.full(
            size, discounted_lifetime_output_mwh
        ),
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "lcoe_eur_per_mwh": lcoe_eur_per_mwh,
        "levelized_net_margin_eur_per_mwh": levelized_net_margin_eur_per_mwh,
    }

    if baseline_values is not None:
        for parameter_name, baseline_value in baseline_values.items():
            result[f"bau_{parameter_name}"] = baseline_value

    if retrofit_values is not None:
        result.update(retrofit_values)

    return result


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
