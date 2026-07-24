"""Electricity-sector parameters for the Monte Carlo simulation.

This file is the electricity assumptions catalogue. It does not perform NPV
calculations; it only records input values and uncertainty ranges for each
technology. The calculation modules import these objects so the modelling logic
stays separate from the numerical assumptions.

The technologies are compared on a normalized annual output of 1,000,000 MWh.
Full-load hours then determine how much installed capacity each technology needs
to produce that same annual output.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


# Electricity revenue is calculated from this fixed retail price and the
# normalized annual output.
RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH = FixedParameter(
    value=94.07,
    unit="EUR/MWh",
    description="Retail price of electricity used in the electricity-sector setup.",
)

# Normalized annual output: every technology is sized to produce this amount so
# the NPV comparison is not driven by different plant sizes.
ANNUAL_ELECTRICITY_OUTPUT_MWH = FixedParameter(
    value=1_000_000.0,
    unit="MWh/year",
    description="Annual electricity output target used to normalize electricity technologies.",
)

# Hard coal technology parameters. Fuel cost and carbon cost are both relevant
# because hard coal has non-zero fuel consumption and direct emissions.
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
    description="Triangular distribution for hard coal direct emissions.",
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


# Hard coal with CCS technology parameters. CCS raises CAPEX/OPEX and fuel use,
# but lowers residual emissions compared with unabated hard coal.
HARD_COAL_CCS_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=3_021.0,
    upper_bound=5_131.0,
    unit="EUR/kW",
    description="Uniform distribution for hard coal with CCS CAPEX, not annualized.",
)

HARD_COAL_CCS_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=61.3,
    mode=82.2,
    maximum=115.9,
    unit="EUR/kW/year",
    description="Triangular distribution for hard coal with CCS fixed OPEX.",
)

HARD_COAL_CCS_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=8.0,
    mode=10.73,
    maximum=15.1,
    unit="EUR/MWh_e",
    description="Triangular distribution for hard coal with CCS variable OPEX excluding fuel and electricity.",
)

HARD_COAL_CCS_FUEL_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=3.08,
    upper_bound=3.24,
    unit="MWh_th/MWh_e",
    description="Uniform distribution for hard coal with CCS fuel consumption.",
)

HARD_COAL_CCS_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=0.010,
    upper_bound=0.110,
    unit="tCO2/MWh_e",
    description="Uniform distribution for hard coal with CCS residual direct emissions.",
)

HARD_COAL_CCS_FULL_LOAD_HOURS = FixedParameter(
    value=4_100.0,
    unit="h/year",
    description="Average full-load hours for the hard coal with CCS technology.",
)

HARD_COAL_CCS_LIFETIME_YEARS = FixedParameter(
    value=30.0,
    unit="years",
    description="Economic lifetime for the hard coal with CCS technology.",
)


# CCGT technology parameters. Gas-price uncertainty is added in the calculation
# module through the shared gas-price distribution.
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
    description="Triangular distribution for CCGT direct emissions.",
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


# CCGT with CCS technology parameters. As with hard coal CCS, the model captures
# higher costs and lower residual emissions relative to the unabated plant.
CCGT_CCS_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1_487.0,
    upper_bound=2_557.0,
    unit="EUR/kW",
    description="Uniform distribution for CCGT with CCS CAPEX, not annualized.",
)

CCGT_CCS_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=32.0,
    mode=42.0,
    maximum=60.2,
    unit="EUR/kW/year",
    description="Triangular distribution for CCGT with CCS fixed OPEX.",
)

CCGT_CCS_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.5,
    mode=6.73,
    maximum=7.6,
    unit="EUR/MWh_e",
    description="Triangular distribution for CCGT with CCS variable OPEX excluding fuel and electricity.",
)

CCGT_CCS_FUEL_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=1.90,
    upper_bound=1.94,
    unit="MWh_th/MWh_e",
    description="Uniform distribution for CCGT with CCS fuel consumption.",
)

CCGT_CCS_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=0.0058,
    upper_bound=0.039,
    unit="tCO2/MWh_e",
    description="Uniform distribution for CCGT with CCS residual direct emissions.",
)

CCGT_CCS_FULL_LOAD_HOURS = FixedParameter(
    value=4_650.0,
    unit="h/year",
    description="Average full-load hours for the CCGT with CCS technology.",
)

CCGT_CCS_LIFETIME_YEARS = FixedParameter(
    value=30.0,
    unit="years",
    description="Economic lifetime for the CCGT with CCS technology.",
)


# Nuclear technology parameters. Direct emissions are modelled as zero here, so
# carbon cost does not affect the nuclear annual cash flow.
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
    description="Direct stack emissions for nuclear electricity generation.",
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


# Offshore wind technology parameters. Fuel consumption and direct emissions are
# fixed at zero, so its uncertainty comes mainly from CAPEX/OPEX and full-load hours.
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
    description="Fuel consumption for offshore wind electricity generation.",
)

WIND_OFFSHORE_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Direct stack emissions for offshore wind electricity generation.",
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


# Onshore wind technology parameters. The structure mirrors offshore wind, but
# different CAPEX/OPEX and full-load hours capture the technology-specific case.
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
    description="Fuel consumption for onshore wind electricity generation.",
)

WIND_ONSHORE_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Direct stack emissions for onshore wind electricity generation.",
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


# PV technology parameters. PV has zero modelled fuel cost, variable OPEX, and
# direct emissions in this setup; the low full-load hours drive required capacity.
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
    description="Variable OPEX excluding fuel and electricity for PV.",
)

PV_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/MWh_e",
    description="Fuel consumption for PV electricity generation.",
)

PV_EMISSIONS = FixedParameter(
    value=0.0,
    unit="tCO2/MWh_e",
    description="Direct stack emissions for PV electricity generation.",
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


# Biogas technology parameters. Biogas has fuel consumption and fuel cost, but
# fossil direct emissions are treated as zero in the current model setup.
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
    description="Fossil direct emissions for biogas electricity generation.",
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

# Bioenergy with carbon capture and storage (BECCS). The supplied source values
# provide bounded ranges but no central estimate, so the techno-economic inputs
# use uniform distributions. Negative direct emissions represent net carbon
# removal and therefore produce a carbon credit in the shared cash-flow formula.
BECCS_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=2_454.0,
    upper_bound=4_239.0,
    unit="EUR/kW",
    description="Uniform distribution for BECCS CAPEX, not annualized.",
)

BECCS_FIXED_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=128.4,
    upper_bound=229.1,
    unit="EUR/kW/year",
    description="Uniform distribution for BECCS fixed OPEX.",
)

BECCS_VARIABLE_OPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=1.16,
    upper_bound=2.31,
    unit="EUR/MWh_e",
    description="Uniform distribution for BECCS variable OPEX excluding fuel and electricity.",
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
    description="Uniform distribution for BECCS net-negative direct emissions.",
)

BECCS_FULL_LOAD_HOURS = FixedParameter(
    value=7_665.0,
    unit="h/year",
    description="Average of the supplied 7,446-7,884 h/year BECCS range.",
)

# No BECCS lifetime was supplied. The model therefore uses the existing
# 25-year bioenergy lifetime assumption applied to biogas.
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
    Mapping[str, FixedParameter],
] = {
    # Full-load hours size the plant before CAPEX and fixed OPEX are calculated.
    # Lifetime controls the NPV discount horizon and lifetime-output denominator.
    "hard_coal": {
        "full_load_hours_per_year": HARD_COAL_FULL_LOAD_HOURS,
        "lifetime_years": HARD_COAL_LIFETIME_YEARS,
    },
    "hard_coal_ccs": {
        "full_load_hours_per_year": HARD_COAL_CCS_FULL_LOAD_HOURS,
        "lifetime_years": HARD_COAL_CCS_LIFETIME_YEARS,
    },
    "ccgt": {
        "full_load_hours_per_year": CCGT_FULL_LOAD_HOURS,
        "lifetime_years": CCGT_LIFETIME_YEARS,
    },
    "ccgt_ccs": {
        "full_load_hours_per_year": CCGT_CCS_FULL_LOAD_HOURS,
        "lifetime_years": CCGT_CCS_LIFETIME_YEARS,
    },
    "nuclear": {
        "full_load_hours_per_year": NUCLEAR_FULL_LOAD_HOURS,
        "lifetime_years": NUCLEAR_LIFETIME_YEARS,
    },
    "wind_offshore": {
        "full_load_hours_per_year": WIND_OFFSHORE_FULL_LOAD_HOURS,
        "lifetime_years": WIND_OFFSHORE_LIFETIME_YEARS,
    },
    "wind_onshore": {
        "full_load_hours_per_year": WIND_ONSHORE_FULL_LOAD_HOURS,
        "lifetime_years": WIND_ONSHORE_LIFETIME_YEARS,
    },
    "pv": {
        "full_load_hours_per_year": PV_FULL_LOAD_HOURS,
        "lifetime_years": PV_LIFETIME_YEARS,
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
    # Each technology uses the same keys so Monte Carlo and deterministic
    # calculations can loop over technologies with one shared formula.
    "hard_coal": {
        "capex_eur_per_kw": HARD_COAL_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": HARD_COAL_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": HARD_COAL_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": HARD_COAL_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": HARD_COAL_EMISSIONS_DISTRIBUTION,
    },
    "hard_coal_ccs": {
        "capex_eur_per_kw": HARD_COAL_CCS_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": HARD_COAL_CCS_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": HARD_COAL_CCS_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": HARD_COAL_CCS_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": HARD_COAL_CCS_EMISSIONS_DISTRIBUTION,
    },
    "ccgt": {
        "capex_eur_per_kw": CCGT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": CCGT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": CCGT_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": CCGT_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": CCGT_EMISSIONS_DISTRIBUTION,
    },
    "ccgt_ccs": {
        "capex_eur_per_kw": CCGT_CCS_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_kw_year": CCGT_CCS_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_mwh": CCGT_CCS_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_mwh_e": CCGT_CCS_FUEL_CONSUMPTION_DISTRIBUTION,
        "emissions_tco2_per_mwh_e": CCGT_CCS_EMISSIONS_DISTRIBUTION,
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
