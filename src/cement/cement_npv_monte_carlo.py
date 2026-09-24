"""Monte Carlo input provider for the shared cement NPV model.

This module samples aligned uncertain inputs and delegates technology
resolution, sector costs, and financial-result assembly to
:mod:`cement.cement_npv_model`. The cement-specific input wrinkle is retrofit
handling: retrofit assumptions are defined relative to BAU.

For retrofit technologies, `retrofit_bau_mode` controls that baseline:

- `"sampled"` samples BAU once per run ID and reuses those sampled BAU values for
  every retrofit technology in the same simulation. This is the default for full
  uncertainty propagation and cross-technology ranking.
- `"deterministic"` uses expected BAU input values and samples only the retrofit
  distributions. This is useful for diagnostics and technology-specific notebooks.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from cement.cement_npv_model import calculate_result, resolve_technology_values
from cement.cement_parameters import (
    CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    CEMENT_TECHNOLOGY_DISTRIBUTIONS,
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
from general_parameters import (
    BIOFUEL_PRICE_DISTRIBUTION,
    COAL_PRICE_DISTRIBUTION,
    ELECTRICITY_PRICE_DISTRIBUTION,
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
    """Dispatch one supported stochastic parameter to its sampler."""

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
    """Sample stochastic parameters and broadcast fixed parameters."""

    if isinstance(parameter, FixedParameter):
        return np.full(size, parameter.value)

    return _sample_distribution(distribution=parameter, size=size, rng=rng)


def _representative_parameter_array(
    parameter: ParameterSpec,
    size: int,
) -> np.ndarray:
    """Broadcast one deterministic expected input value to a sample array."""

    return np.full(size, representative_value(parameter))


def cement_fuel_price_parameter(
    technology: str,
) -> ScaledBetaDistribution | UniformDistribution:
    """Return the fossil fuel-price source for a cement technology."""

    all_technologies = (
        set(CEMENT_TECHNOLOGY_DISTRIBUTIONS)
        | set(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"No fuel-price parameter configured for {technology!r}.")

    return COAL_PRICE_DISTRIBUTION


def _sample_absolute_technology_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample absolute cement technology values from the technology registry."""

    if technology not in CEMENT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute cement technology: {technology!r}.")

    distributions = CEMENT_TECHNOLOGY_DISTRIBUTIONS[technology]
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in distributions.items()
    }


def _deterministic_bau_values(size: int) -> dict[str, np.ndarray]:
    """Return deterministic BAU values as arrays for retrofit baselines."""

    bau_distributions = CEMENT_TECHNOLOGY_DISTRIBUTIONS["bau"]
    return {
        parameter_name: _representative_parameter_array(parameter, size=size)
        for parameter_name, parameter in bau_distributions.items()
    }


def _sample_retrofit_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample BAU-relative retrofit changes for one retrofit technology."""

    if technology not in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown cement retrofit technology: {technology!r}.")

    retrofit_distributions = CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in retrofit_distributions.items()
    }


def _sample_market_values(
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample the market inputs consumed by the shared cement model."""

    return {
        "coal_price_eur_per_mwh_th": _sample_parameter(
            COAL_PRICE_DISTRIBUTION, size=size, rng=rng
        ),
        "biofuel_price_eur_per_mwh_th": _sample_parameter(
            BIOFUEL_PRICE_DISTRIBUTION, size=size, rng=rng
        ),
        "electricity_price_eur_per_mwh": _sample_parameter(
            ELECTRICITY_PRICE_DISTRIBUTION, size=size, rng=rng
        ),
    }


