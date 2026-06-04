"""Deterministic NPV calculations for electricity technologies."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import FixedParameter, ScaledBetaDistribution
from electricity_capacity_calculation import calculate_capacity_kw
from electricity_parameters import (
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
    LIFETIME_ELECTRICITY_YEARS,
    RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
)
from general_parameters import (
    BIOGAS_PRICE_EUR_PER_MWH_TH,
    CARBON_PRICE_EUR_PER_T,
    COAL_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
)
from npv_summary import representative_value
from npv_finance import calculate_npv


def electricity_fuel_price_parameter(
    technology: str,
) -> FixedParameter | ScaledBetaDistribution:
    """Return the fuel-price parameter used by an electricity technology."""

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
    }
    if technology not in fuel_price_by_technology:
        raise ValueError(f"No fuel-price parameter configured for {technology!r}.")

    return fuel_price_by_technology[technology]


def calculate_deterministic_electricity_result(
    technology: str,
) -> Mapping[str, object]:
    """Calculate deterministic electricity inputs and outputs for one technology."""

    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    distributions = ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[technology]
    fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]

    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = representative_value(
        fixed_parameters["full_load_hours_per_year"]
    )
    capacity_kw = calculate_capacity_kw(
        annual_electricity_output_mwh=annual_output_mwh,
        full_load_hours_per_year=full_load_hours,
    )

    capex_eur_per_kw = representative_value(distributions["capex_eur_per_kw"])
    fixed_opex_eur_per_kw_year = representative_value(
        distributions["fixed_opex_eur_per_kw_year"]
    )
    variable_opex_eur_per_mwh = representative_value(
        distributions["variable_opex_eur_per_mwh"]
    )
    fuel_consumption_mwh_th_per_mwh_e = representative_value(
        distributions["fuel_consumption_mwh_th_per_mwh_e"]
    )
    emissions_tco2_per_mwh_e = representative_value(
        distributions["emissions_tco2_per_mwh_e"]
    )
    fuel_price_eur_per_mwh_th = representative_value(
        electricity_fuel_price_parameter(technology)
    )

    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = (
        annual_output_mwh * RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value
    )
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * fuel_price_eur_per_mwh_th
    )
    annual_emissions_cost_eur = (
        annual_output_mwh * emissions_tco2_per_mwh_e * CARBON_PRICE_EUR_PER_T.value
    )
    annual_net_cash_flow_eur = (
        annual_revenue_eur
        - annual_fixed_opex_eur
        - annual_variable_opex_eur
        - annual_fuel_cost_eur
        - annual_emissions_cost_eur
    )
    npv_eur = float(
        calculate_npv(
            initial_capex_eur=np.array([initial_capex_eur]),
            annual_net_cash_flow_eur=np.array([annual_net_cash_flow_eur]),
            lifetime_years=int(LIFETIME_ELECTRICITY_YEARS.value),
            discount_rate=INTEREST_RATE.value,
        )[0]
    )
    lifetime_output_mwh = annual_output_mwh * LIFETIME_ELECTRICITY_YEARS.value
    npv_eur_per_mwh = npv_eur / lifetime_output_mwh

    return {
        "run_id": [0],
        "technology": [technology],
        "annual_output_mwh": [annual_output_mwh],
        "full_load_hours_per_year": [full_load_hours],
        "capex_eur_per_kw": [capex_eur_per_kw],
        "fixed_opex_eur_per_kw_year": [fixed_opex_eur_per_kw_year],
        "variable_opex_eur_per_mwh": [variable_opex_eur_per_mwh],
        "fuel_consumption_mwh_th_per_mwh_e": [
            fuel_consumption_mwh_th_per_mwh_e
        ],
        "emissions_tco2_per_mwh_e": [emissions_tco2_per_mwh_e],
        "fuel_price_eur_per_mwh_th": [fuel_price_eur_per_mwh_th],
        "electricity_price_eur_per_mwh": [
            RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value
        ],
        "carbon_price_eur_per_t": [CARBON_PRICE_EUR_PER_T.value],
        "capacity_mw": [capacity_kw / 1_000.0],
        "capacity_kw": [capacity_kw],
        "initial_capex_eur": [initial_capex_eur],
        "annual_revenue_eur": [annual_revenue_eur],
        "annual_fixed_opex_eur": [annual_fixed_opex_eur],
        "annual_variable_opex_eur": [annual_variable_opex_eur],
        "annual_fuel_cost_eur": [annual_fuel_cost_eur],
        "annual_emissions_cost_eur": [annual_emissions_cost_eur],
        "annual_net_cash_flow_eur": [annual_net_cash_flow_eur],
        "npv_eur": [npv_eur],
        "lifetime_output_mwh": [lifetime_output_mwh],
        "npv_eur_per_mwh": [npv_eur_per_mwh],
        "npv_million_eur_per_mwh": [npv_eur_per_mwh / 1_000_000],
    }


def calculate_deterministic_electricity_npv_eur(technology: str) -> float:
    """Calculate deterministic electricity NPV from representative values."""

    return float(calculate_deterministic_electricity_result(technology)["npv_eur"][0])


def calculate_deterministic_electricity_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic electricity results for all selected technologies."""

    selected_technologies = technologies or tuple(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
    return {
        technology: calculate_deterministic_electricity_result(technology)
        for technology in selected_technologies
    }
