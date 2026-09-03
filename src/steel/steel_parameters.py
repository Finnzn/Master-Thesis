"""Steel-sector parameters for the Monte Carlo simulation.

This file is the steel assumptions catalogue. It records technology input
values and uncertainty ranges without performing financial calculations, in
the same way as the electricity and cement parameter modules.
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

# Steel revenue is calculated from this fixed crude-steel retail price and the
# normalized annual output.
RETAIL_PRICE_STEEL_EUR_PER_TCS = FixedParameter(
    value=650.0,
    unit="EUR/tCS",
    description="Retail price of crude steel used in the steel-sector setup.",
)

# Normalized annual output: every steel technology is compared at this annual
# crude-steel production volume.
ANNUAL_STEEL_OUTPUT_TCS = FixedParameter(
    value=1_000_000.0,
    unit="tCS/year",
    description="Annual crude-steel output target used to normalize steel technologies.",
)


# Greenfield European blast-furnace/basic-oxygen-furnace (BF-BOF) business-as-
# usual technology. The supplied direct-emissions values of 1,770/1,820/1,870
# kgCO2/tCS are stored as 1.770/1.820/1.870 tCO2/tCS so they are compatible with
# the project's carbon-price unit of EUR/tCO2.
BF_BOF_BAU_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=425.0,
    mode=592.0,
    maximum=770.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European BF-BOF BAU CAPEX, not annualized.",
)

BF_BOF_BAU_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=39.0,
    mode=43.0,
    maximum=47.0,
    unit="EUR/tCS",
    description="Triangular distribution for BF-BOF BAU fixed OPEX.",
)

BF_BOF_BAU_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=270.0,
    mode=335.0,
    maximum=335.0,
    unit="EUR/tCS",
    description="Triangular distribution for BF-BOF BAU variable OPEX excluding fuel and electricity.",
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
    description="Triangular distribution for BF-BOF BAU direct emissions.",
)


# Greenfield European scrap-based electric-arc-furnace (Scrap-EAF) technology.
# Charcoal is its supplied fuel/reductant. The direct-emissions values of
# 10/40/40 kgCO2/tCS are stored as 0.010/0.040/0.040 tCO2/tCS to match the
# project's carbon-price unit of EUR/tCO2.
SCRAP_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=247.0,
    mode=247.0,
    maximum=474.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European Scrap-EAF CAPEX, not annualized.",
)

SCRAP_EAF_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=18.0,
    mode=18.0,
    maximum=23.0,
    unit="EUR/tCS",
    description="Triangular distribution for Scrap-EAF fixed OPEX.",
)

SCRAP_EAF_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=449.0,
    mode=475.0,
    maximum=598.0,
    unit="EUR/tCS",
    description="Triangular distribution for Scrap-EAF variable OPEX.",
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
    description="Triangular distribution for Scrap-EAF direct emissions.",
)


# Greenfield European natural-gas direct-reduced-iron electric-arc-furnace
# (NG-DRI-EAF) business-as-usual technology. Natural gas is its supplied
# fuel/reductant. The direct-emissions values of 550/590/1,000 kgCO2/tCS are
# stored as 0.550/0.590/1.000 tCO2/tCS to match the project's carbon-price unit.
NG_DRI_EAF_BAU_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=650.0,
    mode=660.0,
    maximum=660.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European NG-DRI-EAF BAU CAPEX, not annualized.",
)

NG_DRI_EAF_BAU_FIXED_OPEX = FixedParameter(
    value=32.5,
    unit="EUR/tCS",
    description="Fixed OPEX for NG-DRI-EAF BAU.",
)

NG_DRI_EAF_BAU_VARIABLE_OPEX = FixedParameter(
    value=312.0,
    unit="EUR/tCS",
    description="Approximate variable OPEX for NG-DRI-EAF BAU.",
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
    description="Triangular distribution for NG-DRI-EAF BAU direct emissions.",
)


# Greenfield European hydrogen direct-reduced-iron electric-arc-furnace
# (H2-DRI-EAF) technology. Hydrogen and charcoal are stored separately because
# their supplied consumption values use different physical units. The direct-
# emissions values of 5/5/10 kgCO2/tCS are stored as 0.005/0.005/0.010
# tCO2/tCS to match the project's carbon-price unit.
H2_DRI_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=390.0,
    mode=555.0,
    maximum=830.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European H2-DRI-EAF CAPEX, not annualized.",
)

H2_DRI_EAF_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=26.0,
    mode=30.0,
    maximum=37.0,
    unit="EUR/tCS",
    description="Triangular distribution for H2-DRI-EAF fixed OPEX.",
)

H2_DRI_EAF_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=313.0,
    mode=313.0,
    maximum=378.0,
    unit="EUR/tCS",
    description="Triangular distribution for H2-DRI-EAF variable OPEX.",
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
    description="Triangular distribution for H2-DRI-EAF direct emissions.",
)


# Greenfield European molten oxide electrolysis (MOE) technology. It has no
# fuel/reductant consumption or direct process emissions in the supplied setup.
MOE_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=500.0,
    mode=1_000.0,
    maximum=2_000.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European MOE CAPEX, not annualized.",
)

MOE_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=30.0,
    mode=59.0,
    maximum=118.0,
    unit="EUR/tCS",
    description="Triangular distribution for MOE fixed OPEX.",
)

MOE_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=106.0,
    mode=211.0,
    maximum=422.0,
    unit="EUR/tCS",
    description="Triangular distribution for MOE variable OPEX.",
)

MOE_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/tCS",
    description="Fuel and reductant consumption for MOE.",
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
    description="Direct emissions for MOE.",
)


# Greenfield European alkaline-electrolysis electric-arc-furnace (AEL-EAF)
# technology. Its OPEX ranges have no supplied base values and are therefore
# represented as uniform distributions. Charcoal is its supplied reductant.
AEL_EAF_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=400.0,
    mode=434.0,
    maximum=800.0,
    unit="EUR/tCS",
    description="Triangular distribution for greenfield European AEL-EAF CAPEX, not annualized.",
)

AEL_EAF_FIXED_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=43.0,
    upper_bound=88.0,
    unit="EUR/tCS",
    description="Uniform distribution for AEL-EAF fixed OPEX.",
)

AEL_EAF_VARIABLE_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=246.0,
    upper_bound=250.0,
    unit="EUR/tCS",
    description="Uniform distribution for AEL-EAF variable OPEX.",
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
    description="Direct emissions for AEL-EAF, converted from 10 kgCO2/tCS.",
)


# BF-BOF post-combustion CCS is an incremental retrofit relative to BF-BOF BAU.
# Cost changes are added to the BAU values. Positive reduction fractions lower
# a BAU physical intensity, while negative values represent the supplied fuel
# and electricity consumption increases.
BF_BOF_POST_COMBUSTION_CCS_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=177.0,
    upper_bound=231.0,
    unit="EUR/tCS",
    description="Uniform distribution for BF-BOF post-combustion CCS CAPEX increase.",
)

BF_BOF_POST_COMBUSTION_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=6.1,
    upper_bound=8.1,
    unit="EUR/tCS",
    description="Uniform distribution for BF-BOF post-combustion CCS fixed OPEX increase.",
)

BF_BOF_POST_COMBUSTION_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = (
    UniformDistribution(
        lower_bound=4.1,
        upper_bound=4.9,
        unit="EUR/tCS",
        description="Uniform distribution for BF-BOF post-combustion CCS variable OPEX increase.",
    )
)

BF_BOF_POST_COMBUSTION_CCS_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-0.22,
    upper_bound=0.0,
    unit="fraction",
    description="Uniform distribution for BF-BOF post-combustion CCS fuel-consumption reduction relative to BAU; negative values represent increases.",
)

BF_BOF_POST_COMBUSTION_CCS_ELECTRICITY_REDUCTION_DISTRIBUTION = (
    UniformDistribution(
        lower_bound=-5.70,
        upper_bound=0.0,
        unit="fraction",
        description="Uniform distribution for BF-BOF post-combustion CCS electricity-consumption reduction relative to BAU; negative values represent increases.",
    )
)

BF_BOF_POST_COMBUSTION_CCS_EMISSIONS_REDUCTION_DISTRIBUTION = (
    TriangularDistribution(
        minimum=0.52,
        mode=0.73,
        maximum=0.73,
        unit="fraction",
        description="Triangular distribution for BF-BOF post-combustion CCS direct-emissions reduction relative to BAU.",
    )
)


# NG-DRI-EAF CCS is an incremental retrofit relative to NG-DRI-EAF BAU. The
# exact +0.30 MWh/tCS electricity increment is converted to the common negative-
# reduction convention using the fixed 1.06 MWh/tCS BAU electricity intensity.
NG_DRI_EAF_CCS_CAPEX_CHANGE = FixedParameter(
    value=200.0,
    unit="EUR/tCS",
    description="CAPEX increase for the NG-DRI-EAF CCS retrofit.",
)

NG_DRI_EAF_CCS_FIXED_OPEX_CHANGE = FixedParameter(
    value=11.8,
    unit="EUR/tCS",
    description="Fixed OPEX increase for the NG-DRI-EAF CCS retrofit.",
)

NG_DRI_EAF_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=1.2,
    mode=1.5,
    maximum=1.5,
    unit="EUR/tCS",
    description="Triangular distribution for the NG-DRI-EAF CCS variable OPEX increase.",
)

NG_DRI_EAF_CCS_FUEL_REDUCTION = FixedParameter(
    value=0.0,
    unit="fraction",
    description="Natural-gas consumption reduction for NG-DRI-EAF CCS relative to BAU.",
)

NG_DRI_EAF_CCS_ELECTRICITY_CONSUMPTION_CHANGE = FixedParameter(
    value=0.30,
    unit="MWh/tCS",
    description="Absolute purchased-electricity consumption increase for NG-DRI-EAF CCS.",
)

NG_DRI_EAF_CCS_ELECTRICITY_REDUCTION = FixedParameter(
    value=-(
        NG_DRI_EAF_CCS_ELECTRICITY_CONSUMPTION_CHANGE.value
        / NG_DRI_EAF_BAU_ELECTRICITY_CONSUMPTION.value
    ),
    unit="fraction",
    description="Purchased-electricity consumption reduction for NG-DRI-EAF CCS relative to BAU; the negative value represents the exact 0.30 MWh/tCS increase.",
)

NG_DRI_EAF_CCS_EMISSIONS_REDUCTION = FixedParameter(
    value=0.64,
    unit="fraction",
    description="Approximate direct-emissions reduction for NG-DRI-EAF CCS relative to BAU.",
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
    "bf_bof_post_combustion_ccs": "bf_bof_bau",
    "ng_dri_eaf_ccs": "ng_dri_eaf_bau",
}

STEEL_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "bf_bof_post_combustion_ccs": {
        "capex_change_eur_per_tcs": (
            BF_BOF_POST_COMBUSTION_CCS_CAPEX_CHANGE_DISTRIBUTION
        ),
        "fixed_opex_change_eur_per_tcs": (
            BF_BOF_POST_COMBUSTION_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_tcs": (
            BF_BOF_POST_COMBUSTION_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": (
            BF_BOF_POST_COMBUSTION_CCS_FUEL_REDUCTION_DISTRIBUTION
        ),
        "electricity_consumption_reduction_fraction": (
            BF_BOF_POST_COMBUSTION_CCS_ELECTRICITY_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": (
            BF_BOF_POST_COMBUSTION_CCS_EMISSIONS_REDUCTION_DISTRIBUTION
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
