"""General Monte Carlo parameters shared across sector modules.

This module contains global assumptions that are not specific to one sector.
Sector modules can import these constants and combine them with their own
technology or sector-specific parameter distributions.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter, TriangularDistribution

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

ELECTRICITY_PRICE_DISTRIBUTION = TriangularDistribution(
    minimum=74.8,
    mode=183.7,
    maximum=255.2,
    unit="EUR/MWh",
    description="Triangular distribution for electricity price.",
)

GENERAL_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "carbon_price_eur_per_t": CARBON_PRICE_EUR_PER_T,
    "interest_rate": INTEREST_RATE,
}

GENERAL_DISTRIBUTIONS: Mapping[str, TriangularDistribution] = {
    "gas_price_eur_per_mwh": GAS_PRICE_DISTRIBUTION,
    "coal_price_eur_per_mwh": COAL_PRICE_DISTRIBUTION,
    "electricity_price_eur_per_mwh": ELECTRICITY_PRICE_DISTRIBUTION,
}
