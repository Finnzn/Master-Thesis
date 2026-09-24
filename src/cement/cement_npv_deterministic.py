"""Deterministic cement NPV input provider."""

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
)
from general_parameters import (
    BIOFUEL_PRICE_DISTRIBUTION,
    COAL_PRICE_DISTRIBUTION,
    ELECTRICITY_PRICE_DISTRIBUTION,
)
from npv_summary import representative_value


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


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


def _representative_values(
    parameters: Mapping[str, ParameterSpec],
) -> dict[str, np.ndarray]:
    """Return one-element arrays containing representative input values."""

    return {
        name: np.full(1, representative_value(parameter))
        for name, parameter in parameters.items()
    }


def _deterministic_bau_values() -> dict[str, np.ndarray]:
    return _representative_values(CEMENT_TECHNOLOGY_DISTRIBUTIONS["bau"])


def calculate_deterministic_cement_result(
    technology: str,
) -> Mapping[str, object]:
    """Calculate one-row cement results from representative inputs."""

    if technology in CEMENT_TECHNOLOGY_DISTRIBUTIONS:
        values = _representative_values(CEMENT_TECHNOLOGY_DISTRIBUTIONS[technology])
        baseline = None
        increments = None
        technology_type = "absolute"
        bau_mode = "not_applicable"
    elif technology in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        baseline = _deterministic_bau_values()
        increments = _representative_values(
            CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
        )
        values = resolve_technology_values(baseline, increments)
        technology_type = "retrofit"
        bau_mode = "deterministic"
    else:
        raise ValueError(f"Unknown cement technology: {technology!r}.")

    prices = {
        "coal_price_eur_per_mwh_th": np.full(
            1, representative_value(COAL_PRICE_DISTRIBUTION)
        ),
        "biofuel_price_eur_per_mwh_th": np.full(
            1, representative_value(BIOFUEL_PRICE_DISTRIBUTION)
        ),
        "electricity_price_eur_per_mwh": np.full(
            1, representative_value(ELECTRICITY_PRICE_DISTRIBUTION)
        ),
    }
    result = calculate_result(
        technology=technology,
        technology_type=technology_type,
        bau_mode=bau_mode,
        values=values,
        size=1,
        bau_values=baseline,
        retrofit_values=increments,
        market_values=prices,
        include_retrofit_bau_mode=False,
        include_bau_values=False,
    )
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_cement_npv_eur(technology: str) -> float:
    """Calculate deterministic cement NPV from representative inputs."""

    return float(calculate_deterministic_cement_result(technology)["npv_eur"][0])


def calculate_deterministic_cement_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic cement results for selected technologies."""

    selected = technologies or tuple(
        list(CEMENT_TECHNOLOGY_DISTRIBUTIONS)
        + list(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    return {
        technology: calculate_deterministic_cement_result(technology)
        for technology in selected
    }
