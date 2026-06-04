"""Cement-sector parameters for the Monte Carlo simulation.

This is currently a small placeholder-style parameter module for the cement
sector. It follows the same structure as the electricity assumptions so future
cement calculations can import fixed sector parameters from one traceable place.
"""

from __future__ import annotations

from typing import Mapping

from distributions import FixedParameter


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

CEMENT_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "lifetime_cement_years": LIFETIME_CEMENT_YEARS,
    "retail_price_cement_eur_per_t": RETAIL_PRICE_CEMENT_EUR_PER_T,
}
