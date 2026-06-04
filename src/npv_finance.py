"""Sector-independent NPV finance calculations."""

from __future__ import annotations

import numpy as np


def calculate_level_cash_flow_present_value_factor(
    lifetime_years: int,
    discount_rate: float,
) -> float:
    """Calculate the present value factor for a constant annual cash flow."""

    if lifetime_years <= 0:
        raise ValueError("lifetime_years must be positive.")
    if discount_rate < 0:
        raise ValueError("discount_rate must be non-negative.")
    if discount_rate == 0:
        return float(lifetime_years)

    return (1.0 - (1.0 + discount_rate) ** -lifetime_years) / discount_rate


def calculate_npv(
    initial_capex_eur: np.ndarray,
    annual_net_cash_flow_eur: np.ndarray,
    lifetime_years: int,
    discount_rate: float,
) -> np.ndarray:
    """Calculate NPV from initial CAPEX and level annual net cash flow."""

    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=discount_rate,
    )
    return -initial_capex_eur + annual_net_cash_flow_eur * present_value_factor
