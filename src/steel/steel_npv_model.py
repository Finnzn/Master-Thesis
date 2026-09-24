"""Shared steel technology resolution and financial-result model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from general_parameters import (
    CARBON_PRICE_EUR_PER_T,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    INTEREST_RATE,
)
from npv_finance import (
    calculate_ccs_transport_and_storage_cost_per_output,
    calculate_financial_result,
)
from steel.steel_parameters import (
    ANNUAL_STEEL_OUTPUT_TCS,
    LIFETIME_STEEL_YEARS,
    RETAIL_PRICE_STEEL_EUR_PER_TCS,
    STEEL_RETROFIT_BASE_TECHNOLOGIES,
)


STEEL_FUEL_TYPES: Mapping[str, str] = {
    "bf_bof_bau": "pci_coking_coal_mix",
    "bf_bof_ccs": "pci_coking_coal_mix",
    "scrap_eaf": "charcoal",
    "ng_dri_eaf_bau": "natural_gas",
    "ng_dri_eaf_ccs": "natural_gas",
    "h2_dri_eaf": "green_hydrogen_and_charcoal",
    "moe": "none",
    "ael_eaf": "charcoal",
}


def resolve_technology_values(
    bau_values: Mapping[str, np.ndarray],
    retrofit_values: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve absolute steel inputs from BAU arrays and retrofit changes."""

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
    }


def _energy_costs_per_tcs(
    technology: str,
    values: Mapping[str, np.ndarray],
    market_values: Mapping[str, np.ndarray],
    size: int,
) -> dict[str, np.ndarray]:
    """Calculate fuel-carrier cost arrays per tonne of crude steel."""

    pci_cost = np.zeros(size)
    charcoal_cost = np.zeros(size)
    natural_gas_cost = np.zeros(size)
    hydrogen_cost = np.zeros(size)

    if technology in {"bf_bof_bau", "bf_bof_ccs"}:
        pci_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["pci_coking_coal_mix_price_eur_per_mwh_th"]
        )
    elif technology in {"scrap_eaf", "ael_eaf"}:
        charcoal_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["charcoal_price_eur_per_mwh_th"]
        )
    elif technology in {"ng_dri_eaf_bau", "ng_dri_eaf_ccs"}:
        natural_gas_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["gas_price_eur_per_mwh_th"]
        )
    elif technology == "h2_dri_eaf":
        hydrogen_cost = (
            values["hydrogen_consumption_kg_per_tcs"]
            * market_values["green_hydrogen_price_eur_per_kg"]
        )
        charcoal_cost = (
            values["charcoal_consumption_mwh_th_per_tcs"]
            * market_values["charcoal_price_eur_per_mwh_th"]
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
    market_values: Mapping[str, np.ndarray],
    size: int,
) -> np.ndarray:
    """Return one energy-price array, or NaN for dual-fuel H2-DRI-EAF."""

    price_key_by_technology = {
        "bf_bof_bau": "pci_coking_coal_mix_price_eur_per_mwh_th",
        "bf_bof_ccs": "pci_coking_coal_mix_price_eur_per_mwh_th",
        "scrap_eaf": "charcoal_price_eur_per_mwh_th",
        "ng_dri_eaf_bau": "gas_price_eur_per_mwh_th",
        "ng_dri_eaf_ccs": "gas_price_eur_per_mwh_th",
        "moe": "no_fuel_price_eur_per_mwh_th",
        "ael_eaf": "charcoal_price_eur_per_mwh_th",
    }
    if technology == "h2_dri_eaf":
        return np.full(size, np.nan)
    if technology not in price_key_by_technology:
        raise ValueError(f"No fuel price configured for {technology!r}.")
    return market_values[price_key_by_technology[technology]]


