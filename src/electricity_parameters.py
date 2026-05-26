"""Electricity-sector parameters for the Monte Carlo simulation."""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter


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

ELECTRICITY_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_electricity_years": LIFETIME_ELECTRICITY_YEARS,
    "retail_price_electricity_eur_per_mwh": RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
}
