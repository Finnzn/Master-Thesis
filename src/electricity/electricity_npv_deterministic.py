"""Deterministic input provider for the shared electricity NPV model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from electricity.electricity_npv_model import (
    calculate_result,
    resolve_technology_values,
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


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def electricity_fuel_price_parameter(technology: str) -> ParameterSpec:
    """Return the shared fuel-price parameter used by a technology."""

    fuel_price_by_technology = {
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
    if technology not in fuel_price_by_technology:
        raise ValueError(f"No fuel-price parameter configured for {technology!r}.")
    return fuel_price_by_technology[technology]


def _representative_values(
    parameters: Mapping[str, ParameterSpec],
) -> dict[str, np.ndarray]:
    """Convert one parameter mapping to one-element representative arrays."""

    return {
        parameter_name: np.full(1, representative_value(parameter))
        for parameter_name, parameter in parameters.items()
    }


def calculate_deterministic_electricity_result(
    technology: str,
) -> Mapping[str, object]:
    """Choose representative inputs and call the shared electricity model."""

    if technology not in ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    is_retrofit = technology in ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
    baseline_values = None
    retrofit_values = None
    if is_retrofit:
        bau_technology = ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES[technology]
        baseline_values = _representative_values(
            ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[bau_technology]
        )
        retrofit_values = _representative_values(
            ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
        )
        values = resolve_technology_values(baseline_values, retrofit_values)
    else:
        values = _representative_values(
            ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[technology]
        )

    fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]
    value_factor_parameter = fixed_parameters.get("value_factor")
    result = calculate_result(
        technology=technology,
        technology_type="retrofit" if is_retrofit else "absolute",
        bau_mode="deterministic" if is_retrofit else "not_applicable",
        values=values,
        size=1,
        full_load_hours=np.full(
            1,
            representative_value(fixed_parameters["full_load_hours_per_year"]),
        ),
        lifetime_years=representative_value(fixed_parameters["lifetime_years"]),
        value_factor=(
            np.full(1, representative_value(value_factor_parameter))
            if value_factor_parameter is not None
            else np.ones(1)
        ),
        fuel_price_eur_per_mwh_th=np.full(
            1,
            representative_value(electricity_fuel_price_parameter(technology)),
        ),
        baseline_values=baseline_values,
        retrofit_values=retrofit_values,
        beccs_transport_and_storage_cost_eur_per_mwh=(
            np.full(
                1,
                representative_value(BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION),
            )
            if technology == "beccs"
            else None
        ),
        include_retrofit_bau_mode=False,
        include_bau_values=False,
        include_fuel_price_source=False,
        # Preserve the historical deterministic export operation order.
        export_capacity_mw_from_kw=True,
    )
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_electricity_npv_eur(technology: str) -> float:
    """Return the deterministic NPV for one electricity technology."""

    return float(calculate_deterministic_electricity_result(technology)["npv_eur"][0])


def calculate_deterministic_electricity_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic results for all selected technologies."""

    selected_technologies = technologies or tuple(
        ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS
    )
    return {
        technology: calculate_deterministic_electricity_result(technology)
        for technology in selected_technologies
    }
