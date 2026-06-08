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

CEMENT_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
}

CEMENT_TECHNOLOGY_DISTRIBUTIONS: Mapping[
    str,
    Mapping[str, TriangularDistribution | UniformDistribution],
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
}
