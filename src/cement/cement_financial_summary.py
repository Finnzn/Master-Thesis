"""Configure cement-sector financial summaries and exports.

This module mirrors the electricity NPV summary workflow for the cement sector:
it runs deterministic and Monte Carlo cement NPV calculations, writes raw and
processed CSV files, and saves comparison and ranking figures.

The output split is intentional:
- raw CSVs contain sampled or deterministic expected model inputs;
- processed CSVs contain derived costs, cash flow, and NPV;
- figures summarize those outputs for interpretation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Mapping

from cement.cement_npv_deterministic import calculate_deterministic_cement_results
from cement.cement_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    RETROFIT_BAU_MODES,
    simulate_cement_results,
)
from financial_summary_workflow import SectorSummaryConfig, SectorSummaryWorkflow


CEMENT_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "bau": "BAU",
    "electrification": "Electrification",
    "electrolysis": "Electrolysis",
    "clinker_substitution": "Clinker substitution",
    "alternative_fuels": "Alternative fuels",
    "efficiency_improvement": "Efficiency improvement",
    "waste_heat_recovery": "Waste heat recovery",
    "ccs": "CCS",
    "process_heat_integration": "Process heat integration",
}

# Columns exported as raw inputs. These are values that enter the cement model
# directly after retrofit changes have been resolved against the chosen BAU
# baseline.
CEMENT_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "annual_output_t",
    "lifetime_years",
    "capex_eur_per_t",
    "fixed_opex_eur_per_t",
    "variable_opex_eur_per_t",
    "fuel_consumption_mwh_th_per_t",
    "electricity_consumption_mwh_per_t",
    "emissions_tco2_per_t",
    "fuel_price_eur_per_mwh_th",
    "coal_price_eur_per_mwh_th",
    "biofuel_price_eur_per_mwh_th",
    "alternative_fuel_share_fraction",
    "fossil_fuel_share_fraction",
    "electricity_price_eur_per_mwh",
    "cement_price_eur_per_t",
    "carbon_price_eur_per_t",
    "transport_and_storage_share_of_capture_cost",
)

# Columns exported as processed outputs. These are derived from the raw inputs by
# the cost, cash-flow, and NPV calculations.
CEMENT_PROCESSED_OUTPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "initial_capex_eur",
    "annual_revenue_eur",
    "annual_fixed_opex_eur",
    "annual_variable_opex_eur",
    "annual_fuel_cost_eur",
    "annual_electricity_cost_eur",
    "capture_cost_excluding_transport_and_storage_eur_per_t",
    "transport_and_storage_cost_eur_per_t",
    "annual_transport_and_storage_cost_eur",
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_t",
    "present_value_total_cost_eur",
    "lcoc_eur_per_t",
    "levelized_profit_margin_eur_per_t",
)

# Internal simulation arrays use `run_id`; exported CSVs use `simulation_id`
# because that name is clearer for thesis readers.
EXPORT_SIMULATION_ID_RENAME = {"run_id": "simulation_id"}
EXPORT_SORT_COLUMNS = ("simulation_id", "technology")

CEMENT_FINANCIAL_METRIC_OPTIONS = {
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
        "metric_column": "levelized_profit_margin_eur_per_t",
        "metric_unit": "EUR/t",
        "scale": 1.0,
        "summary_column": "levelized_profit_margin_eur_per_t",
        "axis_label": "Levelized profit margin (EUR/t cement)",
        "title_unit": "EUR/t",
        "file_metric": "Levelized_Profit_Margin_per_t",
        "ranking_label": "levelized profit margin",
        "higher_is_better": True,
        "color_by_sign": True,
        "zero_baseline": False,
    },
    "LCOX": {
        "metric_column": "lcoc_eur_per_t",
        "metric_unit": "EUR/t",
        "scale": 1.0,
        "summary_column": "lcoc_eur_per_t",
        "axis_label": "LCOC (EUR/t cement)",
        "title_unit": "EUR/t",
        "file_metric": "LCOC",
        "ranking_label": "LCOC",
        "higher_is_better": False,
        "color_by_sign": False,
        "zero_baseline": True,
    },
}

_WORKFLOW = SectorSummaryWorkflow(
    SectorSummaryConfig(
        sector_key="cement",
        sector_name="Cement",
        technology_labels=CEMENT_TECHNOLOGY_LABELS,
        raw_input_columns=CEMENT_RAW_INPUT_COLUMNS,
        processed_output_columns=CEMENT_PROCESSED_OUTPUT_COLUMNS,
        financial_metrics=CEMENT_FINANCIAL_METRIC_OPTIONS,
        simulate_results=simulate_cement_results,
        deterministic_results=calculate_deterministic_cement_results,
        default_sample_size=DEFAULT_SAMPLE_SIZE,
        default_random_seed=DEFAULT_RANDOM_SEED,
        default_retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
        retrofit_bau_modes=RETROFIT_BAU_MODES,
        simulation_id_rename=EXPORT_SIMULATION_ID_RENAME,
        export_sort_columns=EXPORT_SORT_COLUMNS,
    )
)

# Compatibility names retained for notebooks and existing command lines.
_cement_financial_metric_config = _WORKFLOW.metric_config
_with_cement_display_labels = _WORKFLOW.with_display_labels
_with_deterministic_retrofit_mode = _WORKFLOW.with_deterministic_retrofit_mode
cement_npv_distribution_summary_million_eur = _WORKFLOW.distribution_summary_million_eur
cement_npv_distribution_summary = _WORKFLOW.distribution_summary
_distribution_stat = _WORKFLOW.distribution_stat
calculate_mean_cement_npv_million_eur = _WORKFLOW.calculate_mean_npv_million_eur
calculate_mean_cement_npv = _WORKFLOW.calculate_mean_npv
calculate_deterministic_cement_npv_million_eur = _WORKFLOW.calculate_deterministic_npv_million_eur
calculate_deterministic_cement_npv = _WORKFLOW.calculate_deterministic_npv
save_cement_mean_npv_figure = _WORKFLOW.save_mean_figure
save_cement_deterministic_npv_figure = _WORKFLOW.save_deterministic_figure
save_cement_mean_npv_outputs = _WORKFLOW.save_mean_outputs
calculate_cement_npv_rankings_from_results = _WORKFLOW.calculate_rankings_from_results
calculate_cement_npv_rankings = _WORKFLOW.calculate_rankings
save_cement_npv_ranking_outputs = _WORKFLOW.save_ranking_outputs
generate_cement_npv_rankings = _WORKFLOW.generate_rankings
save_cement_deterministic_npv_outputs = _WORKFLOW.save_deterministic_outputs
save_cement_npv_outputs = _WORKFLOW.save_all_outputs
save_cement_npv_figures = _WORKFLOW.save_figures


def _project_root() -> Path:
    return _WORKFLOW.project_root()


def parse_args() -> argparse.Namespace:
    return _WORKFLOW.parse_args()


def main() -> None:
    _WORKFLOW.main()


if __name__ == "__main__":
    main()
