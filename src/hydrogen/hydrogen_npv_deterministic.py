"""Deterministic hydrogen NPV calculations and shared cash-flow formulas.

CAPEX intensities are EUR per tonne of annual H2 capacity. The fixed and
variable OPEX inputs supplied for this thesis are both EUR per tonne produced.
Fuel and electricity are priced separately. Only supplied direct emissions
enter carbon costs; upstream energy emissions and carbon by-product credits
are outside the supplied parameter boundary.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from hydrogen.hydrogen_parameters import (
    HYDROGEN_RETROFIT_BASE_TECHNOLOGIES,
    HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    HYDROGEN_TECHNOLOGY_DISTRIBUTIONS,
    ANNUAL_HYDROGEN_OUTPUT_TH2,
    LIFETIME_HYDROGEN_YEARS,
    RETAIL_PRICE_HYDROGEN_EUR_PER_T,
)
from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
    sample_scaled_beta,
    sample_triangular,
    sample_uniform,
)
from general_parameters import (
    BIOMASS_PRICE_DISTRIBUTION,
    BIOGAS_PRICE_EUR_PER_MWH_TH,
    CARBON_PRICE_EUR_PER_T,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    ELECTRICITY_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    INTEREST_RATE,
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


ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)
HYDROGEN_TECHNOLOGIES = tuple(HYDROGEN_TECHNOLOGY_DISTRIBUTIONS) + tuple(
    HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
)
ENERGY_CARRIERS = ("natural_gas", "biomethane", "biomass")
# Reuse the shared biomass-energy price, as in the ammonia sector. The user
# approved the existing biogas price as a provisional biomethane price proxy.
MARKET_PARAMETERS: Mapping[str, ParameterSpec] = {
    "gas_price_eur_per_mwh_th": GAS_PRICE_DISTRIBUTION,
    "biomethane_price_eur_per_mwh_th": BIOGAS_PRICE_EUR_PER_MWH_TH,
    "biomass_price_eur_per_mwh_th": BIOMASS_PRICE_DISTRIBUTION,
    "electricity_price_eur_per_mwh": ELECTRICITY_PRICE_DISTRIBUTION,
}
PRICE_KEY_BY_CARRIER = {
    "natural_gas": "gas_price_eur_per_mwh_th",
    "biomethane": "biomethane_price_eur_per_mwh_th",
    "biomass": "biomass_price_eur_per_mwh_th",
}
FUEL_TYPE_BY_TECHNOLOGY = {
    "ng_smr": "natural_gas",
    "ael": "none",
    "pem": "none",
    "soec": "none",
    "methane_pyrolysis_tcd": "natural_gas",
    "biomass_gasification": "biomass",
    "biomethane_smr": "biomethane",
    "ng_smr_ccs": "natural_gas",
}


def parameter_values(
    parameters: Mapping[str, ParameterSpec],
    size: int,
    rng: np.random.Generator | None,
) -> dict[str, np.ndarray]:
    """Return expected-value arrays, or sample the supplied distributions."""

    values: dict[str, np.ndarray] = {}
    for name, parameter in parameters.items():
        if rng is None or isinstance(parameter, FixedParameter):
            value = representative_value(parameter)
            values[name] = np.full(size, value, dtype=float)
        elif isinstance(parameter, ScaledBetaDistribution):
            values[name] = sample_scaled_beta(parameter, size=size, rng=rng)
        elif isinstance(parameter, TriangularDistribution):
            values[name] = sample_triangular(parameter, size=size, rng=rng)
        elif isinstance(parameter, UniformDistribution):
            values[name] = sample_uniform(parameter, size=size, rng=rng)
        else:
            raise TypeError(f"Unsupported parameter type: {type(parameter)!r}.")
    return values


def market_values(
    size: int,
    rng: np.random.Generator | None,
    biomethane_price: ParameterSpec = BIOGAS_PRICE_EUR_PER_MWH_TH,
) -> dict[str, np.ndarray]:
    """Draw each market price once so compared routes share the same prices."""

    parameters = dict(MARKET_PARAMETERS)
    parameters["biomethane_price_eur_per_mwh_th"] = biomethane_price
    return parameter_values(parameters, size=size, rng=rng)


def absolute_values(
    technology: str, size: int, rng: np.random.Generator | None
) -> dict[str, np.ndarray]:
    """Resolve an absolute hydrogen technology from its input catalogue."""

    if technology not in HYDROGEN_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute hydrogen technology: {technology!r}.")
    return parameter_values(
        HYDROGEN_TECHNOLOGY_DISTRIBUTIONS[technology], size=size, rng=rng
    )


def resolve_retrofit_values(
    technology: str,
    parent: Mapping[str, np.ndarray],
    increments: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve additive retrofit inputs, a fuel switch, and CCS capture."""

    if technology not in HYDROGEN_RETROFIT_BASE_TECHNOLOGIES:
        raise ValueError(f"Unknown hydrogen retrofit technology: {technology!r}.")
    values = dict(parent)
    for name in ("capex", "fixed_opex", "variable_opex"):
        key = f"{name}_eur_per_th2"
        values[key] = parent[key] + increments[f"{name}_change_eur_per_th2"]
    for carrier in (*ENERGY_CARRIERS, "electricity"):
        key = f"{carrier}_consumption_mwh_per_th2"
        change_key = f"{carrier}_consumption_change_mwh_per_th2"
        if change_key in increments:
            baseline = parent.get(key, np.zeros_like(parent["capex_eur_per_th2"]))
            values[key] = baseline + increments[change_key]
    if "biomethane_consumption_mwh_per_th2" in increments:
        values["biomethane_consumption_mwh_per_th2"] = increments[
            "biomethane_consumption_mwh_per_th2"
        ]
    if "capture_fraction" in increments:
        values["emissions_tco2_per_th2"] = parent["emissions_tco2_per_th2"] * (
            1.0 - increments["capture_fraction"]
        )
    elif "emissions_tco2_per_th2" in increments:
        values["emissions_tco2_per_th2"] = increments["emissions_tco2_per_th2"]
    else:
        raise ValueError(f"Retrofit {technology!r} has no emissions rule.")
    return values


