"""Shared cement technology resolution and financial-result model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from cement.cement_parameters import (
    ANNUAL_CEMENT_OUTPUT_T,
    LIFETIME_CEMENT_YEARS,
    RETAIL_PRICE_CEMENT_EUR_PER_T,
)
from general_parameters import (
    CARBON_PRICE_EUR_PER_T,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    INTEREST_RATE,
)
from npv_finance import (
    calculate_ccs_transport_and_storage_cost_per_output,
    calculate_financial_result,
)


def resolve_technology_values(
    bau_values: Mapping[str, np.ndarray],
    retrofit_values: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve absolute retrofit values from BAU arrays and retrofit changes."""

    return {
        "capex_eur_per_t": (
            bau_values["capex_eur_per_t"]
            + retrofit_values["capex_change_eur_per_t"]
        ),
        "fixed_opex_eur_per_t": (
            bau_values["fixed_opex_eur_per_t"]
            + retrofit_values["fixed_opex_change_eur_per_t"]
        ),
        "variable_opex_eur_per_t": (
            bau_values["variable_opex_eur_per_t"]
            + retrofit_values["variable_opex_change_eur_per_t"]
        ),
        "fuel_consumption_mwh_th_per_t": (
            bau_values["fuel_consumption_mwh_th_per_t"]
            * (1.0 - retrofit_values["fuel_consumption_reduction_fraction"])
        ),
        "electricity_consumption_mwh_per_t": (
            bau_values["electricity_consumption_mwh_per_t"]
            * (1.0 - retrofit_values["electricity_consumption_reduction_fraction"])
        ),
        "emissions_tco2_per_t": (
            bau_values["emissions_tco2_per_t"]
            * (1.0 - retrofit_values["emissions_reduction_fraction"])
        ),
    }


