"""Shared electricity technology resolution and financial-result model."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from electricity.electricity_parameters import (
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
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


FUEL_PRICE_KEY_BY_TECHNOLOGY = {
    "hard_coal": "coal_price_eur_per_mwh_th",
    "hard_coal_ccs": "coal_price_eur_per_mwh_th",
    "ccgt": "gas_price_eur_per_mwh_th",
    "ccgt_ccs": "gas_price_eur_per_mwh_th",
    "nuclear": "uranium_price_eur_per_mwh_th",
    "wind_offshore": "no_fuel_price_eur_per_mwh_th",
    "wind_onshore": "no_fuel_price_eur_per_mwh_th",
    "pv": "no_fuel_price_eur_per_mwh_th",
    "biogas": "biogas_price_eur_per_mwh_th",
    "beccs": "biomass_price_eur_per_mwh_th",
}


def resolve_technology_values(
    bau_values: Mapping[str, np.ndarray],
    retrofit_values: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve absolute retrofit inputs from BAU arrays and sampled changes."""

    return {
        "capex_eur_per_kw": (
            bau_values["capex_eur_per_kw"]
            + retrofit_values["capex_change_eur_per_kw"]
        ),
        "fixed_opex_eur_per_kw_year": (
            bau_values["fixed_opex_eur_per_kw_year"]
            + retrofit_values["fixed_opex_change_eur_per_kw_year"]
        ),
        "variable_opex_eur_per_mwh": (
            bau_values["variable_opex_eur_per_mwh"]
            + retrofit_values["variable_opex_change_eur_per_mwh"]
        ),
        "fuel_consumption_mwh_th_per_mwh_e": (
            bau_values["fuel_consumption_mwh_th_per_mwh_e"]
            * (1.0 - retrofit_values["fuel_consumption_reduction_fraction"])
        ),
        "emissions_tco2_per_mwh_e": (
            bau_values["emissions_tco2_per_mwh_e"]
            * (1.0 - retrofit_values["emissions_reduction_fraction"])
        ),
    }


