"""Deterministic sensitivity-analysis helpers for the financial dashboard.

The dashboard uses the existing deterministic sector models as its base case.
This module recalculates NPV, levelized net margin, or levelized cost after
explicit user changes to prices, costs, output, lifetime, or discount rate; it
does not change the thesis assumptions stored in the parameter modules.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from io import BytesIO
from pathlib import Path
from typing import Iterable, Mapping

import matplotlib.pyplot as plt
import pandas as pd

from cement.cement_npv_deterministic import calculate_deterministic_cement_result
from cement.cement_parameters import (
    CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS,
    CEMENT_TECHNOLOGY_DISTRIBUTIONS,
)
from electricity.electricity_capacity_calculation import calculate_capacity_kw
from electricity.electricity_npv_deterministic import (
    calculate_deterministic_electricity_result,
)
from electricity.electricity_parameters import ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS
from general_parameters import INTEREST_RATE
from npv_finance import (
    calculate_level_cash_flow_present_value_factor,
    calculate_levelized_cost,
    calculate_levelized_net_margin,
)


@dataclass(frozen=True)
class ScenarioInputs:
    """Inputs that can be changed interactively in the sensitivity dashboard."""

    annual_output: float
    lifetime_years: float
    discount_rate: float
    sales_price: float
    capex: float
    fixed_opex: float
    variable_opex: float
    fuel_consumption: float
    fuel_price: float
    electricity_consumption: float
    electricity_price: float
    transport_and_storage_cost: float
    emissions: float
    carbon_price: float
    full_load_hours: float | None = None
    value_factor: float = 1.0


@dataclass(frozen=True)
class SensitivityParameter:
    """One tornado-chart input and the attribute it changes."""

    label: str
    attribute: str
    minimum: float = 0.0


SECTOR_DISPLAY_NAMES = {
    "cement": "Cement",
    "electricity": "Electricity",
}

SECTOR_UNITS = {
    "cement": "t",
    "electricity": "MWh",
}

FINANCIAL_METRIC_OPTIONS = ("NPV", "LNM", "LCOX")


SENSITIVITY_PARAMETERS: Mapping[str, tuple[SensitivityParameter, ...]] = {
    "cement": (
        SensitivityParameter("Investment cost", "capex"),
        SensitivityParameter("Cement price", "sales_price"),
        SensitivityParameter("Annual production", "annual_output"),
        SensitivityParameter("Lifetime", "lifetime_years", minimum=1.0),
        SensitivityParameter("Discount rate", "discount_rate"),
        SensitivityParameter("Fixed OPEX", "fixed_opex"),
        SensitivityParameter("Variable OPEX", "variable_opex"),
        SensitivityParameter("Fuel use", "fuel_consumption"),
        SensitivityParameter("Fuel price", "fuel_price"),
        SensitivityParameter("Electricity use", "electricity_consumption"),
        SensitivityParameter("Electricity price", "electricity_price"),
        SensitivityParameter("Direct emissions", "emissions"),
        SensitivityParameter("Carbon price", "carbon_price"),
    ),
    "electricity": (
        SensitivityParameter("Investment cost", "capex"),
        SensitivityParameter("Power price", "sales_price"),
        SensitivityParameter("Annual generation", "annual_output"),
        SensitivityParameter("Full-load hours", "full_load_hours", minimum=1.0),
        SensitivityParameter("Lifetime", "lifetime_years", minimum=1.0),
        SensitivityParameter("Discount rate", "discount_rate"),
        SensitivityParameter("Fixed OPEX", "fixed_opex"),
        SensitivityParameter("Variable OPEX", "variable_opex"),
        SensitivityParameter("Fuel use", "fuel_consumption"),
        SensitivityParameter("Fuel price", "fuel_price"),
        # Negative emissions must remain available for BECCS. Other technology
        # base cases remain positive, so removing the zero floor does not alter
        # their standard ±variation calculation.
        SensitivityParameter("Direct emissions", "emissions", minimum=float("-inf")),
        SensitivityParameter("Carbon price", "carbon_price"),
    ),
}


def available_technologies(sector: str) -> tuple[str, ...]:
    """Return technologies available for one sector."""

    if sector == "cement":
        return tuple(CEMENT_TECHNOLOGY_DISTRIBUTIONS) + tuple(
            CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS
        )
    if sector == "electricity":
        # The fixed-parameter registry retains the canonical display order across
        # both absolute technologies and BAU-relative CCS retrofits.
        return tuple(ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS)
    raise ValueError(f"Unknown sector: {sector!r}.")


def display_label(name: str) -> str:
    """Convert snake-case technology or parameter names to display labels."""

    if name == "beccs":
        return "BECCS"
    return name.replace("_", " ").title()


def base_inputs(sector: str, technology: str) -> ScenarioInputs:
    """Load dashboard base inputs from the deterministic model result."""

    if sector == "cement":
        result = _single_value_result(calculate_deterministic_cement_result(technology))
        return ScenarioInputs(
            annual_output=result["annual_output_t"],
            lifetime_years=result["lifetime_years"],
            discount_rate=INTEREST_RATE.value,
            sales_price=result["cement_price_eur_per_t"],
            capex=result["capex_eur_per_t"],
            fixed_opex=result["fixed_opex_eur_per_t"],
            variable_opex=result["variable_opex_eur_per_t"],
            fuel_consumption=result["fuel_consumption_mwh_th_per_t"],
            fuel_price=result["fuel_price_eur_per_mwh_th"],
            electricity_consumption=result["electricity_consumption_mwh_per_t"],
            electricity_price=result["electricity_price_eur_per_mwh"],
            transport_and_storage_cost=result[
                "transport_and_storage_cost_eur_per_t"
            ],
            emissions=result["emissions_tco2_per_t"],
            carbon_price=result["carbon_price_eur_per_t"],
        )

    if sector == "electricity":
        result = _single_value_result(
            calculate_deterministic_electricity_result(technology)
        )
        return ScenarioInputs(
            annual_output=result["annual_output_mwh"],
            lifetime_years=result["lifetime_years"],
            discount_rate=INTEREST_RATE.value,
            sales_price=result["electricity_price_eur_per_mwh"],
            capex=result["capex_eur_per_kw"],
            fixed_opex=result["fixed_opex_eur_per_kw_year"],
            variable_opex=result["variable_opex_eur_per_mwh"],
            fuel_consumption=result["fuel_consumption_mwh_th_per_mwh_e"],
            fuel_price=result["fuel_price_eur_per_mwh_th"],
            electricity_consumption=0.0,
            electricity_price=0.0,
            transport_and_storage_cost=result[
                "transport_and_storage_cost_eur_per_mwh"
            ],
            emissions=result["emissions_tco2_per_mwh_e"],
            carbon_price=result["carbon_price_eur_per_t"],
            full_load_hours=result["full_load_hours_per_year"],
            value_factor=result["value_factor"],
        )

    raise ValueError(f"Unknown sector: {sector!r}.")


def _sector_financial_components(
    sector: str,
    inputs: ScenarioInputs,
) -> tuple[float, float, float]:
    """Return initial CAPEX, annual revenue, and annual cost for a scenario."""

    if sector == "cement":
        initial_capex_eur = inputs.annual_output * inputs.capex
        annual_revenue_eur = inputs.annual_output * inputs.sales_price
        annual_fixed_opex_eur = inputs.annual_output * inputs.fixed_opex
        annual_variable_opex_eur = inputs.annual_output * inputs.variable_opex
        annual_fuel_cost_eur = (
            inputs.annual_output * inputs.fuel_consumption * inputs.fuel_price
        )
        annual_electricity_cost_eur = (
            inputs.annual_output
            * inputs.electricity_consumption
            * inputs.electricity_price
        )
        annual_emissions_cost_eur = (
            inputs.annual_output * inputs.emissions * inputs.carbon_price
        )
    elif sector == "electricity":
        if inputs.full_load_hours is None:
            raise ValueError("Electricity scenarios require full_load_hours.")
        capacity_kw = calculate_capacity_kw(
            annual_electricity_output_mwh=inputs.annual_output,
            full_load_hours_per_year=inputs.full_load_hours,
        )
        initial_capex_eur = capacity_kw * inputs.capex
        annual_revenue_eur = (
            inputs.annual_output * inputs.sales_price * inputs.value_factor
        )
        annual_fixed_opex_eur = capacity_kw * inputs.fixed_opex
        annual_variable_opex_eur = inputs.annual_output * inputs.variable_opex
        annual_fuel_cost_eur = (
            inputs.annual_output * inputs.fuel_consumption * inputs.fuel_price
        )
        annual_electricity_cost_eur = 0.0
        annual_emissions_cost_eur = (
            inputs.annual_output * inputs.emissions * inputs.carbon_price
        )
    else:
        raise ValueError(f"Unknown sector: {sector!r}.")

    annual_total_cost_eur = (
        annual_fixed_opex_eur
        + annual_variable_opex_eur
        + annual_fuel_cost_eur
        + annual_electricity_cost_eur
        + inputs.annual_output * inputs.transport_and_storage_cost
        + annual_emissions_cost_eur
    )
    return initial_capex_eur, annual_revenue_eur, annual_total_cost_eur


def calculate_sector_npv(sector: str, inputs: ScenarioInputs) -> float:
    """Calculate NPV for one sector and one explicit scenario."""

    initial_capex_eur, annual_revenue_eur, annual_total_cost_eur = (
        _sector_financial_components(sector, inputs)
    )
    annual_net_cash_flow_eur = annual_revenue_eur - annual_total_cost_eur
    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=int(round(inputs.lifetime_years)),
        discount_rate=inputs.discount_rate,
    )
    return -initial_capex_eur + annual_net_cash_flow_eur * present_value_factor


def calculate_metric_value(
    sector: str,
    inputs: ScenarioInputs,
    metric: str,
) -> float:
    """Calculate NPV, levelized net margin, or levelized cost for a scenario."""

    if metric not in FINANCIAL_METRIC_OPTIONS:
        valid_metrics = ", ".join(FINANCIAL_METRIC_OPTIONS)
        raise ValueError(
            f"Unknown financial metric {metric!r}. Use one of: {valid_metrics}."
        )
    npv_eur = calculate_sector_npv(sector, inputs)
    if metric == "NPV":
        return npv_eur / 1_000_000.0
    if metric == "LNM":
        return float(
            calculate_levelized_net_margin(
                npv_eur=npv_eur,
                annual_output=inputs.annual_output,
                lifetime_years=int(round(inputs.lifetime_years)),
                discount_rate=inputs.discount_rate,
            )
        )
    initial_capex_eur, _, annual_total_cost_eur = _sector_financial_components(
        sector,
        inputs,
    )
    return float(
        calculate_levelized_cost(
            initial_capex_eur=initial_capex_eur,
            annual_cost_eur=annual_total_cost_eur,
            annual_output=inputs.annual_output,
            lifetime_years=int(round(inputs.lifetime_years)),
            discount_rate=inputs.discount_rate,
        )
    )


def metric_axis_label(sector: str, metric: str) -> str:
    """Return a readable axis label for the selected sensitivity metric."""

    if metric == "NPV":
        return "Impact on NPV (million EUR)"
    if metric == "LNM":
        return f"Impact on levelized net margin (EUR/{SECTOR_UNITS[sector]})"
    if metric == "LCOX":
        levelized_cost_name = "LCOE" if sector == "electricity" else "LCOC"
        return f"Impact on {levelized_cost_name} (EUR/{SECTOR_UNITS[sector]})"

    valid_metrics = ", ".join(FINANCIAL_METRIC_OPTIONS)
    raise ValueError(
        f"Unknown financial metric {metric!r}. Use one of: {valid_metrics}."
    )


def build_sensitivity_table(
    sector: str,
    inputs: ScenarioInputs,
    variation_fraction: float,
    metric: str = "NPV",
    included_attributes: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Calculate one-factor-at-a-time tornado values around a scenario.

    When ``included_attributes`` is provided, only parameters whose ScenarioInputs
    attribute is listed are included. The default remains all sector parameters.
    """

    base_metric_value = calculate_metric_value(sector, inputs, metric)
    selected_attributes = (
        None if included_attributes is None else set(included_attributes)
    )
    rows = []
    for parameter in SENSITIVITY_PARAMETERS[sector]:
        if (
            selected_attributes is not None
            and parameter.attribute not in selected_attributes
        ):
            continue
        base_value = getattr(inputs, parameter.attribute)
        low_value = max(parameter.minimum, base_value * (1.0 - variation_fraction))
        high_value = max(parameter.minimum, base_value * (1.0 + variation_fraction))
        low_inputs = replace(inputs, **{parameter.attribute: low_value})
        high_inputs = replace(inputs, **{parameter.attribute: high_value})
        low_metric_value = calculate_metric_value(
            sector,
            low_inputs,
            metric,
        )
        high_metric_value = calculate_metric_value(
            sector,
            high_inputs,
            metric,
        )
        low_impact = low_metric_value - base_metric_value
        high_impact = high_metric_value - base_metric_value
        low_change = _relative_change_label(base_value, low_value)
        high_change = _relative_change_label(base_value, high_value)
        if metric == "LCOX":
            favorable_impact = min(low_impact, high_impact)
            unfavorable_impact = max(low_impact, high_impact)
            low_is_favorable = low_impact <= high_impact
        else:
            favorable_impact = max(low_impact, high_impact)
            unfavorable_impact = min(low_impact, high_impact)
            low_is_favorable = low_impact >= high_impact
        favorable_change = low_change if low_is_favorable else high_change
        unfavorable_change = high_change if low_is_favorable else low_change
        rows.append(
            {
                "parameter": parameter.label,
                "base_value": base_value,
                "low_value": low_value,
                "high_value": high_value,
                "low_metric_value": low_metric_value,
                "high_metric_value": high_metric_value,
                "low_impact": low_impact,
                "high_impact": high_impact,
                "favorable_impact": favorable_impact,
                "unfavorable_impact": unfavorable_impact,
                "favorable_change": favorable_change,
                "unfavorable_change": unfavorable_change,
                "max_abs_impact": max(
                    abs(low_impact),
                    abs(high_impact),
                ),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "parameter",
                "base_value",
                "low_value",
                "high_value",
                "low_metric_value",
                "high_metric_value",
                "low_impact",
                "high_impact",
                "favorable_impact",
                "unfavorable_impact",
                "favorable_change",
                "unfavorable_change",
                "max_abs_impact",
            ]
        )

    return pd.DataFrame(rows).sort_values(
        "max_abs_impact",
        ascending=False,
    )


