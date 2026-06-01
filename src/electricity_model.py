"""Electricity-sector model calculations."""

from __future__ import annotations

from typing import Mapping

import numpy as np

from distributions import (
    FixedParameter,
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
    GAS_PRICE_DISTRIBUTION,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
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


def _sample_parameter(
    parameter: (
        FixedParameter
        | ScaledBetaDistribution
        | TriangularDistribution
        | UniformDistribution
    ),
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if isinstance(parameter, FixedParameter):
        return np.full(size, parameter.value)

    return _sample_distribution(distribution=parameter, size=size, rng=rng)


def simulate_electricity_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for one electricity technology."""

    if size <= 0:
        raise ValueError("size must be positive.")
    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    generator = rng if rng is not None else np.random.default_rng()
    technology_distributions = ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[technology]
    technology_fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]

    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = _sample_parameter(
        technology_fixed_parameters["full_load_hours_per_year"],
        size=size,
        rng=generator,
    )
    capacity_mw = annual_output_mwh / full_load_hours
    capacity_kw = capacity_mw * 1_000.0

    capex_eur_per_kw = _sample_parameter(
        technology_distributions["capex_eur_per_kw"],
        size=size,
        rng=generator,
    )
    fixed_opex_eur_per_kw_year = _sample_parameter(
        technology_distributions["fixed_opex_eur_per_kw_year"],
        size=size,
        rng=generator,
    )
    variable_opex_eur_per_mwh = _sample_parameter(
        technology_distributions["variable_opex_eur_per_mwh"],
        size=size,
        rng=generator,
    )
    fuel_consumption_mwh_th_per_mwh_e = _sample_parameter(
        technology_distributions["fuel_consumption_mwh_th_per_mwh_e"],
        size=size,
        rng=generator,
    )
    emissions_tco2_per_mwh_e = _sample_parameter(
        technology_distributions["emissions_tco2_per_mwh_e"],
        size=size,
        rng=generator,
    )
    fuel_price_distribution_by_technology = {
        "hard_coal": COAL_PRICE_DISTRIBUTION,
        "ccgt": GAS_PRICE_DISTRIBUTION,
        "nuclear": NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_offshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_onshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
    }
    fuel_price_key_by_technology = {
        "hard_coal": "coal_price_eur_per_mwh_th",
        "ccgt": "gas_price_eur_per_mwh_th",
        "nuclear": "uranium_price_eur_per_mwh_th",
        "wind_offshore": "no_fuel_price_eur_per_mwh_th",
        "wind_onshore": "no_fuel_price_eur_per_mwh_th",
    }
    if technology not in fuel_price_distribution_by_technology:
        raise ValueError(f"No fuel-price distribution configured for {technology!r}.")

    fuel_price_eur_per_mwh_th = _sample_parameter(
        parameter=fuel_price_distribution_by_technology[technology],
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
    npv_eur = calculate_npv(
        initial_capex_eur=initial_capex_eur,
        annual_net_cash_flow_eur=annual_net_cash_flow_eur,
        lifetime_years=int(LIFETIME_ELECTRICITY_YEARS.value),
        discount_rate=INTEREST_RATE.value,
    )
    lifetime_output_mwh = annual_output_mwh * LIFETIME_ELECTRICITY_YEARS.value
    npv_eur_per_mwh = npv_eur / lifetime_output_mwh

    return {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "annual_output_mwh": np.full(size, annual_output_mwh),
        "full_load_hours_per_year": full_load_hours,
        "capacity_mw": capacity_mw,
        "capacity_kw": capacity_kw,
        "capex_eur_per_kw": capex_eur_per_kw,
        "fixed_opex_eur_per_kw_year": fixed_opex_eur_per_kw_year,
        "variable_opex_eur_per_mwh": variable_opex_eur_per_mwh,
        "fuel_consumption_mwh_th_per_mwh_e": fuel_consumption_mwh_th_per_mwh_e,
        "emissions_tco2_per_mwh_e": emissions_tco2_per_mwh_e,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        fuel_price_key_by_technology[technology]: fuel_price_eur_per_mwh_th,
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
        "lifetime_output_mwh": np.full(size, lifetime_output_mwh),
        "npv_eur_per_mwh": npv_eur_per_mwh,
        "npv_million_eur_per_mwh": npv_eur_per_mwh / 1_000_000,
    }


def simulate_hard_coal_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for the hard coal electricity plant."""

    return simulate_electricity_technology_npv(
        technology="hard_coal",
        size=size,
        rng=rng,
    )


def simulate_ccgt_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a CCGT electricity plant."""

    return simulate_electricity_technology_npv(
        technology="ccgt",
        size=size,
        rng=rng,
    )


def simulate_nuclear_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for a nuclear electricity plant."""

    return simulate_electricity_technology_npv(
        technology="nuclear",
        size=size,
        rng=rng,
    )


def simulate_wind_offshore_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for an offshore wind electricity plant."""

    return simulate_electricity_technology_npv(
        technology="wind_offshore",
        size=size,
        rng=rng,
    )


def simulate_wind_onshore_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for an onshore wind electricity plant."""

    return simulate_electricity_technology_npv(
        technology="wind_onshore",
        size=size,
        rng=rng,
    )


def simulate_electricity_technologies_npv(
    size: int,
    technologies: tuple[str, ...] = (
        "hard_coal",
        "ccgt",
        "nuclear",
        "wind_offshore",
        "wind_onshore",
    ),
    rng: np.random.Generator | None = None,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run NPV simulations for multiple technologies with aligned run IDs."""

    if size <= 0:
        raise ValueError("size must be positive.")

    generator = rng if rng is not None else np.random.default_rng()
    return {
        technology: simulate_electricity_technology_npv(
            technology=technology,
            size=size,
            rng=generator,
        )
        for technology in technologies
    }
