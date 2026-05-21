"""Cement-sector parameters for the Monte Carlo simulation."""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter


# Economic lifetime for cement-sector investments.
LIFETIME_CEMENT_YEARS = FixedParameter(
    value=25.0,
    unit="years",
    description="Economic lifetime of cement-sector assets.",
)

# Cement retail price placeholder specified for the model setup.
RETAIL_PRICE_CEMENT_EUR_PER_T = FixedParameter(
    value=1.0,
    unit="EUR/t",
    description="Retail price of cement used in the cement-sector setup.",
)

CEMENT_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
}