def calculate_result(
    technology: str,
    technology_type: str,
    bau_mode: str,
    values: Mapping[str, np.ndarray],
    size: int,
    market_values: Mapping[str, np.ndarray],
    *,
    bau_values: Mapping[str, np.ndarray] | None = None,
    retrofit_values: Mapping[str, np.ndarray] | None = None,
    include_retrofit_bau_mode: bool = True,
    include_bau_values: bool = True,
) -> Mapping[str, np.ndarray]:
    """Calculate all steel costs and financial outputs from resolved inputs."""

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
        "fuel_consumption_mwh_th_per_tcs", np.full(size, np.nan)
    )
    hydrogen_consumption_kg_per_tcs = values.get(
        "hydrogen_consumption_kg_per_tcs", np.full(size, np.nan)
    )
    charcoal_consumption_mwh_th_per_tcs = values.get(
        "charcoal_consumption_mwh_th_per_tcs", np.full(size, np.nan)
    )
    energy_costs_per_tcs = _energy_costs_per_tcs(
        technology=technology,
        values=values,
        market_values=market_values,
        size=size,
    )
    fuel_price_eur_per_mwh_th = _technology_fuel_price_eur_per_mwh_th(
        technology=technology,
        market_values=market_values,
        size=size,
    )

    initial_capex_eur = annual_output_tcs * capex_eur_per_tcs
    annual_revenue_eur = np.full(
        size, annual_output_tcs * RETAIL_PRICE_STEEL_EUR_PER_TCS.value
    )
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
        * market_values["electricity_price_eur_per_mwh"]
    )

    capture_cost_excluding_transport_and_storage_eur_per_tcs = np.full(
        size, np.nan
    )
    transport_and_storage_cost_eur_per_tcs = np.zeros(size)
    transport_and_storage_share_of_capture_cost = np.full(size, np.nan)
    if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES:
        if bau_values is None:
            raise ValueError("Steel CCS requires BAU values for its T&S cost basis.")
        transport_and_storage_share_of_capture_cost = np.full(
            size, CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
        )
        bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        bau_energy_costs_per_tcs = _energy_costs_per_tcs(
            technology=bau_technology,
            values=bau_values,
            market_values=market_values,
            size=size,
        )
        bau_initial_capex_eur = annual_output_tcs * bau_values["capex_eur_per_tcs"]
        bau_annual_cost_excluding_carbon_eur = annual_output_tcs * (
            bau_values["fixed_opex_eur_per_tcs"]
            + bau_values["variable_opex_eur_per_tcs"]
            + bau_energy_costs_per_tcs["fuel_cost_eur_per_tcs"]
            + bau_values["electricity_consumption_mwh_per_tcs"]
            * market_values["electricity_price_eur_per_mwh"]
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
            bau_annual_cost_excluding_carbon_eur=bau_annual_cost_excluding_carbon_eur,
            annual_output=annual_output_tcs,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
            ),
        )

    annual_transport_and_storage_cost_eur = (
        annual_output_tcs * transport_and_storage_cost_eur_per_tcs
    )
    annual_emissions_cost_eur = (
        annual_output_tcs * emissions_tco2_per_tcs * CARBON_PRICE_EUR_PER_T.value
    )
    financial_result = calculate_financial_result(
        initial_capex_eur=initial_capex_eur,
        annual_output=annual_output_tcs,
        annual_revenue_eur=annual_revenue_eur,
        annual_fixed_opex_eur=annual_fixed_opex_eur,
        annual_variable_opex_eur=annual_variable_opex_eur,
        annual_fuel_cost_eur=annual_fuel_cost_eur,
        annual_electricity_cost_eur=annual_electricity_cost_eur,
        annual_transport_and_storage_cost_eur=annual_transport_and_storage_cost_eur,
        annual_emissions_cost_eur=annual_emissions_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    annual_total_cost_eur = financial_result["annual_total_cost_eur"]
    annual_net_cash_flow_eur = financial_result["annual_net_cash_flow_eur"]
    npv_eur = financial_result["npv_eur"]
    discounted_lifetime_output_tcs = financial_result[
        "discounted_lifetime_output"
    ]
    present_value_total_cost_eur = financial_result[
        "present_value_total_cost_eur"
    ]
    lcos_eur_per_tcs = financial_result["levelized_cost"]
    levelized_profit_margin_eur_per_tcs = financial_result[
        "levelized_profit_margin"
    ]

    result = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, technology_type),
        "retrofit_bau_mode": np.full(size, bau_mode),
        "annual_output_tcs": np.full(size, annual_output_tcs),
        "lifetime_years": np.full(size, lifetime_years),
        "capex_eur_per_tcs": capex_eur_per_tcs,
        "fixed_opex_eur_per_tcs": fixed_opex_eur_per_tcs,
        "variable_opex_eur_per_tcs": variable_opex_eur_per_tcs,
        "fuel_type": np.full(size, STEEL_FUEL_TYPES[technology]),
        "fuel_consumption_mwh_th_per_tcs": fuel_consumption_mwh_th_per_tcs,
        "hydrogen_consumption_kg_per_tcs": hydrogen_consumption_kg_per_tcs,
        "charcoal_consumption_mwh_th_per_tcs": charcoal_consumption_mwh_th_per_tcs,
        "electricity_consumption_mwh_per_tcs": electricity_consumption_mwh_per_tcs,
        "emissions_tco2_per_tcs": emissions_tco2_per_tcs,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        **market_values,
        "steel_price_eur_per_tcs": np.full(
            size, RETAIL_PRICE_STEEL_EUR_PER_TCS.value
        ),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "capture_cost_excluding_transport_and_storage_eur_per_tcs": (
            capture_cost_excluding_transport_and_storage_eur_per_tcs
        ),
        "transport_and_storage_cost_eur_per_tcs": (
            transport_and_storage_cost_eur_per_tcs
        ),
        "transport_and_storage_share_of_capture_cost": (
            transport_and_storage_share_of_capture_cost
        ),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_pci_coking_coal_cost_eur": annual_pci_coking_coal_cost_eur,
        "annual_charcoal_cost_eur": annual_charcoal_cost_eur,
        "annual_natural_gas_cost_eur": annual_natural_gas_cost_eur,
        "annual_hydrogen_cost_eur": annual_hydrogen_cost_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_electricity_cost_eur": annual_electricity_cost_eur,
        "annual_transport_and_storage_cost_eur": annual_transport_and_storage_cost_eur,
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output_tcs": np.full(
            size, discounted_lifetime_output_tcs
        ),
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "lcos_eur_per_tcs": lcos_eur_per_tcs,
        "levelized_profit_margin_eur_per_tcs": levelized_profit_margin_eur_per_tcs,
    }

    if bau_values is not None and include_bau_values:
        for parameter_name, baseline_value in bau_values.items():
            result[f"bau_{parameter_name}"] = baseline_value
    if retrofit_values is not None:
        result.update(retrofit_values)
    if not include_retrofit_bau_mode:
        result.pop("retrofit_bau_mode")
    return result
