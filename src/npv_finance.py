"""Sector-independent discounted financial calculations.

All sector models eventually reduce to the same financial structure: an upfront
capital cost at year 0 and a constant annual net cash flow over the asset
lifetime. Keeping the NPV, levelized profit margin, and levelized cost formulas
here makes it easier to compare electricity, cement, and future sectors with
consistent discounting.
"""

from __future__ import annotations

import numpy as np


def calculate_financial_result(
    *,
    initial_capex_eur: float | np.ndarray,
    annual_output: float | np.ndarray,
    annual_revenue_eur: float | np.ndarray,
    annual_fixed_opex_eur: float | np.ndarray,
    annual_variable_opex_eur: float | np.ndarray,
    annual_fuel_cost_eur: float | np.ndarray,
    annual_electricity_cost_eur: float | np.ndarray,
    annual_transport_and_storage_cost_eur: float | np.ndarray,
    annual_emissions_cost_eur: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
    subtract_cost_components_sequentially: bool = False,
) -> dict[str, float | np.ndarray]:
    """Calculate the common financial outputs from explicit annual cash flows.

    Sector modules remain responsible for translating their physical inputs into
    the annual cost components below.  This function is the single discounted
    financial calculation used by deterministic, Monte Carlo, and sensitivity
    workflows.
    """

    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_electricity_cost_eur
        + annual_transport_and_storage_cost_eur
        + annual_emissions_cost_eur
    )
    if subtract_cost_components_sequentially:
        # Electricity and cement historically formed net cash flow with a
        # subtraction chain.  Retaining that operation order keeps their
        # floating-point outputs bit-for-bit compatible.
        annual_net_cash_flow_eur = (
            annual_revenue_eur
            - annual_fixed_opex_eur
            - annual_variable_opex_eur
            - annual_fuel_cost_eur
            - annual_electricity_cost_eur
            - annual_transport_and_storage_cost_eur
            - annual_emissions_cost_eur
        )
    else:
        annual_net_cash_flow_eur = annual_revenue_eur - annual_total_cost_eur
    npv_eur = calculate_npv(
        initial_capex_eur=np.asarray(initial_capex_eur),
        annual_net_cash_flow_eur=np.asarray(annual_net_cash_flow_eur),
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    discounted_lifetime_output = calculate_discounted_lifetime_output(
        annual_output=annual_output,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    present_value_total_cost_eur = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    levelized_cost = np.asarray(present_value_total_cost_eur) / np.asarray(
        discounted_lifetime_output
    )
    levelized_profit_margin = np.asarray(npv_eur) / np.asarray(
        discounted_lifetime_output
    )

    return {
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output": discounted_lifetime_output,
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "levelized_cost": levelized_cost,
        "levelized_profit_margin": levelized_profit_margin,
    }


def calculate_product_financial_result(
    *,
    annual_output: float | np.ndarray,
    capex_per_output: float | np.ndarray,
    sales_price_per_output: float | np.ndarray,
    fixed_opex_per_output: float | np.ndarray,
    variable_opex_per_output: float | np.ndarray,
    fuel_consumption_per_output: float | np.ndarray,
    fuel_price: float | np.ndarray,
    electricity_consumption_per_output: float | np.ndarray,
    electricity_price: float | np.ndarray,
    transport_and_storage_cost_per_output: float | np.ndarray,
    emissions_per_output: float | np.ndarray,
    carbon_price: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
    secondary_fuel_consumption_per_output: float | np.ndarray = 0.0,
    secondary_fuel_price: float | np.ndarray = 0.0,
    include_secondary_fuel: bool = False,
) -> dict[str, float | np.ndarray]:
    """Translate per-output assumptions into the common financial result."""

    initial_capex_eur = annual_output * capex_per_output
    annual_revenue_eur = annual_output * sales_price_per_output
    annual_fixed_opex_eur = annual_output * fixed_opex_per_output
    annual_variable_opex_eur = annual_output * variable_opex_per_output
    if include_secondary_fuel:
        annual_fuel_cost_eur = annual_output * (
            fuel_consumption_per_output * fuel_price
            + secondary_fuel_consumption_per_output * secondary_fuel_price
        )
    else:
        annual_fuel_cost_eur = (
            annual_output * fuel_consumption_per_output * fuel_price
        )
    annual_electricity_cost_eur = (
        annual_output * electricity_consumption_per_output * electricity_price
    )
    annual_transport_and_storage_cost_eur = (
        annual_output * transport_and_storage_cost_per_output
    )
    annual_emissions_cost_eur = annual_output * emissions_per_output * carbon_price
    result = calculate_financial_result(
        initial_capex_eur=initial_capex_eur,
        annual_output=annual_output,
        annual_revenue_eur=annual_revenue_eur,
        annual_fixed_opex_eur=annual_fixed_opex_eur,
        annual_variable_opex_eur=annual_variable_opex_eur,
        annual_fuel_cost_eur=annual_fuel_cost_eur,
        annual_electricity_cost_eur=annual_electricity_cost_eur,
        annual_transport_and_storage_cost_eur=(
            annual_transport_and_storage_cost_eur
        ),
        annual_emissions_cost_eur=annual_emissions_cost_eur,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    return {
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_electricity_cost_eur": annual_electricity_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        **result,
    }


def calculate_electricity_financial_result(
    *,
    annual_output_mwh: float | np.ndarray,
    full_load_hours_per_year: float | np.ndarray,
    capex_eur_per_kw: float | np.ndarray,
    electricity_price_eur_per_mwh: float | np.ndarray,
    value_factor: float | np.ndarray,
    fixed_opex_eur_per_kw_year: float | np.ndarray,
    variable_opex_eur_per_mwh: float | np.ndarray,
    fuel_consumption_mwh_th_per_mwh_e: float | np.ndarray,
    fuel_price_eur_per_mwh_th: float | np.ndarray,
    transport_and_storage_cost_eur_per_mwh: float | np.ndarray,
    emissions_tco2_per_mwh_e: float | np.ndarray,
    carbon_price_eur_per_t: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> dict[str, float | np.ndarray]:
    """Translate electricity assumptions into the common financial result."""

    capacity_kw = annual_output_mwh / full_load_hours_per_year * 1_000.0
    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = (
        annual_output_mwh * electricity_price_eur_per_mwh * value_factor
    )
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * fuel_price_eur_per_mwh_th
    )
    annual_transport_and_storage_cost_eur = (
        annual_output_mwh * transport_and_storage_cost_eur_per_mwh
    )
    annual_emissions_cost_eur = (
        annual_output_mwh * emissions_tco2_per_mwh_e * carbon_price_eur_per_t
    )
    result = calculate_financial_result(
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
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    return {
        "capacity_kw": capacity_kw,
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        **result,
    }


def calculate_level_cash_flow_present_value_factor(
    lifetime_years: int,
    discount_rate: float,
) -> float:
    """Calculate the present value factor for a constant annual cash flow.

    The factor is the discounted value today of receiving one EUR every year for
    `lifetime_years`. Multiplying annual net cash flow by this factor converts
    the yearly operating result into a present value.
    """

    if lifetime_years <= 0:
        raise ValueError("lifetime_years must be positive.")
    if discount_rate < 0:
        raise ValueError("discount_rate must be non-negative.")
    if discount_rate == 0:
        # With no discounting, the present value is simply one unit per year.
        return float(lifetime_years)

    return (1.0 - (1.0 + discount_rate) ** -lifetime_years) / discount_rate


def calculate_npv(
    initial_capex_eur: np.ndarray,
    annual_net_cash_flow_eur: np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> np.ndarray:
    """Calculate NPV from initial CAPEX and level annual net cash flow.

    Inputs can be arrays, which is why the same function works for both one
    deterministic result and many Monte Carlo draws.
    """

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    # Initial CAPEX is paid at year 0; annual cash flow is discounted over the lifetime.
    return -initial_capex_eur + annual_net_cash_flow_eur * present_value_factor


def calculate_discounted_lifetime_output(
    annual_output: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> float | np.ndarray:
    """Calculate lifetime output discounted on the same basis as annual cash flow."""

    output = np.asarray(annual_output)
    if np.any(output <= 0):
        raise ValueError("annual_output must be positive.")

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    discounted_output = output * present_value_factor
    if np.ndim(discounted_output) == 0:
        return float(discounted_output)
    return discounted_output


def calculate_levelized_profit_margin(
    npv_eur: float | np.ndarray,
    annual_output: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> float | np.ndarray:
    """Calculate levelized profit margin as NPV per discounted lifetime output.

    The numerator and denominator use the same lifetime and discount rate. The
    result is therefore expressed in EUR per physical unit of output, while
    retaining NPV's sign: positive values create value and negative values
    destroy value under the stated assumptions. This is algebraically equal to
    levelized revenue minus levelized cost when both use the same discounted
    lifetime-output denominator.
    """

    discounted_output = calculate_discounted_lifetime_output(
        annual_output=annual_output,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    levelized_profit_margin = np.asarray(npv_eur) / discounted_output
    if np.ndim(levelized_profit_margin) == 0:
        return float(levelized_profit_margin)
    return levelized_profit_margin


def calculate_total_cost_present_value(
    initial_capex_eur: float | np.ndarray,
    annual_cost_eur: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> float | np.ndarray:
    """Calculate discounted lifetime cost including year-zero CAPEX."""

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    present_value_total_cost = (
        np.asarray(initial_capex_eur)
        + np.asarray(annual_cost_eur) * present_value_factor
    )
    if np.ndim(present_value_total_cost) == 0:
        return float(present_value_total_cost)
    return present_value_total_cost


def calculate_levelized_cost(
    initial_capex_eur: float | np.ndarray,
    annual_cost_eur: float | np.ndarray,
    annual_output: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> float | np.ndarray:
    """Calculate LCOX as discounted lifetime cost per discounted output.

    Revenue is deliberately excluded. ``annual_cost_eur`` should contain the
    operating, fuel, energy, and carbon costs included in the model boundary.
    Electricity reports the result as LCOE; cement reports it as LCOC.
    """

    present_value_total_cost = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_cost_eur,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    discounted_output = calculate_discounted_lifetime_output(
        annual_output=annual_output,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    levelized_cost = np.asarray(present_value_total_cost) / discounted_output
    if np.ndim(levelized_cost) == 0:
        return float(levelized_cost)
    return levelized_cost


def calculate_ccs_transport_and_storage_cost_per_output(
    ccs_initial_capex_eur: float | np.ndarray,
    bau_initial_capex_eur: float | np.ndarray,
    ccs_annual_cost_excluding_carbon_eur: float | np.ndarray,
    bau_annual_cost_excluding_carbon_eur: float | np.ndarray,
    annual_output: float | np.ndarray,
    lifetime_years: int,
    discount_rate: float,
    transport_and_storage_share: float,
) -> tuple[float | np.ndarray, float | np.ndarray]:
    """Return levelized capture cost and its T&S surcharge.

    Capture cost is the levelized difference between BAU+CCS and BAU across
    CAPEX and non-carbon annual costs. Carbon-price effects and T&S itself are
    deliberately outside the basis.
    """

    if transport_and_storage_share < 0.0:
        raise ValueError("transport_and_storage_share must be non-negative.")

    capture_cost_excluding_transport_and_storage = calculate_levelized_cost(
        initial_capex_eur=ccs_initial_capex_eur - bau_initial_capex_eur,
        annual_cost_eur=(
            ccs_annual_cost_excluding_carbon_eur
            - bau_annual_cost_excluding_carbon_eur
        ),
        annual_output=annual_output,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    transport_and_storage_cost = (
        transport_and_storage_share
        * capture_cost_excluding_transport_and_storage
    )
    return capture_cost_excluding_transport_and_storage, transport_and_storage_cost
