"""Expected-input ammonia NPV, LCOA, and levelized-margin calculations."""

from __future__ import annotations

from typing import Mapping

from ammonia._ammonia_model import (
    AMMONIA_TECHNOLOGIES,
    absolute_values,
    calculate_result,
    market_values,
    parameter_values,
    resolve_retrofit_values,
)
from ammonia.ammonia_parameters import (
    AMMONIA_RETROFIT_BASE_TECHNOLOGIES,
    AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
)


def calculate_deterministic_ammonia_result(technology: str) -> Mapping[str, object]:
    """Calculate a one-row result using every uncertain parameter's mean."""

    if technology not in AMMONIA_TECHNOLOGIES:
        raise ValueError(f"Unknown ammonia technology: {technology!r}.")
    prices = market_values(size=1, rng=None)
    if technology in AMMONIA_RETROFIT_BASE_TECHNOLOGIES:
        parent_name = AMMONIA_RETROFIT_BASE_TECHNOLOGIES[technology]
        parent = absolute_values(parent_name, size=1, rng=None)
        increments = parameter_values(
            AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology],
            size=1,
            rng=None,
        )
        values = resolve_retrofit_values(technology, parent, increments)
        result = calculate_result(
            technology,
            values,
            prices,
            retrofit_bau_mode="deterministic",
            parent_values=parent,
            increments=increments,
        )
    else:
        values = absolute_values(technology, size=1, rng=None)
        result = calculate_result(technology, values, prices)
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_ammonia_npv_eur(technology: str) -> float:
    """Return the expected-input NPV for one ammonia technology."""

    return float(calculate_deterministic_ammonia_result(technology)["npv_eur"][0])


def calculate_deterministic_ammonia_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate expected-input results for selected or all ammonia routes."""

    selected = AMMONIA_TECHNOLOGIES if technologies is None else technologies
    return {
        technology: calculate_deterministic_ammonia_result(technology)
        for technology in selected
    }
