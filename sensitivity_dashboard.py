"""Streamlit dashboard for deterministic NPV sensitivity analysis."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from sensitivity_analysis import (  # noqa: E402
    METRIC_SPECIFIC,
    METRIC_TOTAL,
    SECTOR_DISPLAY_NAMES,
    SECTOR_UNITS,
    available_technologies,
    base_inputs,
    build_sensitivity_table,
    calculate_metric_value,
    calculate_sector_npv,
    display_label,
    figure_to_png_bytes,
    metric_axis_label,
    plot_tornado,
)


st.set_page_config(
    page_title="NPV Sensitivity Dashboard",
    layout="wide",
)


def main() -> None:
    """Render the sensitivity-analysis dashboard."""

    st.title("NPV Sensitivity Dashboard")
    st.caption("Deterministic one-factor-at-a-time sensitivity around editable inputs.")

    cement_tab, electricity_tab = st.tabs(["Cement", "Electricity"])
    with cement_tab:
        render_sector_dashboard("cement")
    with electricity_tab:
        render_sector_dashboard("electricity")


def render_sector_dashboard(sector: str) -> None:
    """Render controls and outputs for one sector."""

    technologies = available_technologies(sector)
    technology = st.selectbox(
        "Technology",
        technologies,
        format_func=display_label,
        key=f"{sector}_technology",
    )
    defaults = base_inputs(sector, technology)

    controls, figure_area = st.columns([0.34, 0.66], gap="large")
    with controls:
        st.subheader("Scenario Inputs")
        variation_percent = st.slider(
            "Tornado variation",
            min_value=1,
            max_value=75,
            value=20,
            step=1,
            format="%d%%",
            key=f"{sector}_variation",
        )
        metric = st.selectbox(
            "NPV metric",
            [METRIC_TOTAL, METRIC_SPECIFIC],
            format_func=lambda value: format_metric_option(sector, value),
            key=f"{sector}_metric",
        )
        scenario_inputs = build_input_controls(sector, technology, defaults)

    base_npv = calculate_sector_npv(sector, scenario_inputs)
    base_metric_value = calculate_metric_value(sector, scenario_inputs, metric)
    sensitivity_table = build_sensitivity_table(
        sector=sector,
        inputs=scenario_inputs,
        variation_fraction=variation_percent / 100.0,
        metric=metric,
    )
    title = (
        f"Tornado Diagram: {SECTOR_DISPLAY_NAMES[sector]} "
        f"{display_label(technology)} NPV"
    )
    x_axis_label = metric_axis_label(sector, metric)
    fig = plot_tornado(
        sensitivity_table,
        title=title,
        x_axis_label=x_axis_label,
    )

    with figure_area:
        metric_columns = st.columns(3)
        metric_columns[0].metric(
            selected_metric_label(sector, metric),
            format_metric_value(sector, metric, base_metric_value),
        )
        metric_columns[1].metric("Variation", f"+/- {variation_percent}%")
        metric_columns[2].metric("Technology", display_label(technology))
        st.pyplot(fig, clear_figure=False)

        png_bytes = figure_to_png_bytes(fig)
        filename = (
            f"{date.today().isoformat()}-Sensitivity_"
            f"{SECTOR_DISPLAY_NAMES[sector]}_{technology}_{metric}.png"
        )
        button_columns = st.columns([0.5, 0.5])
        button_columns[0].download_button(
            "Download graph",
            data=png_bytes,
            file_name=filename,
            mime="image/png",
            key=f"{sector}_download",
        )
        if button_columns[1].button("Save graph to figures", key=f"{sector}_save"):
            output_path = PROJECT_ROOT / "figures" / filename
            plot_tornado(
                sensitivity_table,
                title=title,
                x_axis_label=x_axis_label,
                output_path=output_path,
            )
            st.success(f"Saved {output_path.relative_to(PROJECT_ROOT)}")

        with st.expander("Sensitivity values"):
            st.dataframe(
                format_sensitivity_table(sensitivity_table, x_axis_label),
                width="stretch",
            )

    plt.close(fig)


def build_input_controls(sector: str, technology: str, defaults):
    """Build sector-specific numeric controls and return scenario inputs."""

    unit = SECTOR_UNITS[sector]
    annual_output_label = {
        "cement": "Annual production (t/year)",
        "electricity": "Annual generation (MWh/year)",
    }[sector]
    sales_price_label = {
        "cement": "Cement price (EUR/t)",
        "electricity": "Power price (EUR/MWh)",
    }[sector]
    capex_label = {
        "cement": "Investment cost (EUR/t)",
        "electricity": "Investment cost (EUR/kW)",
    }[sector]
    fixed_opex_label = {
        "cement": "Fixed OPEX (EUR/t)",
        "electricity": "Fixed OPEX (EUR/kW/year)",
    }[sector]
    variable_opex_label = {
        "cement": "Variable OPEX (EUR/t)",
        "electricity": "Variable OPEX (EUR/MWh)",
    }[sector]
    fuel_consumption_label = {
        "cement": "Fuel use (MWh_th/t)",
        "electricity": "Fuel use (MWh_th/MWh)",
    }[sector]
    emissions_label = {
        "cement": "Direct emissions (tCO2/t)",
        "electricity": "Direct emissions (tCO2/MWh)",
    }[sector]

    annual_output = st.number_input(
        annual_output_label,
        min_value=1.0,
        value=float(defaults.annual_output),
        step=max(1.0, defaults.annual_output * 0.05),
        key=f"{sector}_{technology}_annual_output",
    )
    lifetime_years = st.number_input(
        "Lifetime (years)",
        min_value=1.0,
        value=float(defaults.lifetime_years),
        step=1.0,
        key=f"{sector}_{technology}_lifetime",
    )
    full_load_hours = defaults.full_load_hours
    if sector == "electricity":
        full_load_hours = st.number_input(
            "Full-load hours (h/year)",
            min_value=1.0,
            value=float(defaults.full_load_hours),
            step=max(1.0, defaults.full_load_hours * 0.05),
            key=f"{sector}_{technology}_full_load_hours",
        )
    discount_rate_percent = st.number_input(
        "Interest rate (%)",
        min_value=0.0,
        value=float(defaults.discount_rate * 100.0),
        step=0.25,
        key=f"{sector}_{technology}_discount",
    )
    sales_price = st.number_input(
        sales_price_label,
        min_value=0.0,
        value=float(defaults.sales_price),
        step=max(0.1, defaults.sales_price * 0.05),
        key=f"{sector}_{technology}_sales_price",
    )
    capex = st.number_input(
        capex_label,
        min_value=0.0,
        value=float(defaults.capex),
        step=max(0.1, defaults.capex * 0.05),
        key=f"{sector}_{technology}_capex",
    )
    fixed_opex = st.number_input(
        fixed_opex_label,
        min_value=0.0,
        value=float(defaults.fixed_opex),
        step=max(0.1, defaults.fixed_opex * 0.05),
        key=f"{sector}_{technology}_fixed_opex",
    )
    variable_opex = st.number_input(
        variable_opex_label,
        min_value=0.0,
        value=float(defaults.variable_opex),
        step=max(0.1, defaults.variable_opex * 0.05),
        key=f"{sector}_{technology}_variable_opex",
    )
    fuel_consumption = st.number_input(
        fuel_consumption_label,
        min_value=0.0,
        value=float(defaults.fuel_consumption),
        step=max(0.001, defaults.fuel_consumption * 0.05),
        format="%.4f",
        key=f"{sector}_{technology}_fuel_consumption",
    )
    fuel_price = st.number_input(
        "Fuel price (EUR/MWh_th)",
        min_value=0.0,
        value=float(defaults.fuel_price),
        step=max(0.1, defaults.fuel_price * 0.05),
        key=f"{sector}_{technology}_fuel_price",
    )
    electricity_consumption = defaults.electricity_consumption
    electricity_price = defaults.electricity_price
    if sector == "cement":
        electricity_consumption = st.number_input(
            f"Electricity use (MWh/{unit})",
            min_value=0.0,
            value=float(defaults.electricity_consumption),
            step=max(0.001, defaults.electricity_consumption * 0.05),
            format="%.4f",
            key=f"{sector}_{technology}_electricity_consumption",
        )
        electricity_price = st.number_input(
            "Electricity price (EUR/MWh)",
            min_value=0.0,
            value=float(defaults.electricity_price),
            step=max(0.1, defaults.electricity_price * 0.05),
            key=f"{sector}_{technology}_electricity_price",
        )

    emissions = st.number_input(
        emissions_label,
        min_value=0.0,
        value=float(defaults.emissions),
        step=max(0.001, defaults.emissions * 0.05),
        format="%.4f",
        key=f"{sector}_{technology}_emissions",
    )
    carbon_price = st.number_input(
        "Carbon price (EUR/tCO2)",
        min_value=0.0,
        value=float(defaults.carbon_price),
        step=max(0.1, defaults.carbon_price * 0.05),
        key=f"{sector}_{technology}_carbon_price",
    )

    return defaults.__class__(
        annual_output=annual_output,
        lifetime_years=lifetime_years,
        discount_rate=discount_rate_percent / 100.0,
        sales_price=sales_price,
        capex=capex,
        fixed_opex=fixed_opex,
        variable_opex=variable_opex,
        fuel_consumption=fuel_consumption,
        fuel_price=fuel_price,
        electricity_consumption=electricity_consumption,
        electricity_price=electricity_price,
        emissions=emissions,
        carbon_price=carbon_price,
        full_load_hours=full_load_hours,
    )


def format_metric_option(sector: str, metric: str) -> str:
    """Return the selectbox label for one metric option."""

    if metric == METRIC_TOTAL:
        return "Total NPV (MEUR)"
    return f"Specific NPV (EUR/{SECTOR_UNITS[sector]})"


def selected_metric_label(sector: str, metric: str) -> str:
    """Return the headline metric label."""

    if metric == METRIC_TOTAL:
        return "Scenario NPV"
    return f"Scenario NPV/{SECTOR_UNITS[sector]}"


def format_metric_value(sector: str, metric: str, value: float) -> str:
    """Format a selected metric value for the dashboard headline."""

    if metric == METRIC_TOTAL:
        return f"{value:,.1f} MEUR"
    return f"{value:,.2f} EUR/{SECTOR_UNITS[sector]}"


def format_sensitivity_table(table: pd.DataFrame, impact_label: str) -> pd.DataFrame:
    """Format values for display in the dashboard table."""

    columns = [
        "parameter",
        "base_value",
        "low_value",
        "high_value",
        "unfavorable_change",
        "favorable_change",
        "unfavorable_impact",
        "favorable_impact",
    ]
    formatted = table.loc[:, columns].copy()
    return formatted.rename(
        columns={
            "parameter": "Parameter",
            "base_value": "Base value",
            "low_value": "Low value",
            "high_value": "High value",
            "unfavorable_change": "Unfavorable input change",
            "favorable_change": "Favorable input change",
            "unfavorable_impact": f"Unfavorable {impact_label}",
            "favorable_impact": f"Favorable {impact_label}",
        }
    )


if __name__ == "__main__":
    main()
