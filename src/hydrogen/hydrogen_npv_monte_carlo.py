"""Monte Carlo input provider for the shared hydrogen NPV model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from hydrogen.hydrogen_npv_model import (
    HYDROGEN_TECHNOLOGIES,
    MARKET_PARAMETERS,
    calculate_result,
    resolve_technology_values,
)
from hydrogen.hydrogen_parameters import (
    HYDROGEN_RETROFIT_BASE_TECHNOLOGIES,
    HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    HYDROGEN_TECHNOLOGY_DISTRIBUTIONS,
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


def _parameter_values(
    parameters: Mapping[str, ParameterSpec],
    size: int,
    rng: np.random.Generator | None,
) -> dict[str, np.ndarray]:
    """Sample Monte Carlo inputs, or broadcast means for deterministic BAU."""

    values: dict[str, np.ndarray] = {}
    for name, parameter in parameters.items():
        if rng is None or isinstance(parameter, FixedParameter):
            values[name] = np.full(
                size, representative_value(parameter), dtype=float
            )
        elif isinstance(parameter, ScaledBetaDistribution):
            values[name] = sample_scaled_beta(parameter, size=size, rng=rng)
        elif isinstance(parameter, TriangularDistribution):
            values[name] = sample_triangular(parameter, size=size, rng=rng)
        elif isinstance(parameter, UniformDistribution):
            values[name] = sample_uniform(parameter, size=size, rng=rng)
        else:
            raise TypeError(f"Unsupported parameter type: {type(parameter)!r}.")
    return values


def _absolute_values(
    technology: str,
    size: int,
    rng: np.random.Generator | None,
) -> dict[str, np.ndarray]:
    if technology not in HYDROGEN_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute hydrogen technology: {technology!r}.")
    return _parameter_values(
        HYDROGEN_TECHNOLOGY_DISTRIBUTIONS[technology], size=size, rng=rng
    )


def _validate(size: int, retrofit_bau_mode: str) -> None:
    if size <= 0:
        raise ValueError("size must be positive.")
    if retrofit_bau_mode not in RETROFIT_BAU_MODES:
        raise ValueError(
            f"retrofit_bau_mode must be one of {RETROFIT_BAU_MODES!r}."
        )


def simulate_hydrogen_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Simulate one hydrogen route, with optional shared prices and parent draws."""

    _validate(size, retrofit_bau_mode)
    if technology not in HYDROGEN_TECHNOLOGIES:
        raise ValueError(f"Unknown hydrogen technology: {technology!r}.")
    generator = rng if rng is not None else np.random.default_rng()
    prices = (
        dict(market_values)
        if market_values is not None
        else _parameter_values(MARKET_PARAMETERS, size=size, rng=generator)
    )
    if technology not in HYDROGEN_RETROFIT_BASE_TECHNOLOGIES:
        values = (
            dict(bau_values)
            if bau_values is not None
            else _absolute_values(technology, size=size, rng=generator)
        )
        return calculate_result(technology, values, prices)

    parent_name = HYDROGEN_RETROFIT_BASE_TECHNOLOGIES[technology]
    parent = (
        dict(bau_values)
        if bau_values is not None and retrofit_bau_mode == "sampled"
        else _absolute_values(
            parent_name,
            size=size,
            rng=generator if retrofit_bau_mode == "sampled" else None,
        )
    )
    increments = _parameter_values(
        HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology],
        size=size,
        rng=generator,
    )
    values = resolve_technology_values(technology, parent, increments)
    return calculate_result(
        technology,
        values,
        prices,
        retrofit_bau_mode=retrofit_bau_mode,
        parent_values=parent,
        increments=increments,
    )


def simulate_hydrogen_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run selected routes with aligned price and sampled-parent arrays."""

    _validate(size, retrofit_bau_mode)
    selected = HYDROGEN_TECHNOLOGIES if technologies is None else technologies
    unknown = set(selected) - set(HYDROGEN_TECHNOLOGIES)
    if unknown:
        raise ValueError(f"Unknown hydrogen technologies: {sorted(unknown)!r}.")
    generator = rng if rng is not None else np.random.default_rng()
    prices = _parameter_values(MARKET_PARAMETERS, size=size, rng=generator)
    parents_needed = {
        HYDROGEN_RETROFIT_BASE_TECHNOLOGIES[technology]
        for technology in selected
        if technology in HYDROGEN_RETROFIT_BASE_TECHNOLOGIES
    }
    shared_parents = (
        {
            parent: _absolute_values(parent, size=size, rng=generator)
            for parent in HYDROGEN_TECHNOLOGIES
            if parent in parents_needed
        }
        if retrofit_bau_mode == "sampled"
        else {}
    )
    return {
        technology: simulate_hydrogen_technology_npv(
            technology,
            size=size,
            rng=generator,
            market_values=prices,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=shared_parents.get(
                HYDROGEN_RETROFIT_BASE_TECHNOLOGIES.get(technology, technology)
            ),
        )
        for technology in selected
    }


def simulate_hydrogen_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run reproducible aligned hydrogen simulations."""

    return simulate_hydrogen_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=np.random.default_rng(random_seed),
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ng_smr_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("ng_smr", size=size, rng=rng)


def simulate_ael_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("ael", size=size, rng=rng)


def simulate_pem_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("pem", size=size, rng=rng)


def simulate_soec_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("soec", size=size, rng=rng)


def simulate_methane_pyrolysis_tcd_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("methane_pyrolysis_tcd", size=size, rng=rng)


def simulate_biomass_gasification_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_hydrogen_technology_npv("biomass_gasification", size=size, rng=rng)


def simulate_biomethane_smr_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
):
    return simulate_hydrogen_technology_npv(
        "biomethane_smr", size=size, rng=rng, retrofit_bau_mode=retrofit_bau_mode
    )


def simulate_ng_smr_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
):
    return simulate_hydrogen_technology_npv(
        "ng_smr_ccs", size=size, rng=rng, retrofit_bau_mode=retrofit_bau_mode
    )
