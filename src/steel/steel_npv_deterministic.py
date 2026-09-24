"""Deterministic input provider for the shared steel NPV model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
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
from steel.steel_npv_model import (
    STEEL_FUEL_TYPES,
    calculate_result,
    resolve_technology_values,
)
from steel.steel_parameters import (
    STEEL_RETROFIT_BASE_TECHNOLOGIES,
    STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    STEEL_TECHNOLOGY_DISTRIBUTIONS,
)


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def steel_fuel_price_parameters(technology: str) -> Mapping[str, ParameterSpec]:
    """Return the shared fuel-price parameters used by a steel technology."""

    prices_by_technology: Mapping[str, Mapping[str, ParameterSpec]] = {
        "bf_bof_bau": {
            "pci_coking_coal_mix": PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
        },
        "bf_bof_ccs": {
            "pci_coking_coal_mix": PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
        },
        "scrap_eaf": {"charcoal": CHARCOAL_PRICE_EUR_PER_MWH_TH},
        "ng_dri_eaf_bau": {"natural_gas": GAS_PRICE_DISTRIBUTION},
        "ng_dri_eaf_ccs": {"natural_gas": GAS_PRICE_DISTRIBUTION},
        "h2_dri_eaf": {
            "green_hydrogen": GREEN_HYDROGEN_PRICE_EUR_PER_KG,
            "charcoal": CHARCOAL_PRICE_EUR_PER_MWH_TH,
        },
        "moe": {"none": NO_FUEL_PRICE_EUR_PER_MWH_TH},
        "ael_eaf": {"charcoal": CHARCOAL_PRICE_EUR_PER_MWH_TH},
    }
    if technology not in prices_by_technology:
        raise ValueError(f"No fuel-price parameters configured for {technology!r}.")
    return prices_by_technology[technology]


def _representative_values(
    parameters: Mapping[str, ParameterSpec],
) -> dict[str, np.ndarray]:
    """Convert one parameter mapping to one-element representative arrays."""

    return {
        parameter_name: np.full(1, representative_value(parameter))
        for parameter_name, parameter in parameters.items()
    }


def _deterministic_market_prices() -> dict[str, np.ndarray]:
    """Return shared energy prices as one-element representative arrays."""

    return {
        "pci_coking_coal_mix_price_eur_per_mwh_th": np.full(
            1, PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH.value
        ),
        "charcoal_price_eur_per_mwh_th": np.full(
            1, CHARCOAL_PRICE_EUR_PER_MWH_TH.value
        ),
        "gas_price_eur_per_mwh_th": np.full(
            1, representative_value(GAS_PRICE_DISTRIBUTION)
        ),
        "green_hydrogen_price_eur_per_kg": np.full(
            1, GREEN_HYDROGEN_PRICE_EUR_PER_KG.value
        ),
        "no_fuel_price_eur_per_mwh_th": np.full(
            1, NO_FUEL_PRICE_EUR_PER_MWH_TH.value
        ),
        "electricity_price_eur_per_mwh": np.full(
            1, representative_value(ELECTRICITY_PRICE_DISTRIBUTION)
        ),
    }


def calculate_deterministic_steel_result(
    technology: str,
) -> Mapping[str, object]:
    """Choose representative inputs and call the shared steel model."""

    all_technologies = (
        set(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        | set(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"Unknown steel technology: {technology!r}.")

    is_retrofit = technology in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
    bau_values = None
    retrofit_values = None
    if is_retrofit:
        bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        bau_values = _representative_values(
            STEEL_TECHNOLOGY_DISTRIBUTIONS[bau_technology]
        )
        retrofit_values = _representative_values(
            STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
        )
        values = resolve_technology_values(bau_values, retrofit_values)
    else:
        values = _representative_values(STEEL_TECHNOLOGY_DISTRIBUTIONS[technology])

    result = calculate_result(
        technology=technology,
        technology_type="retrofit" if is_retrofit else "absolute",
        bau_mode="deterministic" if is_retrofit else "not_applicable",
        values=values,
        size=1,
        market_values=_deterministic_market_prices(),
        bau_values=bau_values,
        retrofit_values=retrofit_values,
        include_retrofit_bau_mode=False,
        include_bau_values=False,
    )
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_steel_npv_eur(technology: str) -> float:
    """Return the deterministic NPV for one steel technology."""

    return float(calculate_deterministic_steel_result(technology)["npv_eur"][0])


def calculate_deterministic_steel_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic results for selected or all technologies."""

    selected_technologies = technologies or tuple(
        list(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        + list(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    return {
        technology: calculate_deterministic_steel_result(technology)
        for technology in selected_technologies
    }
