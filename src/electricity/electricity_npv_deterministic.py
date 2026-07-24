"""Deterministic NPV calculations for electricity technologies.

The deterministic calculation is the one-point counterpart to the Monte Carlo
model. It uses the same electricity assumptions and cash-flow formula, but each
uncertain parameter is replaced by one representative value. This gives a
baseline NPV that can be compared with the simulated mean and uncertainty range.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import FixedParameter, ScaledBetaDistribution
from electricity.electricity_capacity_calculation import calculate_capacity_kw
from electricity.electricity_parameters import (
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
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
from npv_finance import (
    calculate_discounted_lifetime_output,
    calculate_levelized_cost,
    calculate_levelized_net_margin,
    calculate_npv,
    calculate_total_cost_present_value,
)


def electricity_fuel_price_parameter(
    technology: str,
) -> FixedParameter | ScaledBetaDistribution:
    """Return the fuel-price parameter used by an electricity technology.

    Fuel prices are not stored inside every technology block because several
    technologies share the same fuel market assumption. This mapping connects
    each electricity technology to the relevant shared fuel-price parameter.
    """

    # Fuel-price assumptions match the Monte Carlo model. The deterministic run
    # later reduces the returned parameter to its representative value.
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
    """Calculate deterministic electricity inputs and outputs for one technology.

    The returned structure deliberately mirrors the Monte Carlo result keys, but
    each value is a one-element list. This allows shared CSV and plotting helpers
    to work for deterministic and simulated results.
    """

    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    distributions = ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[technology]
    fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]

    # Deterministic calculations use one representative value for each uncertain
    # input, then follow the same sizing and cash-flow sequence as the Monte Carlo
    # calculation.
    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = representative_value(
        fixed_parameters["full_load_hours_per_year"]
    )
    lifetime_years = representative_value(fixed_parameters["lifetime_years"])
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

    # The cash-flow structure mirrors the Monte Carlo calculation: revenue from
    # electricity sales minus fixed OPEX, variable OPEX, fuel cost, and carbon cost.
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
    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_emissions_cost_eur
    )
    npv_eur = float(
        calculate_npv(
            initial_capex_eur=np.array([initial_capex_eur]),
            annual_net_cash_flow_eur=np.array([annual_net_cash_flow_eur]),
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
        )[0]
    )
    discounted_lifetime_output_mwh = calculate_discounted_lifetime_output(
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    levelized_net_margin_eur_per_mwh = calculate_levelized_net_margin(
        npv_eur=npv_eur,
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    present_value_total_cost_eur = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    lcoe_eur_per_mwh = calculate_levelized_cost(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        annual_output=annual_output_mwh,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )

    # Keep the same output keys as the Monte Carlo result for shared export helpers.
    return {
        "run_id": [0],
        "technology": [technology],
        "annual_output_mwh": [annual_output_mwh],
        "full_load_hours_per_year": [full_load_hours],
        "lifetime_years": [lifetime_years],
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
        "annual_total_cost_eur": [annual_total_cost_eur],
        "annual_net_cash_flow_eur": [annual_net_cash_flow_eur],
        "npv_eur": [npv_eur],
        "discounted_lifetime_output_mwh": [discounted_lifetime_output_mwh],
        "present_value_total_cost_eur": [present_value_total_cost_eur],
        "lcoe_eur_per_mwh": [lcoe_eur_per_mwh],
        "levelized_net_margin_eur_per_mwh": [
            levelized_net_margin_eur_per_mwh
        ],
    }


def calculate_deterministic_electricity_npv_eur(technology: str) -> float:
    """Calculate deterministic electricity NPV from representative values.

    This small wrapper is useful when only the final NPV is needed and not the
    intermediate deterministic inputs and cost components.
    """

    return float(calculate_deterministic_electricity_result(technology)["npv_eur"][0])


def calculate_deterministic_electricity_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic electricity results for all selected technologies.

    By default this follows the order of the electricity technology registry, so
    adding a technology to `ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS` automatically
    includes it in the deterministic comparison.
    """

    selected_technologies = technologies or tuple(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
    return {
        technology: calculate_deterministic_electricity_result(technology)
        for technology in selected_technologies
    }