def calculate_result(
    technology: str,
    technology_type: str,
    bau_mode: str,
    values: Mapping[str, np.ndarray],
    size: int,
    bau_values: Mapping[str, np.ndarray] | None = None,
    retrofit_values: Mapping[str, np.ndarray] | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    include_retrofit_bau_mode: bool = True,
    include_bau_values: bool = True,
) -> Mapping[str, np.ndarray]:
    """Calculate cement cash flows and NPV from absolute technology arrays."""

    annual_output_t = ANNUAL_CEMENT_OUTPUT_T.value
    lifetime_years = LIFETIME_CEMENT_YEARS.value
    capex_eur_per_t = values["capex_eur_per_t"]
    fixed_opex_eur_per_t = values["fixed_opex_eur_per_t"]
    variable_opex_eur_per_t = values["variable_opex_eur_per_t"]
    fuel_consumption_mwh_th_per_t = values["fuel_consumption_mwh_th_per_t"]
    electricity_consumption_mwh_per_t = values["electricity_consumption_mwh_per_t"]
    emissions_tco2_per_t = values["emissions_tco2_per_t"]

    if market_values is None:
        raise ValueError("Cement market values must be supplied by the caller.")
    coal_price_eur_per_mwh_th = market_values["coal_price_eur_per_mwh_th"]
    biofuel_price_eur_per_mwh_th = market_values["biofuel_price_eur_per_mwh_th"]
    electricity_price_eur_per_mwh = market_values["electricity_price_eur_per_mwh"]
    alternative_fuel_share_fraction = np.full(size, np.nan)
    fossil_fuel_share_fraction = np.full(size, np.nan)
    if technology == "alternative_fuels":
        if retrofit_values is None:
            raise ValueError("Alternative fuels requires retrofit share values.")
        alternative_fuel_share_fraction = retrofit_values[
            "alternative_fuel_share_fraction"
        ]
        fossil_fuel_share_fraction = 1.0 - alternative_fuel_share_fraction
        fuel_price_eur_per_mwh_th = (
            alternative_fuel_share_fraction * biofuel_price_eur_per_mwh_th
            + fossil_fuel_share_fraction * coal_price_eur_per_mwh_th
        )
    else:
        fuel_price_eur_per_mwh_th = coal_price_eur_per_mwh_th

    initial_capex_eur = annual_output_t * capex_eur_per_t
    annual_revenue_eur = annual_output_t * RETAIL_PRICE_CEMENT_EUR_PER_T.value
    annual_fixed_opex_eur = annual_output_t * fixed_opex_eur_per_t
    annual_variable_opex_eur = annual_output_t * variable_opex_eur_per_t
    annual_fuel_cost_eur = (
        annual_output_t
        * fuel_consumption_mwh_th_per_t
        * fuel_price_eur_per_mwh_th
    )
    annual_electricity_cost_eur = (
        annual_output_t
        * electricity_consumption_mwh_per_t
        * electricity_price_eur_per_mwh
    )
    capture_cost_excluding_transport_and_storage_eur_per_t = np.full(
        size, np.nan
    )
    transport_and_storage_cost_eur_per_t = np.zeros(size)
    transport_and_storage_share_of_capture_cost = np.full(size, np.nan)
    if technology == "ccs":
        if bau_values is None:
            raise ValueError("CCS requires BAU values for its T&S cost basis.")
        transport_and_storage_share_of_capture_cost = np.full(
            size,
            CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value,
        )
        bau_initial_capex_eur = annual_output_t * bau_values["capex_eur_per_t"]
        bau_annual_cost_excluding_carbon_eur = annual_output_t * (
            bau_values["fixed_opex_eur_per_t"]
            + bau_values["variable_opex_eur_per_t"]
            + bau_values["fuel_consumption_mwh_th_per_t"]
            * fuel_price_eur_per_mwh_th
            + bau_values["electricity_consumption_mwh_per_t"]
            * electricity_price_eur_per_mwh
        )
        annual_cost_excluding_carbon_eur = (
            annual_fixed_opex_eur
            + annual_variable_opex_eur
            + annual_fuel_cost_eur
            + annual_electricity_cost_eur
        )
        (
            capture_cost_excluding_transport_and_storage_eur_per_t,
            transport_and_storage_cost_eur_per_t,
        ) = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=initial_capex_eur,
            bau_initial_capex_eur=bau_initial_capex_eur,
            ccs_annual_cost_excluding_carbon_eur=(
                annual_cost_excluding_carbon_eur
            ),
            bau_annual_cost_excluding_carbon_eur=(
                bau_annual_cost_excluding_carbon_eur
            ),
            annual_output=annual_output_t,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
            ),
        )
    annual_transport_and_storage_cost_eur = (
        annual_output_t * transport_and_storage_cost_eur_per_t
    )
    annual_emissions_cost_eur = (
        annual_output_t * emissions_tco2_per_t * CARBON_PRICE_EUR_PER_T.value
    )
    financial_result = calculate_financial_result(
        initial_capex_eur=initial_capex_eur,
        annual_output=annual_output_t,
        annual_revenue_eur=annual_revenue_eur,
        annual_fixed_opex_eur=annual_fixed_opex_eur,
        annual_variable_opex_eur=annual_variable_opex_eur,
        annual_fuel_cost_eur=annual_fuel_cost_eur,
        annual_electricity_cost_eur=annual_electricity_cost_eur,
        annual_transport_and_storage_cost_eur=(
            annual_transport_and_storage_cost_eur
        ),
        annual_emissions_cost_eur=annual_emissions_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
        subtract_cost_components_sequentially=True,
    )
    annual_total_cost_eur = financial_result["annual_total_cost_eur"]
    annual_net_cash_flow_eur = financial_result["annual_net_cash_flow_eur"]
    npv_eur = financial_result["npv_eur"]
    discounted_lifetime_output_t = financial_result[
        "discounted_lifetime_output"
    ]
    present_value_total_cost_eur = financial_result[
        "present_value_total_cost_eur"
    ]
    lcoc_eur_per_t = financial_result["levelized_cost"]
    levelized_profit_margin_eur_per_t = financial_result[
        "levelized_profit_margin"
    ]

    result = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, technology_type),
        "retrofit_bau_mode": np.full(size, bau_mode),
        "annual_output_t": np.full(size, annual_output_t),
        "lifetime_years": np.full(size, lifetime_years),
        "capex_eur_per_t": capex_eur_per_t,
        "fixed_opex_eur_per_t": fixed_opex_eur_per_t,
        "variable_opex_eur_per_t": variable_opex_eur_per_t,
        "fuel_consumption_mwh_th_per_t": fuel_consumption_mwh_th_per_t,
        "electricity_consumption_mwh_per_t": electricity_consumption_mwh_per_t,
        "emissions_tco2_per_t": emissions_tco2_per_t,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        "coal_price_eur_per_mwh_th": coal_price_eur_per_mwh_th,
        "biofuel_price_eur_per_mwh_th": biofuel_price_eur_per_mwh_th,
        "alternative_fuel_share_fraction": alternative_fuel_share_fraction,
        "fossil_fuel_share_fraction": fossil_fuel_share_fraction,
        "electricity_price_eur_per_mwh": electricity_price_eur_per_mwh,
        "cement_price_eur_per_t": np.full(size, RETAIL_PRICE_CEMENT_EUR_PER_T.value),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "capture_cost_excluding_transport_and_storage_eur_per_t": (
            capture_cost_excluding_transport_and_storage_eur_per_t
        ),
        "transport_and_storage_cost_eur_per_t": (
            transport_and_storage_cost_eur_per_t
        ),
        "transport_and_storage_share_of_capture_cost": (
            transport_and_storage_share_of_capture_cost
        ),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": np.full(size, annual_revenue_eur),
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_electricity_cost_eur": annual_electricity_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output_t": np.full(
            size, discounted_lifetime_output_t
        ),
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "lcoc_eur_per_t": lcoc_eur_per_t,
        "levelized_profit_margin_eur_per_t": levelized_profit_margin_eur_per_t,
    }

    if bau_values is not None and include_bau_values:
        for parameter_name, baseline_value in bau_values.items():
            result[f"bau_{parameter_name}"] = baseline_value

    if retrofit_values is not None:
        result.update(retrofit_values)
    if not include_retrofit_bau_mode:
        result.pop("retrofit_bau_mode")

    return result
