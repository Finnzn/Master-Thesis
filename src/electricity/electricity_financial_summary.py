"""Configure electricity-sector financial summaries and exports.

This module is the bridge between model calculations and thesis artefacts. It
runs deterministic and Monte Carlo electricity NPV calculations, writes raw and
processed CSV files, and saves comparison figures.

The output split is intentional:
- raw CSVs contain sampled or deterministic expected model inputs;
- processed CSVs contain derived quantities such as capacity, costs, cash flow,
  and NPV;
- figures summarize those outputs for interpretation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from electricity.electricity_npv_deterministic import (
    calculate_deterministic_electricity_results
)
from electricity.electricity_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    RETROFIT_BAU_MODES,
    simulate_electricity_results,
)
from financial_summary_workflow import SectorSummaryConfig, SectorSummaryWorkflow


ELECTRICITY_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "hard_coal": "Hard coal",
    "hard_coal_ccs": "Hard coal + CCS",
    "ccgt": "CCGT",
    "ccgt_ccs": "CCGT + CCS",
    "nuclear": "Nuclear",
    "wind_offshore": "Wind Offshore",
    "wind_onshore": "Wind Onshore",
    "pv": "PV",
    "biogas": "Biogas",
    "beccs": "BECCS",
}

# Columns exported as raw inputs. These are values that enter the model directly:
# sampled techno-economic assumptions, fixed prices, value factor, and carbon
# price.
ELECTRICITY_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "annual_output_mwh",
    "full_load_hours_per_year",
    "lifetime_years",
    "capex_eur_per_kw",
    "fixed_opex_eur_per_kw_year",
    "variable_opex_eur_per_mwh",
    "fuel_consumption_mwh_th_per_mwh_e",
    "emissions_tco2_per_mwh_e",
    "fuel_price_eur_per_mwh_th",
    "electricity_price_eur_per_mwh",
    "value_factor",
    "carbon_price_eur_per_t",
    "transport_and_storage_share_of_capture_cost",
    "transport_and_storage_cost_input_eur_per_mwh",
)

# Columns exported as processed outputs. These are derived from the raw inputs by
# the capacity, cost, cash-flow, and NPV calculations.
ELECTRICITY_PROCESSED_OUTPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "capacity_mw",
    "capacity_kw",
    "initial_capex_eur",
    "captured_electricity_price_eur_per_mwh",
    "annual_revenue_eur",
    "annual_fixed_opex_eur",
    "annual_variable_opex_eur",
    "annual_fuel_cost_eur",
    "capture_cost_excluding_transport_and_storage_eur_per_mwh",
    "transport_and_storage_cost_eur_per_mwh",
    "annual_transport_and_storage_cost_eur",
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_mwh",
    "present_value_total_cost_eur",
    "lcoe_eur_per_mwh",
    "levelized_profit_margin_eur_per_mwh",
)

# Internal simulation arrays use `run_id`; exported CSVs use `simulation_id`
# because that name is clearer for thesis readers.
EXPORT_SIMULATION_ID_RENAME = {"run_id": "simulation_id"}
EXPORT_SORT_COLUMNS = ("simulation_id", "technology")

ELECTRICITY_FINANCIAL_METRIC_OPTIONS = {
    "NPV": {
        "metric_column": "npv_eur",
        "metric_unit": "EUR",
        "scale": 1_000_000.0,
        "summary_column": "npv_m_eur",
        "axis_label": "NPV (million EUR)",
        "title_unit": "million EUR",
        "file_metric": "NPV",
        "ranking_label": "NPV",
        "higher_is_better": True,
        "color_by_sign": True,
        "zero_baseline": False,
    },
    "LPM": {
        "metric_column": "levelized_profit_margin_eur_per_mwh",
        "metric_unit": "EUR/MWh",
        "scale": 1.0,
        "summary_column": "levelized_profit_margin_eur_per_mwh",
        "axis_label": "Levelized profit margin (EUR/MWh)",
        "title_unit": "EUR/MWh",
        "file_metric": "Levelized_Profit_Margin_per_MWh",
        "ranking_label": "levelized profit margin",
        "higher_is_better": True,
        "color_by_sign": True,
        "zero_baseline": False,
    },
    "LCOX": {
        "metric_column": "lcoe_eur_per_mwh",
        "metric_unit": "EUR/MWh",
        "scale": 1.0,
        "summary_column": "lcoe_eur_per_mwh",
        "axis_label": "LCOE (EUR/MWh)",
        "title_unit": "EUR/MWh",
        "file_metric": "LCOE",
        "ranking_label": "LCOE",
        "higher_is_better": False,
        "color_by_sign": False,
        "zero_baseline": True,
    },
}

_WORKFLOW = SectorSummaryWorkflow(
    SectorSummaryConfig(
        sector_key="electricity",
        sector_name="Electricity",
        technology_labels=ELECTRICITY_TECHNOLOGY_LABELS,
        raw_input_columns=ELECTRICITY_RAW_INPUT_COLUMNS,
        processed_output_columns=ELECTRICITY_PROCESSED_OUTPUT_COLUMNS,
        financial_metrics=ELECTRICITY_FINANCIAL_METRIC_OPTIONS,
        simulate_results=simulate_electricity_results,
        deterministic_results=calculate_deterministic_electricity_results,
        default_sample_size=DEFAULT_SAMPLE_SIZE,
        default_random_seed=DEFAULT_RANDOM_SEED,
        default_retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
        retrofit_bau_modes=RETROFIT_BAU_MODES,
        simulation_id_rename=EXPORT_SIMULATION_ID_RENAME,
        export_sort_columns=EXPORT_SORT_COLUMNS,
    )
)

# Compatibility names retained for notebooks and existing command lines.
_electricity_financial_metric_config = _WORKFLOW.metric_config
_with_electricity_display_labels = _WORKFLOW.with_display_labels
_with_deterministic_retrofit_mode = _WORKFLOW.with_deterministic_retrofit_mode
electricity_npv_distribution_summary_million_eur = _WORKFLOW.distribution_summary_million_eur
electricity_npv_distribution_summary = _WORKFLOW.distribution_summary
_distribution_stat = _WORKFLOW.distribution_stat
calculate_mean_electricity_npv_million_eur = _WORKFLOW.calculate_mean_npv_million_eur
calculate_mean_electricity_npv = _WORKFLOW.calculate_mean_npv
calculate_deterministic_electricity_npv_million_eur = _WORKFLOW.calculate_deterministic_npv_million_eur
calculate_deterministic_electricity_npv = _WORKFLOW.calculate_deterministic_npv
save_electricity_mean_npv_figure = _WORKFLOW.save_mean_figure
save_electricity_deterministic_npv_figure = _WORKFLOW.save_deterministic_figure
save_electricity_mean_npv_outputs = _WORKFLOW.save_mean_outputs
calculate_electricity_npv_rankings_from_results = _WORKFLOW.calculate_rankings_from_results
calculate_electricity_npv_rankings = _WORKFLOW.calculate_rankings
save_electricity_npv_ranking_outputs = _WORKFLOW.save_ranking_outputs
generate_electricity_npv_rankings = _WORKFLOW.generate_rankings
save_electricity_deterministic_npv_outputs = _WORKFLOW.save_deterministic_outputs
save_electricity_npv_outputs = _WORKFLOW.save_all_outputs
save_electricity_npv_figures = _WORKFLOW.save_figures


def _project_root() -> Path:
    return _WORKFLOW.project_root()


def parse_args() -> argparse.Namespace:
    return _WORKFLOW.parse_args()


def main() -> None:
    _WORKFLOW.main()


if __name__ == "__main__":
    main()
