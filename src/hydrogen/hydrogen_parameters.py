"""Hydrogen-sector assumptions used by the deterministic and Monte Carlo models.

Technology CAPEX and OPEX use the supplied 2024 values; methane-pyrolysis TCD
costs remain at their supplied values as specified. The 2030 labels on the
electrolysis routes describe the technology case, while 2024 EUR describes the
monetary basis.

Absolute technologies define complete hydrogen-production routes. Biomethane
SMR and NG-SMR+CCS define changes relative to NG-SMR. Emissions parameters use
the model's direct operational accounting boundary; zero values do not imply
zero upstream, life-cycle, or necessarily physical biogenic stack emissions.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution


ANNUAL_HYDROGEN_OUTPUT_TH2 = FixedParameter(
    value=100_000.0,
    unit="tH2/year",
    description="Common annual hydrogen output for all compared technologies.",
)

LIFETIME_HYDROGEN_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of hydrogen-sector assets.",
)

ELECTROLYSIS_HYDROGEN_RETAIL_PRICE_EUR_PER_T = FixedParameter(
    value=7_500.0,
    unit="EUR/tH2",
    description="Fixed hydrogen sales price for AEL, PEM, and SOEC routes.",
)

NON_ELECTROLYSIS_HYDROGEN_RETAIL_PRICE_EUR_PER_T = FixedParameter(
    value=2_800.0,
    unit="EUR/tH2",
    description="Fixed hydrogen sales price for non-electrolysis routes.",
)

ELECTROLYSIS_HYDROGEN_TECHNOLOGIES = frozenset({"ael", "pem", "soec"})


# NG-SMR is the greenfield European natural-gas reference route without capture.
# Feedstock and process-fuel components are documented separately, while their
# total is registered once to avoid double counting energy costs. Source
# emissions reported in kgCO2/tH2 are stored as tCO2/tH2 for carbon pricing.
NG_SMR_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=2_555.0,
    mode=3_006.0,
    maximum=4_059.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for greenfield European NG-SMR CAPEX in 2024 EUR, not annualized.",
)

NG_SMR_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=113.1,
    mode=133.0,
    maximum=179.6,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR fixed OPEX in 2024 EUR.",
)

NG_SMR_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=7.78,
    mode=9.15,
    maximum=12.35,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR variable OPEX in 2024 EUR.",
)

NG_SMR_NATURAL_GAS_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=37.67,
    unit="MWh/tH2",
    description="Natural-gas feedstock component of NG-SMR consumption.",
)

NG_SMR_NATURAL_GAS_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=6.22,
    unit="MWh/tH2",
    description="Natural-gas process-fuel component of NG-SMR consumption.",
)

NG_SMR_NATURAL_GAS_CONSUMPTION = FixedParameter(
    value=43.89,
    unit="MWh/tH2",
    description="Total NG-SMR natural-gas consumption, including feedstock and process fuel.",
)

NG_SMR_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Assumed zero net purchased electricity for NG-SMR at 200 bar.",
)

NG_SMR_EMISSIONS = FixedParameter(
    value=9.0,
    unit="tCO2/tH2",
    description="Approximate NG-SMR direct operational CO2 emissions.",
)


# AEL is a greenfield European 2030 electrolysis case. Direct fuel use and
# operational CO2 emissions are modelled as zero; purchased electricity is
# specified for hydrogen delivered at 200 bar.
AEL_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=7_506.0,
    mode=10_723.0,
    maximum=16_084.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European AEL CAPEX in 2024 EUR, not annualized.",
)

AEL_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=216.0,
    mode=308.6,
    maximum=462.9,
    unit="EUR/tH2",
    description="Triangular distribution for AEL fixed OPEX in 2024 EUR.",
)

AEL_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=33.81,
    mode=48.31,
    maximum=72.46,
    unit="EUR/tH2",
    description="Triangular distribution for AEL variable OPEX in 2024 EUR.",
)

AEL_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Assumed zero direct fuel and reductant consumption for AEL.",
)

AEL_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=51.54,
    unit="MWh/tH2",
    description="Purchased electricity for AEL hydrogen production at 200 bar.",
)

AEL_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero direct operational CO2 emissions for AEL.",
)


# PEM is a greenfield European 2030 electrolysis case. Direct fuel use and
# operational CO2 emissions are modelled as zero; purchased electricity is
# specified for hydrogen delivered at 200 bar.
PEM_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=9_650.0,
    mode=13_786.0,
    maximum=20_679.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European PEM CAPEX in 2024 EUR, not annualized.",
)

PEM_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=341.9,
    mode=488.4,
    maximum=732.6,
    unit="EUR/tH2",
    description="Triangular distribution for PEM fixed OPEX in 2024 EUR.",
)

PEM_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=33.81,
    mode=48.31,
    maximum=72.46,
    unit="EUR/tH2",
    description="Triangular distribution for PEM variable OPEX in 2024 EUR.",
)

PEM_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Assumed zero direct fuel and reductant consumption for PEM.",
)

PEM_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=50.88,
    unit="MWh/tH2",
    description="Purchased electricity for PEM hydrogen production at 200 bar.",
)

PEM_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero direct operational CO2 emissions for PEM.",
)


# SOEC is a greenfield European 2030 electrolysis case with electric process
# heat. Direct fuel use and operational CO2 emissions are modelled as zero;
# purchased electricity includes the electric-heat requirement.
SOEC_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_768.0,
    mode=5_382.0,
    maximum=8_074.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European SOEC CAPEX with electric heat in 2024 EUR, not annualized.",
)

SOEC_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=177.1,
    mode=252.9,
    maximum=379.4,
    unit="EUR/tH2",
    description="Triangular distribution for SOEC fixed OPEX in 2024 EUR.",
)

SOEC_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=80.21,
    mode=80.21,
    maximum=83.33,
    unit="EUR/tH2",
    description="Triangular distribution for SOEC variable OPEX in 2024 EUR.",
)

SOEC_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Assumed zero direct fuel and reductant consumption for SOEC.",
)

SOEC_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=42.2,
    unit="MWh/tH2",
    description="Purchased electricity for SOEC hydrogen production with electric heat.",
)

SOEC_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero direct operational CO2 emissions for SOEC.",
)


# TCD is a greenfield European methane-pyrolysis route. Natural gas is modelled
# as feedstock rather than process fuel. Its monetary inputs remain unchanged
# from the supplied values, while purchased-electricity uncertainty is explicit.
METHANE_PYROLYSIS_TCD_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_690.0,
    mode=5_270.0,
    maximum=7_910.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for TCD CAPEX retained at supplied values, not annualized.",
)

METHANE_PYROLYSIS_TCD_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=62.0,
    mode=89.0,
    maximum=134.0,
    unit="EUR/tH2",
    description="Triangular distribution for TCD fixed OPEX retained at supplied values.",
)

METHANE_PYROLYSIS_TCD_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.9,
    mode=7.0,
    maximum=10.5,
    unit="EUR/tH2",
    description="Triangular distribution for TCD variable OPEX retained at supplied values.",
)

METHANE_PYROLYSIS_TCD_NATURAL_GAS_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=61.1,
    unit="MWh/tH2",
    description="Natural-gas feedstock consumption for methane pyrolysis (TCD).",
)

METHANE_PYROLYSIS_TCD_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=10.0,
    mode=10.0,
    maximum=14.2,
    unit="MWh/tH2",
    description="Triangular distribution for methane pyrolysis (TCD) purchased electricity.",
)

METHANE_PYROLYSIS_TCD_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero direct operational CO2 emissions for TCD.",
)


# Biomass gasification is a conceptual greenfield route without capture. Base
# values at lower bounds are retained as triangular modes. Its zero direct-
# emissions input follows the model's biogenic-carbon accounting boundary.
BIOMASS_GASIFICATION_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=949.0,
    mode=949.0,
    maximum=1_954.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for greenfield conceptual biomass gasification CAPEX without CCS in 2024 EUR, not annualized.",
)

BIOMASS_GASIFICATION_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=57.8,
    mode=57.8,
    maximum=94.9,
    unit="EUR/tH2",
    description="Triangular distribution for biomass gasification fixed OPEX in 2024 EUR.",
)

BIOMASS_GASIFICATION_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=767.8,
    mode=767.8,
    maximum=828.4,
    unit="EUR/tH2",
    description="Triangular distribution for biomass gasification variable OPEX in 2024 EUR.",
)

BIOMASS_GASIFICATION_BIOMASS_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=33.3,
    mode=33.3,
    maximum=50.0,
    unit="MWh/tH2",
    description="Triangular distribution for biomass gasification biomass consumption.",
)

BIOMASS_GASIFICATION_PURCHASED_ELECTRICITY_DISTRIBUTION = TriangularDistribution(
    minimum=0.47,
    mode=0.47,
    maximum=2.26,
    unit="MWh/tH2",
    description="Triangular distribution for biomass gasification purchased electricity.",
)

BIOMASS_GASIFICATION_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero fossil direct CO2 emissions for biomass gasification.",
)


# Biomethane SMR is a fuel-switch retrofit of NG-SMR. It inherits parent CAPEX
# and OPEX, replaces the full natural-gas input with biomethane, and uses the
# source-provided zero fossil-emissions value. That value reflects the model's
# accounting boundary and does not imply zero physical biogenic stack CO2.
BIOMETHANE_SMR_CAPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/(tH2/y)",
    description="Assumed zero incremental CAPEX for biomethane SMR relative to NG-SMR.",
)

BIOMETHANE_SMR_FIXED_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Assumed zero incremental fixed OPEX for biomethane SMR.",
)

BIOMETHANE_SMR_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Assumed zero incremental variable OPEX for biomethane SMR.",
)

BIOMETHANE_SMR_NATURAL_GAS_CONSUMPTION_CHANGE = FixedParameter(
    value=-43.89,
    unit="MWh/tH2",
    description="Removal of the parent NG-SMR natural-gas input when switching to biomethane.",
)

BIOMETHANE_SMR_BIOMETHANE_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=37.67,
    unit="MWh/tH2",
    description="Biomethane feedstock component of biomethane SMR consumption.",
)

BIOMETHANE_SMR_BIOMETHANE_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=6.22,
    unit="MWh/tH2",
    description="Biomethane process-fuel component of biomethane SMR consumption.",
)

BIOMETHANE_SMR_BIOMETHANE_CONSUMPTION = FixedParameter(
    value=43.89,
    unit="MWh/tH2",
    description="Total biomethane consumption for biomethane SMR, including feedstock and process fuel.",
)

BIOMETHANE_SMR_ELECTRICITY_CONSUMPTION_CHANGE = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Assumed zero purchased-electricity change relative to NG-SMR.",
)

BIOMETHANE_SMR_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Assumed zero fossil direct CO2 emissions for biomethane SMR.",
)


# NG-SMR+CCS is an incremental capture retrofit of NG-SMR. Cost and energy
# changes are added to the parent, and the capture fraction reduces parent
# direct operational emissions. Only the natural-gas increment is registered
# for the retrofit; documented feedstock, process-fuel, and total values are
# traceability aids rather than additional cost inputs.
NG_SMR_CCS_CAPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=2_310.0,
    mode=2_369.0,
    maximum=2_637.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for European NG-SMR + CCS incremental CAPEX in 2024 EUR.",
)

NG_SMR_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=39.3,
    mode=70.8,
    maximum=100.2,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR + CCS fixed OPEX increase in 2024 EUR.",
)

NG_SMR_CCS_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Assumed zero non-energy variable-OPEX change for NG-SMR + CCS.",
)

NG_SMR_CCS_NATURAL_GAS_FEEDSTOCK_CONSUMPTION = FixedParameter(
    value=37.67,
    unit="MWh/tH2",
    description="Natural-gas feedstock component of NG-SMR + CCS consumption.",
)

NG_SMR_CCS_NATURAL_GAS_PROCESS_FUEL_CONSUMPTION = FixedParameter(
    value=10.55,
    unit="MWh/tH2",
    description="Natural-gas process-fuel component of NG-SMR + CCS consumption.",
)

NG_SMR_CCS_NATURAL_GAS_CONSUMPTION = FixedParameter(
    value=48.22,
    unit="MWh/tH2",
    description="Total NG-SMR + CCS natural-gas consumption, including feedstock and process fuel.",
)

NG_SMR_CCS_NATURAL_GAS_CONSUMPTION_CHANGE = FixedParameter(
    value=4.33,
    unit="MWh/tH2",
    description="Natural-gas increase for NG-SMR + CCS relative to 43.89 MWh/tH2 NG-SMR.",
)

NG_SMR_CCS_ELECTRICITY_CONSUMPTION_CHANGE = FixedParameter(
    value=1.05,
    unit="MWh/tH2",
    description="Approximate net purchased-electricity increase for NG-SMR + CCS at 200 bar.",
)

NG_SMR_CCS_CAPTURE_FRACTION = FixedParameter(
    value=0.90,
    unit="fraction",
    description="Direct operational CO2 capture fraction applied to parent NG-SMR emissions.",
)


HYDROGEN_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "annual_hydrogen_output_th2": ANNUAL_HYDROGEN_OUTPUT_TH2,
    "lifetime_hydrogen_years": LIFETIME_HYDROGEN_YEARS,
    "electrolysis_hydrogen_retail_price_eur_per_t": (
        ELECTROLYSIS_HYDROGEN_RETAIL_PRICE_EUR_PER_T
    ),
    "non_electrolysis_hydrogen_retail_price_eur_per_t": (
        NON_ELECTROLYSIS_HYDROGEN_RETAIL_PRICE_EUR_PER_T
    ),
}

HYDROGEN_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution],
] = {
    "ng_smr": {
        "capex_eur_per_th2": NG_SMR_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": NG_SMR_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": NG_SMR_VARIABLE_OPEX_DISTRIBUTION,
        "natural_gas_consumption_mwh_per_th2": NG_SMR_NATURAL_GAS_CONSUMPTION,
        "electricity_consumption_mwh_per_th2": NG_SMR_PURCHASED_ELECTRICITY_CONSUMPTION,
        "emissions_tco2_per_th2": NG_SMR_EMISSIONS,
    },
    "ael": {
        "capex_eur_per_th2": AEL_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": AEL_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": AEL_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_per_th2": AEL_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_th2": AEL_PURCHASED_ELECTRICITY_CONSUMPTION,
        "emissions_tco2_per_th2": AEL_EMISSIONS,
    },
    "pem": {
        "capex_eur_per_th2": PEM_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": PEM_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": PEM_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_per_th2": PEM_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_th2": PEM_PURCHASED_ELECTRICITY_CONSUMPTION,
        "emissions_tco2_per_th2": PEM_EMISSIONS,
    },
    "soec": {
        "capex_eur_per_th2": SOEC_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": SOEC_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": SOEC_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_per_th2": SOEC_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_th2": SOEC_PURCHASED_ELECTRICITY_CONSUMPTION,
        "emissions_tco2_per_th2": SOEC_EMISSIONS,
    },
    "methane_pyrolysis_tcd": {
        "capex_eur_per_th2": METHANE_PYROLYSIS_TCD_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": METHANE_PYROLYSIS_TCD_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": METHANE_PYROLYSIS_TCD_VARIABLE_OPEX_DISTRIBUTION,
        "natural_gas_consumption_mwh_per_th2": (
            METHANE_PYROLYSIS_TCD_NATURAL_GAS_FEEDSTOCK_CONSUMPTION
        ),
        "electricity_consumption_mwh_per_th2": (
            METHANE_PYROLYSIS_TCD_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_th2": METHANE_PYROLYSIS_TCD_EMISSIONS,
    },
    "biomass_gasification": {
        "capex_eur_per_th2": BIOMASS_GASIFICATION_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_th2": BIOMASS_GASIFICATION_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_th2": (
            BIOMASS_GASIFICATION_VARIABLE_OPEX_DISTRIBUTION
        ),
        "biomass_consumption_mwh_per_th2": (
            BIOMASS_GASIFICATION_BIOMASS_CONSUMPTION_DISTRIBUTION
        ),
        "electricity_consumption_mwh_per_th2": (
            BIOMASS_GASIFICATION_PURCHASED_ELECTRICITY_DISTRIBUTION
        ),
        "emissions_tco2_per_th2": BIOMASS_GASIFICATION_EMISSIONS,
    },
}

HYDROGEN_RETROFIT_BASE_TECHNOLOGIES: Mapping[str, str] = {
    "biomethane_smr": "ng_smr",
    "ng_smr_ccs": "ng_smr",
}

HYDROGEN_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution],
] = {
    "biomethane_smr": {
        "capex_change_eur_per_th2": BIOMETHANE_SMR_CAPEX_CHANGE,
        "fixed_opex_change_eur_per_th2": BIOMETHANE_SMR_FIXED_OPEX_CHANGE,
        "variable_opex_change_eur_per_th2": BIOMETHANE_SMR_VARIABLE_OPEX_CHANGE,
        "natural_gas_consumption_change_mwh_per_th2": (
            BIOMETHANE_SMR_NATURAL_GAS_CONSUMPTION_CHANGE
        ),
        "biomethane_consumption_mwh_per_th2": BIOMETHANE_SMR_BIOMETHANE_CONSUMPTION,
        "electricity_consumption_change_mwh_per_th2": (
            BIOMETHANE_SMR_ELECTRICITY_CONSUMPTION_CHANGE
        ),
        "emissions_tco2_per_th2": BIOMETHANE_SMR_EMISSIONS,
    },
    "ng_smr_ccs": {
        "capex_change_eur_per_th2": NG_SMR_CCS_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_th2": (
            NG_SMR_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_th2": NG_SMR_CCS_VARIABLE_OPEX_CHANGE,
        "natural_gas_consumption_change_mwh_per_th2": (
            NG_SMR_CCS_NATURAL_GAS_CONSUMPTION_CHANGE
        ),
        "electricity_consumption_change_mwh_per_th2": (
            NG_SMR_CCS_ELECTRICITY_CONSUMPTION_CHANGE
        ),
        "capture_fraction": NG_SMR_CCS_CAPTURE_FRACTION,
    },
}
