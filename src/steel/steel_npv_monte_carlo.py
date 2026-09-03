"""Monte Carlo NPV calculations for steel technologies.

The steel simulation samples technology and market assumptions, resolves CCS
retrofits against either sampled or deterministic parent-technology values,
and calculates traceable annual cash-flow and financial outputs for each run.
Shared market arrays and sampled BAU arrays are reused across technologies with
the same run IDs so technology rankings compare aligned uncertain worlds.
"""

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
from general_parameters import (
    CARBON_PRICE_EUR_PER_T,
    CHARCOAL_PRICE_EUR_PER_MWH_TH,
    CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST,
    ELECTRICITY_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    GREEN_HYDROGEN_PRICE_EUR_PER_KG,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
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
from steel.steel_npv_deterministic import STEEL_FUEL_TYPES
from steel.steel_parameters import (
    ANNUAL_STEEL_OUTPUT_TCS,
    LIFETIME_STEEL_YEARS,
    RETAIL_PRICE_STEEL_EUR_PER_TCS,
    STEEL_RETROFIT_BASE_TECHNOLOGIES,
    STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    STEEL_TECHNOLOGY_DISTRIBUTIONS,
)


DEFAULT_SAMPLE_SIZE = 100_000
DEFAULT_RANDOM_SEED = 42
DEFAULT_RETROFIT_BAU_MODE = "sampled"
RETROFIT_BAU_MODES = ("sampled", "deterministic")

ParameterSpec = (
    FixedParameter
    | ScaledBetaDistribution
    | TriangularDistribution
    | UniformDistribution
)


def _validate_size(size: int) -> None:
    """Validate a positive Monte Carlo sample size."""

    if size <= 0:
        raise ValueError("size must be positive.")


def _validate_retrofit_bau_mode(retrofit_bau_mode: str) -> None:
    """Validate the BAU baseline mode used for retrofit technologies."""

    if retrofit_bau_mode not in RETROFIT_BAU_MODES:
        allowed = ", ".join(repr(mode) for mode in RETROFIT_BAU_MODES)
        raise ValueError(
            f"retrofit_bau_mode must be one of {allowed}; "
            f"got {retrofit_bau_mode!r}."
        )


def _sample_distribution(
    distribution: (
        ScaledBetaDistribution | TriangularDistribution | UniformDistribution
    ),
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Dispatch one supported stochastic parameter to its sampler."""

    if isinstance(distribution, ScaledBetaDistribution):
        return sample_scaled_beta(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, TriangularDistribution):
        return sample_triangular(distribution=distribution, size=size, rng=rng)
    if isinstance(distribution, UniformDistribution):
        return sample_uniform(distribution=distribution, size=size, rng=rng)
    raise TypeError(f"Unsupported distribution type: {type(distribution)!r}")


def _sample_parameter(
    parameter: ParameterSpec,
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample a stochastic parameter or broadcast a fixed value."""

    if isinstance(parameter, FixedParameter):
        return np.full(size, parameter.value)
    return _sample_distribution(distribution=parameter, size=size, rng=rng)


def _representative_parameter_array(
    parameter: ParameterSpec,
    size: int,
) -> np.ndarray:
    """Broadcast one deterministic representative value to a sample array."""

    return np.full(size, representative_value(parameter))


def _sample_absolute_technology_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample absolute steel inputs from the technology registry."""

    if technology not in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown absolute steel technology: {technology!r}.")
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in STEEL_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _deterministic_bau_values(
    technology: str,
    size: int,
) -> dict[str, np.ndarray]:
    """Return representative parent-technology inputs as sample arrays."""

    if technology not in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown steel BAU technology: {technology!r}.")
    return {
        parameter_name: _representative_parameter_array(parameter, size=size)
        for parameter_name, parameter in STEEL_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _sample_retrofit_values(
    technology: str,
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample incremental changes for one steel retrofit technology."""

    if technology not in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown steel retrofit technology: {technology!r}.")
    return {
        parameter_name: _sample_parameter(parameter, size=size, rng=rng)
        for parameter_name, parameter in STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS[
            technology
        ].items()
    }


def _resolve_retrofit_values(
    bau_values: Mapping[str, np.ndarray],
    retrofit_values: Mapping[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Resolve absolute steel inputs from BAU arrays and retrofit changes."""

    return {
        "capex_eur_per_tcs": (
            bau_values["capex_eur_per_tcs"]
            + retrofit_values["capex_change_eur_per_tcs"]
        ),
        "fixed_opex_eur_per_tcs": (
            bau_values["fixed_opex_eur_per_tcs"]
            + retrofit_values["fixed_opex_change_eur_per_tcs"]
        ),
        "variable_opex_eur_per_tcs": (
            bau_values["variable_opex_eur_per_tcs"]
            + retrofit_values["variable_opex_change_eur_per_tcs"]
        ),
        "fuel_consumption_mwh_th_per_tcs": (
            bau_values["fuel_consumption_mwh_th_per_tcs"]
            * (1.0 - retrofit_values["fuel_consumption_reduction_fraction"])
        ),
        "electricity_consumption_mwh_per_tcs": (
            bau_values["electricity_consumption_mwh_per_tcs"]
            * (
                1.0
                - retrofit_values["electricity_consumption_reduction_fraction"]
            )
        ),
        "emissions_tco2_per_tcs": (
            bau_values["emissions_tco2_per_tcs"]
            * (1.0 - retrofit_values["emissions_reduction_fraction"])
        ),
    }


def _sample_market_values(
    size: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Sample or broadcast market assumptions shared across steel technologies."""

    return {
        "pci_coking_coal_mix_price_eur_per_mwh_th": _sample_parameter(
            PCI_COKING_COAL_MIX_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "charcoal_price_eur_per_mwh_th": _sample_parameter(
            CHARCOAL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "gas_price_eur_per_mwh_th": _sample_parameter(
            GAS_PRICE_DISTRIBUTION,
            size=size,
            rng=rng,
        ),
        "green_hydrogen_price_eur_per_kg": _sample_parameter(
            GREEN_HYDROGEN_PRICE_EUR_PER_KG,
            size=size,
            rng=rng,
        ),
        "no_fuel_price_eur_per_mwh_th": _sample_parameter(
            NO_FUEL_PRICE_EUR_PER_MWH_TH,
            size=size,
            rng=rng,
        ),
        "electricity_price_eur_per_mwh": _sample_parameter(
            ELECTRICITY_PRICE_DISTRIBUTION,
            size=size,
            rng=rng,
        ),
    }


def _energy_costs_per_tcs(
    technology: str,
    values: Mapping[str, np.ndarray],
    market_values: Mapping[str, np.ndarray],
    size: int,
) -> dict[str, np.ndarray]:
    """Calculate fuel-carrier cost arrays per tonne of crude steel."""

    pci_cost = np.zeros(size)
    charcoal_cost = np.zeros(size)
    natural_gas_cost = np.zeros(size)
    hydrogen_cost = np.zeros(size)

    if technology in {"bf_bof_bau", "bf_bof_post_combustion_ccs"}:
        pci_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["pci_coking_coal_mix_price_eur_per_mwh_th"]
        )
    elif technology in {"scrap_eaf", "ael_eaf"}:
        charcoal_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["charcoal_price_eur_per_mwh_th"]
        )
    elif technology in {"ng_dri_eaf_bau", "ng_dri_eaf_ccs"}:
        natural_gas_cost = (
            values["fuel_consumption_mwh_th_per_tcs"]
            * market_values["gas_price_eur_per_mwh_th"]
        )
    elif technology == "h2_dri_eaf":
        hydrogen_cost = (
            values["hydrogen_consumption_kg_per_tcs"]
            * market_values["green_hydrogen_price_eur_per_kg"]
        )
        charcoal_cost = (
            values["charcoal_consumption_mwh_th_per_tcs"]
            * market_values["charcoal_price_eur_per_mwh_th"]
        )
    elif technology != "moe":
        raise ValueError(f"No energy-cost calculation configured for {technology!r}.")

    return {
        "pci_coking_coal_cost_eur_per_tcs": pci_cost,
        "charcoal_cost_eur_per_tcs": charcoal_cost,
        "natural_gas_cost_eur_per_tcs": natural_gas_cost,
        "hydrogen_cost_eur_per_tcs": hydrogen_cost,
        "fuel_cost_eur_per_tcs": (
            pci_cost + charcoal_cost + natural_gas_cost + hydrogen_cost
        ),
    }


def _technology_fuel_price_eur_per_mwh_th(
    technology: str,
    market_values: Mapping[str, np.ndarray],
    size: int,
) -> np.ndarray:
    """Return one energy-price array, or NaN for dual-fuel H2-DRI-EAF."""

    price_key_by_technology = {
        "bf_bof_bau": "pci_coking_coal_mix_price_eur_per_mwh_th",
        "bf_bof_post_combustion_ccs": (
            "pci_coking_coal_mix_price_eur_per_mwh_th"
        ),
        "scrap_eaf": "charcoal_price_eur_per_mwh_th",
        "ng_dri_eaf_bau": "gas_price_eur_per_mwh_th",
        "ng_dri_eaf_ccs": "gas_price_eur_per_mwh_th",
        "moe": "no_fuel_price_eur_per_mwh_th",
        "ael_eaf": "charcoal_price_eur_per_mwh_th",
    }
    if technology == "h2_dri_eaf":
        return np.full(size, np.nan)
    if technology not in price_key_by_technology:
        raise ValueError(f"No fuel price configured for {technology!r}.")
    return market_values[price_key_by_technology[technology]]


def _calculate_steel_cash_flow_result(
    technology: str,
    technology_type: str,
    bau_mode: str,
    values: Mapping[str, np.ndarray],
    size: int,
    market_values: Mapping[str, np.ndarray],
    bau_values: Mapping[str, np.ndarray] | None = None,
    retrofit_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Calculate steel cash-flow and financial arrays from absolute inputs."""

    annual_output_tcs = ANNUAL_STEEL_OUTPUT_TCS.value
    lifetime_years = LIFETIME_STEEL_YEARS.value
    capex_eur_per_tcs = values["capex_eur_per_tcs"]
    fixed_opex_eur_per_tcs = values["fixed_opex_eur_per_tcs"]
    variable_opex_eur_per_tcs = values["variable_opex_eur_per_tcs"]
    electricity_consumption_mwh_per_tcs = values[
        "electricity_consumption_mwh_per_tcs"
    ]
    emissions_tco2_per_tcs = values["emissions_tco2_per_tcs"]
    fuel_consumption_mwh_th_per_tcs = values.get(
        "fuel_consumption_mwh_th_per_tcs",
        np.full(size, np.nan),
    )
    hydrogen_consumption_kg_per_tcs = values.get(
        "hydrogen_consumption_kg_per_tcs",
        np.full(size, np.nan),
    )
    charcoal_consumption_mwh_th_per_tcs = values.get(
        "charcoal_consumption_mwh_th_per_tcs",
        np.full(size, np.nan),
    )
    energy_costs_per_tcs = _energy_costs_per_tcs(
        technology=technology,
        values=values,
        market_values=market_values,
        size=size,
    )
    fuel_price_eur_per_mwh_th = _technology_fuel_price_eur_per_mwh_th(
        technology=technology,
        market_values=market_values,
        size=size,
    )

    initial_capex_eur = annual_output_tcs * capex_eur_per_tcs
    annual_revenue_eur = np.full(
        size,
        annual_output_tcs * RETAIL_PRICE_STEEL_EUR_PER_TCS.value,
    )
    annual_fixed_opex_eur = annual_output_tcs * fixed_opex_eur_per_tcs
    annual_variable_opex_eur = annual_output_tcs * variable_opex_eur_per_tcs
    annual_pci_coking_coal_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["pci_coking_coal_cost_eur_per_tcs"]
    )
    annual_charcoal_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["charcoal_cost_eur_per_tcs"]
    )
    annual_natural_gas_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["natural_gas_cost_eur_per_tcs"]
    )
    annual_hydrogen_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["hydrogen_cost_eur_per_tcs"]
    )
    annual_fuel_cost_eur = (
        annual_output_tcs * energy_costs_per_tcs["fuel_cost_eur_per_tcs"]
    )
    annual_electricity_cost_eur = (
        annual_output_tcs
        * electricity_consumption_mwh_per_tcs
        * market_values["electricity_price_eur_per_mwh"]
    )

    capture_cost_excluding_transport_and_storage_eur_per_tcs = np.full(
        size,
        np.nan,
    )
    transport_and_storage_cost_eur_per_tcs = np.zeros(size)
    transport_and_storage_share_of_capture_cost = np.full(size, np.nan)
    if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES:
        if bau_values is None:
            raise ValueError("Steel CCS requires BAU values for its T&S cost basis.")
        transport_and_storage_share_of_capture_cost = np.full(
            size,
            CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value,
        )
        bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        bau_energy_costs_per_tcs = _energy_costs_per_tcs(
            technology=bau_technology,
            values=bau_values,
            market_values=market_values,
            size=size,
        )
        bau_initial_capex_eur = (
            annual_output_tcs * bau_values["capex_eur_per_tcs"]
        )
        bau_annual_cost_excluding_carbon_eur = annual_output_tcs * (
            bau_values["fixed_opex_eur_per_tcs"]
            + bau_values["variable_opex_eur_per_tcs"]
            + bau_energy_costs_per_tcs["fuel_cost_eur_per_tcs"]
            + bau_values["electricity_consumption_mwh_per_tcs"]
            * market_values["electricity_price_eur_per_mwh"]
        )
        annual_cost_excluding_carbon_eur = (
            annual_fixed_opex_eur
            + annual_variable_opex_eur
            + annual_fuel_cost_eur
            + annual_electricity_cost_eur
        )
        (
            capture_cost_excluding_transport_and_storage_eur_per_tcs,
            transport_and_storage_cost_eur_per_tcs,
        ) = calculate_ccs_transport_and_storage_cost_per_output(
            ccs_initial_capex_eur=initial_capex_eur,
            bau_initial_capex_eur=bau_initial_capex_eur,
            ccs_annual_cost_excluding_carbon_eur=annual_cost_excluding_carbon_eur,
            bau_annual_cost_excluding_carbon_eur=(
                bau_annual_cost_excluding_carbon_eur
            ),
            annual_output=annual_output_tcs,
            lifetime_years=int(lifetime_years),
            discount_rate=INTEREST_RATE.value,
            transport_and_storage_share=(
                CCS_TRANSPORT_STORAGE_SHARE_OF_CAPTURE_COST.value
            ),
        )

    annual_transport_and_storage_cost_eur = (
        annual_output_tcs * transport_and_storage_cost_eur_per_tcs
    )
    annual_emissions_cost_eur = (
        annual_output_tcs * emissions_tco2_per_tcs * CARBON_PRICE_EUR_PER_T.value
    )
    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_electricity_cost_eur
        + annual_transport_and_storage_cost_eur
        + annual_emissions_cost_eur
    )
    annual_net_cash_flow_eur = annual_revenue_eur - annual_total_cost_eur
    npv_eur = calculate_npv(
        initial_capex_eur=initial_capex_eur,
        annual_net_cash_flow_eur=annual_net_cash_flow_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    discounted_lifetime_output_tcs = calculate_discounted_lifetime_output(
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    levelized_net_margin_eur_per_tcs = calculate_levelized_net_margin(
        npv_eur=npv_eur,
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    present_value_total_cost_eur = calculate_total_cost_present_value(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )
    lcos_eur_per_tcs = calculate_levelized_cost(
        initial_capex_eur=initial_capex_eur,
        annual_cost_eur=annual_total_cost_eur,
        annual_output=annual_output_tcs,
        lifetime_years=int(lifetime_years),
        discount_rate=INTEREST_RATE.value,
    )

    result = {
        "run_id": np.arange(size),
        "technology": np.full(size, technology),
        "technology_type": np.full(size, technology_type),
        "retrofit_bau_mode": np.full(size, bau_mode),
        "annual_output_tcs": np.full(size, annual_output_tcs),
        "lifetime_years": np.full(size, lifetime_years),
        "capex_eur_per_tcs": capex_eur_per_tcs,
        "fixed_opex_eur_per_tcs": fixed_opex_eur_per_tcs,
        "variable_opex_eur_per_tcs": variable_opex_eur_per_tcs,
        "fuel_type": np.full(size, STEEL_FUEL_TYPES[technology]),
        "fuel_consumption_mwh_th_per_tcs": fuel_consumption_mwh_th_per_tcs,
        "hydrogen_consumption_kg_per_tcs": hydrogen_consumption_kg_per_tcs,
        "charcoal_consumption_mwh_th_per_tcs": (
            charcoal_consumption_mwh_th_per_tcs
        ),
        "electricity_consumption_mwh_per_tcs": (
            electricity_consumption_mwh_per_tcs
        ),
        "emissions_tco2_per_tcs": emissions_tco2_per_tcs,
        "fuel_price_eur_per_mwh_th": fuel_price_eur_per_mwh_th,
        **market_values,
        "steel_price_eur_per_tcs": np.full(
            size,
            RETAIL_PRICE_STEEL_EUR_PER_TCS.value,
        ),
        "carbon_price_eur_per_t": np.full(size, CARBON_PRICE_EUR_PER_T.value),
        "capture_cost_excluding_transport_and_storage_eur_per_tcs": (
            capture_cost_excluding_transport_and_storage_eur_per_tcs
        ),
        "transport_and_storage_cost_eur_per_tcs": (
            transport_and_storage_cost_eur_per_tcs
        ),
        "transport_and_storage_share_of_capture_cost": (
            transport_and_storage_share_of_capture_cost
        ),
        "initial_capex_eur": initial_capex_eur,
        "annual_revenue_eur": annual_revenue_eur,
        "annual_fixed_opex_eur": annual_fixed_opex_eur,
        "annual_variable_opex_eur": annual_variable_opex_eur,
        "annual_pci_coking_coal_cost_eur": annual_pci_coking_coal_cost_eur,
        "annual_charcoal_cost_eur": annual_charcoal_cost_eur,
        "annual_natural_gas_cost_eur": annual_natural_gas_cost_eur,
        "annual_hydrogen_cost_eur": annual_hydrogen_cost_eur,
        "annual_fuel_cost_eur": annual_fuel_cost_eur,
        "annual_electricity_cost_eur": annual_electricity_cost_eur,
        "annual_transport_and_storage_cost_eur": (
            annual_transport_and_storage_cost_eur
        ),
        "annual_emissions_cost_eur": annual_emissions_cost_eur,
        "annual_total_cost_eur": annual_total_cost_eur,
        "annual_net_cash_flow_eur": annual_net_cash_flow_eur,
        "npv_eur": npv_eur,
        "discounted_lifetime_output_tcs": np.full(
            size,
            discounted_lifetime_output_tcs,
        ),
        "present_value_total_cost_eur": present_value_total_cost_eur,
        "lcos_eur_per_tcs": lcos_eur_per_tcs,
        "levelized_net_margin_eur_per_tcs": levelized_net_margin_eur_per_tcs,
    }

    if bau_values is not None:
        for parameter_name, baseline_value in bau_values.items():
            result[f"bau_{parameter_name}"] = baseline_value
    if retrofit_values is not None:
        result.update(retrofit_values)
    return result


def simulate_steel_technology_npv(
    technology: str,
    size: int,
    rng: np.random.Generator | None = None,
    market_values: Mapping[str, np.ndarray] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    bau_values: Mapping[str, np.ndarray] | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for one steel technology."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    all_technologies = (
        set(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        | set(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    if technology not in all_technologies:
        raise ValueError(f"Unknown steel technology: {technology!r}.")

    generator = rng if rng is not None else np.random.default_rng()
    shared_market_values = (
        dict(market_values)
        if market_values is not None
        else _sample_market_values(size=size, rng=generator)
    )

    if technology in STEEL_TECHNOLOGY_DISTRIBUTIONS:
        parent_technologies = set(STEEL_RETROFIT_BASE_TECHNOLOGIES.values())
        values = (
            dict(bau_values)
            if technology in parent_technologies and bau_values is not None
            else _sample_absolute_technology_values(
                technology=technology,
                size=size,
                rng=generator,
            )
        )
        return _calculate_steel_cash_flow_result(
            technology=technology,
            technology_type="absolute",
            bau_mode="not_applicable",
            values=values,
            size=size,
            market_values=shared_market_values,
        )

    bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
    if retrofit_bau_mode == "sampled":
        baseline_values = (
            dict(bau_values)
            if bau_values is not None
            else _sample_absolute_technology_values(
                technology=bau_technology,
                size=size,
                rng=generator,
            )
        )
    else:
        baseline_values = _deterministic_bau_values(
            technology=bau_technology,
            size=size,
        )
    retrofit_values = _sample_retrofit_values(
        technology=technology,
        size=size,
        rng=generator,
    )
    values = _resolve_retrofit_values(
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
    )
    return _calculate_steel_cash_flow_result(
        technology=technology,
        technology_type="retrofit",
        bau_mode=retrofit_bau_mode,
        values=values,
        size=size,
        market_values=shared_market_values,
        bau_values=baseline_values,
        retrofit_values=retrofit_values,
    )


def simulate_bf_bof_bau_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for BF-BOF BAU."""

    return simulate_steel_technology_npv("bf_bof_bau", size=size, rng=rng)


def simulate_scrap_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for Scrap-EAF."""

    return simulate_steel_technology_npv("scrap_eaf", size=size, rng=rng)


def simulate_ng_dri_eaf_bau_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for NG-DRI-EAF BAU."""

    return simulate_steel_technology_npv("ng_dri_eaf_bau", size=size, rng=rng)


def simulate_h2_dri_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for H2-DRI-EAF."""

    return simulate_steel_technology_npv("h2_dri_eaf", size=size, rng=rng)


def simulate_moe_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for molten oxide electrolysis."""

    return simulate_steel_technology_npv("moe", size=size, rng=rng)


def simulate_ael_eaf_npv(
    size: int,
    rng: np.random.Generator | None = None,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for AEL-EAF."""

    return simulate_steel_technology_npv("ael_eaf", size=size, rng=rng)


def simulate_bf_bof_post_combustion_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for BF-BOF post-combustion CCS."""

    return simulate_steel_technology_npv(
        "bf_bof_post_combustion_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_ng_dri_eaf_ccs_npv(
    size: int,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, np.ndarray]:
    """Run a Monte Carlo NPV simulation for NG-DRI-EAF CCS."""

    return simulate_steel_technology_npv(
        "ng_dri_eaf_ccs",
        size=size,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )


def simulate_steel_technologies_npv(
    size: int,
    technologies: tuple[str, ...] | None = None,
    rng: np.random.Generator | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run aligned Monte Carlo simulations for multiple steel technologies."""

    _validate_size(size)
    _validate_retrofit_bau_mode(retrofit_bau_mode)
    selected_technologies = technologies or tuple(
        list(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        + list(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    all_technologies = (
        set(STEEL_TECHNOLOGY_DISTRIBUTIONS)
        | set(STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)
    )
    unknown_technologies = set(selected_technologies) - all_technologies
    if unknown_technologies:
        raise ValueError(
            f"Unknown steel technologies: {sorted(unknown_technologies)!r}."
        )

    generator = rng if rng is not None else np.random.default_rng()
    market_values = _sample_market_values(size=size, rng=generator)
    retrofit_parent_technologies = {
        STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
        for technology in selected_technologies
        if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES
    }
    sampled_bau_values: dict[str, Mapping[str, np.ndarray]] = {}
    results: dict[str, Mapping[str, np.ndarray]] = {}
    for technology in selected_technologies:
        technology_bau_values = None
        if retrofit_bau_mode == "sampled":
            if technology in STEEL_RETROFIT_BASE_TECHNOLOGIES:
                bau_technology = STEEL_RETROFIT_BASE_TECHNOLOGIES[technology]
                if bau_technology not in sampled_bau_values:
                    sampled_bau_values[bau_technology] = (
                        _sample_absolute_technology_values(
                            technology=bau_technology,
                            size=size,
                            rng=generator,
                        )
                    )
                technology_bau_values = sampled_bau_values[bau_technology]
            elif technology in retrofit_parent_technologies:
                if technology not in sampled_bau_values:
                    sampled_bau_values[technology] = (
                        _sample_absolute_technology_values(
                            technology=technology,
                            size=size,
                            rng=generator,
                        )
                    )
                technology_bau_values = sampled_bau_values[technology]

        results[technology] = simulate_steel_technology_npv(
            technology=technology,
            size=size,
            rng=generator,
            market_values=market_values,
            retrofit_bau_mode=retrofit_bau_mode,
            bau_values=technology_bau_values,
        )
    return results


def simulate_steel_results(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> Mapping[str, Mapping[str, np.ndarray]]:
    """Run reproducible steel NPV simulations for selected technologies."""

    rng = np.random.default_rng(random_seed)
    return simulate_steel_technologies_npv(
        size=sample_size,
        technologies=technologies,
        rng=rng,
        retrofit_bau_mode=retrofit_bau_mode,
    )
