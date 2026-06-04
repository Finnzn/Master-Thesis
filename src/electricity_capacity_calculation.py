"""Electricity-specific capacity calculations."""

from __future__ import annotations


def calculate_capacity_mw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed electricity capacity from output and FLH."""

    if annual_electricity_output_mwh <= 0:
        raise ValueError("annual_electricity_output_mwh must be positive.")
    if full_load_hours_per_year <= 0:
        raise ValueError("full_load_hours_per_year must be positive.")

    return annual_electricity_output_mwh / full_load_hours_per_year


def calculate_capacity_kw(
    annual_electricity_output_mwh: float,
    full_load_hours_per_year: float,
) -> float:
    """Calculate required installed electricity capacity in kW."""

    return calculate_capacity_mw(
        annual_electricity_output_mwh=annual_electricity_output_mwh,
        full_load_hours_per_year=full_load_hours_per_year,
    ) * 1_000.0
