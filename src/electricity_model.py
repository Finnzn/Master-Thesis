"""Electricity-sector model calculations."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import (
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
    sample_scaled_beta,
    sample_triangular,
    sample_uniform,
)
from electricity_parameters import (
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
    LIFETIME_ELECTRICITY_YEARS,
    RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
)
from general_parameters import (
    CARBON_PRICE_EUR_PER_T,
    COAL_PRICE_DISTRIBUTION,
    INTEREST_RATE,
)


def calculate_capacity_mw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed capacity from annual output and FLH."""

    if annual_electricity_output_mwh <= 0:
        raise ValueError("annual_electricity_output_mwh must be positive.")
    if full_load_hours_per_year <= 0:
        raise ValueError("full_load_hours_per_year must be positive.")

    return annual_electricity_output_mwh / full_load_hours_per_year


def calculate_capacity_kw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed capacity in kW."""

    return calculate_capacity_mw(
        annual_electricity_output_mwh=annual_electricity_output_mwh,
        full_load_hours_per_year=full_load_hours_per_year,
    ) * 1_000.0


def calculate_level_cash_flow_present_value_factor(
    lifetime_years: int,
    discount_rate: float,
) -> float:
    """Calculate the present value factor for a constant annual cash flow."""

    if lifetime_years <= 0:
        raise ValueError("lifetime_years must be positive.")
    if discount_rate < 0:
        raise ValueError("discount_rate must be non-negative.")
    if discount_rate == 0:
        return float(lifetime_years)

    return (1.0 - (1.0 + discount_rate) ** -lifetime_years) / discount_rate


def calculate_npv(
    initial_capex_eur: np.ndarray,
    annual_net_cash_flow_eur: np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> np.ndarray:
    """Calculate NPV from initial CAPEX and level annual net cash flow."""

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    return -initial_capex_eur + annual_net_cash_flow_eur * present_value_factor


def _sample_distribution(
    distribution: (
        ScaledBetaDistribution | TriangularDistribution | UniformDistribution
    ),
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if isinstance(distribution, ScaledBetaDistribution):
        return sample_scaled_beta(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, TriangularDistribution):
        return sample_triangular(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, UniformDistribution):
        return sample_uniform(distribution=distribution, size=size, rng=rng)

    raise TypeError(f"Unsupported distribution type: {type(distribution)!r}")


def simulate_hard_coal_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for the hard coal electricity plant."""

    if size <= 0:
        raise ValueError("size must be positive.")

    generator = rng if rng is not None else np.random.default_rng()
    technology_distributions = ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS["hard_coal"]
    technology_fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS["hard_coal"]

    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = technology_fixed_parameters["full_load_hours_per_year"].value
    capacity_mw = calculate_capacity_mw(
        annual_electricity_output_mwh=annual_output_mwh,
        full_load_hours_per_year=full_load_hours,
    )
    capacity_kw = capacity_mw * 1_000.0

    capex_eur_per_kw = _sample_distribution(
        technology_distributions["capex_eur_per_kw"],
        size=size,
        rng=generator,
    )
    fixed_opex_eur_per_kw_year = _sample_distribution(
        technology_distributions["fixed_opex_eur_per_kw_year"],
        size=size,
        rng=generator,
    )
    variable_opex_eur_per_mwh = _sample_distribution(
        technology_distributions["variable_opex_eur_per_mwh"],
        size=size,
        rng=generator,
    )
    fuel_consumption_mwh_th_per_mwh_e = _sample_distribution(
        technology_distributions["fuel_consumption_mwh_th_per_mwh_e"],
        size=size,
        rng=generator,
    )
    emissions_tco2_per_mwh_e = _sample_distribution(
        technology_distributions["emissions_tco2_per_mwh_e"],
        size=size,
        rng=generator,
    )
    coal_price_eur_per_mwh_th = sample_scaled_beta(
        distribution=COAL_PRICE_DISTRIBUTION,
        size=size,
        rng=generator,
    )
    electricity_price_eur_per_mwh = RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value

    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = annual_output_mwh * electricity_price_eur_per_mwh
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * coal_price_eur_per_mwh_th
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
    npv_eur = calculate_npv(
        initial_capex_eur=initial_capex_eur,
        annual_net_cash_flow_eur=annual_net_cash_flow_eur,
        lifetime_years=int(LIFETIME_ELECTRICITY_YEARS.value),
        discount_rate=INTEREST_RATE.value,
    )

    return {
        "run_id": np.arange(size),
        "annual_output_mwh": np.full(size, annual_output_mwh),
        "capacity_mw": np.full(size, capacity_mw),
        "capacity_kw": np.full(size, capacity_kw),
        "capex_eur_per_kw": capex_eur_per_kw,
        "fixed_opex_eur_per_kw_year": fixed_opex_eur_per_kw_year,
        "variable_opex_eur_per_mwh": variable_opex_eur_per_mwh,
        "fuel_consumption_mwh_th_per_mwh_e": fuel_consumption_mwh_th_per_mwh_e,
        "emissions_tco2_per_mwh_e": emissions_tco2_per_mwh_e,
        "coal_price_eur_per_mwh_th": coal_price_eur_per_mwh_th,
        "electricity_price_eur_per_mwh": np.full(size, electricity_price_eur_per_mwh),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": np.full(size, annual_revenue_eur),
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
    }