def simulate_cement_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for one cement technology.

    BAU and alternative technologies are sampled as absolute technologies.
    Retrofit technologies sample retrofit changes and resolve them against
    either a sampled or deterministic BAU baseline.
    """

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)

    generator = rng if rng is not None else np.random.default_rng()

    if technology in CEMENT_TECHNOLOGY_DISTRIBUTIONS:
        values = (
            dict(bau_values)
            if technology == "bau" and bau_values is not None
            else _sample_absolute_technology_values(
                technology=technology,
                size=size,
                rng=generator,
            )
        )
        prices = (
            dict(market_values)
            if market_values is not None
            else _sample_market_values(size=size, rng=generator)
        )
        return calculate_result(
            technology=technology,
            technology_type="absolute",
            bau_mode="not_applicable",
            values=values,
            size=size,
            market_values=prices,
        )

    if technology not in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown cement technology: {technology!r}.")

    if retrofit_bau_mode == "sampled":
        baseline_values = (
            dict(bau_values)
            if bau_values is not None
            else _sample_absolute_technology_values(
                technology="bau",
                size=size,
                rng=generator,
            )
        )
    else:
        baseline_values = _deterministic_bau_values(size=size)

    retrofit_values = _sample_retrofit_values(
        technology=technology,
        size=size,
        rng=generator,
    )
    values = resolve_technology_values(
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
    )
    prices = (
        dict(market_values)
        if market_values is not None
        else _sample_market_values(size=size, rng=generator)
    )
    return calculate_result(
        technology=technology,
        technology_type="retrofit",
        bau_mode=retrofit_bau_mode,
        values=values,
        size=size,
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
        market_values=prices,
    )


def simulate_bau_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for BAU cement."""

    return simulate_cement_technology_npv(
        technology="bau",
        size=size,
        rng=rng,
    )


def simulate_electrification_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for electrification cement."""

    return simulate_cement_technology_npv(
        technology="electrification",
        size=size,
        rng=rng,
    )


def simulate_electrolysis_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for electrolysis cement."""

    return simulate_cement_technology_npv(
        technology="electrolysis",
        size=size,
        rng=rng,
    )


def simulate_clinker_substitution_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for clinker substitution cement."""

    return simulate_cement_technology_npv(
        technology="clinker_substitution",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_alternative_fuels_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for alternative fuels cement."""

    return simulate_cement_technology_npv(
        technology="alternative_fuels",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_efficiency_improvement_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for efficiency improvement cement."""

    return simulate_cement_technology_npv(
        technology="efficiency_improvement",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_waste_heat_recovery_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for waste heat recovery cement."""

    return simulate_cement_technology_npv(
        technology="waste_heat_recovery",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for CCS cement."""

    return simulate_cement_technology_npv(
        technology="ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_process_heat_integration_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for process heat integration cement."""

    return simulate_cement_technology_npv(
        technology="process_heat_integration",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_cement_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run NPV simulations for multiple cement technologies with aligned IDs."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)

    selected_technologies = technologies or tuple(
        list(CEMENT_TECHNOLOGY_DISTRIBUTIONS)
        + list(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    generator = rng if rng is not None else np.random.default_rng()

    sampled_bau_values = None
    if (
        retrofit_bau_mode == "sampled"
        and any(
            technology in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
            for technology in selected_technologies
        )
    ):
        sampled_bau_values = _sample_absolute_technology_values(
            technology="bau",
            size=size,
            rng=generator,
        )

    market_values = {
        "coal_price_eur_per_mwh_th": _sample_parameter(
            COAL_PRICE_DISTRIBUTION,
            size=size,
            rng=generator,
        ),
        "biofuel_price_eur_per_mwh_th": _sample_parameter(
            BIOFUEL_PRICE_DISTRIBUTION,
            size=size,
            rng=generator,
        ),
        "electricity_price_eur_per_mwh": _sample_parameter(
            ELECTRICITY_PRICE_DISTRIBUTION,
            size=size,
            rng=generator,
        ),
    }

    return {
        technology: simulate_cement_technology_npv(
            technology=technology,
            size=size,
            rng=generator,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=sampled_bau_values,
            market_values=market_values,
        )
        for technology in selected_technologies
    }


def simulate_cement_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run cement NPV simulations for all selected technologies."""

    rng = np.random.default_rng(random_seed)
    return simulate_cement_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )
