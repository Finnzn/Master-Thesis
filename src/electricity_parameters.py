"""Electricity-sector parameters for the Monte Carlo simulation."""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution, UniformDistribution


# Economic lifetime for electricity-sector investments.
LIFETIME_ELECTRICITY_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of electricity-sector assets.",
)

# Electricity retail price placeholder specified for the model setup.
RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH = FixedParameter(
    value=94.07,
    unit="EUR/MWh",
    description="Retail price of electricity used in the electricity-sector setup.",
)

# Normalized annual electricity output used to compare technologies.
ANNUAL_ELECTRICITY_OUTPUT_MWH = FixedParameter(
    value=1_000_000.0,
    unit="MWh/year",
    description="Annual electricity output target used to normalize electricity technologies.",
)

# Hard coal technology parameters.
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


# CCGT technology parameters.
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


# Nuclear technology parameters.
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
    value=5_300.0,
    unit="h/year",
    description="Average full-load hours for the nuclear technology.",
)


# Offshore wind technology parameters.
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


# Onshore wind technology parameters.
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


# Parameter registries.
ELECTRICITY_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_electricity_years": LIFETIME_ELECTRICITY_YEARS,
    "retail_price_electricity_eur_per_mwh": RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
    "annual_electricity_output_mwh": ANNUAL_ELECTRICITY_OUTPUT_MWH,
}

ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS: Mapping[
    str,
    Mapping[str, FixedParameter],
] = {
    "hard_coal": {
        "full_load_hours_per_year": HARD_COAL_FULL_LOAD_HOURS,
    },
    "ccgt": {
        "full_load_hours_per_year": CCGT_FULL_LOAD_HOURS,
    },
    "nuclear": {
        "full_load_hours_per_year": NUCLEAR_FULL_LOAD_HOURS,
    },
    "wind_offshore": {
        "full_load_hours_per_year": WIND_OFFSHORE_FULL_LOAD_HOURS,
    },
    "wind_onshore": {
        "full_load_hours_per_year": WIND_ONSHORE_FULL_LOAD_HOURS,
    },
}

ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, FixedParameter | TriangularDistribution | UniformDistribution],
] = {
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
}
