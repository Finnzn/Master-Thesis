"""Hydrogen-sector assumptions for future technology comparisons."""

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

RETAIL_PRICE_HYDROGEN_EUR_PER_T = FixedParameter(
    value=3_000.0,
    unit="EUR/t",
    description="Retail price of hydrogen used in the hydrogen-sector setup.",
)


# Greenfield European natural-gas steam-methane reforming (NG-SMR), without
# carbon capture. Supplied base values are used as triangular modes. Natural
# gas includes feedstock and process fuel; only the total enters the technology
# registry to avoid double counting. Approximate emissions of 9,000 kgCO2/tH2
# are stored as 9 tCO2/tH2 to match the carbon-price unit of EUR/tCO2.
NG_SMR_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=1_840.0,
    mode=2_165.0,
    maximum=2_920.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for greenfield European NG-SMR CAPEX, not annualized.",
)

NG_SMR_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=81.0,
    mode=96.0,
    maximum=129.0,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR fixed OPEX.",
)

NG_SMR_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=5.6,
    mode=6.6,
    maximum=8.9,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR variable OPEX.",
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
    description="Approximate net purchased electricity for NG-SMR at 200 bar.",
)

NG_SMR_EMISSIONS = FixedParameter(
    value=9.0,
    unit="tCO2/tH2",
    description="Approximate direct NG-SMR emissions; supplied as 9,000 kgCO2/tH2.",
)


# Greenfield European alkaline electrolysis (AEL) for 2030. Supplied base
# values are used as triangular modes; electricity use is specified at 200 bar.
AEL_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=5_590.0,
    mode=7_991.0,
    maximum=11_990.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European AEL CAPEX, not annualized.",
)

AEL_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=161.0,
    mode=230.0,
    maximum=345.0,
    unit="EUR/tH2",
    description="Triangular distribution for AEL fixed OPEX.",
)

AEL_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=25.0,
    mode=36.0,
    maximum=54.0,
    unit="EUR/tH2",
    description="Triangular distribution for AEL variable OPEX.",
)

AEL_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Fuel and reductant consumption for AEL.",
)

AEL_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=51.54,
    unit="MWh/tH2",
    description="Purchased electricity for AEL hydrogen production at 200 bar.",
)

AEL_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Direct emissions for AEL hydrogen production.",
)


# Greenfield European proton-exchange-membrane electrolysis (PEM) for 2030.
# Supplied base values are triangular modes; electricity use is at 200 bar.
PEM_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=7_190.0,
    mode=10_274.0,
    maximum=15_410.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European PEM CAPEX, not annualized.",
)

PEM_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=255.0,
    mode=364.0,
    maximum=546.0,
    unit="EUR/tH2",
    description="Triangular distribution for PEM fixed OPEX.",
)

PEM_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=25.0,
    mode=36.0,
    maximum=54.0,
    unit="EUR/tH2",
    description="Triangular distribution for PEM variable OPEX.",
)

PEM_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Fuel and reductant consumption for PEM.",
)

PEM_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=50.88,
    unit="MWh/tH2",
    description="Purchased electricity for PEM hydrogen production at 200 bar.",
)

PEM_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Direct emissions for PEM hydrogen production.",
)


# Greenfield European solid-oxide electrolysis cell (SOEC) for 2030, with
# electric process heat. Supplied base values are used as triangular modes.
SOEC_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_840.0,
    mode=5_490.0,
    maximum=8_240.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for 2030 greenfield European SOEC CAPEX with electric heat, not annualized.",
)

SOEC_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=181.0,
    mode=258.0,
    maximum=387.0,
    unit="EUR/tH2",
    description="Triangular distribution for SOEC fixed OPEX.",
)

SOEC_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=80.0,
    mode=80.0,
    maximum=85.0,
    unit="EUR/tH2",
    description="Triangular distribution for SOEC variable OPEX.",
)

SOEC_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh/tH2",
    description="Fuel and reductant consumption for SOEC with electric heat.",
)

SOEC_PURCHASED_ELECTRICITY_CONSUMPTION = FixedParameter(
    value=42.2,
    unit="MWh/tH2",
    description="Purchased electricity for SOEC hydrogen production with electric heat.",
)

