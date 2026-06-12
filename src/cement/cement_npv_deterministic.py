"""Deterministic NPV calculations for cement technologies.

The deterministic cement calculation mirrors the electricity deterministic
workflow: each uncertain input is reduced to one representative value, annual
cash flow is calculated for a normalized output volume, and the shared NPV
formula discounts that cash flow over the asset lifetime.

BAU and alternative cement technologies use absolute parameter values. Retrofit
technologies are different: their assumptions are changes relative to the BAU
cement baseline, so this module first resolves them into absolute intensities
before calculating costs and NPV.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from cement.cement_parameters import (
    ANNUAL_CEMENT_OUTPUT_T,
    CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    CEMENT_TECHNOLOGY_DISTRIBUTIONS,
    LIFETIME_CEMENT_YEARS,
    RETAIL_PRICE_CEMENT_EUR_PER_T,
)
from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from general_parameters import (
    BIOFUEL_PRICE_DISTRIBUTION,
    CARBON_PRICE_EUR_PER_T,
    COAL_PRICE_DISTRIBUTION,
    ELECTRICITY_PRICE_DISTRIBUTION,
    INTEREST_RATE,
)
from npv_finance import calculate_npv
from npv_summary import representative_value


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def cement_fuel_price_parameter(
    technology: str,
) -> ScaledBetaDistribution | UniformDistribution:
    """Return the deterministic fuel-price source for a cement technology.

    Cement BAU and most cement technologies use the shared coal thermal fuel
    price assumption. The alternative-fuels retrofit uses the biofuel price
    assumption that was added with that retrofit technology.
    """

    if technology == "alternative_fuels":
        return BIOFUEL_PRICE_DISTRIBUTION

    all_technologies = (
        set(CEMENT_TECHNOLOGY_DISTRIBUTIONS)
        | set(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"No fuel-price parameter configured for {technology!r}.")

    return COAL_PRICE_DISTRIBUTION


def _representative_values(
    parameters: Mapping[str, ParameterSpec],
) -> dict[str, float]:
    """Convert one parameter mapping into deterministic representative values."""

    return {
        parameter_name: representative_value(parameter)
        for parameter_name, parameter in parameters.items()
    }


def _deterministic_bau_values() -> dict[str, float]:
    """Return deterministic absolute BAU cement values."""

    return _representative_values(CEMENT_TECHNOLOGY_DISTRIBUTIONS["bau"])


def _deterministic_cement_technology_values(technology: str) -> dict[str, float]:
    """Resolve absolute deterministic values for one cement technology.

    Absolute technologies are read directly from the cement technology registry.
    Retrofit technologies are calculated relative to deterministic BAU values:
    CAPEX and OPEX changes are added to BAU, while positive reduction fractions
    reduce BAU fuel use, electricity use, and direct emissions. Negative
    reduction fractions therefore increase the corresponding BAU value.
    """

    if technology in CEMENT_TECHNOLOGY_DISTRIBUTIONS:
        return _representative_values(CEMENT_TECHNOLOGY_DISTRIBUTIONS[technology])

    if technology not in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown cement technology: {technology!r}.")

    bau_values = _deterministic_bau_values()
    retrofit_values = _representative_values(
        CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology]
    )

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
        "capex_change_eur_per_t": retrofit_values["capex_change_eur_per_t"],
        "fixed_opex_change_eur_per_t": (
            retrofit_values["fixed_opex_change_eur_per_t"]
        ),
        "variable_opex_change_eur_per_t": (
            retrofit_values["variable_opex_change_eur_per_t"]
        ),
        "fuel_consumption_reduction_fraction": (
            retrofit_values["fuel_consumption_reduction_fraction"]
        ),
        "electricity_consumption_reduction_fraction": (
            retrofit_values["electricity_consumption_reduction_fraction"]
        ),
        "emissions_reduction_fraction": (
            retrofit_values["emissions_reduction_fraction"]
        ),
    }


def calculate_deterministic_cement_result(
    technology: str,
) -> Mapping[str, object]:
    """Calculate deterministic cement inputs and outputs for one technology."""

    values = _deterministic_cement_technology_values(technology)

    annual_output_t = ANNUAL_CEMENT_OUTPUT_T.value
    lifetime_years = LIFETIME_CEMENT_YEARS.value
    capex_eur_per_t = values["capex_eur_per_t"]
    fixed_opex_eur_per_t = values["fixed_opex_eur_per_t"]
    variable_opex_eur_per_t = values["variable_opex_eur_per_t"]
    fuel_consumption_mwh_th_per_t = values["fuel_consumption_mwh_th_per_t"]
    electricity_consumption_mwh_per_t = values["electricity_consumption_mwh_per_t"]
    emissions_tco2_per_t = values["emissions_tco2_per_t"]
    fuel_price_eur_per_mwh_th = representative_value(
        cement_fuel_price_parameter(technology)
    )
    electricity_price_eur_per_mwh = representative_value(
        ELECTRICITY_PRICE_DISTRIBUTION
    )

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
    annual_emissions_cost_eur = (
        annual_output_t * emissions_tco2_per_t * CARBON_PRICE_EUR_PER_T.value
    )
    annual_net_cash_flow_eur = (
        annual_revenue_eur
        - annual_fixed_opex_eur
        - annual_variable_opex_eur
        - annual_fuel_cost_eur
        - annual_electricity_cost_eur
        - annual_emissions_cost_eur
    )
    npv_eur = float(
        calculate_npv(
            initial_capex_eur=np.array([initial_capex_eur]),
            annual_net_cash_flow_eur=np.array([annual_net_cash_flow_eur]),
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
        )[0]
    )
    lifetime_output_t = annual_output_t * lifetime_years
    npv_eur_per_t = npv_eur / lifetime_output_t

    result = {
        "run_id": [0],
        "technology": [technology],
        "technology_type": [
            "retrofit"
            if technology in CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
            else "absolute"
        ],
        "annual_output_t": [annual_output_t],
        "lifetime_years": [lifetime_years],
        "capex_eur_per_t": [capex_eur_per_t],
        "fixed_opex_eur_per_t": [fixed_opex_eur_per_t],
        "variable_opex_eur_per_t": [variable_opex_eur_per_t],
        "fuel_consumption_mwh_th_per_t": [fuel_consumption_mwh_th_per_t],
        "electricity_consumption_mwh_per_t": [electricity_consumption_mwh_per_t],
        "emissions_tco2_per_t": [emissions_tco2_per_t],
        "fuel_price_eur_per_mwh_th": [fuel_price_eur_per_mwh_th],
        "electricity_price_eur_per_mwh": [electricity_price_eur_per_mwh],
        "cement_price_eur_per_t": [RETAIL_PRICE_CEMENT_EUR_PER_T.value],
        "carbon_price_eur_per_t": [CARBON_PRICE_EUR_PER_T.value],
        "initial_capex_eur": [initial_capex_eur],
        "annual_revenue_eur": [annual_revenue_eur],
        "annual_fixed_opex_eur": [annual_fixed_opex_eur],
        "annual_variable_opex_eur": [annual_variable_opex_eur],
        "annual_fuel_cost_eur": [annual_fuel_cost_eur],
        "annual_electricity_cost_eur": [annual_electricity_cost_eur],
        "annual_emissions_cost_eur": [annual_emissions_cost_eur],
        "annual_net_cash_flow_eur": [annual_net_cash_flow_eur],
        "npv_eur": [npv_eur],
        "lifetime_output_t": [lifetime_output_t],
        "npv_eur_per_t": [npv_eur_per_t],
        "npv_million_eur_per_t": [npv_eur_per_t / 1_000_000],
    }

    for retrofit_key in (
        "capex_change_eur_per_t",
        "fixed_opex_change_eur_per_t",
        "variable_opex_change_eur_per_t",
        "fuel_consumption_reduction_fraction",
        "electricity_consumption_reduction_fraction",
        "emissions_reduction_fraction",
    ):
        if retrofit_key in values:
            result[retrofit_key] = [values[retrofit_key]]

    return result


def calculate_deterministic_cement_npv_eur(technology: str) -> float:
    """Calculate deterministic cement NPV from representative values."""

    return float(calculate_deterministic_cement_result(technology)["npv_eur"][0])


def calculate_deterministic_cement_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate deterministic cement results for all selected technologies."""

    selected_technologies = technologies or tuple(
        list(CEMENT_TECHNOLOGY_DISTRIBUTIONS)
        + list(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    return {
        technology: calculate_deterministic_cement_result(technology)
        for technology in selected_technologies
    }
