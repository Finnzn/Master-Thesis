"""Deterministic hydrogen NPV input provider.

Representative inputs are resolved by the shared sector model and returned as
one-row result mappings for exports and notebooks.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from hydrogen.hydrogen_npv_model import (
    HYDROGEN_TECHNOLOGIES,
    ENERGY_CARRIERS,
    FUEL_TYPE_BY_TECHNOLOGY,
    MARKET_PARAMETERS,
    PRICE_KEY_BY_CARRIER,
    calculate_result,
    resolve_technology_values,
)
from hydrogen.hydrogen_parameters import (
    HYDROGEN_RETROFIT_BASE_TECHNOLOGIES,
    HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    HYDROGEN_TECHNOLOGY_DISTRIBUTIONS,
)
from npv_summary import representative_value


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def _representative_values(
    parameters: Mapping[str, ParameterSpec],
) -> dict[str, np.ndarray]:
    """Choose one representative value for every deterministic input."""

    return {
        name: np.full(1, representative_value(parameter), dtype=float)
        for name, parameter in parameters.items()
    }


def _absolute_values(technology: str) -> dict[str, np.ndarray]:
    if technology not in HYDROGEN_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute hydrogen technology: {technology!r}.")
    return _representative_values(HYDROGEN_TECHNOLOGY_DISTRIBUTIONS[technology])


def calculate_deterministic_hydrogen_result(technology: str) -> Mapping[str, object]:
    """Calculate a one-row result using every uncertain parameter's mean."""

    if technology not in HYDROGEN_TECHNOLOGIES:
        raise ValueError(f"Unknown hydrogen technology: {technology!r}.")
    prices = _representative_values(MARKET_PARAMETERS)
    if technology in HYDROGEN_RETROFIT_BASE_TECHNOLOGIES:
        parent_name = HYDROGEN_RETROFIT_BASE_TECHNOLOGIES[technology]
        parent = _absolute_values(parent_name)
        increments = _representative_values(
            HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
        )
        values = resolve_technology_values(technology, parent, increments)
        result = calculate_result(
            technology,
            values,
            prices,
            retrofit_bau_mode="deterministic",
            parent_values=parent,
            increments=increments,
        )
    else:
        values = _absolute_values(technology)
        result = calculate_result(technology, values, prices)
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_hydrogen_npv_eur(technology: str) -> float:
    """Return the expected-input NPV for one hydrogen technology."""

    return float(calculate_deterministic_hydrogen_result(technology)["npv_eur"][0])


def calculate_deterministic_hydrogen_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate expected-input results for selected or all hydrogen routes."""

    selected = HYDROGEN_TECHNOLOGIES if technologies is None else technologies
    return {
        technology: calculate_deterministic_hydrogen_result(technology)
        for technology in selected
    }