def calculate_result(
    technology: str,
    values: Mapping[str, np.ndarray],
    prices: Mapping[str, np.ndarray],
    *,
    retrofit_bau_mode: str = "not_applicable",
    parent_values: Mapping[str, np.ndarray] | None = None,
    increments: Mapping[str, np.ndarray] | None = None,
) -> dict[str, np.ndarray]:
    """Calculate annual cash flows, NPV, LCOH, and levelized net margin."""

    size = len(values["capex_eur_per_th2"])
    output = ANNUAL_HYDROGEN_OUTPUT_TH2.value
    lifetime = int(LIFETIME_HYDROGEN_YEARS.value)
    zeros = np.zeros(size)
    consumption = {
        carrier: values.get(f"{carrier}_consumption_mwh_per_th2", zeros)
        for carrier in ENERGY_CARRIERS
    }
    electricity = values["electricity_consumption_mwh_per_th2"]
    emissions = values["emissions_tco2_per_th2"]
    def carrier_costs(inputs: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
        costs: dict[str, np.ndarray] = {}
        for carrier in ENERGY_CARRIERS:
            amount = inputs.get(f"{carrier}_consumption_mwh_per_th2", zeros)
            price_key = PRICE_KEY_BY_CARRIER[carrier]
            if np.any(amount != 0) and price_key not in prices:
                raise ValueError(
                    f"{price_key} is required to calculate {technology!r}."
                )
            costs[carrier] = output * amount * prices[price_key] if price_key in prices else zeros
        return costs

    energy_costs = carrier_costs(values)
    annual_fuel = sum(energy_costs.values())
    annual_electricity = output * electricity * prices["electricity_price_eur_per_mwh"]
    capex = output * values["capex_eur_per_th2"]
    annual_revenue = np.full(size, output * RETAIL_PRICE_HYDROGEN_EUR_PER_T.value)
    annual_fixed_opex = output * values["fixed_opex_eur_per_th2"]
    annual_variable_opex = output * values["variable_opex_eur_per_th2"]
    annual_cost_before_carbon_and_storage = (
        annual_fixed_opex + annual_variable_opex + annual_fuel + annual_electricity
    )

    capture_cost = np.full(size, np.nan)
    storage_cost_per_th2 = np.zeros(size)
    storage_share = np.full(size, np.nan)
    if technology == "ng_smr_ccs":
        if parent_values is None:
            raise ValueError("ng_smr_ccs requires its NG-SMR parent values.")
        parent_carrier_cost = sum(carrier_costs(parent_values).values())
        parent_annual_cost = output * (
            parent_values["fixed_opex_eur_per_th2"]
            + parent_values["variable_opex_eur_per_th2"]
            + parent_values["electricity_consumption_mwh_per_th2"]
            * prices["electricity_price_eur_per_mwh"]
        ) + parent_carrier_cost
        share = CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
        capture_cost, storage_cost_per_th2 = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=capex,
            bau_initial_capex_eur=output * parent_values["capex_eur_per_th2"],
            ccs_annual_cost_excluding_carbon_eur=annual_cost_before_carbon_and_storage,
            bau_annual_cost_excluding_carbon_eur=parent_annual_cost,
            annual_output=output,
            lifetime_years=lifetime,
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=share,
        )
        storage_share = np.full(size, share)

    annual_storage = output * storage_cost_per_th2
    annual_emissions_cost = output * emissions * CARBON_PRICE_EUR_PER_T.value
    annual_total_cost = (
        annual_cost_before_carbon_and_storage + annual_storage + annual_emissions_cost
    )
    annual_net_cash_flow = annual_revenue - annual_total_cost
    npv = calculate_npv(
        initial_capex_eur=capex,
        annual_net_cash_flow_eur=annual_net_cash_flow,
        lifetime_years=lifetime,
        discount_rate=INTEREST_RATE.value,
    )
    discounted_output = calculate_discounted_lifetime_output(
        annual_output=output, lifetime_years=lifetime, discount_rate=INTEREST_RATE.value
    )
    present_value_total_cost = calculate_total_cost_present_value(
        initial_capex_eur=capex,
        annual_cost_eur=annual_total_cost,
        lifetime_years=lifetime,
        discount_rate=INTEREST_RATE.value,
    )
    result: dict[str, np.ndarray] = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, "retrofit" if parent_values is not None else "absolute"),
        "retrofit_bau_mode": np.full(size, retrofit_bau_mode),
        "annual_output_th2": np.full(size, output),
        "lifetime_years": np.full(size, lifetime),
        "capex_eur_per_th2": values["capex_eur_per_th2"],
        "fixed_opex_eur_per_th2": values["fixed_opex_eur_per_th2"],
        "variable_opex_eur_per_th2": values["variable_opex_eur_per_th2"],
        "fuel_type": np.full(size, FUEL_TYPE_BY_TECHNOLOGY[technology]),
        **{
            f"{carrier}_consumption_mwh_per_th2": consumption[carrier]
            for carrier in ENERGY_CARRIERS
        },
        "electricity_consumption_mwh_per_th2": electricity,
        "emissions_tco2_per_th2": emissions,
        **dict(prices),
        "biomethane_price_eur_per_mwh_th": prices.get(
            "biomethane_price_eur_per_mwh_th", np.full(size, np.nan)
        ),
        "hydrogen_price_eur_per_th2": np.full(size, RETAIL_PRICE_HYDROGEN_EUR_PER_T.value),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "transport_and_storage_share_of_capture_cost": storage_share,
        "transport_and_storage_cost_eur_per_th2": storage_cost_per_th2,
        "capture_cost_excluding_transport_and_storage_eur_per_th2": capture_cost,
        "initial_capex_eur": capex,
        "annual_revenue_eur": annual_revenue,
        "annual_fixed_opex_eur": annual_fixed_opex,
        "annual_variable_opex_eur": annual_variable_opex,
        "annual_natural_gas_cost_eur": energy_costs["natural_gas"],
        "annual_biomethane_cost_eur": energy_costs["biomethane"],
        "annual_biomass_cost_eur": energy_costs["biomass"],
        "annual_fuel_cost_eur": annual_fuel,
        "annual_electricity_cost_eur": annual_electricity,
        "annual_transport_and_storage_cost_eur": annual_storage,
        "annual_emissions_cost_eur": annual_emissions_cost,
        "annual_total_cost_eur": annual_total_cost,
        "annual_net_cash_flow_eur": annual_net_cash_flow,
        "npv_eur": npv,
        "discounted_lifetime_output_th2": np.full(size, discounted_output),
        "present_value_total_cost_eur": present_value_total_cost,
        "lcoh_eur_per_th2": calculate_levelized_cost(
            initial_capex_eur=capex,
            annual_cost_eur=annual_total_cost,
            annual_output=output,
            lifetime_years=lifetime,
            discount_rate=INTEREST_RATE.value,
        ),
        "levelized_net_margin_eur_per_th2": calculate_levelized_net_margin(
            npv_eur=npv,
            annual_output=output,
            lifetime_years=lifetime,
            discount_rate=INTEREST_RATE.value,
        ),
    }
    if parent_values is not None:
        result.update({f"bau_{key}": value for key, value in parent_values.items()})
    if increments is not None:
        result.update(increments)
    return result