def calculate_result(
    technology: str,
    technology_type: str,
    bau_mode: str,
    values: Mapping[str, np.ndarray],
    size: int,
    full_load_hours: np.ndarray,
    lifetime_years: float,
    value_factor: np.ndarray,
    fuel_price_eur_per_mwh_th: np.ndarray,
    *,
    baseline_values: Mapping[str, np.ndarray] | None = None,
    retrofit_values: Mapping[str, np.ndarray] | None = None,
    beccs_transport_and_storage_cost_eur_per_mwh: np.ndarray | None = None,
    include_retrofit_bau_mode: bool = True,
    include_bau_values: bool = True,
    include_fuel_price_source: bool = True,
    export_capacity_mw_from_kw: bool = False,
) -> Mapping[str, np.ndarray]:
    """Calculate all electricity costs and financial outputs from resolved inputs."""

    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    capacity_mw = annual_output_mwh / full_load_hours
    capacity_kw = capacity_mw * 1_000.0

    # Absolute and resolved retrofit values use one shared key schema, so the
    # capacity, cash-flow, and NPV formulas below remain technology-agnostic.
    capex_eur_per_kw = values["capex_eur_per_kw"]
    fixed_opex_eur_per_kw_year = values["fixed_opex_eur_per_kw_year"]
    variable_opex_eur_per_mwh = values["variable_opex_eur_per_mwh"]
    fuel_consumption_mwh_th_per_mwh_e = values[
        "fuel_consumption_mwh_th_per_mwh_e"
    ]
    emissions_tco2_per_mwh_e = values["emissions_tco2_per_mwh_e"]
    fuel_price_key = FUEL_PRICE_KEY_BY_TECHNOLOGY[technology]
    electricity_price_eur_per_mwh = RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value
    captured_electricity_price_eur_per_mwh = (
        electricity_price_eur_per_mwh * value_factor
    )

    # Renewable value factors scale the common sales-price proxy to the captured
    # price. Annual cash flow is revenue minus operating, fuel, and carbon-cost
    # terms; CAPEX is handled separately in the NPV formula.
    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = (
        annual_output_mwh * captured_electricity_price_eur_per_mwh
    )
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * fuel_price_eur_per_mwh_th
    )
    capture_cost_excluding_transport_and_storage_eur_per_mwh = np.full(
        size, np.nan
    )
    transport_and_storage_cost_eur_per_mwh = np.zeros(size)
    transport_and_storage_cost_input_eur_per_mwh = np.full(size, np.nan)
    transport_and_storage_share_of_capture_cost = np.full(size, np.nan)
    if baseline_values is not None:
        transport_and_storage_share_of_capture_cost = np.full(
            size,
            CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value,
        )
        bau_initial_capex_eur = capacity_kw * baseline_values["capex_eur_per_kw"]
        bau_annual_cost_excluding_carbon_eur = (
            capacity_kw * baseline_values["fixed_opex_eur_per_kw_year"]
            + annual_output_mwh * baseline_values["variable_opex_eur_per_mwh"]
            + annual_output_mwh
            * baseline_values["fuel_consumption_mwh_th_per_mwh_e"]
            * fuel_price_eur_per_mwh_th
        )
        annual_cost_excluding_carbon_eur = (
            annual_fixed_opex_eur
            + annual_variable_opex_eur
            + annual_fuel_cost_eur
        )
        (
            capture_cost_excluding_transport_and_storage_eur_per_mwh,
            transport_and_storage_cost_eur_per_mwh,
        ) = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=initial_capex_eur,
            bau_initial_capex_eur=bau_initial_capex_eur,
            ccs_annual_cost_excluding_carbon_eur=(
                annual_cost_excluding_carbon_eur
            ),
            bau_annual_cost_excluding_carbon_eur=(
                bau_annual_cost_excluding_carbon_eur
            ),
            annual_output=annual_output_mwh,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
            ),
        )
    elif technology == "beccs":
        if beccs_transport_and_storage_cost_eur_per_mwh is None:
            raise ValueError("BECCS requires an explicit transport/storage input.")
        transport_and_storage_cost_eur_per_mwh = (
            beccs_transport_and_storage_cost_eur_per_mwh
        )
        transport_and_storage_cost_input_eur_per_mwh = (
            transport_and_storage_cost_eur_per_mwh.copy()
        )
    annual_transport_and_storage_cost_eur = (
        annual_output_mwh * transport_and_storage_cost_eur_per_mwh
    )
    # For BECCS, sampled emissions are negative. The resulting negative
    # carbon-cost value is subtracted from cash flow and therefore acts as
    # carbon-removal revenue while retaining one shared formula.
    annual_emissions_cost_eur = (
        annual_output_mwh * emissions_tco2_per_mwh_e * CARBON_PRICE_EUR_PER_T.value
    )
    financial_result = calculate_financial_result(
        initial_capex_eur=initial_capex_eur,
        annual_output=annual_output_mwh,
        annual_revenue_eur=annual_revenue_eur,
        annual_fixed_opex_eur=annual_fixed_opex_eur,
        annual_variable_opex_eur=annual_variable_opex_eur,
        annual_fuel_cost_eur=annual_fuel_cost_eur,
        annual_electricity_cost_eur=0.0,
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
    discounted_lifetime_output_mwh = financial_result[
        "discounted_lifetime_output"
    ]
    present_value_total_cost_eur = financial_result[
        "present_value_total_cost_eur"
    ]
    lcoe_eur_per_mwh = financial_result["levelized_cost"]
    levelized_profit_margin_eur_per_mwh = financial_result[
        "levelized_profit_margin"
    ]

    # Return both sampled inputs and derived outputs so CSV exports are traceable.
    # `run_id` links technologies when they are ranked within the same simulation.
    exported_capacity_mw = (
        capacity_kw / 1_000.0 if export_capacity_mw_from_kw else capacity_mw
    )
    result = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, technology_type),
        "retrofit_bau_mode": np.full(size, bau_mode),
        "annual_output_mwh": np.full(size, annual_output_mwh),
        "full_load_hours_per_year": full_load_hours,
        "lifetime_years": np.full(size, lifetime_years),
        "capacity_mw": exported_capacity_mw,
        "capacity_kw": capacity_kw,
        "capex_eur_per_kw": capex_eur_per_kw,
        "fixed_opex_eur_per_kw_year": fixed_opex_eur_per_kw_year,
        "variable_opex_eur_per_mwh": variable_opex_eur_per_mwh,
        "fuel_consumption_mwh_th_per_mwh_e": fuel_consumption_mwh_th_per_mwh_e,
        "emissions_tco2_per_mwh_e": emissions_tco2_per_mwh_e,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        fuel_price_key: fuel_price_eur_per_mwh_th,
        "electricity_price_eur_per_mwh": np.full(size, electricity_price_eur_per_mwh),
        "value_factor": value_factor,
        "captured_electricity_price_eur_per_mwh": (
            captured_electricity_price_eur_per_mwh
        ),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "capture_cost_excluding_transport_and_storage_eur_per_mwh": (
            capture_cost_excluding_transport_and_storage_eur_per_mwh
        ),
        "transport_and_storage_cost_eur_per_mwh": (
            transport_and_storage_cost_eur_per_mwh
        ),
        "transport_and_storage_cost_input_eur_per_mwh": (
            transport_and_storage_cost_input_eur_per_mwh
        ),
        "transport_and_storage_share_of_capture_cost": (
            transport_and_storage_share_of_capture_cost
        ),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output_mwh": np.full(
            size, discounted_lifetime_output_mwh
        ),
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "lcoe_eur_per_mwh": lcoe_eur_per_mwh,
        "levelized_profit_margin_eur_per_mwh": levelized_profit_margin_eur_per_mwh,
    }

    if baseline_values is not None and include_bau_values:
        for parameter_name, baseline_value in baseline_values.items():
            result[f"bau_{parameter_name}"] = baseline_value

    if retrofit_values is not None:
        result.update(retrofit_values)
    if not include_retrofit_bau_mode:
        result.pop("retrofit_bau_mode")
    if not include_fuel_price_source:
        result.pop(fuel_price_key)

    return result
