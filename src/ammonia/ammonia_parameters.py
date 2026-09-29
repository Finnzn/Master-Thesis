"""Ammonia-sector assumptions used by the deterministic and Monte Carlo models.

Technology CAPEX and OPEX use the supplied 2024 values. Absolute technologies
define complete ammonia-production routes; CCS technologies define incremental
changes relative to their registered parent routes. Feedstock and process-fuel
components are documented separately where useful, but only their total enters
energy cost calculations.

Emissions parameters represent direct operational CO2, not upstream or
life-cycle emissions. Source values reported in kgCO2/tNH3 were divided by
1,000 and stored as tCO2/tNH3 for use with the EUR/tCO2 carbon price.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


ANNUAL_AMMONIA_OUTPUT_TNH3 = FixedParameter(
    value=1_000_000.0,
    unit="tNH3/year",
    description="Common annual ammonia output for all compared technologies.",
)

# Economic lifetime used when ammonia-sector annual cash flows are discounted.
LIFETIME_AMMONIA_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of ammonia-sector assets.",
)

# Fixed ammonia sales price used to calculate annual revenue.
RETAIL_PRICE_AMMONIA_EUR_PER_T = FixedParameter(
    value=890.0,
    unit="EUR/t",
    description="Fixed ammonia sales price used by the financial model.",
)


# NG-SMR+HB is the greenfield European natural-gas reference route without
# capture. CAPEX is expressed per unit of annual ammonia-production capacity.
NG_SMR_HB_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1_006.0,
    upper_bound=2_187.0,
    unit="EUR/(tNH3/y)",
    description="Uniform distribution for greenfield European NG-SMR + HB CAPEX in 2024 EUR, not annualized.",
)

NG_SMR_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=39.0,
    mode=39.4,
    maximum=39.9,
    unit="EUR/tNH3",
    description="Triangular distribution for NG-SMR + HB fixed OPEX in 2024 EUR.",
)

NG_SMR_HB_VARIABLE_OPEX = FixedParameter(
    value=12.01,
    unit="EUR/tNH3",
    description="Variable OPEX for NG-SMR + HB in 2024 EUR.",
)

NG_SMR_HB_NATURAL_GAS_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=7.89,
    mode=8.64,
    maximum=8.92,
    unit="MWh/tNH3",
    description="Triangular distribution for NG-SMR + HB natural-gas consumption.",
)

NG_SMR_HB_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero purchased-electricity consumption for NG-SMR + HB.",
)

NG_SMR_HB_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=1.620,
    mode=1.770,
    maximum=1.800,
    unit="tCO2/tNH3",
    description="Triangular distribution for NG-SMR + HB direct operational CO2 emissions.",
)


# Coal gasification+HB is a greenfield route without capture. Coal feedstock and
# process-fuel components are recorded for traceability, while their total is
# registered once to avoid double counting energy costs.
COAL_GASIFICATION_HB_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_274.0,
    mode=4_093.0,
    maximum=5_320.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield coal gasification + HB CAPEX in 2024 EUR, not annualized.",
)

COAL_GASIFICATION_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=121.7,
    mode=152.1,
    maximum=197.7,
    unit="EUR/tNH3",
    description="Triangular distribution for coal gasification + HB fixed OPEX in 2024 EUR.",
)

COAL_GASIFICATION_HB_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=17.1,
    mode=21.3,
    maximum=27.7,
    unit="EUR/tNH3",
    description="Triangular distribution for coal gasification + HB variable OPEX in 2024 EUR.",
)

COAL_GASIFICATION_HB_COAL_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=5.17,
    unit="MWh/tNH3",
    description="Coal feedstock component of coal gasification + HB consumption.",
)

COAL_GASIFICATION_HB_COAL_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=4.19,
    unit="MWh/tNH3",
    description="Coal process-fuel component of coal gasification + HB consumption.",
)

COAL_GASIFICATION_HB_COAL_CONSUMPTION = FixedParameter(
    value=9.36,
    unit="MWh/tNH3",
    description="Total coal consumption for coal gasification + HB, including feedstock and process fuel.",
)

COAL_GASIFICATION_HB_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=1.03,
    unit="MWh/tNH3",
    description="Purchased-electricity consumption for coal gasification + HB.",
)

COAL_GASIFICATION_HB_EMISSIONS = FixedParameter(
    value=3.200,
    unit="tCO2/tNH3",
    description="Modelled direct operational CO2 emissions for coal gasification + HB.",
)


# AEL/PEM electrolysis+HB is a greenfield European electricity-based route.
# Direct fuel/reductant use and operational CO2 emissions are modelled as zero;
# purchased electricity is represented explicitly.
AEL_PEM_ELECTROLYSIS_HB_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=1_785.0,
    mode=2_549.0,
    maximum=3_824.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield European AEL/PEM electrolysis + HB CAPEX in 2024 EUR, not annualized.",
)

AEL_PEM_ELECTROLYSIS_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=35.0,
    mode=50.1,
    maximum=75.1,
    unit="EUR/tNH3",
    description="Triangular distribution for AEL/PEM electrolysis + HB fixed OPEX in 2024 EUR.",
)

AEL_PEM_ELECTROLYSIS_HB_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3.26,
    mode=4.66,
    maximum=6.98,
    unit="EUR/tNH3",
    description="Triangular distribution for AEL/PEM electrolysis + HB variable OPEX in 2024 EUR.",
)

AEL_PEM_ELECTROLYSIS_HB_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero direct fuel and reductant consumption for AEL/PEM + HB.",
)

AEL_PEM_ELECTROLYSIS_HB_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=8.6,
    mode=9.6,
    maximum=10.0,
    unit="MWh/tNH3",
    description="Triangular distribution for AEL/PEM electrolysis + HB purchased electricity.",
)

AEL_PEM_ELECTROLYSIS_HB_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tNH3",
    description="Assumed zero direct operational CO2 emissions for AEL/PEM + HB.",
)


# Biomass gasification+HB is a greenfield bioenergy route. Feedstock and
# process-fuel components are recorded separately, while their total is
# registered once. Direct operational CO2 emissions are modelled as zero.
BIOMASS_GASIFICATION_HB_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_729.0,
    mode=5_327.0,
    maximum=7_991.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield biomass gasification + HB CAPEX in 2024 EUR, not annualized.",
)

BIOMASS_GASIFICATION_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=35.8,
    mode=51.2,
    maximum=76.8,
    unit="EUR/tNH3",
    description="Triangular distribution for biomass gasification + HB fixed OPEX in 2024 EUR.",
)

BIOMASS_GASIFICATION_HB_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=17.3,
    mode=24.7,
    maximum=37.0,
    unit="EUR/tNH3",
    description="Triangular distribution for biomass gasification + HB variable OPEX in 2024 EUR.",
)

BIOMASS_GASIFICATION_HB_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=5.17,
    unit="MWh/tNH3",
    description="Biomass feedstock component of biomass gasification + HB consumption.",
)

BIOMASS_GASIFICATION_HB_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=4.58,
    unit="MWh/tNH3",
    description="Biomass process-fuel component of biomass gasification + HB consumption.",
)

BIOMASS_GASIFICATION_HB_BIOMASS_CONSUMPTION = FixedParameter(
    value=9.75,
    unit="MWh/tNH3",
    description="Total biomass consumption for biomass gasification + HB, including feedstock and process fuel.",
)

BIOMASS_GASIFICATION_HB_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=0.39,
    unit="MWh/tNH3",
    description="Purchased-electricity consumption for biomass gasification + HB.",
)

BIOMASS_GASIFICATION_HB_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tNH3",
    description="Fixed zero direct operational CO2 emissions for biomass gasification + HB.",
)


# Methane pyrolysis+HB is a greenfield route with an electrically heated
# molten-metal reactor. Natural gas is used as feedstock; the model records no
# additional natural-gas process fuel or direct operational CO2 emissions.
METHANE_PYROLYSIS_HB_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=815.0,
    mode=1_165.0,
    maximum=1_747.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield methane pyrolysis + HB CAPEX in 2024 EUR, not annualized.",
)

METHANE_PYROLYSIS_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=37.2,
    mode=53.1,
    maximum=79.7,
    unit="EUR/tNH3",
    description="Triangular distribution for methane pyrolysis + HB fixed OPEX in 2024 EUR.",
)

METHANE_PYROLYSIS_HB_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3.85,
    mode=5.50,
    maximum=8.25,
    unit="EUR/tNH3",
    description="Triangular distribution for methane pyrolysis + HB variable OPEX in 2024 EUR.",
)

METHANE_PYROLYSIS_HB_NATURAL_GAS_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=9.80,
    unit="MWh/tNH3",
    description="Natural-gas feedstock consumption for methane pyrolysis + HB.",
)

METHANE_PYROLYSIS_HB_NATURAL_GAS_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero natural-gas process-fuel use for methane pyrolysis + HB.",
)

METHANE_PYROLYSIS_HB_NATURAL_GAS_CONSUMPTION = FixedParameter(
    value=9.80,
    unit="MWh/tNH3",
    description="Total natural-gas consumption for methane pyrolysis + HB, used once for energy costs.",
)

METHANE_PYROLYSIS_HB_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=2.09,
    mode=2.18,
    maximum=2.27,
    unit="MWh/tNH3",
    description="Triangular distribution for methane pyrolysis + HB purchased electricity.",
)

METHANE_PYROLYSIS_HB_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tNH3",
    description="Assumed zero direct operational CO2 emissions for methane pyrolysis + HB.",
)


# SOEC+HB is a greenfield electricity-based route. Direct fuel/reductant use and
# operational CO2 emissions are modelled as zero.
SOEC_HB_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=2_024.0,
    mode=2_892.0,
    maximum=4_338.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield SOEC + HB CAPEX in 2024 EUR, not annualized.",
)

SOEC_HB_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=159.7,
    mode=228.1,
    maximum=342.2,
    unit="EUR/tNH3",
    description="Triangular distribution for SOEC + HB fixed OPEX in 2024 EUR.",
)

SOEC_HB_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=18.4,
    mode=18.4,
    maximum=23.4,
    unit="EUR/tNH3",
    description="Triangular distribution for SOEC + HB variable OPEX in 2024 EUR.",
)

SOEC_HB_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero direct fuel and reductant consumption for SOEC + HB.",
)

SOEC_HB_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=7.3,
    mode=8.25,
    maximum=8.25,
    unit="MWh/tNH3",
    description="Triangular distribution for SOEC + HB purchased electricity.",
)

SOEC_HB_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tNH3",
    description="Assumed zero direct operational CO2 emissions for SOEC + HB.",
)


# Aqueous direct NRR is a greenfield electricity-based route operating at
# ambient conditions. The source identifies the lower-bound CAPEX and fixed-OPEX
# values as the purge-case base; those values are retained as triangular modes.
# Direct fuel/reductant use and operational CO2 emissions are modelled as zero.
AQUEOUS_DIRECT_NRR_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4_767.0,
    mode=4_767.0,
    maximum=5_367.0,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for greenfield aqueous direct NRR CAPEX in 2024 EUR, not annualized.",
)

AQUEOUS_DIRECT_NRR_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=222.1,
    mode=222.1,
    maximum=244.5,
    unit="EUR/tNH3",
    description="Triangular distribution for aqueous direct NRR fixed OPEX in 2024 EUR.",
)

AQUEOUS_DIRECT_NRR_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=10.54,
    mode=19.76,
    maximum=28.98,
    unit="EUR/tNH3",
    description="Triangular distribution for aqueous direct NRR variable OPEX in 2024 EUR.",
)

AQUEOUS_DIRECT_NRR_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero direct fuel and reductant consumption for aqueous direct NRR.",
)

AQUEOUS_DIRECT_NRR_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=16.1,
    mode=18.9,
    maximum=18.9,
    unit="MWh/tNH3",
    description="Triangular distribution for aqueous direct NRR purchased electricity.",
)

AQUEOUS_DIRECT_NRR_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tNH3",
    description="Assumed zero direct operational CO2 emissions for aqueous direct NRR.",
)


# NG-SMR+HB+CCS is an incremental capture retrofit of NG-SMR+HB. Cost and energy
# changes are added to the parent, and the capture fraction reduces parent
# direct operational emissions. Electricity is an absolute increment because
# the parent has zero purchased electricity, making a percentage change
# undefined.
NG_SMR_HB_CCS_CAPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=93.9,
    mode=100.6,
    maximum=107.3,
    unit="EUR/(tNH3/y)",
    description="Triangular distribution for NG-SMR + HB CCS incremental CAPEX in 2024 EUR.",
)

NG_SMR_HB_CCS_FIXED_OPEX_CHANGE = FixedParameter(
    value=28.5,
    unit="EUR/tNH3",
    description="Fixed OPEX increase for NG-SMR + HB CCS in 2024 EUR.",
)

NG_SMR_HB_CCS_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tNH3",
    description="Assumed zero non-energy variable-OPEX change for NG-SMR + HB + CCS.",
)

NG_SMR_HB_CCS_NATURAL_GAS_CONSUMPTION_CHANGE = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero natural-gas consumption change relative to NG-SMR + HB.",
)

NG_SMR_HB_CCS_ELECTRICITY_CONSUMPTION_CHANGE = FixedParameter(
    value=0.194,
    unit="MWh/tNH3",
    description="Purchased-electricity consumption increase for NG-SMR + HB CCS.",
)

NG_SMR_HB_CCS_EMISSIONS_REDUCTION_DISTRIBUTION = TriangularDistribution(
    minimum=0.85,
    mode=0.90,
    maximum=0.90,
    unit="fraction",
    description="Triangular distribution for direct operational CO2 reduction relative to NG-SMR + HB.",
)


# Coal gasification+HB+CCS is an incremental capture retrofit of coal
# gasification+HB. The source provides best-available-technology point estimates
# for energy changes; these are added to the parent, while the capture fraction
# reduces parent direct operational emissions.
COAL_GASIFICATION_HB_CCS_CAPEX_CHANGE = FixedParameter(
    value=288.5,
    unit="EUR/(tNH3/y)",
    description="CAPEX increase for coal gasification + HB CCS in 2024 EUR.",
)

COAL_GASIFICATION_HB_CCS_FIXED_OPEX_CHANGE = FixedParameter(
    value=45.6,
    unit="EUR/tNH3",
    description="Fixed OPEX increase for coal gasification + HB CCS in 2024 EUR.",
)

COAL_GASIFICATION_HB_CCS_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tNH3",
    description="Assumed zero non-energy variable-OPEX change for coal gasification + HB + CCS.",
)

COAL_GASIFICATION_HB_CCS_COAL_CONSUMPTION_CHANGE = FixedParameter(
    value=0.0,
    unit="MWh/tNH3",
    description="Assumed zero coal-consumption change relative to coal gasification + HB.",
)

COAL_GASIFICATION_HB_CCS_ELECTRICITY_CONSUMPTION_CHANGE = FixedParameter(
    value=0.333,
    unit="MWh/tNH3",
    description="Point estimate for purchased-electricity increase relative to coal gasification + HB.",
)

COAL_GASIFICATION_HB_CCS_EMISSIONS_REDUCTION = FixedParameter(
    value=0.90,
    unit="fraction",
    description="Point estimate for direct operational CO2 reduction relative to the parent route.",
)


AMMONIA_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "annual_ammonia_output_tnh3": ANNUAL_AMMONIA_OUTPUT_TNH3,
    "lifetime_ammonia_years": LIFETIME_AMMONIA_YEARS,
    "retail_price_ammonia_eur_per_t": RETAIL_PRICE_AMMONIA_EUR_PER_T,
}

AMMONIA_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "ng_smr_hb": {
        "capex_eur_per_tnh3": NG_SMR_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": NG_SMR_HB_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tnh3": NG_SMR_HB_VARIABLE_OPEX,
        "natural_gas_consumption_mwh_per_tnh3": (
            NG_SMR_HB_NATURAL_GAS_CONSUMPTION_DISTRIBUTION
        ),
        "electricity_consumption_mwh_per_tnh3": (
            NG_SMR_HB_PURCHASED_ELECTRICITY_CONSUMPTION
        ),
        "emissions_tco2_per_tnh3": NG_SMR_HB_EMISSIONS_DISTRIBUTION,
    },
    "coal_gasification_hb": {
        "capex_eur_per_tnh3": COAL_GASIFICATION_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": COAL_GASIFICATION_HB_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tnh3": (
            COAL_GASIFICATION_HB_VARIABLE_OPEX_DISTRIBUTION
        ),
        "coal_consumption_mwh_per_tnh3": COAL_GASIFICATION_HB_COAL_CONSUMPTION,
        "electricity_consumption_mwh_per_tnh3": (
            COAL_GASIFICATION_HB_PURCHASED_ELECTRICITY_CONSUMPTION
        ),
        "emissions_tco2_per_tnh3": COAL_GASIFICATION_HB_EMISSIONS,
    },
    "ael_pem_electrolysis_hb": {
        "capex_eur_per_tnh3": AEL_PEM_ELECTROLYSIS_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": (
            AEL_PEM_ELECTROLYSIS_HB_FIXED_OPEX_DISTRIBUTION
        ),
        "variable_opex_eur_per_tnh3": (
            AEL_PEM_ELECTROLYSIS_HB_VARIABLE_OPEX_DISTRIBUTION
        ),
        "fuel_consumption_mwh_per_tnh3": (
            AEL_PEM_ELECTROLYSIS_HB_FUEL_CONSUMPTION
        ),
        "electricity_consumption_mwh_per_tnh3": (
            AEL_PEM_ELECTROLYSIS_HB_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_tnh3": AEL_PEM_ELECTROLYSIS_HB_EMISSIONS,
    },
    "biomass_gasification_hb": {
        "capex_eur_per_tnh3": BIOMASS_GASIFICATION_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": (
            BIOMASS_GASIFICATION_HB_FIXED_OPEX_DISTRIBUTION
        ),
        "variable_opex_eur_per_tnh3": (
            BIOMASS_GASIFICATION_HB_VARIABLE_OPEX_DISTRIBUTION
        ),
        "biomass_consumption_mwh_per_tnh3": (
            BIOMASS_GASIFICATION_HB_BIOMASS_CONSUMPTION
        ),
        "electricity_consumption_mwh_per_tnh3": (
            BIOMASS_GASIFICATION_HB_PURCHASED_ELECTRICITY_CONSUMPTION
        ),
        "emissions_tco2_per_tnh3": BIOMASS_GASIFICATION_HB_EMISSIONS,
    },
    "methane_pyrolysis_hb": {
        "capex_eur_per_tnh3": METHANE_PYROLYSIS_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": (
            METHANE_PYROLYSIS_HB_FIXED_OPEX_DISTRIBUTION
        ),
        "variable_opex_eur_per_tnh3": (
            METHANE_PYROLYSIS_HB_VARIABLE_OPEX_DISTRIBUTION
        ),
        "natural_gas_consumption_mwh_per_tnh3": (
            METHANE_PYROLYSIS_HB_NATURAL_GAS_CONSUMPTION
        ),
        "electricity_consumption_mwh_per_tnh3": (
            METHANE_PYROLYSIS_HB_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_tnh3": METHANE_PYROLYSIS_HB_EMISSIONS,
    },
    "soec_hb": {
        "capex_eur_per_tnh3": SOEC_HB_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": SOEC_HB_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tnh3": SOEC_HB_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_per_tnh3": SOEC_HB_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_tnh3": (
            SOEC_HB_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_tnh3": SOEC_HB_EMISSIONS,
    },
    "aqueous_direct_nrr": {
        "capex_eur_per_tnh3": AQUEOUS_DIRECT_NRR_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_tnh3": AQUEOUS_DIRECT_NRR_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_tnh3": (
            AQUEOUS_DIRECT_NRR_VARIABLE_OPEX_DISTRIBUTION
        ),
        "fuel_consumption_mwh_per_tnh3": AQUEOUS_DIRECT_NRR_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_tnh3": (
            AQUEOUS_DIRECT_NRR_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_tnh3": AQUEOUS_DIRECT_NRR_EMISSIONS,
    },
}

AMMONIA_RETROFIT_BASE_TECHNOLOGIES: Mapping[str, str] = {
    "ng_smr_hb_ccs": "ng_smr_hb",
    "coal_gasification_hb_ccs": "coal_gasification_hb",
}

AMMONIA_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "ng_smr_hb_ccs": {
        "capex_change_eur_per_tnh3": NG_SMR_HB_CCS_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_tnh3": NG_SMR_HB_CCS_FIXED_OPEX_CHANGE,
        "variable_opex_change_eur_per_tnh3": NG_SMR_HB_CCS_VARIABLE_OPEX_CHANGE,
        "natural_gas_consumption_change_mwh_per_tnh3": (
            NG_SMR_HB_CCS_NATURAL_GAS_CONSUMPTION_CHANGE
        ),
        "electricity_consumption_change_mwh_per_tnh3": (
            NG_SMR_HB_CCS_ELECTRICITY_CONSUMPTION_CHANGE
        ),
        "emissions_reduction_fraction": (
            NG_SMR_HB_CCS_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "coal_gasification_hb_ccs": {
        "capex_change_eur_per_tnh3": COAL_GASIFICATION_HB_CCS_CAPEX_CHANGE,
        "fixed_opex_change_eur_per_tnh3": (
            COAL_GASIFICATION_HB_CCS_FIXED_OPEX_CHANGE
        ),
        "variable_opex_change_eur_per_tnh3": (
            COAL_GASIFICATION_HB_CCS_VARIABLE_OPEX_CHANGE
        ),
        "coal_consumption_change_mwh_per_tnh3": (
            COAL_GASIFICATION_HB_CCS_COAL_CONSUMPTION_CHANGE
        ),
        "electricity_consumption_change_mwh_per_tnh3": (
            COAL_GASIFICATION_HB_CCS_ELECTRICITY_CONSUMPTION_CHANGE
        ),
        "emissions_reduction_fraction": (
            COAL_GASIFICATION_HB_CCS_EMISSIONS_REDUCTION
        ),
    },
}
