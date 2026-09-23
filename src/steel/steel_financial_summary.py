"""Configure steel-sector financial summaries and exports.

This module mirrors the electricity NPV summary workflow for the steel sector:
it runs deterministic and Monte Carlo steel NPV calculations, writes raw and
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

from steel.steel_npv_deterministic import calculate_deterministic_steel_results
from steel.steel_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    RETROFIT_BAU_MODES,
    simulate_steel_results,
)
from financial_summary_workflow import SectorSummaryConfig, SectorSummaryWorkflow


STEEL_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "bf_bof_bau": "BF-BOF BAU",
    "scrap_eaf": "Scrap-EAF",
    "ng_dri_eaf_bau": "NG-DRI-EAF BAU",
    "h2_dri_eaf": "H2-DRI-EAF",
    "moe": "MOE",
    "ael_eaf": "AEL-EAF",
    "bf_bof_ccs": "BF + BOF + CCS",
    "ng_dri_eaf_ccs": "NG-DRI-EAF + CCS",
}

# Columns exported as raw inputs. These are values that enter the steel model
# directly after retrofit changes have been resolved against the chosen BAU
# baseline.
STEEL_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "annual_output_tcs",
    "lifetime_years",
    "capex_eur_per_tcs",
    "fixed_opex_eur_per_tcs",
    "variable_opex_eur_per_tcs",
    "fuel_type",
    "fuel_consumption_mwh_th_per_tcs",
    "hydrogen_consumption_kg_per_tcs",
    "charcoal_consumption_mwh_th_per_tcs",
    "electricity_consumption_mwh_per_tcs",
    "emissions_tco2_per_tcs",
    "fuel_price_eur_per_mwh_th",
    "pci_coking_coal_mix_price_eur_per_mwh_th",
    "charcoal_price_eur_per_mwh_th",
    "gas_price_eur_per_mwh_th",
    "green_hydrogen_price_eur_per_kg",
    "electricity_price_eur_per_mwh",
    "steel_price_eur_per_tcs",
    "carbon_price_eur_per_t",
    "transport_and_storage_share_of_capture_cost",
)

# Columns exported as processed outputs. These are derived from the raw inputs by
# the cost, cash-flow, and NPV calculations.
STEEL_PROCESSED_OUTPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "initial_capex_eur",
    "annual_revenue_eur",
    "annual_fixed_opex_eur",
    "annual_variable_opex_eur",
    "annual_pci_coking_coal_cost_eur",
    "annual_charcoal_cost_eur",
    "annual_natural_gas_cost_eur",
    "annual_hydrogen_cost_eur",
    "annual_fuel_cost_eur",
    "annual_electricity_cost_eur",
    "capture_cost_excluding_transport_and_storage_eur_per_tcs",
    "transport_and_storage_cost_eur_per_tcs",
    "annual_transport_and_storage_cost_eur",
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_tcs",
    "present_value_total_cost_eur",
    "lcos_eur_per_tcs",
    "levelized_profit_margin_eur_per_tcs",
)

# Internal simulation arrays use `run_id`; exported CSVs use `simulation_id`
# because that name is clearer for thesis readers.
EXPORT_SIMULATION_ID_RENAME = {"run_id": "simulation_id"}
EXPORT_SORT_COLUMNS = ("simulation_id", "technology")

STEEL_FINANCIAL_METRIC_OPTIONS = {
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
        "axis_tick_step": 500.0,
    },
    "LPM": {
        "metric_column": "levelized_profit_margin_eur_per_tcs",
        "metric_unit": "EUR/tCS",
        "scale": 1.0,
        "summary_column": "levelized_profit_margin_eur_per_tcs",
        "axis_label": "Levelized profit margin (EUR/tCS)",
        "title_unit": "EUR/tCS",
        "file_metric": "Levelized_Profit_Margin_per_tCS",
        "ranking_label": "levelized profit margin",
        "higher_is_better": True,
        "color_by_sign": True,
        "zero_baseline": False,
    },
    "LCOX": {
        "metric_column": "lcos_eur_per_tcs",
        "metric_unit": "EUR/tCS",
        "scale": 1.0,
        "summary_column": "lcos_eur_per_tcs",
        "axis_label": "LCOS (EUR/tCS)",
        "title_unit": "EUR/tCS",
        "file_metric": "LCOS",
        "ranking_label": "LCOS",
        "higher_is_better": False,
        "color_by_sign": False,
        "zero_baseline": True,
    },
}

_WORKFLOW = SectorSummaryWorkflow(
    SectorSummaryConfig(
        sector_key="steel",
        sector_name="Steel",
        technology_labels=STEEL_TECHNOLOGY_LABELS,
        raw_input_columns=STEEL_RAW_INPUT_COLUMNS,
        processed_output_columns=STEEL_PROCESSED_OUTPUT_COLUMNS,
        financial_metrics=STEEL_FINANCIAL_METRIC_OPTIONS,
        simulate_results=simulate_steel_results,
        deterministic_results=calculate_deterministic_steel_results,
        default_sample_size=DEFAULT_SAMPLE_SIZE,
        default_random_seed=DEFAULT_RANDOM_SEED,
        default_retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
        retrofit_bau_modes=RETROFIT_BAU_MODES,
        simulation_id_rename=EXPORT_SIMULATION_ID_RENAME,
        export_sort_columns=EXPORT_SORT_COLUMNS,
    )
)

# Compatibility names retained for notebooks and existing command lines.
_steel_financial_metric_config = _WORKFLOW.metric_config
_with_steel_display_labels = _WORKFLOW.with_display_labels
_with_deterministic_retrofit_mode = _WORKFLOW.with_deterministic_retrofit_mode
steel_npv_distribution_summary_million_eur = _WORKFLOW.distribution_summary_million_eur
steel_npv_distribution_summary = _WORKFLOW.distribution_summary
_distribution_stat = _WORKFLOW.distribution_stat
calculate_mean_steel_npv_million_eur = _WORKFLOW.calculate_mean_npv_million_eur
calculate_mean_steel_npv = _WORKFLOW.calculate_mean_npv
calculate_deterministic_steel_npv_million_eur = _WORKFLOW.calculate_deterministic_npv_million_eur
calculate_deterministic_steel_npv = _WORKFLOW.calculate_deterministic_npv
save_steel_mean_npv_figure = _WORKFLOW.save_mean_figure
save_steel_deterministic_npv_figure = _WORKFLOW.save_deterministic_figure
save_steel_mean_npv_outputs = _WORKFLOW.save_mean_outputs
calculate_steel_npv_rankings_from_results = _WORKFLOW.calculate_rankings_from_results
calculate_steel_npv_rankings = _WORKFLOW.calculate_rankings
save_steel_npv_ranking_outputs = _WORKFLOW.save_ranking_outputs
generate_steel_npv_rankings = _WORKFLOW.generate_rankings
save_steel_deterministic_npv_outputs = _WORKFLOW.save_deterministic_outputs
save_steel_npv_outputs = _WORKFLOW.save_all_outputs
save_steel_npv_figures = _WORKFLOW.save_figures


def _project_root() -> Path:
    return _WORKFLOW.project_root()


def parse_args() -> argparse.Namespace:
    return _WORKFLOW.parse_args()


def main() -> None:
    _WORKFLOW.main()


if __name__ == "__main__":
    main()
