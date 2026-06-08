"""Cement-sector parameters for the Monte Carlo simulation.

This is currently a small placeholder-style parameter module for the cement
sector. It follows the same structure as the electricity assumptions so future
cement calculations can import fixed sector parameters from one traceable place.
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

# Cement revenue placeholder for the current model setup.
RETAIL_PRICE_CEMENT_EUR_PER_T = FixedParameter(
    value=150.0,
    unit="EUR/t",
    description="Retail price of cement used in the cement-sector setup.",
)

# BAU cement technology parameters. Fuel consumption, electricity consumption,
# and emissions are absolute intensities, not percentage reductions.
BAU_CEMENT_CAPEX_DISTRIBUTION = UniformDistribution(
    lower_bound=150.0,
    upper_bound=170.0,
    unit="EUR/t",
    description="Uniform distribution for BAU cement CAPEX, not annualized.",
)

BAU_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=13.0,
    mode=15.0,
    maximum=15.0,
    unit="EUR/t",
    description="Triangular distribution for BAU cement fixed OPEX.",
)

BAU_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=4.5,
    mode=5.5,
    maximum=5.5,
    unit="EUR/t",
    description="Triangular distribution for BAU cement variable OPEX excluding fuel and electricity.",
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
    minimum=600.0,
    mode=600.0,
    maximum=700.0,
    unit="kgCO2/t",
    description="Triangular distribution for BAU cement direct emissions.",
)


# Electrification is an alternative cement technology. Fuel consumption is fixed
# at zero, while electricity consumption is an absolute intensity, not a
# percentage reduction.
ELECTRIFICATION_CEMENT_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=140.0,
    mode=204.0,
    maximum=300.0,
    unit="EUR/t",
    description="Triangular distribution for electrification cement CAPEX, not annualized.",
)

ELECTRIFICATION_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=13.0,
    mode=19.0,
    maximum=28.0,
    unit="EUR/t",
    description="Triangular distribution for electrification cement fixed OPEX.",
)

ELECTRIFICATION_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=5.1,
    mode=7.3,
    maximum=11.0,
    unit="EUR/t",
    description="Triangular distribution for electrification cement variable OPEX excluding fuel and electricity.",
)

ELECTRIFICATION_CEMENT_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/t",
    description="Fuel consumption for electrification cement production.",
)

ELECTRIFICATION_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=0.90,
    upper_bound=1.00,
    unit="MWh/t",
    description="Uniform distribution for electrification cement electricity consumption.",
)

ELECTRIFICATION_CEMENT_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=350.0,
    upper_bound=450.0,
    unit="kgCO2/t",
    description="Uniform distribution for electrification cement direct emissions.",
)


# Electrolysis is an alternative cement technology. Fuel consumption is fixed at
# zero, while electricity consumption and emissions are absolute intensities.
ELECTROLYSIS_CEMENT_CAPEX_DISTRIBUTION = TriangularDistribution(
    minimum=255.0,
    mode=362.0,
    maximum=545.0,
    unit="EUR/t",
    description="Triangular distribution for electrolysis cement CAPEX, not annualized.",
)

ELECTROLYSIS_CEMENT_FIXED_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=24.0,
    mode=34.0,
    maximum=51.0,
    unit="EUR/t",
    description="Triangular distribution for electrolysis cement fixed OPEX.",
)

ELECTROLYSIS_CEMENT_VARIABLE_OPEX_DISTRIBUTION = TriangularDistribution(
    minimum=13.0,
    mode=19.0,
    maximum=28.0,
    unit="EUR/t",
    description="Triangular distribution for electrolysis cement variable OPEX excluding fuel and electricity.",
)

ELECTROLYSIS_CEMENT_FUEL_CONSUMPTION = FixedParameter(
    value=0.0,
    unit="MWh_th/t",
    description="Fuel consumption for electrolysis cement production.",
)

ELECTROLYSIS_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION = UniformDistribution(
    lower_bound=1.60,
    upper_bound=3.10,
    unit="MWh/t",
    description="Uniform distribution for electrolysis cement electricity consumption.",
)

ELECTROLYSIS_CEMENT_EMISSIONS_DISTRIBUTION = UniformDistribution(
    lower_bound=60.0,
    upper_bound=140.0,
    unit="kgCO2/t",
    description="Uniform distribution for electrolysis cement direct emissions.",
)

CEMENT_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
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
        "emissions_kgco2_per_t": BAU_CEMENT_EMISSIONS_DISTRIBUTION,
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
        "emissions_kgco2_per_t": ELECTRIFICATION_CEMENT_EMISSIONS_DISTRIBUTION,
    },
    "electrolysis": {
        "capex_eur_per_t": ELECTROLYSIS_CEMENT_CAPEX_DISTRIBUTION,
        "fixed_opex_eur_per_t": ELECTROLYSIS_CEMENT_FIXED_OPEX_DISTRIBUTION,
        "variable_opex_eur_per_t": ELECTROLYSIS_CEMENT_VARIABLE_OPEX_DISTRIBUTION,
        "fuel_consumption_mwh_th_per_t": ELECTROLYSIS_CEMENT_FUEL_CONSUMPTION,
        "electricity_consumption_mwh_per_t": (
            ELECTROLYSIS_CEMENT_ELECTRICITY_CONSUMPTION_DISTRIBUTION
        ),
        "emissions_kgco2_per_t": ELECTROLYSIS_CEMENT_EMISSIONS_DISTRIBUTION,
    },
}