def calculate_deterministic_hydrogen_result(technology: str) -> Mapping[str, object]:
    """Calculate a one-row result using every uncertain parameter's mean."""

    if technology not in HYDROGEN_TECHNOLOGIES:
        raise ValueError(f"Unknown hydrogen technology: {technology!r}.")
    prices = market_values(size=1, rng=None)
    if technology in HYDROGEN_RETROFIT_BASE_TECHNOLOGIES:
        parent_name = HYDROGEN_RETROFIT_BASE_TECHNOLOGIES[technology]
        parent = absolute_values(parent_name, size=1, rng=None)
        increments = parameter_values(
            HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[technology],
            size=1,
            rng=None,
        )
        values = resolve_retrofit_values(technology, parent, increments)
        result = calculate_result(
            technology,
            values,
            prices,
            retrofit_bau_mode="deterministic",
            parent_values=parent,
            increments=increments,
        )
    else:
        values = absolute_values(technology, size=1, rng=None)
        result = calculate_result(technology, values, prices)
    return {key: value.tolist() for key, value in result.items()}


def calculate_deterministic_hydrogen_npv_eur(technology: str) -> float:
    """Return the expected-input NPV for one hydrogen technology."""

    return float(calculate_deterministic_hydrogen_result(technology)["npv_eur"][0])


def calculate_deterministic_hydrogen_results(
    technologies: tuple[str, ...] | None = None,
) -> Mapping[str, Mapping[str, object]]:
    """Calculate expected-input results for selected or all hydrogen routes."""

    selected = HYDROGEN_TECHNOLOGIES if technologies is None else technologies
    return {
        technology: calculate_deterministic_hydrogen_result(technology)
        for technology in selected
    }