def plot_tornado(
    sensitivity_table: pd.DataFrame,
    title: str,
    x_axis_label: str = "Impact on NPV (million EUR)",
    output_path: Path | None = None,
) -> plt.Figure:
    """Plot a tornado diagram from a sensitivity table."""

    if sensitivity_table.empty:
        raise ValueError("sensitivity_table must contain at least one row.")

    table = sensitivity_table.sort_values(
        "max_abs_impact",
        ascending=True,
    )
    labels = table["parameter"].tolist()
    favorable = table["favorable_impact"].astype(float).tolist()
    unfavorable = table["unfavorable_impact"].astype(float).tolist()
    favorable_changes = table["favorable_change"].tolist()
    unfavorable_changes = table["unfavorable_change"].tolist()
    y_positions = list(range(len(table)))

    fig_height = max(4.8, 0.48 * len(labels) + 1.5)
    fig, ax = plt.subplots(figsize=(8.6, fig_height), dpi=160)
    ax.barh(
        y_positions,
        unfavorable,
        height=0.5,
        color="#ff6468",
        label="Worse for selected financial metric",
    )
    ax.barh(
        y_positions,
        favorable,
        height=0.5,
        color="#69b36d",
        label="Better for selected financial metric",
    )
    ax.axvline(0, color="#222222", linewidth=1.0)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=9, color="#26345d")
    ax.set_title(title, fontsize=13, color="#26345d", loc="left", pad=12)
    ax.set_xlabel(x_axis_label, fontsize=9, color="#26345d")
    ax.grid(axis="x", color="#e8e8e8", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.13),
        frameon=False,
        fontsize=8,
        ncol=2,
    )
    ax.tick_params(axis="x", colors="#4e5a7f", labelsize=8)
    ax.tick_params(axis="y", left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    max_abs = float(
        table[["unfavorable_impact", "favorable_impact"]]
        .abs()
        .to_numpy()
        .max()
    )
    margin = max(1.0, 0.30 * max_abs)
    ax.set_xlim(-max_abs - margin, max_abs + margin)
    label_offset = margin * 0.10
    annotations = (
        (favorable, favorable_changes, "#2c6f32"),
        (unfavorable, unfavorable_changes, "#9a3033"),
    )
    for values, changes, color in annotations:
        for y_position, value, change in zip(y_positions, values, changes):
            is_negative = value < 0
            ax.text(
                value - label_offset if is_negative else value + label_offset,
                y_position,
                change,
                va="center",
                ha="right" if is_negative else "left",
                fontsize=8,
                color=color,
            )
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout(pad=1.4)

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")

    return fig


def figure_to_png_bytes(fig: plt.Figure) -> bytes:
    """Serialize a Matplotlib figure as PNG bytes."""

    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    return buffer.getvalue()


def _single_value_result(result: Mapping[str, Iterable[object]]) -> dict[str, float]:
    """Flatten one-element deterministic result mappings."""

    flattened: dict[str, float] = {}
    for key, value in result.items():
        item = list(value)[0]
        if isinstance(item, (int, float)):
            flattened[key] = float(item)
    return flattened


def _relative_change_label(base_value: float, changed_value: float) -> str:
    """Format the actual relative input movement for a tornado side."""

    if base_value == 0:
        return "0%" if changed_value == 0 else "n/a"
    relative_change = (changed_value / base_value - 1.0) * 100.0
    return f"{relative_change:+.0f}%"
