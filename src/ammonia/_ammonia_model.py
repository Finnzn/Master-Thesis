"""Shared ammonia input resolution and cash-flow calculations.

CAPEX intensities are EUR per tonne of annual NH3 capacity. The fixed and
variable OPEX inputs supplied for this thesis are both EUR per tonne produced.
Only direct stack emissions enter carbon costs; upstream energy emissions and
any carbon by-product credit are outside the supplied parameter boundary.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from ammonia.ammonia_parameters import (
    AMMONIA_RETROFIT_BASE_TECHNOLOGIES,
    AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    AMMONIA_TECHNOLOGY_DISTRIBUTIONS,
    ANNUAL_AMMONIA_OUTPUT_TNH3,
    LIFETIME_AMMONIA_YEARS,
    RETAIL_PRICE_AMMONIA_EUR_PER_T,
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
    CARBON_PRICE_EUR_PER_T,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    COAL_PRICE_DISTRIBUTION,
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
AMMONIA_TECHNOLOGIES = tuple(AMMONIA_TECHNOLOGY_DISTRIBUTIONS) + tuple(
    AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
)
ENERGY_CARRIERS = ("natural_gas", "coal", "biomass")
# No ammonia-specific biomass price was supplied. This reuses the shared
# biomass-energy price already used by the electricity sector as a working proxy.
MARKET_PARAMETERS: Mapping[str, ParameterSpec] = {
    "gas_price_eur_per_mwh_th": GAS_PRICE_DISTRIBUTION,
    "coal_price_eur_per_mwh_th": COAL_PRICE_DISTRIBUTION,
    "biomass_price_eur_per_mwh_th": BIOMASS_PRICE_DISTRIBUTION,
    "electricity_price_eur_per_mwh": ELECTRICITY_PRICE_DISTRIBUTION,
}
FUEL_TYPE_BY_TECHNOLOGY = {
    "ng_smr_hb": "natural_gas",
    "ng_smr_hb_ccs": "natural_gas",
    "coal_gasification_hb": "coal",
    "coal_gasification_hb_ccs": "coal",
    "biomass_gasification_hb": "biomass",
    "methane_pyrolysis_hb": "natural_gas",
    "ael_pem_electrolysis_hb": "none",
    "soec_hb": "none",
    "aqueous_direct_nrr": "none",
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


def market_values(size: int, rng: np.random.Generator | None) -> dict[str, np.ndarray]:
    """Draw each market price once so compared routes share the same prices."""

    return parameter_values(MARKET_PARAMETERS, size=size, rng=rng)


def absolute_values(
    technology: str, size: int, rng: np.random.Generator | None
) -> dict[str, np.ndarray]:
    """Resolve an absolute ammonia technology from its input catalogue."""

    if technology not in AMMONIA_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute ammonia technology: {technology!r}.")
    return parameter_values(
        AMMONIA_TECHNOLOGY_DISTRIBUTIONS[technology], size=size, rng=rng
    )


def resolve_retrofit_values(
    technology: str,
    parent: Mapping[str, np.ndarray],
    increments: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Add CCS increments to its parent and apply the direct-emissions reduction."""

    if technology not in AMMONIA_RETROFIT_BASE_TECHNOLOGIES:
        raise ValueError(f"Unknown ammonia retrofit technology: {technology!r}.")
    values = dict(parent)
    for name in ("capex", "fixed_opex", "variable_opex"):
        key = f"{name}_eur_per_tnh3"
        values[key] = parent[key] + increments[f"{name}_change_eur_per_tnh3"]
    for carrier in (*ENERGY_CARRIERS, "electricity"):
        key = f"{carrier}_consumption_mwh_per_tnh3"
        change_key = f"{carrier}_consumption_change_mwh_per_tnh3"
        if change_key in increments:
            baseline = parent.get(key, np.zeros_like(parent["capex_eur_per_tnh3"]))
            values[key] = baseline + increments[change_key]
    values["emissions_tco2_per_tnh3"] = parent["emissions_tco2_per_tnh3"] * (
        1.0 - increments["emissions_reduction_fraction"]
    )
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
    """Calculate annual cash flows, NPV, LCOA, and levelized net margin."""

    size = len(values["capex_eur_per_tnh3"])
    output = ANNUAL_AMMONIA_OUTPUT_TNH3.value
    lifetime = int(LIFETIME_AMMONIA_YEARS.value)
    zeros = np.zeros(size)
    consumption = {
        carrier: values.get(f"{carrier}_consumption_mwh_per_tnh3", zeros)
        for carrier in ENERGY_CARRIERS
    }
    electricity = values["electricity_consumption_mwh_per_tnh3"]
    emissions = values["emissions_tco2_per_tnh3"]
    energy_costs = {
        "natural_gas": output * consumption["natural_gas"] * prices["gas_price_eur_per_mwh_th"],
        "coal": output * consumption["coal"] * prices["coal_price_eur_per_mwh_th"],
        "biomass": output * consumption["biomass"] * prices["biomass_price_eur_per_mwh_th"],
    }
    annual_fuel = sum(energy_costs.values())
    annual_electricity = output * electricity * prices["electricity_price_eur_per_mwh"]
    capex = output * values["capex_eur_per_tnh3"]
    annual_revenue = np.full(size, output * RETAIL_PRICE_AMMONIA_EUR_PER_T.value)
    annual_fixed_opex = output * values["fixed_opex_eur_per_tnh3"]
    annual_variable_opex = output * values["variable_opex_eur_per_tnh3"]
    annual_cost_before_carbon_and_storage = (
        annual_fixed_opex + annual_variable_opex + annual_fuel + annual_electricity
    )

    capture_cost = np.full(size, np.nan)
    storage_cost_per_tnh3 = np.zeros(size)
    storage_share = np.full(size, np.nan)
    if parent_values is not None:
        parent_carrier_cost = sum(
            output
            * parent_values.get(f"{carrier}_consumption_mwh_per_tnh3", zeros)
            * prices[f"{('gas' if carrier == 'natural_gas' else carrier)}_price_eur_per_mwh_th"]
            for carrier in ENERGY_CARRIERS
        )
        parent_annual_cost = output * (
            parent_values["fixed_opex_eur_per_tnh3"]
            + parent_values["variable_opex_eur_per_tnh3"]
            + parent_values["electricity_consumption_mwh_per_tnh3"]
            * prices["electricity_price_eur_per_mwh"]
        ) + parent_carrier_cost
        share = CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
        capture_cost, storage_cost_per_tnh3 = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=capex,
            bau_initial_capex_eur=output * parent_values["capex_eur_per_tnh3"],
            ccs_annual_cost_excluding_carbon_eur=annual_cost_before_carbon_and_storage,
            bau_annual_cost_excluding_carbon_eur=parent_annual_cost,
            annual_output=output,
            lifetime_years=lifetime,
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=share,
        )
        storage_share = np.full(size, share)

    annual_storage = output * storage_cost_per_tnh3
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
        "annual_output_tnh3": np.full(size, output),
        "lifetime_years": np.full(size, lifetime),
        "capex_eur_per_tnh3": values["capex_eur_per_tnh3"],
        "fixed_opex_eur_per_tnh3": values["fixed_opex_eur_per_tnh3"],
        "variable_opex_eur_per_tnh3": values["variable_opex_eur_per_tnh3"],
        "fuel_type": np.full(size, FUEL_TYPE_BY_TECHNOLOGY[technology]),
        **{
            f"{carrier}_consumption_mwh_per_tnh3": consumption[carrier]
            for carrier in ENERGY_CARRIERS
        },
        "electricity_consumption_mwh_per_tnh3": electricity,
        "emissions_tco2_per_tnh3": emissions,
        **dict(prices),
        "ammonia_price_eur_per_tnh3": np.full(size, RETAIL_PRICE_AMMONIA_EUR_PER_T.value),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "transport_and_storage_share_of_capture_cost": storage_share,
        "transport_and_storage_cost_eur_per_tnh3": storage_cost_per_tnh3,
        "capture_cost_excluding_transport_and_storage_eur_per_tnh3": capture_cost,
        "initial_capex_eur": capex,
        "annual_revenue_eur": annual_revenue,
        "annual_fixed_opex_eur": annual_fixed_opex,
        "annual_variable_opex_eur": annual_variable_opex,
        "annual_natural_gas_cost_eur": energy_costs["natural_gas"],
        "annual_coal_cost_eur": energy_costs["coal"],
        "annual_biomass_cost_eur": energy_costs["biomass"],
        "annual_fuel_cost_eur": annual_fuel,
        "annual_electricity_cost_eur": annual_electricity,
        "annual_transport_and_storage_cost_eur": annual_storage,
        "annual_emissions_cost_eur": annual_emissions_cost,
        "annual_total_cost_eur": annual_total_cost,
        "annual_net_cash_flow_eur": annual_net_cash_flow,
        "npv_eur": npv,
        "discounted_lifetime_output_tnh3": np.full(size, discounted_output),
        "present_value_total_cost_eur": present_value_total_cost,
        "lcoa_eur_per_tnh3": calculate_levelized_cost(
            initial_capex_eur=capex,
            annual_cost_eur=annual_total_cost,
            annual_output=output,
            lifetime_years=lifetime,
            discount_rate=INTEREST_RATE.value,
        ),
        "levelized_net_margin_eur_per_tnh3": calculate_levelized_net_margin(
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
