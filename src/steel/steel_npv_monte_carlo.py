"""Monte Carlo input provider for the shared steel NPV model.

This module samples technology and market assumptions and delegates retrofit
resolution, sector costs, and financial-result assembly to
:mod:`steel.steel_npv_model`. Shared market arrays and sampled BAU arrays are
reused across technologies with the same run IDs.
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
from general_parameters import (
    CHARCOAL_PRICE_EUR_PER_MWH_TH,
    ELECTRICITY_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    GREEN_HYDROGEN_PRICE_EUR_PER_KG,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
)
from npv_summary import representative_value
from steel.steel_npv_model import calculate_result, resolve_technology_values
from steel.steel_parameters import (
    STEEL_RETROFIT_BASE_TECHNOLOGIES,
    STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    STEEL_TECHNOLOGY_DISTRIBUTIONS,
)


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
    """Sample a stochastic parameter or broadcast a fixed value."""

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
    """Sample absolute steel inputs from the technology registry."""

    if technology not in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute steel technology: {technology!r}.")
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in STEEL_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _deterministic_bau_values(
    technology: str,
    size: int,
) -> dict[str, np.ndarray]:
    """Return expected parent-technology inputs as sample arrays."""

    if technology not in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown steel BAU technology: {technology!r}.")
    return {
        parameter_name: _representative_parameter_array(parameter, size=size)
        for parameter_name, parameter in STEEL_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _sample_retrofit_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample incremental changes for one steel retrofit technology."""

    if technology not in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown steel retrofit technology: {technology!r}.")
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _sample_market_values(
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample or broadcast market assumptions shared across steel technologies."""

    return {
        "pci_coking_coal_mix_price_eur_per_mwh_th": _sample_parameter(
            PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "charcoal_price_eur_per_mwh_th": _sample_parameter(
            CHARCOAL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "gas_price_eur_per_mwh_th": _sample_parameter(
            GAS_PRICE_DISTRIBUTION,
            size=size,
            rng=rng,
        ),
        "green_hydrogen_price_eur_per_kg": _sample_parameter(
            GREEN_HYDROGEN_PRICE_EUR_PER_KG,
            size=size,
            rng=rng,
        ),
        "no_fuel_price_eur_per_mwh_th": _sample_parameter(
            NO_FUEL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "electricity_price_eur_per_mwh": _sample_parameter(
            ELECTRICITY_PRICE_DISTRIBUTION,
            size=size,
            rng=rng,
        ),
    }


def simulate_steel_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for one steel technology."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    all_technologies = (
        set(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        | set(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"Unknown steel technology: {technology!r}.")

    generator = rng if rng is not None else np.random.default_rng()
    shared_market_values = (
        dict(market_values)
        if market_values is not None
        else _sample_market_values(size=size, rng=generator)
    )

    if technology in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        parent_technologies = set(STEEL_RETROFIT_BASE_TECHNOLOGIES.values())
        values = (
            dict(bau_values)
            if technology in parent_technologies and bau_values is not None
            else _sample_absolute_technology_values(
                technology=technology,
                size=size,
                rng=generator,
            )
        )
        return calculate_result(
            technology=technology,
            technology_type="absolute",
            bau_mode="not_applicable",
            values=values,
            size=size,
            market_values=shared_market_values,
        )

    bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
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
    values = resolve_technology_values(
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
    )
    return calculate_result(
        technology=technology,
        technology_type="retrofit",
        bau_mode=retrofit_bau_mode,
        values=values,
        size=size,
        market_values=shared_market_values,
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
    )


def simulate_bf_bof_bau_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for BF-BOF BAU."""

    return simulate_steel_technology_npv("bf_bof_bau", size=size, rng=rng)


def simulate_scrap_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for Scrap-EAF."""

    return simulate_steel_technology_npv("scrap_eaf", size=size, rng=rng)


def simulate_ng_dri_eaf_bau_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for NG-DRI-EAF BAU."""

    return simulate_steel_technology_npv("ng_dri_eaf_bau", size=size, rng=rng)


def simulate_h2_dri_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for H2-DRI-EAF."""

    return simulate_steel_technology_npv("h2_dri_eaf", size=size, rng=rng)


def simulate_moe_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for molten oxide electrolysis."""

    return simulate_steel_technology_npv("moe", size=size, rng=rng)


def simulate_ael_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for AEL-EAF."""

    return simulate_steel_technology_npv("ael_eaf", size=size, rng=rng)


def simulate_bf_bof_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for BF + BOF + CCS."""

    return simulate_steel_technology_npv(
        "bf_bof_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ng_dri_eaf_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for NG-DRI-EAF CCS."""

    return simulate_steel_technology_npv(
        "ng_dri_eaf_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_steel_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run aligned Monte Carlo simulations for multiple steel technologies."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    selected_technologies = technologies or tuple(
        list(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        + list(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    all_technologies = (
        set(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        | set(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    unknown_technologies = set(selected_technologies) - all_technologies
    if unknown_technologies:
        raise ValueError(
            f"Unknown steel technologies: {sorted(unknown_technologies)!r}."
        )

    generator = rng if rng is not None else np.random.default_rng()
    market_values = _sample_market_values(size=size, rng=generator)
    retrofit_parent_technologies = {
        STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        for technology in selected_technologies
        if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES
    }
    sampled_bau_values: dict[str, Mapping[str, np.ndarray]] = {}
    results: dict[str, Mapping[str, np.ndarray]] = {}
    for technology in selected_technologies:
        technology_bau_values = None
        if retrofit_bau_mode == "sampled":
            if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES:
                bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
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
                    sampled_bau_values[technology] = (
                        _sample_absolute_technology_values(
                            technology=technology,
                            size=size,
                            rng=generator,
                        )
                    )
                technology_bau_values = sampled_bau_values[technology]

        results[technology] = simulate_steel_technology_npv(
            technology=technology,
            size=size,
            rng=generator,
            market_values=market_values,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=technology_bau_values,
        )
    return results


def simulate_steel_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run reproducible steel NPV simulations for selected technologies."""

    rng = np.random.default_rng(random_seed)
    return simulate_steel_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )
