"""Sector-independent NPV finance calculations.

All sector models eventually reduce to the same financial structure: an upfront
capital cost at year 0 and a constant annual net cash flow over the asset
lifetime. Keeping that formula here makes it easier to compare electricity,
cement, and future sectors with one consistent NPV definition.
"""

from __future__ import annotations

import numpy as np


def calculate_level_cash_flow_present_value_factor(
    lifetime_years: int,
    discount_rate: float,
) -> float:
    """Calculate the present value factor for a constant annual cash flow.

    The factor is the discounted value today of receiving one EUR every year for
    `lifetime_years`. Multiplying annual net cash flow by this factor converts
    the yearly operating result into a present value.
    """

    if lifetime_years <= 0:
        raise ValueError("lifetime_years must be positive.")
    if discount_rate < 0:
        raise ValueError("discount_rate must be non-negative.")
    if discount_rate == 0:
        # With no discounting, the present value is simply one unit per year.
        return float(lifetime_years)

    return (1.0 - (1.0 + discount_rate) ** -lifetime_years) / discount_rate


def calculate_npv(
    initial_capex_eur: np.ndarray,
    annual_net_cash_flow_eur: np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> np.ndarray:
    """Calculate NPV from initial CAPEX and level annual net cash flow.

    Inputs can be arrays, which is why the same function works for both one
    deterministic result and many Monte Carlo draws.
    """

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    # Initial CAPEX is paid at year 0; annual cash flow is discounted over the lifetime.
    return -initial_capex_eur + annual_net_cash_flow_eur * present_value_factor
