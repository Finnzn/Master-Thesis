"""Deterministic NPV calculations for steel technologies.

The deterministic steel calculation is the one-point counterpart to the Monte
Carlo model. Each uncertain parameter is replaced by its representative value,
incremental CCS technologies are resolved against their parent BAU technology,
and the resulting annual cash flow is discounted over the shared steel-sector
lifetime.
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
from general_parameters import (
    CARBON_PRICE_EUR_PER_T,
    CHARCOAL_PRICE_EUR_PER_MWH_TH,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    ELECTRICITY_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    GREEN_HYDROGEN_PRICE_EUR_PER_KG,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
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
from steel.steel_parameters import (
    ANNUAL_STEEL_OUTPUT_TCS,
    LIFETIME_STEEL_YEARS,
    RETAIL_PRICE_STEEL_EUR_PER_TCS,
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

STEEL_FUEL_TYPES: Mapping[str, str] = {
    "bf_bof_bau": "pci_coking_coal_mix",
    "bf_bof_post_combustion_ccs": "pci_coking_coal_mix",
    "scrap_eaf": "charcoal",
    "ng_dri_eaf_bau": "natural_gas",
    "ng_dri_eaf_ccs": "natural_gas",
    "h2_dri_eaf": "green_hydrogen_and_charcoal",
    "moe": "none",
    "ael_eaf": "charcoal",
}


def steel_fuel_price_parameters(technology: str) -> Mapping[str, ParameterSpec]:
    """Return the shared fuel-price parameters used by a steel technology."""

    prices_by_technology: Mapping[str, Mapping[str, ParameterSpec]] = {
        "bf_bof_bau": {
            "pci_coking_coal_mix": PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
        },
        "bf_bof_post_combustion_ccs": {
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
) -> dict[str, float]:
    """Convert one parameter mapping into deterministic representative values."""

    return {
        parameter_name: representative_value(parameter)
        for parameter_name, parameter in parameters.items()
    }


def _deterministic_steel_technology_values(
    technology: str,
) -> dict[str, float]:
    """Resolve absolute deterministic inputs for one steel technology."""

    if technology in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        return _representative_values(STEEL_TECHNOLOGY_DISTRIBUTIONS[technology])

    if technology not in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown steel technology: {technology!r}.")

    bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
    bau_values = _representative_values(
        STEEL_TECHNOLOGY_DISTRIBUTIONS[bau_technology]
    )
    retrofit_values = _representative_values(
        STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
    )

    return {
        "capex_eur_per_tcs": (
            bau_values["capex_eur_per_tcs"]
            + retrofit_values["capex_change_eur_per_tcs"]
        ),
        "fixed_opex_eur_per_tcs": (
            bau_values["fixed_opex_eur_per_tcs"]
            + retrofit_values["fixed_opex_change_eur_per_tcs"]
        ),
        "variable_opex_eur_per_tcs": (
            bau_values["variable_opex_eur_per_tcs"]
            + retrofit_values["variable_opex_change_eur_per_tcs"]
        ),
        "fuel_consumption_mwh_th_per_tcs": (
            bau_values["fuel_consumption_mwh_th_per_tcs"]
            * (1.0 - retrofit_values["fuel_consumption_reduction_fraction"])
        ),
        "electricity_consumption_mwh_per_tcs": (
            bau_values["electricity_consumption_mwh_per_tcs"]
            * (
                1.0
                - retrofit_values["electricity_consumption_reduction_fraction"]
            )
        ),
        "emissions_tco2_per_tcs": (
            bau_values["emissions_tco2_per_tcs"]
            * (1.0 - retrofit_values["emissions_reduction_fraction"])
        ),
        **retrofit_values,
    }


def _deterministic_market_prices() -> dict[str, float]:
    """Return representative shared energy prices for deterministic steel runs."""

    return {
        "pci_coking_coal_mix_price_eur_per_mwh_th": (
            PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH.value
        ),
        "charcoal_price_eur_per_mwh_th": CHARCOAL_PRICE_EUR_PER_MWH_TH.value,
        "gas_price_eur_per_mwh_th": representative_value(GAS_PRICE_DISTRIBUTION),
        "green_hydrogen_price_eur_per_kg": GREEN_HYDROGEN_PRICE_EUR_PER_KG.value,
        "no_fuel_price_eur_per_mwh_th": NO_FUEL_PRICE_EUR_PER_MWH_TH.value,
        "electricity_price_eur_per_mwh": representative_value(
            ELECTRICITY_PRICE_DISTRIBUTION
        ),
    }


def _energy_costs_per_tcs(
    technology: str,
    values: Mapping[str, float],
    market_prices: Mapping[str, float],
) -> dict[str, float]:
    """Calculate technology fuel-carrier costs per tonne of crude steel."""

    pci_cost = 0.0
    charcoal_cost = 0.0
    natural_gas_cost = 0.0
    hydrogen_cost = 0.0

    if technology in {"bf_bof_bau", "bf_bof_post_combustion_ccs"}:
        pci_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_prices["pci_coking_coal_mix_price_eur_per_mwh_th"]
        )
    elif technology in {"scrap_eaf", "ael_eaf"}:
        charcoal_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_prices["charcoal_price_eur_per_mwh_th"]
        )
    elif technology in {"ng_dri_eaf_bau", "ng_dri_eaf_ccs"}:
        natural_gas_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_prices["gas_price_eur_per_mwh_th"]
        )
    elif technology == "h2_dri_eaf":
        hydrogen_cost = (
            values["hydrogen_consumption_kg_per_tcs"]
            * market_prices["green_hydrogen_price_eur_per_kg"]
        )
        charcoal_cost = (
            values["charcoal_consumption_mwh_th_per_tcs"]
            * market_prices["charcoal_price_eur_per_mwh_th"]
        )
    elif technology != "moe":
        raise ValueError(f"No energy-cost calculation configured for {technology!r}.")

    return {
        "pci_coking_coal_cost_eur_per_tcs": pci_cost,
        "charcoal_cost_eur_per_tcs": charcoal_cost,
        "natural_gas_cost_eur_per_tcs": natural_gas_cost,
        "hydrogen_cost_eur_per_tcs": hydrogen_cost,
        "fuel_cost_eur_per_tcs": (
            pci_cost + charcoal_cost + natural_gas_cost + hydrogen_cost
        ),
    }


def _technology_fuel_price_eur_per_mwh_th(
    technology: str,
    market_prices: Mapping[str, float],
) -> float:
    """Return the single-fuel energy price, or NaN for dual-fuel H2-DRI-EAF."""

    price_key_by_technology = {
        "bf_bof_bau": "pci_coking_coal_mix_price_eur_per_mwh_th",
        "bf_bof_post_combustion_ccs": (
            "pci_coking_coal_mix_price_eur_per_mwh_th"
        ),
        "scrap_eaf": "charcoal_price_eur_per_mwh_th",
        "ng_dri_eaf_bau": "gas_price_eur_per_mwh_th",
        "ng_dri_eaf_ccs": "gas_price_eur_per_mwh_th",
        "moe": "no_fuel_price_eur_per_mwh_th",
        "ael_eaf": "charcoal_price_eur_per_mwh_th",
    }
    if technology == "h2_dri_eaf":
        return float("nan")
    if technology not in price_key_by_technology:
        raise ValueError(f"No fuel price configured for {technology!r}.")
    return market_prices[price_key_by_technology[technology]]


def calculate_deterministic_steel_result(
    technology: str,
) -> Mapping[str, object]:
    """Calculate deterministic steel inputs and financial outputs."""

    values = _deterministic_steel_technology_values(technology)
    market_prices = _deterministic_market_prices()
    annual_output_tcs = ANNUAL_STEEL_OUTPUT_TCS.value
    lifetime_years = LIFETIME_STEEL_YEARS.value

    capex_eur_per_tcs = values["capex_eur_per_tcs"]
    fixed_opex_eur_per_tcs = values["fixed_opex_eur_per_tcs"]
    variable_opex_eur_per_tcs = values["variable_opex_eur_per_tcs"]
    electricity_consumption_mwh_per_tcs = values[
        "electricity_consumption_mwh_per_tcs"
    ]
    emissions_tco2_per_tcs = values["emissions_tco2_per_tcs"]
    fuel_consumption_mwh_th_per_tcs = values.get(
        "fuel_consumption_mwh_th_per_tcs",
        float("nan"),
    )
    hydrogen_consumption_kg_per_tcs = values.get(
        "hydrogen_consumption_kg_per_tcs",
        float("nan"),
    )
    charcoal_consumption_mwh_th_per_tcs = values.get(
        "charcoal_consumption_mwh_th_per_tcs",
        float("nan"),
    )
    energy_costs_per_tcs = _energy_costs_per_tcs(
        technology=technology,
        values=values,
        market_prices=market_prices,
    )
    fuel_price_eur_per_mwh_th = _technology_fuel_price_eur_per_mwh_th(
        technology=technology,
        market_prices=market_prices,
    )

    initial_capex_eur = annual_output_tcs * capex_eur_per_tcs
    annual_revenue_eur = annual_output_tcs * RETAIL_PRICE_STEEL_EUR_PER_TCS.value
    annual_fixed_opex_eur = annual_output_tcs * fixed_opex_eur_per_tcs
    annual_variable_opex_eur = annual_output_tcs * variable_opex_eur_per_tcs
    annual_pci_coking_coal_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["pci_coking_coal_cost_eur_per_tcs"]
    )
    annual_charcoal_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["charcoal_cost_eur_per_tcs"]
    )
    annual_natural_gas_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["natural_gas_cost_eur_per_tcs"]
    )
    annual_hydrogen_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["hydrogen_cost_eur_per_tcs"]
    )
    annual_fuel_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["fuel_cost_eur_per_tcs"]
    )
    annual_electricity_cost_eur = (
        annual_output_tcs
        * electricity_consumption_mwh_per_tcs
        * market_prices["electricity_price_eur_per_mwh"]
    )

    capture_cost_excluding_transport_and_storage_eur_per_tcs = float("nan")
    transport_and_storage_cost_eur_per_tcs = 0.0
    transport_and_storage_share_of_capture_cost = float("nan")
    if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES:
        transport_and_storage_share_of_capture_cost = (
            CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
        )
        bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        bau_values = _representative_values(
            STEEL_TECHNOLOGY_DISTRIBUTIONS[bau_technology]
        )
        bau_energy_costs_per_tcs = _energy_costs_per_tcs(
            technology=bau_technology,
            values=bau_values,
            market_prices=market_prices,
        )
        bau_initial_capex_eur = (
            annual_output_tcs * bau_values["capex_eur_per_tcs"]
        )
        bau_annual_cost_excluding_carbon_eur = annual_output_tcs * (
            bau_values["fixed_opex_eur_per_tcs"]
            + bau_values["variable_opex_eur_per_tcs"]
            + bau_energy_costs_per_tcs["fuel_cost_eur_per_tcs"]
            + bau_values["electricity_consumption_mwh_per_tcs"]
            * market_prices["electricity_price_eur_per_mwh"]
        )
        annual_cost_excluding_carbon_eur = (
            annual_fixed_opex_eur
            + annual_variable_opex_eur
            + annual_fuel_cost_eur
            + annual_electricity_cost_eur
        )
        (
            capture_cost_excluding_transport_and_storage_eur_per_tcs,
            transport_and_storage_cost_eur_per_tcs,
        ) = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=initial_capex_eur,
            bau_initial_capex_eur=bau_initial_capex_eur,
            ccs_annual_cost_excluding_carbon_eur=annual_cost_excluding_carbon_eur,
            bau_annual_cost_excluding_carbon_eur=(
                bau_annual_cost_excluding_carbon_eur
            ),
            annual_output=annual_output_tcs,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                transport_and_storage_share_of_capture_cost
            ),
        )

    annual_transport_and_storage_cost_eur = (
        annual_output_tcs * transport_and_storage_cost_eur_per_tcs
    )
    annual_emissions_cost_eur = (
        annual_output_tcs * emissions_tco2_per_tcs * CARBON_PRICE_EUR_PER_T.value
    )
    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_electricity_cost_eur
        + annual_transport_and_storage_cost_eur
        + annual_emissions_cost_eur
    )
    annual_net_cash_flow_eur = annual_revenue_eur - annual_total_cost_eur
    npv_eur = float(
        calculate_npv(
            initial_capex_eur=np.array([initial_capex_eur]),
            annual_net_cash_flow_eur=np.array([annual_net_cash_flow_eur]),
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
        )[0]
    )
    discounted_lifetime_output_tcs = calculate_discounted_lifetime_output(
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    levelized_net_margin_eur_per_tcs = calculate_levelized_net_margin(
        npv_eur=npv_eur,
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    present_value_total_cost_eur = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    lcos_eur_per_tcs = calculate_levelized_cost(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )

    result = {
        "run_id": [0],
        "technology": [technology],
        "technology_type": [
            "retrofit"
            if technology in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
            else "absolute"
        ],
        "annual_output_tcs": [annual_output_tcs],
        "lifetime_years": [lifetime_years],
        "capex_eur_per_tcs": [capex_eur_per_tcs],
        "fixed_opex_eur_per_tcs": [fixed_opex_eur_per_tcs],
        "variable_opex_eur_per_tcs": [variable_opex_eur_per_tcs],
        "fuel_type": [STEEL_FUEL_TYPES[technology]],
        "fuel_consumption_mwh_th_per_tcs": [fuel_consumption_mwh_th_per_tcs],
        "hydrogen_consumption_kg_per_tcs": [hydrogen_consumption_kg_per_tcs],
        "charcoal_consumption_mwh_th_per_tcs": [
            charcoal_consumption_mwh_th_per_tcs
        ],
        "electricity_consumption_mwh_per_tcs": [
            electricity_consumption_mwh_per_tcs
        ],
        "emissions_tco2_per_tcs": [emissions_tco2_per_tcs],
        "fuel_price_eur_per_mwh_th": [fuel_price_eur_per_mwh_th],
        **{key: [value] for key, value in market_prices.items()},
        "steel_price_eur_per_tcs": [RETAIL_PRICE_STEEL_EUR_PER_TCS.value],
        "carbon_price_eur_per_t": [CARBON_PRICE_EUR_PER_T.value],
        "capture_cost_excluding_transport_and_storage_eur_per_tcs": [
            capture_cost_excluding_transport_and_storage_eur_per_tcs
        ],
        "transport_and_storage_cost_eur_per_tcs": [
            transport_and_storage_cost_eur_per_tcs
        ],
        "transport_and_storage_share_of_capture_cost": [
            transport_and_storage_share_of_capture_cost
        ],
        "initial_capex_eur": [initial_capex_eur],
        "annual_revenue_eur": [annual_revenue_eur],
        "annual_fixed_opex_eur": [annual_fixed_opex_eur],
        "annual_variable_opex_eur": [annual_variable_opex_eur],
        "annual_pci_coking_coal_cost_eur": [annual_pci_coking_coal_cost_eur],
        "annual_charcoal_cost_eur": [annual_charcoal_cost_eur],
        "annual_natural_gas_cost_eur": [annual_natural_gas_cost_eur],
        "annual_hydrogen_cost_eur": [annual_hydrogen_cost_eur],
        "annual_fuel_cost_eur": [annual_fuel_cost_eur],
        "annual_electricity_cost_eur": [annual_electricity_cost_eur],
        "annual_transport_and_storage_cost_eur": [
            annual_transport_and_storage_cost_eur
        ],
        "annual_emissions_cost_eur": [annual_emissions_cost_eur],
        "annual_total_cost_eur": [annual_total_cost_eur],
        "annual_net_cash_flow_eur": [annual_net_cash_flow_eur],
        "npv_eur": [npv_eur],
        "discounted_lifetime_output_tcs": [discounted_lifetime_output_tcs],
        "present_value_total_cost_eur": [present_value_total_cost_eur],
        "lcos_eur_per_tcs": [lcos_eur_per_tcs],
        "levelized_net_margin_eur_per_tcs": [
            levelized_net_margin_eur_per_tcs
        ],
    }

    for retrofit_key in (
        "capex_change_eur_per_tcs",
        "fixed_opex_change_eur_per_tcs",
        "variable_opex_change_eur_per_tcs",
        "fuel_consumption_reduction_fraction",
        "electricity_consumption_reduction_fraction",
        "emissions_reduction_fraction",
    ):
        if retrofit_key in values:
            result[retrofit_key] = [values[retrofit_key]]

    return result


def calculate_deterministic_steel_npv_eur(technology: str) -> float:
    """Calculate deterministic steel NPV from representative values."""

    return float(calculate_deterministic_steel_result(technology)["npv_eur"][0])


def calculate_deterministic_steel_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic results for selected or all steel technologies."""

    selected_technologies = technologies or tuple(
        list(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        + list(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    return {
        technology: calculate_deterministic_steel_result(technology)
        for technology in selected_technologies
    }