SOEC_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Direct emissions for SOEC hydrogen production.",
)


# Greenfield European methane pyrolysis (TCD). The supplied 61.1 MWh/tH2
# natural-gas consumption is feedstock; only that amount enters the technology
# registry. Supplied base values are used as triangular modes.
METHANE_PYROLYSIS_TCD_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3_690.0,
    mode=5_270.0,
    maximum=7_910.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for greenfield European methane pyrolysis (TCD) CAPEX, not annualized.",
)

METHANE_PYROLYSIS_TCD_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=62.0,
    mode=89.0,
    maximum=134.0,
    unit="EUR/tH2",
    description="Triangular distribution for methane pyrolysis (TCD) fixed OPEX.",
)

METHANE_PYROLYSIS_TCD_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.9,
    mode=7.0,
    maximum=10.5,
    unit="EUR/tH2",
    description="Triangular distribution for methane pyrolysis (TCD) variable OPEX.",
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
    description="Direct emissions for methane pyrolysis (TCD).",
)


# Greenfield conceptual biomass gasification without carbon capture. Supplied
# base values are used as triangular modes, including those at lower bounds.
BIOMASS_GASIFICATION_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=950.0,
    mode=950.0,
    maximum=1_950.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for greenfield conceptual biomass gasification CAPEX without CCS, not annualized.",
)

BIOMASS_GASIFICATION_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=58.0,
    mode=58.0,
    maximum=95.0,
    unit="EUR/tH2",
    description="Triangular distribution for biomass gasification fixed OPEX.",
)

BIOMASS_GASIFICATION_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=768.0,
    mode=768.0,
    maximum=828.0,
    unit="EUR/tH2",
    description="Triangular distribution for biomass gasification variable OPEX.",
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
    description="Direct emissions for biomass gasification without CCS.",
)


# Biomethane SMR is a fuel-switch retrofit of NG-SMR without CCS. CAPEX and
# OPEX changes are zero; the parent natural-gas input is replaced by the same
# total quantity of biomethane. Direct emissions are the supplied absolute zero
# rather than an additive change to the parent emissions.
BIOMETHANE_SMR_CAPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/(tH2/y)",
    description="CAPEX increase for biomethane SMR relative to NG-SMR.",
)

BIOMETHANE_SMR_FIXED_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Fixed OPEX increase for biomethane SMR relative to NG-SMR.",
)

BIOMETHANE_SMR_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Variable OPEX increase for biomethane SMR relative to NG-SMR.",
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
    description="No change to approximately zero net NG-SMR purchased electricity at 200 bar.",
)

BIOMETHANE_SMR_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/tH2",
    description="Supplied absolute direct emissions for biomethane SMR without CCS.",
)


# European NG-SMR + CCS retrofit relative to NG-SMR. Cost and energy changes
# are additive; supplied 90% capture reduces the parent's direct emissions.
# Only the natural-gas increment enters the retrofit registry, not the total.
NG_SMR_CCS_CAPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=1_610.0,
    mode=1_706.0,
    maximum=1_900.0,
    unit="EUR/(tH2/y)",
    description="Triangular distribution for European NG-SMR + CCS incremental CAPEX.",
)

NG_SMR_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=27.0,
    mode=51.0,
    maximum=72.0,
    unit="EUR/tH2",
    description="Triangular distribution for NG-SMR + CCS fixed OPEX increase.",
)

NG_SMR_CCS_VARIABLE_OPEX_CHANGE = FixedParameter(
    value=0.0,
    unit="EUR/tH2",
    description="Variable OPEX increase for NG-SMR + CCS.",
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
    description="CO2 capture fraction for NG-SMR + CCS, applied to parent direct emissions.",
)


HYDROGEN_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "annual_hydrogen_output_th2": ANNUAL_HYDROGEN_OUTPUT_TH2,
    "lifetime_hydrogen_years": LIFETIME_HYDROGEN_YEARS,
    "retail_price_hydrogen_eur_per_t": RETAIL_PRICE_HYDROGEN_EUR_PER_T,
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
