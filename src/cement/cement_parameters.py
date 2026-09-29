"""Cement-sector assumptions used by the deterministic and Monte Carlo models.

Technology CAPEX and OPEX are expressed in 2024 EUR after CEPCI normalization
where a monetary basis year is available. The alternative-fuels CAPEX allowance
is the one exception because its thesis-selected range has no monetary basis
year. Emissions parameters represent direct operational CO2 only; upstream and
life-cycle emissions are outside the model boundary.

Absolute technologies define complete plant inputs. Retrofit technologies
define changes relative to BAU. For reduction fractions, positive values reduce
the BAU intensity and negative values increase it.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


# Economic lifetime used when cement-sector annual cash flows are discounted.
LIFETIME_CEMENT_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of cement-sector assets.",
)

# Fixed cement sales price used to calculate annual revenue.
RETAIL_PRICE_CEMENT_EUR_PER_T = FixedParameter(
    value=150.0,
    unit="EUR/t",
    description="Fixed cement sales price used by the financial model.",
)

# Normalized annual output: every cement technology is compared at this annual
# cement production volume.
ANNUAL_CEMENT_OUTPUT_T = FixedParameter(
    value=1_000_000.0,
    unit="t/year",
    description="Annual cement output target used to normalize cement technologies.",
)

# BAU is the reference cement-production route. Its energy use and direct
# operational emissions are absolute intensities.
BAU_CEMENT_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=208.30,
    upper_bound=225.50,
    unit="EUR/(t/year)",
    description="Uniform distribution for BAU cement CAPEX in 2024 EUR, not annualized.",
)

BAU_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=18.05,
    mode=19.90,
    maximum=19.90,
    unit="EUR/t",
    description="Triangular distribution for BAU cement fixed OPEX in 2024 EUR.",
)

BAU_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=6.25,
    mode=7.30,
    maximum=7.30,
    unit="EUR/t",
    description="Triangular distribution for BAU cement variable OPEX in 2024 EUR excluding fuel and electricity.",
)

BAU_CEMENT_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=0.61,
    mode=0.61,
    maximum=0.78,
    unit="MWh_th/t",
    description="Triangular distribution for BAU cement fuel consumption.",
)

BAU_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=0.080,
    mode=0.080,
    maximum=0.100,
    unit="MWh/t",
    description="Triangular distribution for BAU cement electricity consumption.",
)

BAU_CEMENT_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.600,
    mode=0.600,
    maximum=0.700,
    unit="tCO2/t",
    description="Triangular distribution for BAU direct operational CO2 emissions.",
)


# Electrification is a complete alternative route rather than a BAU retrofit.
# Direct fuel use is modelled as zero; electricity use and residual direct
# process emissions are absolute intensities.
ELECTRIFICATION_CEMENT_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=185.71,
    mode=270.60,
    maximum=397.94,
    unit="EUR/(t/year)",
    description="Triangular distribution for electrification cement CAPEX in 2024 EUR, not annualized.",
)

ELECTRIFICATION_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=17.24,
    mode=25.20,
    maximum=37.14,
    unit="EUR/t",
    description="Triangular distribution for electrification cement fixed OPEX in 2024 EUR.",
)

ELECTRIFICATION_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=6.76,
    mode=9.68,
    maximum=14.59,
    unit="EUR/t",
    description="Triangular distribution for electrification cement variable OPEX in 2024 EUR excluding fuel and electricity.",
)

ELECTRIFICATION_CEMENT_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/t",
    description="Assumed zero direct fuel consumption for electrified cement production.",
)

ELECTRIFICATION_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.90,
    upper_bound=1.00,
    unit="MWh/t",
    description="Uniform distribution for electrification cement electricity consumption.",
)

ELECTRIFICATION_CEMENT_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=0.350,
    upper_bound=0.450,
    unit="tCO2/t",
    description="Uniform distribution for electrification direct operational CO2 emissions.",
)


# Electrolysis is a complete alternative route. Direct fuel use is modelled as
# zero; electricity use and residual direct process emissions are absolute
# intensities.
ELECTROLYSIS_CEMENT_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=255.67,
    mode=362.95,
    maximum=546.43,
    unit="EUR/(t/year)",
    description="Triangular distribution for electrolysis cement CAPEX in 2024 EUR, not annualized.",
)

ELECTROLYSIS_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=24.06,
    mode=34.09,
    maximum=51.13,
    unit="EUR/t",
    description="Triangular distribution for electrolysis cement fixed OPEX in 2024 EUR.",
)

ELECTROLYSIS_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=13.03,
    mode=19.05,
    maximum=28.07,
    unit="EUR/t",
    description="Triangular distribution for electrolysis cement variable OPEX in 2024 EUR excluding fuel and electricity.",
)

ELECTROLYSIS_CEMENT_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/t",
    description="Assumed zero direct fuel consumption for electrolysis cement production.",
)

ELECTROLYSIS_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=1.60,
    upper_bound=3.10,
    unit="MWh/t",
    description="Uniform distribution for electrolysis cement electricity consumption.",
)

ELECTROLYSIS_CEMENT_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=0.060,
    upper_bound=0.140,
    unit="tCO2/t",
    description="Uniform distribution for electrolysis direct operational CO2 emissions.",
)


# Clinker substitution is represented as a BAU-relative retrofit. It has no
# incremental CAPEX or fixed OPEX in the model; its cost effect is an increase
# in variable OPEX.
CLINKER_SUBSTITUTION_CEMENT_CAPEX = FixedParameter(
    value=0.0,
    unit="EUR/(t/year)",
    description="Assumed zero incremental CAPEX for clinker substitution, not annualized.",
)

CLINKER_SUBSTITUTION_CEMENT_FIXED_OPEX = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero incremental fixed OPEX for clinker substitution.",
)

CLINKER_SUBSTITUTION_CEMENT_VARIABLE_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=2.94,
    upper_bound=6.43,
    unit="EUR/t",
    description="Uniform distribution for clinker substitution variable OPEX increase in 2024 EUR.",
)

CLINKER_SUBSTITUTION_CEMENT_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.15,
    upper_bound=0.25,
    unit="fraction",
    description="Uniform distribution for clinker substitution fuel-consumption reduction relative to BAU.",
)

CLINKER_SUBSTITUTION_CEMENT_ELECTRICITY_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero electricity-consumption change relative to BAU.",
)

CLINKER_SUBSTITUTION_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.05,
    upper_bound=0.20,
    unit="fraction",
    description="Uniform distribution for the direct operational CO2 reduction relative to BAU.",
)


# Alternative fuels are represented as a BAU-relative fuel-switch retrofit.
# Thermal-energy demand is unchanged; the NPV model instead blends fossil and
# alternative fuel prices according to the sampled alternative-fuel share.
ALTERNATIVE_FUELS_CEMENT_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=2.0,
    unit="EUR/(t/year)",
    description="Uniform distribution for alternative fuels retrofit CAPEX increase; retained without CEPCI normalization because the thesis-selected allowance has no monetary basis year.",
)

ALTERNATIVE_FUELS_CEMENT_FIXED_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero incremental fixed OPEX for the alternative-fuels retrofit.",
)

ALTERNATIVE_FUELS_CEMENT_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero non-energy variable-OPEX change for the alternative-fuels retrofit.",
)

ALTERNATIVE_FUELS_CEMENT_FUEL_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero change in thermal-energy demand relative to BAU.",
)

ALTERNATIVE_FUELS_CEMENT_ELECTRICITY_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero change in electricity consumption relative to BAU.",
)

ALTERNATIVE_FUELS_CEMENT_SHARE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.25,
    upper_bound=0.60,
    unit="fraction",
    description="Uniform distribution for alternative fuel share in thermal fuel demand.",
)

ALTERNATIVE_FUELS_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.03,
    upper_bound=0.17,
    unit="fraction",
    description="Uniform distribution for the direct operational CO2 reduction relative to BAU.",
)


# Efficiency improvement is a BAU-relative retrofit. Its CAPEX is incremental;
# sampled reductions are applied to BAU energy use and direct operational
# emissions.
EFFICIENCY_IMPROVEMENT_CEMENT_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=27.45,
    unit="EUR/(t/year)",
    description="Uniform distribution for efficiency improvement retrofit CAPEX increase in 2024 EUR.",
)

EFFICIENCY_IMPROVEMENT_CEMENT_FIXED_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero incremental fixed OPEX for efficiency improvement.",
)

EFFICIENCY_IMPROVEMENT_CEMENT_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero non-energy variable-OPEX change for efficiency improvement.",
)

EFFICIENCY_IMPROVEMENT_CEMENT_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=0.10,
    unit="fraction",
    description="Uniform distribution for efficiency improvement fuel-consumption reduction relative to BAU.",
)

EFFICIENCY_IMPROVEMENT_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=0.20,
    unit="fraction",
    description="Uniform distribution for efficiency improvement electricity-consumption reduction relative to BAU.",
)

EFFICIENCY_IMPROVEMENT_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=0.02,
    unit="fraction",
    description="Uniform distribution for the direct operational CO2 reduction relative to BAU.",
)


# Waste heat recovery is a BAU-relative retrofit with incremental CAPEX and
# fixed OPEX. Its modelled operating benefit is lower electricity consumption.
WASTE_HEAT_RECOVERY_CEMENT_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=2.78,
    upper_bound=25.00,
    unit="EUR/(t/year)",
    description="Uniform distribution for waste heat recovery retrofit CAPEX increase in 2024 EUR.",
)

WASTE_HEAT_RECOVERY_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.14,
    upper_bound=0.69,
    unit="EUR/t",
    description="Uniform distribution for waste heat recovery fixed OPEX increase in 2024 EUR.",
)

WASTE_HEAT_RECOVERY_CEMENT_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero non-energy variable-OPEX change for waste heat recovery.",
)

WASTE_HEAT_RECOVERY_CEMENT_FUEL_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero fuel-consumption change relative to BAU.",
)

WASTE_HEAT_RECOVERY_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.17,
    upper_bound=0.40,
    unit="fraction",
    description="Uniform distribution for waste heat recovery electricity-consumption reduction relative to BAU.",
)

WASTE_HEAT_RECOVERY_CEMENT_EMISSIONS_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero direct operational CO2 reduction relative to BAU.",
)


# CCS is a BAU-relative capture retrofit. Incremental cost and energy-penalty
# assumptions are combined with the parent route; the emissions-reduction
# fraction is applied to BAU direct operational emissions.
CCS_CEMENT_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=76.38,
    upper_bound=256.90,
    unit="EUR/(t/year)",
    description="Uniform distribution for CCS retrofit CAPEX increase in 2024 EUR.",
)

CCS_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=5.55,
    upper_bound=13.89,
    unit="EUR/t",
    description="Uniform distribution for CCS fixed OPEX increase in 2024 EUR.",
)

CCS_CEMENT_VARIABLE_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=4.17,
    unit="EUR/t",
    description="Uniform distribution for CCS variable OPEX increase in 2024 EUR excluding fuel and electricity.",
)

CCS_CEMENT_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-1.30,
    upper_bound=0.0,
    unit="fraction",
    description="Uniform distribution for CCS fuel-consumption reduction relative to BAU; negative values represent increases.",
)

CCS_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-2.60,
    upper_bound=0.70,
    unit="fraction",
    description="Uniform distribution for CCS electricity-consumption reduction relative to BAU; negative values represent increases.",
)

CCS_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.88,
    upper_bound=0.94,
    unit="fraction",
    description="Uniform distribution for the direct operational CO2 reduction relative to BAU.",
)


# Process heat integration is a BAU-relative retrofit with incremental CAPEX
# and fixed OPEX. Its benefits are lower fuel use and direct operational
# emissions.
PROCESS_HEAT_INTEGRATION_CEMENT_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=1.48,
    upper_bound=19.93,
    unit="EUR/(t/year)",
    description="Uniform distribution for process heat integration retrofit CAPEX increase in 2024 EUR.",
)

PROCESS_HEAT_INTEGRATION_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0,
    upper_bound=0.77,
    unit="EUR/t",
    description="Uniform distribution for process heat integration fixed OPEX increase in 2024 EUR.",
)

PROCESS_HEAT_INTEGRATION_CEMENT_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/t",
    description="Assumed zero non-energy variable-OPEX change for process heat integration.",
)

PROCESS_HEAT_INTEGRATION_CEMENT_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.03,
    upper_bound=0.30,
    unit="fraction",
    description="Uniform distribution for process heat integration fuel-consumption reduction relative to BAU.",
)

PROCESS_HEAT_INTEGRATION_CEMENT_ELECTRICITY_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero electricity-consumption change relative to BAU.",
)

PROCESS_HEAT_INTEGRATION_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.01,
    upper_bound=0.12,
    unit="fraction",
    description="Uniform distribution for the direct operational CO2 reduction relative to BAU.",
)

CEMENT_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
    "annual_cement_output_t": ANNUAL_CEMENT_OUTPUT_T,
}

CEMENT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "bau": {
        "capex_eur_per_t": BAU_CEMENT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_t": BAU_CEMENT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_t": BAU_CEMENT_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_t": BAU_CEMENT_FUEL_CONSUMPTION_DISTRIBUTION,
        "electricity_consumption_mwh_per_t": (
            BAU_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_t": BAU_CEMENT_EMISSIONS_DISTRIBUTION,
    },
    "electrification": {
        "capex_eur_per_t": ELECTRIFICATION_CEMENT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_t": ELECTRIFICATION_CEMENT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_t": (
            ELECTRIFICATION_CEMENT_VARIABLE_OPEX_DISTRIBUTION
        ),
        "fuel_consumption_mwh_th_per_t": ELECTRIFICATION_CEMENT_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_t": (
            ELECTRIFICATION_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_t": ELECTRIFICATION_CEMENT_EMISSIONS_DISTRIBUTION,
    },
    "electrolysis": {
        "capex_eur_per_t": ELECTROLYSIS_CEMENT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_t": ELECTROLYSIS_CEMENT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_t": ELECTROLYSIS_CEMENT_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_t": ELECTROLYSIS_CEMENT_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_t": (
            ELECTROLYSIS_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_t": ELECTROLYSIS_CEMENT_EMISSIONS_DISTRIBUTION,
    },
}

CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | UniformDistribution],
] = {
    "clinker_substitution": {
        "capex_change_eur_per_t": CLINKER_SUBSTITUTION_CEMENT_CAPEX,
        "fixed_opex_change_eur_per_t": CLINKER_SUBSTITUTION_CEMENT_FIXED_OPEX,
        "variable_opex_change_eur_per_t": (
            CLINKER_SUBSTITUTION_CEMENT_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": (
            CLINKER_SUBSTITUTION_CEMENT_FUEL_REDUCTION_DISTRIBUTION
        ),
        "electricity_consumption_reduction_fraction": (
            CLINKER_SUBSTITUTION_CEMENT_ELECTRICITY_REDUCTION
        ),
        "emissions_reduction_fraction": (
            CLINKER_SUBSTITUTION_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "alternative_fuels": {
        "capex_change_eur_per_t": ALTERNATIVE_FUELS_CEMENT_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_t": ALTERNATIVE_FUELS_CEMENT_FIXED_OPEX_CHANGE,
        "variable_opex_change_eur_per_t": (
            ALTERNATIVE_FUELS_CEMENT_VARIABLE_OPEX_CHANGE
        ),
        "fuel_consumption_reduction_fraction": ALTERNATIVE_FUELS_CEMENT_FUEL_REDUCTION,
        "electricity_consumption_reduction_fraction": (
            ALTERNATIVE_FUELS_CEMENT_ELECTRICITY_REDUCTION
        ),
        "alternative_fuel_share_fraction": ALTERNATIVE_FUELS_CEMENT_SHARE_DISTRIBUTION,
        "emissions_reduction_fraction": (
            ALTERNATIVE_FUELS_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "efficiency_improvement": {
        "capex_change_eur_per_t": (
            EFFICIENCY_IMPROVEMENT_CEMENT_CAPEX_CHANGE_DISTRIBUTION
        ),
        "fixed_opex_change_eur_per_t": (
            EFFICIENCY_IMPROVEMENT_CEMENT_FIXED_OPEX_CHANGE
        ),
        "variable_opex_change_eur_per_t": (
            EFFICIENCY_IMPROVEMENT_CEMENT_VARIABLE_OPEX_CHANGE
        ),
        "fuel_consumption_reduction_fraction": (
            EFFICIENCY_IMPROVEMENT_CEMENT_FUEL_REDUCTION_DISTRIBUTION
        ),
        "electricity_consumption_reduction_fraction": (
            EFFICIENCY_IMPROVEMENT_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": (
            EFFICIENCY_IMPROVEMENT_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "waste_heat_recovery": {
        "capex_change_eur_per_t": (
            WASTE_HEAT_RECOVERY_CEMENT_CAPEX_CHANGE_DISTRIBUTION
        ),
        "fixed_opex_change_eur_per_t": (
            WASTE_HEAT_RECOVERY_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_t": (
            WASTE_HEAT_RECOVERY_CEMENT_VARIABLE_OPEX_CHANGE
        ),
        "fuel_consumption_reduction_fraction": (
            WASTE_HEAT_RECOVERY_CEMENT_FUEL_REDUCTION
        ),
        "electricity_consumption_reduction_fraction": (
            WASTE_HEAT_RECOVERY_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": (
            WASTE_HEAT_RECOVERY_CEMENT_EMISSIONS_REDUCTION
        ),
    },
    "ccs": {
        "capex_change_eur_per_t": CCS_CEMENT_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_t": CCS_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION,
        "variable_opex_change_eur_per_t": (
            CCS_CEMENT_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": CCS_CEMENT_FUEL_REDUCTION_DISTRIBUTION,
        "electricity_consumption_reduction_fraction": (
            CCS_CEMENT_ELECTRICITY_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": CCS_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION,
    },
    "process_heat_integration": {
        "capex_change_eur_per_t": (
            PROCESS_HEAT_INTEGRATION_CEMENT_CAPEX_CHANGE_DISTRIBUTION
        ),
        "fixed_opex_change_eur_per_t": (
            PROCESS_HEAT_INTEGRATION_CEMENT_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_t": (
            PROCESS_HEAT_INTEGRATION_CEMENT_VARIABLE_OPEX_CHANGE
        ),
        "fuel_consumption_reduction_fraction": (
            PROCESS_HEAT_INTEGRATION_CEMENT_FUEL_REDUCTION_DISTRIBUTION
        ),
        "electricity_consumption_reduction_fraction": (
            PROCESS_HEAT_INTEGRATION_CEMENT_ELECTRICITY_REDUCTION
        ),
        "emissions_reduction_fraction": (
            PROCESS_HEAT_INTEGRATION_CEMENT_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
}
