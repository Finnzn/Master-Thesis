"""Electricity-specific capacity calculations.

Electricity technologies are compared at the same annual output. Installed
capacity therefore depends on full-load hours: a technology with fewer full-load
hours needs more MW installed to produce the same yearly MWh.
"""

from __future__ import annotations


def calculate_capacity_mw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed electricity capacity from output and FLH.

    The formula is `capacity MW = annual output MWh / full-load hours`. This
    capacity then drives CAPEX and fixed OPEX in the NPV model.
    """

    if annual_electricity_output_mwh <= 0:
        raise ValueError("annual_electricity_output_mwh must be positive.")
    if full_load_hours_per_year <= 0:
        raise ValueError("full_load_hours_per_year must be positive.")

    return annual_electricity_output_mwh / full_load_hours_per_year


def calculate_capacity_kw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed electricity capacity in kW.

    CAPEX and fixed OPEX assumptions are stored per kW, so the MW result is
    converted before costs are calculated.
    """

    return calculate_capacity_mw(
        annual_electricity_output_mwh=annual_electricity_output_mwh,
        full_load_hours_per_year=full_load_hours_per_year,
    ) * 1_000.0
