"""General Monte Carlo parameters shared across sector modules.

This module contains global assumptions that are not specific to one sector.
Sector modules can import these constants and combine them with their own
technology or sector-specific parameter distributions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from distributions import TriangularDistribution


@dataclass(frozen=True)
class FixedParameter:
    """A deterministic model parameter."""

    value: float
    unit: str
    description: str


# Economic lifetime for cement-sector investments.
LIFETIME_CEMENT_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of cement-sector assets.",
)

# Economic lifetime for electricity-sector investments.
LIFETIME_ELECTRICITY_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of electricity-sector assets.",
)

# Cement retail price placeholder specified for the general model setup.
RETAIL_PRICE_CEMENT_EUR_PER_T = FixedParameter(
    value=1.0,
    unit="EUR/t",
    description="Retail price of cement used in the general setup.",
)

# Electricity retail price placeholder specified for the general model setup.
RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH = FixedParameter(
    value=1.0,
    unit="EUR/MWh",
    description="Retail price of electricity used in the general setup.",
)

# Carbon price placeholder specified for the general model setup.
CARBON_PRICE_EUR_PER_T = FixedParameter(
    value=1.0,
    unit="EUR/tCO2",
    description="Carbon price used in the general setup.",
)

# Annual interest rate used for cost annualization and discounting.
INTEREST_RATE = FixedParameter(
    value=0.08,
    unit="fraction/year",
    description="Annual interest rate.",
)

# Fuel-price distributions extracted from the attached low/mid/high price table.
GAS_PRICE_DISTRIBUTION = TriangularDistribution(
    minimum=12.5,
    mode=39.3,
    maximum=89.7,
    unit="EUR/MWh",
    description="Triangular distribution for gas price.",
)

COAL_PRICE_DISTRIBUTION = TriangularDistribution(
    minimum=8.14,
    mode=12.11,
    maximum=24.17,
    unit="EUR/MWh",
    description="Triangular distribution for coal price.",
)

GENERAL_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "lifetime_electricity_years": LIFETIME_ELECTRICITY_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
    "retail_price_electricity_eur_per_mwh": RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
    "carbon_price_eur_per_t": CARBON_PRICE_EUR_PER_T,
    "interest_rate": INTEREST_RATE,
}

GENERAL_DISTRIBUTIONS: Mapping[str, TriangularDistribution] = {
    "gas_price_eur_per_mwh": GAS_PRICE_DISTRIBUTION,
    "coal_price_eur_per_mwh": COAL_PRICE_DISTRIBUTION,
}
