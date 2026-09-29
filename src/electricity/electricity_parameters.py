"""Electricity-sector assumptions used by the deterministic and Monte Carlo models.

This file is the electricity assumptions catalogue. It does not perform NPV
calculations; it only records input values and uncertainty ranges for each
technology. The calculation modules import these objects so the modelling logic
stays separate from the numerical assumptions.

The technologies are compared on a normalized annual output of 1,000,000 MWh.
Full-load hours then determine how much installed capacity each technology needs
to produce that same annual output.

The BECCS and CCS cost assumptions identified below are expressed in 2024 EUR
after CEPCI normalization. Where the normalized table supplies only new bounds,
the triangular mode retains its original relative position within the range.

Emissions parameters represent direct operational fossil CO2 unless explicitly
identified as a net-emissions accounting value. Zero direct emissions do not
imply zero life-cycle emissions. For CCS retrofit reduction fractions, positive
values reduce the parent intensity and negative values increase it.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


# Fixed electricity sales price used to calculate annual revenue.
RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH = FixedParameter(
    value=94.07,
    unit="EUR/MWh",
    description="Fixed electricity sales price used by the financial model.",
)

# Renewable value factors scale the common electricity price to the average
# price captured by each variable renewable technology. Their supplied
# minimum/base/maximum assumptions are modelled as triangular distributions;
# deterministic calculations use the triangular expected value.
VF_PV = TriangularDistribution(
    minimum=0.80,
    mode=0.90,
    maximum=1.00,
    unit="dimensionless",
    description="Triangular value-factor distribution for PV electricity sales revenue.",
)

VF_Wind_onshore = TriangularDistribution(
    minimum=0.80,
    mode=0.90,
    maximum=1.00,
    unit="dimensionless",
    description="Triangular value-factor distribution for onshore-wind electricity sales revenue.",
)

VF_windoffshore = TriangularDistribution(
    minimum=0.85,
    mode=0.95,
    maximum=1.00,
    unit="dimensionless",
    description="Triangular value-factor distribution for offshore-wind electricity sales revenue.",
)

# Normalized annual output: every technology is sized to produce this amount so
# the NPV comparison is not driven by different plant sizes.
ANNUAL_ELECTRICITY_OUTPUT_MWH = FixedParameter(
    value=1_000_000.0,
    unit="MWh/year",
    description="Annual electricity output target used to normalize electricity technologies.",
)

# Hard coal is an absolute generation route with fossil-fuel use and direct
# operational CO2 emissions; both fuel and carbon costs enter its cash flow.
HARD_COAL_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1_700.0,
    upper_bound=2_300.0,
    unit="EUR/kW",
    description="Uniform distribution for hard coal CAPEX, not annualized.",
)

HARD_COAL_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=29.6,
    mode=37.0,
    maximum=48.1,
    unit="EUR/kW/year",
    description="Triangular distribution for hard coal fixed OPEX.",
)

HARD_COAL_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.0,
    mode=5.0,
    maximum=6.5,
    unit="EUR/MWh_e",
    description="Triangular distribution for hard coal variable OPEX excluding fuel and electricity.",
)

HARD_COAL_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=2.44,
    mode=2.56,
    maximum=2.70,
    unit="MWh_th/MWh_e",
    description="Triangular distribution for hard coal fuel consumption.",
)

HARD_COAL_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.83,
    mode=0.87,
    maximum=0.92,
    unit="tCO2/MWh_e",
    description="Triangular distribution for hard-coal direct operational CO2 emissions.",
)

HARD_COAL_FULL_LOAD_HOURS = FixedParameter(
    value=4_100.0,
    unit="h/year",
    description="Full-load hours for the hard coal technology.",
)

HARD_COAL_LIFETIME_YEARS = FixedParameter(
    value=30.0,
    unit="years",
    description="Economic lifetime for the hard coal technology.",
)


# Hard coal with CCS is represented as a retrofit of the hard-coal parent.
# Incremental costs are added to the parent, the fuel penalty increases parent
# fuel use, and the capture fraction reduces parent direct operational emissions.
HARD_COAL_CCS_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=1_752.0,
    upper_bound=3_755.0,
    unit="EUR/kW",
    description="Uniform distribution for hard coal CCS retrofit CAPEX increase in 2024 EUR, not annualized.",
)

HARD_COAL_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=42.0,
    mode=60.0,
    maximum=90.0,
    unit="EUR/kW/year",
    description="Triangular distribution for hard coal CCS retrofit fixed OPEX increase in 2024 EUR.",
)

HARD_COAL_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=5.32,
    mode=7.61,
    maximum=11.40,
    unit="EUR/MWh_e",
    description="Triangular distribution for hard coal CCS retrofit variable OPEX increase in 2024 EUR excluding fuel and electricity.",
)

HARD_COAL_CCS_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-0.33,
    upper_bound=-0.14,
    unit="fraction",
    description="Uniform distribution for hard coal CCS fuel-consumption reduction relative to BAU; negative values represent increases.",
)

HARD_COAL_CCS_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.87,
    upper_bound=0.99,
    unit="fraction",
    description="Uniform distribution for direct operational CO2 reduction relative to hard coal.",
)


# CCGT is an absolute natural-gas generation route. Natural-gas price
# uncertainty is applied separately by the financial model.
CCGT_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=900.0,
    upper_bound=1_300.0,
    unit="EUR/kW",
    description="Uniform distribution for CCGT CAPEX, not annualized.",
)

CCGT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=16.0,
    mode=20.0,
    maximum=26.0,
    unit="EUR/kW/year",
    description="Triangular distribution for CCGT fixed OPEX.",
)

CCGT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.0,
    mode=5.0,
    maximum=6.5,
    unit="EUR/MWh_e",
    description="Triangular distribution for CCGT variable OPEX excluding fuel and electricity.",
)

CCGT_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=1.61,
    mode=1.66,
    maximum=1.72,
    unit="MWh_th/MWh_e",
    description="Triangular distribution for CCGT fuel consumption.",
)

CCGT_EMISSIONS_DISTRIBUTION = TriangularDistribution(
    minimum=0.326,
    mode=0.337,
    maximum=0.348,
    unit="tCO2/MWh_e",
    description="Triangular distribution for CCGT direct operational CO2 emissions.",
)

CCGT_FULL_LOAD_HOURS = FixedParameter(
    value=4_650.0,
    unit="h/year",
    description="Average full-load hours for the CCGT technology.",
)

CCGT_LIFETIME_YEARS = FixedParameter(
    value=30.0,
    unit="years",
    description="Economic lifetime for the CCGT technology.",
)


# CCGT with CCS is represented as a retrofit of the CCGT parent. Incremental
# costs and the fuel penalty are added to the parent, while the capture fraction
# reduces parent direct operational emissions.
CCGT_CCS_CAPEX_CHANGE_DISTRIBUTION = UniformDistribution(
    lower_bound=778.0,
    upper_bound=1_667.0,
    unit="EUR/kW",
    description="Uniform distribution for CCGT CCS retrofit CAPEX increase in 2024 EUR, not annualized.",
)

CCGT_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=21.16,
    mode=30.20,
    maximum=45.35,
    unit="EUR/kW/year",
    description="Triangular distribution for CCGT CCS retrofit fixed OPEX increase in 2024 EUR.",
)

CCGT_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION = TriangularDistribution(
    minimum=0.677,
    mode=0.965,
    maximum=1.450,
    unit="EUR/MWh_e",
    description="Triangular distribution for CCGT CCS retrofit variable OPEX increase in 2024 EUR excluding fuel and electricity.",
)

CCGT_CCS_FUEL_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=-0.20,
    upper_bound=-0.10,
    unit="fraction",
    description="Uniform distribution for CCGT CCS fuel-consumption reduction relative to BAU; negative values represent increases.",
)

CCGT_CCS_EMISSIONS_REDUCTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.88,
    upper_bound=0.98,
    unit="fraction",
    description="Uniform distribution for direct operational CO2 reduction relative to CCGT.",
)


# Nuclear has zero direct operational CO2 emissions within the model boundary;
# upstream fuel-cycle and construction emissions are excluded.
NUCLEAR_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=6_000.0,
    upper_bound=16_000.0,
    unit="EUR/kW",
    description="Uniform distribution for nuclear CAPEX, not annualized.",
)

NUCLEAR_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=80.0,
    mode=100.0,
    maximum=130.0,
    unit="EUR/kW/year",
    description="Triangular distribution for nuclear fixed OPEX.",
)

NUCLEAR_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=5.6,
    mode=7.0,
    maximum=9.1,
    unit="EUR/MWh_e",
    description="Triangular distribution for nuclear variable OPEX excluding fuel and electricity.",
)

NUCLEAR_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=2.70,
    mode=2.85,
    maximum=3.03,
    unit="MWh_th/MWh_e",
    description="Triangular distribution for nuclear fuel consumption.",
)

NUCLEAR_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Assumed zero direct operational CO2 emissions for nuclear generation.",
)

NUCLEAR_FULL_LOAD_HOURS = FixedParameter(
    value=7_900.0,
    unit="h/year",
    description="Average full-load hours for the nuclear technology.",
)

NUCLEAR_LIFETIME_YEARS = FixedParameter(
    value=45.0,
    unit="years",
    description="Economic lifetime for the nuclear technology.",
)


# Offshore wind has zero direct fuel use and operational CO2 emissions within
# the model boundary. Its uncertainty is concentrated in CAPEX, OPEX, and
# full-load hours.
WIND_OFFSHORE_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=2_200.0,
    upper_bound=3_400.0,
    unit="EUR/kW",
    description="Uniform distribution for offshore wind CAPEX, not annualized.",
)

WIND_OFFSHORE_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=31.2,
    mode=39.0,
    maximum=50.7,
    unit="EUR/kW/year",
    description="Triangular distribution for offshore wind fixed OPEX.",
)

WIND_OFFSHORE_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=6.4,
    mode=8.0,
    maximum=10.4,
    unit="EUR/MWh_e",
    description="Triangular distribution for offshore wind variable OPEX excluding fuel and electricity.",
)

WIND_OFFSHORE_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/MWh_e",
    description="Assumed zero direct fuel consumption for offshore-wind generation.",
)

WIND_OFFSHORE_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Assumed zero direct operational CO2 emissions for offshore wind.",
)

WIND_OFFSHORE_FULL_LOAD_HOURS = FixedParameter(
    value=3_850.0,
    unit="h/year",
    description="Average full-load hours for the offshore wind technology.",
)

WIND_OFFSHORE_LIFETIME_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime for the offshore wind technology.",
)


# Onshore wind has the same accounting boundary as offshore wind, with
# technology-specific CAPEX, OPEX, and full-load hours.
WIND_ONSHORE_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1_300.0,
    upper_bound=1_900.0,
    unit="EUR/kW",
    description="Uniform distribution for onshore wind CAPEX, not annualized.",
)

WIND_ONSHORE_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=25.6,
    mode=32.0,
    maximum=41.6,
    unit="EUR/kW/year",
    description="Triangular distribution for onshore wind fixed OPEX.",
)

WIND_ONSHORE_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=5.6,
    mode=7.0,
    maximum=9.1,
    unit="EUR/MWh_e",
    description="Triangular distribution for onshore wind variable OPEX excluding fuel and electricity.",
)

WIND_ONSHORE_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/MWh_e",
    description="Assumed zero direct fuel consumption for onshore-wind generation.",
)

WIND_ONSHORE_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Assumed zero direct operational CO2 emissions for onshore wind.",
)

WIND_ONSHORE_FULL_LOAD_HOURS = FixedParameter(
    value=2_500.0,
    unit="h/year",
    description="Average full-load hours for the onshore wind technology.",
)

WIND_ONSHORE_LIFETIME_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime for the onshore wind technology.",
)


# PV has zero direct fuel use, variable OPEX, and operational CO2 emissions in
# the model. Its full-load hours determine the capacity required for the common
# annual output.
PV_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=700.0,
    upper_bound=900.0,
    unit="EUR/kW",
    description="Uniform distribution for PV CAPEX, not annualized.",
)

PV_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=10.6,
    mode=13.3,
    maximum=17.3,
    unit="EUR/kW/year",
    description="Triangular distribution for PV fixed OPEX.",
)

PV_VARIABLE_OPEX = FixedParameter(
    value=0.0,
    unit="EUR/MWh_e",
    description="Assumed zero non-energy variable OPEX for PV.",
)

PV_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/MWh_e",
    description="Assumed zero direct fuel consumption for PV generation.",
)

PV_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Assumed zero direct operational CO2 emissions for PV.",
)

PV_FULL_LOAD_HOURS = FixedParameter(
    value=1_107.5,
    unit="h/year",
    description="Average full-load hours for the PV technology.",
)

PV_LIFETIME_YEARS = FixedParameter(
    value=30.0,
    unit="years",
    description="Economic lifetime for the PV technology.",
)


# Biogas consumes a priced biomass-derived fuel. Fossil direct CO2 emissions
# are modelled as zero; biogenic and life-cycle emissions are outside the carbon
# cost applied here.
BIOGAS_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=2_894.0,
    upper_bound=5_788.0,
    unit="EUR/kW",
    description="Uniform distribution for biogas CAPEX, not annualized.",
)

BIOGAS_FIXED_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=92.6,
    upper_bound=301.0,
    unit="EUR/kW/year",
    description="Uniform distribution for biogas fixed OPEX.",
)

BIOGAS_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=3.2,
    mode=4.0,
    maximum=5.2,
    unit="EUR/MWh_e",
    description="Triangular distribution for biogas variable OPEX excluding fuel and electricity.",
)

BIOGAS_FUEL_CONSUMPTION_DISTRIBUTION = TriangularDistribution(
    minimum=2.38,
    mode=2.50,
    maximum=2.70,
    unit="MWh_th/MWh_e",
    description="Triangular distribution for biogas fuel consumption.",
)

BIOGAS_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Assumed zero fossil direct CO2 emissions for biogas generation.",
)

BIOGAS_FULL_LOAD_HOURS = FixedParameter(
    value=5_300.0,
    unit="h/year",
    description="Average full-load hours for the biogas technology.",
)

BIOGAS_LIFETIME_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime for the biogas technology.",
)

# BECCS is an absolute generation route. Source ranges have no central estimate,
# so its uncertain inputs are uniform. Its negative emissions parameter is a
# net accounting value after capture and biogenic-carbon treatment—not a
# physically negative stack flow—and therefore creates a modelled carbon credit.
BECCS_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=3_255.0,
    upper_bound=5_976.0,
    unit="EUR/kW",
    description="Uniform distribution for BECCS CAPEX in 2024 EUR, not annualized.",
)

BECCS_FIXED_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=170.4,
    upper_bound=322.9,
    unit="EUR/kW/year",
    description="Uniform distribution for BECCS fixed OPEX in 2024 EUR.",
)

BECCS_VARIABLE_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1.53,
    upper_bound=3.26,
    unit="EUR/MWh_e",
    description="Uniform distribution for BECCS variable OPEX in 2024 EUR excluding fuel and electricity.",
)

BECCS_TRANSPORT_STORAGE_COST_DISTRIBUTION = UniformDistribution(
    lower_bound=22.0,
    upper_bound=29.0,
    unit="EUR/MWh_e",
    description="Uniform distribution for BECCS CO2 transport and storage cost.",
)

BECCS_FUEL_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=2.42,
    upper_bound=3.27,
    unit="MWh_th/MWh_e",
    description="Uniform distribution for BECCS biomass fuel consumption.",
)

BECCS_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=-1.33,
    upper_bound=-1.01,
    unit="tCO2/MWh_e",
    description="Uniform distribution for the modelled net CO2 balance of BECCS.",
)

BECCS_FULL_LOAD_HOURS = FixedParameter(
    value=7_665.0,
    unit="h/year",
    description="Average of the supplied 7,446-7,884 h/year BECCS range.",
)

# No BECCS lifetime was supplied; the model adopts the 25-year lifetime used for
# the other bioenergy route.
BECCS_LIFETIME_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Assumed BECCS economic lifetime, aligned with biogas.",
)


# Parameter registries.
#
# The calculation modules use these dictionaries instead of importing each
# technology constant one by one. Adding a new electricity technology therefore
# means adding its assumptions above and registering the same standard keys here.
ELECTRICITY_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "retail_price_electricity_eur_per_mwh": RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
    "annual_electricity_output_mwh": ANNUAL_ELECTRICITY_OUTPUT_MWH,
}

ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution],
] = {
    # Full-load hours size the plant before CAPEX and fixed OPEX are calculated.
    # Lifetime controls the NPV discount horizon and lifetime-output denominator.
    # Variable renewables also carry a value factor that scales captured revenue.
    "hard_coal": {
        "full_load_hours_per_year": HARD_COAL_FULL_LOAD_HOURS,
        "lifetime_years": HARD_COAL_LIFETIME_YEARS,
    },
    "hard_coal_ccs": {
        "full_load_hours_per_year": HARD_COAL_FULL_LOAD_HOURS,
        "lifetime_years": HARD_COAL_LIFETIME_YEARS,
    },
    "ccgt": {
        "full_load_hours_per_year": CCGT_FULL_LOAD_HOURS,
        "lifetime_years": CCGT_LIFETIME_YEARS,
    },
    "ccgt_ccs": {
        "full_load_hours_per_year": CCGT_FULL_LOAD_HOURS,
        "lifetime_years": CCGT_LIFETIME_YEARS,
    },
    "nuclear": {
        "full_load_hours_per_year": NUCLEAR_FULL_LOAD_HOURS,
        "lifetime_years": NUCLEAR_LIFETIME_YEARS,
    },
    "wind_offshore": {
        "full_load_hours_per_year": WIND_OFFSHORE_FULL_LOAD_HOURS,
        "lifetime_years": WIND_OFFSHORE_LIFETIME_YEARS,
        "value_factor": VF_windoffshore,
    },
    "wind_onshore": {
        "full_load_hours_per_year": WIND_ONSHORE_FULL_LOAD_HOURS,
        "lifetime_years": WIND_ONSHORE_LIFETIME_YEARS,
        "value_factor": VF_Wind_onshore,
    },
    "pv": {
        "full_load_hours_per_year": PV_FULL_LOAD_HOURS,
        "lifetime_years": PV_LIFETIME_YEARS,
        "value_factor": VF_PV,
    },
    "biogas": {
        "full_load_hours_per_year": BIOGAS_FULL_LOAD_HOURS,
        "lifetime_years": BIOGAS_LIFETIME_YEARS,
    },
    "beccs": {
        "full_load_hours_per_year": BECCS_FULL_LOAD_HOURS,
        "lifetime_years": BECCS_LIFETIME_YEARS,
    },
}

ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    # Absolute technologies use the same keys so Monte Carlo and deterministic
    # calculations can resolve one shared cash-flow formula.
    "hard_coal": {
        "capex_eur_per_kw": HARD_COAL_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": HARD_COAL_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": HARD_COAL_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": HARD_COAL_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": HARD_COAL_EMISSIONS_DISTRIBUTION,
    },
    "ccgt": {
        "capex_eur_per_kw": CCGT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": CCGT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": CCGT_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": CCGT_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": CCGT_EMISSIONS_DISTRIBUTION,
    },
    "nuclear": {
        "capex_eur_per_kw": NUCLEAR_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": NUCLEAR_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": NUCLEAR_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": NUCLEAR_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": NUCLEAR_EMISSIONS,
    },
    "wind_offshore": {
        "capex_eur_per_kw": WIND_OFFSHORE_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": WIND_OFFSHORE_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": WIND_OFFSHORE_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": WIND_OFFSHORE_FUEL_CONSUMPTION,
        "emissions_tco2_per_mwh_e": WIND_OFFSHORE_EMISSIONS,
    },
    "wind_onshore": {
        "capex_eur_per_kw": WIND_ONSHORE_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": WIND_ONSHORE_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": WIND_ONSHORE_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": WIND_ONSHORE_FUEL_CONSUMPTION,
        "emissions_tco2_per_mwh_e": WIND_ONSHORE_EMISSIONS,
    },
    "pv": {
        "capex_eur_per_kw": PV_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": PV_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": PV_VARIABLE_OPEX,
        "fuel_consumption_mwh_th_per_mwh_e": PV_FUEL_CONSUMPTION,
        "emissions_tco2_per_mwh_e": PV_EMISSIONS,
    },
    "biogas": {
        "capex_eur_per_kw": BIOGAS_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": BIOGAS_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": BIOGAS_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": BIOGAS_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": BIOGAS_EMISSIONS,
    },
    "beccs": {
        "capex_eur_per_kw": BECCS_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": BECCS_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": BECCS_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": BECCS_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": BECCS_EMISSIONS_DISTRIBUTION,
    },
}

ELECTRICITY_RETROFIT_BASE_TECHNOLOGIES: Mapping[str, str] = {
    "hard_coal_ccs": "hard_coal",
    "ccgt_ccs": "ccgt",
}

ELECTRICITY_RETROFIT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
    "hard_coal_ccs": {
        "capex_change_eur_per_kw": HARD_COAL_CCS_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_kw_year": (
            HARD_COAL_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_mwh": (
            HARD_COAL_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": (
            HARD_COAL_CCS_FUEL_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": (
            HARD_COAL_CCS_EMISSIONS_REDUCTION_DISTRIBUTION
        ),
    },
    "ccgt_ccs": {
        "capex_change_eur_per_kw": CCGT_CCS_CAPEX_CHANGE_DISTRIBUTION,
        "fixed_opex_change_eur_per_kw_year": (
            CCGT_CCS_FIXED_OPEX_CHANGE_DISTRIBUTION
        ),
        "variable_opex_change_eur_per_mwh": (
            CCGT_CCS_VARIABLE_OPEX_CHANGE_DISTRIBUTION
        ),
        "fuel_consumption_reduction_fraction": (
            CCGT_CCS_FUEL_REDUCTION_DISTRIBUTION
        ),
        "emissions_reduction_fraction": CCGT_CCS_EMISSIONS_REDUCTION_DISTRIBUTION,
    },
}
