"""Aligned Monte Carlo NPV simulations for ammonia technologies."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from ammonia._ammonia_model import (
    AMMONIA_TECHNOLOGIES,
    absolute_values,
    calculate_result,
    market_values as draw_market_values,
    parameter_values,
    resolve_retrofit_values,
)
from ammonia.ammonia_parameters import (
    AMMONIA_RETROFIT_BASE_TECHNOLOGIES,
    AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
)


DEFAULT_SAMPLE_SIZE = 100_000
DEFAULT_RANDOM_SEED = 42
DEFAULT_RETROFIT_BAU_MODE = "sampled"
RETROFIT_BAU_MODES = ("sampled", "deterministic")


def _validate(size: int, retrofit_bau_mode: str) -> None:
    if size <= 0:
        raise ValueError("size must be positive.")
    if retrofit_bau_mode not in RETROFIT_BAU_MODES:
        raise ValueError(
            f"retrofit_bau_mode must be one of {RETROFIT_BAU_MODES!r}."
        )


def simulate_ammonia_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Simulate one ammonia route, with optional shared prices and parent draws."""

    _validate(size, retrofit_bau_mode)
    if technology not in AMMONIA_TECHNOLOGIES:
        raise ValueError(f"Unknown ammonia technology: {technology!r}.")
    generator = rng if rng is not None else np.random.default_rng()
    prices = (
        dict(market_values)
        if market_values is not None
        else draw_market_values(size=size, rng=generator)
    )
    if technology not in AMMONIA_RETROFIT_BASE_TECHNOLOGIES:
        values = (
            dict(bau_values)
            if bau_values is not None
            else absolute_values(technology, size=size, rng=generator)
        )
        return calculate_result(technology, values, prices)

    parent_name = AMMONIA_RETROFIT_BASE_TECHNOLOGIES[technology]
    parent = (
        dict(bau_values)
        if bau_values is not None and retrofit_bau_mode == "sampled"
        else absolute_values(
            parent_name,
            size=size,
            rng=generator if retrofit_bau_mode == "sampled" else None,
        )
    )
    increments = parameter_values(
        AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology],
        size=size,
        rng=generator,
    )
    values = resolve_retrofit_values(technology, parent, increments)
    return calculate_result(
        technology,
        values,
        prices,
        retrofit_bau_mode=retrofit_bau_mode,
        parent_values=parent,
        increments=increments,
    )


def simulate_ammonia_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run selected routes with aligned price and sampled-parent arrays."""

    _validate(size, retrofit_bau_mode)
    selected = AMMONIA_TECHNOLOGIES if technologies is None else technologies
    unknown = set(selected) - set(AMMONIA_TECHNOLOGIES)
    if unknown:
        raise ValueError(f"Unknown ammonia technologies: {sorted(unknown)!r}.")
    generator = rng if rng is not None else np.random.default_rng()
    prices = draw_market_values(size=size, rng=generator)
    parents_needed = {
        AMMONIA_RETROFIT_BASE_TECHNOLOGIES[technology]
        for technology in selected
        if technology in AMMONIA_RETROFIT_BASE_TECHNOLOGIES
    }
    shared_parents = (
        {
            parent: absolute_values(parent, size=size, rng=generator)
            for parent in AMMONIA_TECHNOLOGIES
            if parent in parents_needed
        }
        if retrofit_bau_mode == "sampled"
        else {}
    )
    return {
        technology: simulate_ammonia_technology_npv(
            technology,
            size=size,
            rng=generator,
            market_values=prices,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=shared_parents.get(
                AMMONIA_RETROFIT_BASE_TECHNOLOGIES.get(technology, technology)
            ),
        )
        for technology in selected
    }


def simulate_ammonia_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run reproducible aligned ammonia simulations."""

    return simulate_ammonia_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=np.random.default_rng(random_seed),
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ng_smr_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("ng_smr_hb", size=size, rng=rng)


def simulate_coal_gasification_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("coal_gasification_hb", size=size, rng=rng)


def simulate_ael_pem_electrolysis_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("ael_pem_electrolysis_hb", size=size, rng=rng)


def simulate_biomass_gasification_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("biomass_gasification_hb", size=size, rng=rng)


def simulate_methane_pyrolysis_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("methane_pyrolysis_hb", size=size, rng=rng)


def simulate_soec_hb_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("soec_hb", size=size, rng=rng)


def simulate_aqueous_direct_nrr_npv(size: int, rng: np.random.Generator | None = None):
    return simulate_ammonia_technology_npv("aqueous_direct_nrr", size=size, rng=rng)


def simulate_ng_smr_hb_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
):
    return simulate_ammonia_technology_npv(
        "ng_smr_hb_ccs", size=size, rng=rng, retrofit_bau_mode=retrofit_bau_mode
    )


def simulate_coal_gasification_hb_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
):
    return simulate_ammonia_technology_npv(
        "coal_gasification_hb_ccs", size=size, rng=rng, retrofit_bau_mode=retrofit_bau_mode
    )
