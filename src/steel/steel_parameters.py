"""Steel-sector assumptions used by the deterministic and Monte Carlo models.

This module records technology inputs and uncertainty ranges without performing
financial calculations.

Technology cost assumptions use the supplied 2024 values. Absolute technologies
define complete production routes; CCS technologies define changes relative to
their registered parent routes. Reduction fractions are positive for reductions
and negative for increases.

Emissions parameters represent direct operational CO2, not upstream or
life-cycle emissions. Source values reported in kgCO2/tCS were divided by 1,000
and are stored consistently as tCO2/tCS for use with the EUR/tCO2 carbon price.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


# Economic lifetime used when steel-sector annual cash flows are discounted.
LIFETIME_STEEL_YEARS = FixedParameter(
    value=20.0,
    unit="years",
    description="Economic lifetime of steel-sector assets.",
)

# Fixed crude-steel sales price used to calculate annual revenue.
RETAIL_PRICE_STEEL_EUR_PER_TCS = FixedParameter(
    value=750.0,
    unit="EUR/tCS",
    description="Fixed crude-steel sales price used by the financial model.",
)

# Normalized annual output: every steel technology is compared at this annual
# crude-steel production volume.
ANNUAL_STEEL_OUTPUT_TCS = FixedParameter(
    value=1_000_000.0,
    unit="tCS/year",
    description="Annual crude-steel output target used to normalize steel technologies.",
)


# BF-BOF is the greenfield European reference route. Its combined fuel and
# reductant demand, purchased electricity, and direct operational emissions are
# absolute production intensities.
BF_BOF_BAU_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=570.0,
    mode=581.0,
    maximum=1_033.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European BF-BOF BAU CAPEX in 2024 EUR, not annualized.",
)

BF_BOF_BAU_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=42.2,
    mode=42.4,
    maximum=53.1,
    unit="EUR/tCS",
    description="Triangular distribution for BF-BOF BAU fixed OPEX in 2024 EUR.",
)

BF_BOF_BAU_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=328.0,
    mode=328.0,
    maximum=362.3,
    unit="EUR/tCS",
    description="Triangular distribution for BF-BOF BAU variable OPEX in 2024 EUR excluding fuel and electricity.",
)

BF_BOF_BAU_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=5.4,
    mode=5.56,
    maximum=5.8,
    unit="MWh_th/tCS",
    description="Triangular distribution for BF-BOF BAU fuel and reductant consumption.",
)

BF_BOF_BAU_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=0.115,
    unit="MWh/tCS",
    description="Purchased-electricity consumption for the BF-BOF BAU fuel mix.",
)

BF_BOF_BAU_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=1.770,
    mode=1.820,
    maximum=1.870,
    unit="tCO2/tCS",
    description="Triangular distribution for BF-BOF direct operational CO2 emissions.",
)


# Scrap-EAF is a greenfield European scrap-based route using charcoal as its
# modelled fuel and reductant. Its normalized variable-OPEX range no longer
# contains the former base value, so that input is represented as uniform.
SCRAP_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=242.0,
    mode=242.0,
    maximum=636.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European Scrap-EAF CAPEX in 2024 EUR, not annualized.",
)

SCRAP_EAF_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=17.2,
    mode=17.2,
    maximum=26.5,
    unit="EUR/tCS",
    description="Triangular distribution for Scrap-EAF fixed OPEX in 2024 EUR.",
)

SCRAP_EAF_VARIABLE_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=602.5,
    upper_bound=802.4,
    unit="EUR/tCS",
    description="Uniform distribution for Scrap-EAF variable OPEX in 2024 EUR.",
)

SCRAP_EAF_CHARCOAL_CONSUMPTION = FixedParameter(
    value=0.103,
    unit="MWh_th/tCS",
    description="Charcoal fuel and reductant consumption for Scrap-EAF.",
)

SCRAP_EAF_ELECTRICITY_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=0.667,
    mode=0.667,
    maximum=0.683,
    unit="MWh/tCS",
    description="Triangular distribution for Scrap-EAF purchased-electricity consumption.",
)

SCRAP_EAF_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.010,
    mode=0.040,
    maximum=0.040,
    unit="tCO2/tCS",
    description="Triangular distribution for Scrap-EAF direct operational CO2 emissions.",
)


# NG-DRI-EAF is the greenfield European natural-gas DRI reference route.
# Natural gas provides the modelled fuel and reductant demand.
NG_DRI_EAF_BAU_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=647.0,
    mode=647.0,
    maximum=734.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European NG-DRI-EAF BAU CAPEX in 2024 EUR, not annualized.",
)

NG_DRI_EAF_BAU_FIXED_OPEX = FixedParameter(
    value=31.9,
    unit="EUR/tCS",
    description="Fixed OPEX for NG-DRI-EAF BAU in 2024 EUR.",
)

NG_DRI_EAF_BAU_VARIABLE_OPEX = FixedParameter(
    value=305.9,
    unit="EUR/tCS",
    description="Approximate variable OPEX for NG-DRI-EAF BAU in 2024 EUR.",
)

NG_DRI_EAF_BAU_NATURAL_GAS_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=2.44,
    mode=2.70,
    maximum=2.70,
    unit="MWh_th/tCS",
    description="Triangular distribution for NG-DRI-EAF BAU natural-gas consumption.",
)

NG_DRI_EAF_BAU_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=1.06,
    unit="MWh/tCS",
    description="Purchased-electricity consumption for NG-DRI-EAF BAU.",
)

NG_DRI_EAF_BAU_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.550,
    mode=0.590,
    maximum=1.000,
    unit="tCO2/tCS",
    description="Triangular distribution for NG-DRI-EAF direct operational CO2 emissions.",
)


# H2-DRI-EAF is a greenfield European hydrogen-based DRI route. Hydrogen and
# charcoal inputs remain separate because they use different physical units and
# are priced through different model inputs.
H2_DRI_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=381.0,
    mode=544.0,
    maximum=816.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European H2-DRI-EAF CAPEX in 2024 EUR, not annualized.",
)

H2_DRI_EAF_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=25.6,
    mode=29.4,
    maximum=35.8,
    unit="EUR/tCS",
    description="Triangular distribution for H2-DRI-EAF fixed OPEX in 2024 EUR.",
)

H2_DRI_EAF_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=306.9,
    mode=306.9,
    maximum=507.2,
    unit="EUR/tCS",
    description="Triangular distribution for H2-DRI-EAF variable OPEX in 2024 EUR.",
)

H2_DRI_EAF_HYDROGEN_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=44.6,
    mode=44.6,
    maximum=68.8,
    unit="kg/tCS",
    description="Triangular distribution for H2-DRI-EAF hydrogen consumption.",
)

H2_DRI_EAF_CHARCOAL_CONSUMPTION = FixedParameter(
    value=0.147,
    unit="MWh_th/tCS",
    description="Charcoal fuel and reductant consumption for H2-DRI-EAF.",
)

H2_DRI_EAF_ELECTRICITY_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=0.57,
    mode=1.06,
    maximum=1.06,
    unit="MWh/tCS",
    description="Triangular distribution for H2-DRI-EAF purchased-electricity consumption.",
)

H2_DRI_EAF_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.005,
    mode=0.005,
    maximum=0.010,
    unit="tCO2/tCS",
    description="Triangular distribution for H2-DRI-EAF direct operational CO2 emissions.",
)


# MOE is a greenfield European electrolysis route. Direct fuel/reductant use and
# operational CO2 emissions are modelled as zero; electricity use is explicit.
MOE_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=564.0,
    mode=1_129.0,
    maximum=2_257.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European MOE CAPEX in 2024 EUR, not annualized.",
)

MOE_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=40.3,
    mode=79.2,
    maximum=158.3,
    unit="EUR/tCS",
    description="Triangular distribution for MOE fixed OPEX in 2024 EUR.",
)

MOE_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=142.3,
    mode=283.1,
    maximum=566.2,
    unit="EUR/tCS",
    description="Triangular distribution for MOE variable OPEX in 2024 EUR.",
)

MOE_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/tCS",
    description="Assumed zero direct fuel and reductant consumption for MOE.",
)

MOE_ELECTRICITY_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=3.44,
    mode=4.10,
    maximum=4.11,
    unit="MWh/tCS",
    description="Triangular distribution for MOE purchased-electricity consumption.",
)

MOE_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tCS",
    description="Assumed zero direct operational CO2 emissions for MOE.",
)


# AEL-EAF is a greenfield European alkaline-electrolysis route using charcoal as
# its modelled reductant. Fixed and variable OPEX are uniform because their
# source ranges provide no central estimates.
AEL_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=451.0,
    mode=490.0,
    maximum=903.0,
    unit="EUR/(tCS/year)",
    description="Triangular distribution for greenfield European AEL-EAF CAPEX in 2024 EUR, not annualized.",
)

AEL_EAF_FIXED_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=57.7,
    upper_bound=118.1,
    unit="EUR/tCS",
    description="Uniform distribution for AEL-EAF fixed OPEX in 2024 EUR.",
)

AEL_EAF_VARIABLE_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=330.1,
    upper_bound=335.5,
    unit="EUR/tCS",
    description="Uniform distribution for AEL-EAF variable OPEX in 2024 EUR.",
)

AEL_EAF_CHARCOAL_CONSUMPTION = FixedParameter(
    value=0.103,
    unit="MWh_th/tCS",
    description="Charcoal fuel and reductant consumption for AEL-EAF.",
)

AEL_EAF_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=3.81,
    unit="MWh/tCS",
    description="Purchased-electricity consumption for AEL-EAF.",
)

AEL_EAF_EMISSIONS = FixedParameter(
    value=0.010,
    unit="tCO2/tCS",
    description="Modelled direct operational CO2 emissions for AEL-EAF.",
)


# BF-BOF+CCS is an incremental retrofit of BF-BOF. Cost changes are added to the
# parent route; energy-penalty ranges increase parent fuel and electricity use;
# the capture fraction reduces parent direct operational emissions.
BF_BOF_CCS_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=256.5,
    upper_bound=335.8,
    unit="EUR/(tCS/year)",
    description="Uniform distribution for BF + BOF + CCS CAPEX increase in 2024 EUR.",
)

BF_BOF_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=8.9,
    upper_bound=11.8,
    unit="EUR/tCS",
    description="Uniform distribution for BF + BOF + CCS fixed OPEX increase in 2024 EUR.",
)

BF_BOF_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = (
    UniformDistribution(
        lower_bound=6.0,
        upper_bound=7.1,
        unit="EUR/tCS",
        description="Uniform distribution for BF + BOF + CCS variable OPEX increase in 2024 EUR.",
    )
)

BF_BOF_CCS_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-0.22,
    upper_bound=0.0,
    unit="fraction",
    description="Uniform distribution for BF + BOF + CCS fuel-consumption reduction relative to BAU; negative values represent additional natural gas while baseline coal demand remains unchanged.",
)

BF_BOF_CCS_ELECTRICITY_REDUCTION_DISTRIBUTION = (
    UniformDistribution(
        lower_bound=-5.70,
        upper_bound=0.0,
        unit="fraction",
        description="Uniform distribution for BF + BOF + CCS electricity-consumption reduction relative to BAU; negative values represent increases.",
    )
)

BF_BOF_CCS_EMISSIONS_REDUCTION_DISTRIBUTION = (
    TriangularDistribution(
        minimum=0.52,
        mode=0.73,
        maximum=0.73,
        unit="fraction",
        description="Triangular distribution for direct operational CO2 reduction relative to BF-BOF.",
    )
)


# NG-DRI-EAF+CCS is an incremental retrofit of NG-DRI-EAF. Energy changes
# are stored directly as reduction fractions; negative values mean increases.
NG_DRI_EAF_CCS_CAPEX_CHANGE = FixedParameter(
    value=225.7,
    unit="EUR/(tCS/year)",
    description="CAPEX increase for the NG-DRI-EAF CCS retrofit in 2024 EUR.",
)

NG_DRI_EAF_CCS_FIXED_OPEX_CHANGE = FixedParameter(
    value=13.3,
    unit="EUR/tCS",
    description="Fixed OPEX increase for the NG-DRI-EAF CCS retrofit in 2024 EUR.",
)

NG_DRI_EAF_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=1.7,
    mode=2.2,
    maximum=2.2,
    unit="EUR/tCS",
    description="Triangular distribution for the NG-DRI-EAF CCS variable OPEX increase in 2024 EUR.",
)

NG_DRI_EAF_CCS_FUEL_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Assumed zero natural-gas consumption change relative to NG-DRI-EAF.",
)

NG_DRI_EAF_CCS_ELECTRICITY_REDUCTION = FixedParameter(
    value=-0.2830188679245283,
    unit="fraction",
    description="Purchased-electricity consumption reduction fraction for NG-DRI-EAF CCS; negative means increased demand.",
)

NG_DRI_EAF_CCS_EMISSIONS_REDUCTION = FixedParameter(
    value=0.64,
    unit="fraction",
    description="Approximate direct operational CO2 reduction relative to NG-DRI-EAF.",
)


STEEL_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_steel_years": LIFETIME_STEEL_YEARS,
    "retail_price_steel_eur_per_tcs": RETAIL_PRICE_STEEL_EUR_PER_TCS,
    "annual_steel_output_tcs": ANNUAL_STEEL_OUTPUT_TCS,
}

STEEL_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "bf_bof_bau": {
        "capex_eur_per_tcs": BF_BOF_BAU_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": BF_BOF_BAU_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tcs": BF_BOF_BAU_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_tcs": (
            BF_BOF_BAU_FUEL_CONSUMPTION_DISTRIBUTION
        ),
        "electricity_consumption_mwh_per_tcs": (
            BF_BOF_BAU_ELECTRICITY_CONSUMPTION
        ),
        "emissions_tco2_per_tcs": BF_BOF_BAU_EMISSIONS_DISTRIBUTION,
    },
    "scrap_eaf": {
        "capex_eur_per_tcs": SCRAP_EAF_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": SCRAP_EAF_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tcs": SCRAP_EAF_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_tcs": SCRAP_EAF_CHARCOAL_CONSUMPTION,
        "electricity_consumption_mwh_per_tcs": (
            SCRAP_EAF_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_tcs": SCRAP_EAF_EMISSIONS_DISTRIBUTION,
    },
    "ng_dri_eaf_bau": {
        "capex_eur_per_tcs": NG_DRI_EAF_BAU_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": NG_DRI_EAF_BAU_FIXED_OPEX,
        "variable_opex_eur_per_tcs": NG_DRI_EAF_BAU_VARIABLE_OPEX,
        "fuel_consumption_mwh_th_per_tcs": (
            NG_DRI_EAF_BAU_NATURAL_GAS_CONSUMPTION_DISTRIBUTION
        ),
        "electricity_consumption_mwh_per_tcs": (
            NG_DRI_EAF_BAU_ELECTRICITY_CONSUMPTION
        ),
        "emissions_tco2_per_tcs": NG_DRI_EAF_BAU_EMISSIONS_DISTRIBUTION,
    },
    "h2_dri_eaf": {
        "capex_eur_per_tcs": H2_DRI_EAF_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": H2_DRI_EAF_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tcs": H2_DRI_EAF_VARIABLE_OPEX_DISTRIBUTION,
        "hydrogen_consumption_kg_per_tcs": (
            H2_DRI_EAF_HYDROGEN_CONSUMPTION_DISTRIBUTION
        ),
        "charcoal_consumption_mwh_th_per_tcs": (
            H2_DRI_EAF_CHARCOAL_CONSUMPTION
        ),
        "electricity_consumption_mwh_per_tcs": (
            H2_DRI_EAF_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_tcs": H2_DRI_EAF_EMISSIONS_DISTRIBUTION,
    },
    "moe": {
        "capex_eur_per_tcs": MOE_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": MOE_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tcs": MOE_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_tcs": MOE_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_tcs": (
            MOE_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_tco2_per_tcs": MOE_EMISSIONS,
    },
    "ael_eaf": {
        "capex_eur_per_tcs": AEL_EAF_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tcs": AEL_EAF_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tcs": AEL_EAF_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_tcs": AEL_EAF_CHARCOAL_CONSUMPTION,
        "electricity_consumption_mwh_per_tcs": AEL_EAF_ELECTRICITY_CONSUMPTION,
        "emissions_tco2_per_tcs": AEL_EAF_EMISSIONS,
    },
}

STEEL_RETROFIT_BASE_TECHNOLOGIES: Mapping[str, str] = {
    "bf_bof_ccs": "bf_bof_bau",
    "ng_dri_eaf_ccs": "ng_dri_eaf_bau",
}

STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "bf_bof_ccs": {
        "capex_change_eur_per_tcs": (
            BF_BOF_CCS_CAPEX_CHANGE_DISTRIBUTION
        ),
        "fixed_opex_change_eur_per_tcs": (
            BF_BOF_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_tcs": (
            BF_BOF_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": (
            BF_BOF_CCS_FUEL_REDUCTION_DISTRIBUTION
        ),
        "electricity_consumption_reduction_fraction": (
            BF_BOF_CCS_ELECTRICITY_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": (
            BF_BOF_CCS_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "ng_dri_eaf_ccs": {
        "capex_change_eur_per_tcs": NG_DRI_EAF_CCS_CAPEX_CHANGE,
        "fixed_opex_change_eur_per_tcs": NG_DRI_EAF_CCS_FIXED_OPEX_CHANGE,
        "variable_opex_change_eur_per_tcs": (
            NG_DRI_EAF_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": NG_DRI_EAF_CCS_FUEL_REDUCTION,
        "electricity_consumption_reduction_fraction": (
            NG_DRI_EAF_CCS_ELECTRICITY_REDUCTION
        ),
        "emissions_reduction_fraction": NG_DRI_EAF_CCS_EMISSIONS_REDUCTION,
    },
}
