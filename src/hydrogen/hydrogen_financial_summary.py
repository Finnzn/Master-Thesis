"""Configure hydrogen-sector financial summaries and exports.

This module mirrors the electricity NPV summary workflow for the hydrogen sector:
it runs deterministic and Monte Carlo hydrogen NPV calculations, writes raw and
processed CSV files, and saves comparison and ranking figures.

The output split is intentional:
- raw CSVs contain sampled or deterministic expected model inputs;
- processed CSVs contain derived costs, cash flow, and NPV;
- figures summarize those outputs for interpretation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Mapping

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hydrogen.hydrogen_npv_deterministic import calculate_deterministic_hydrogen_results
from hydrogen.hydrogen_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    RETROFIT_BAU_MODES,
    simulate_hydrogen_results,
)
from financial_summary_workflow import SectorSummaryConfig, SectorSummaryWorkflow


HYDROGEN_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "ng_smr": "NG-SMR",
    "ael": "AEL",
    "pem": "PEM",
    "soec": "SOEC",
    "methane_pyrolysis_tcd": "Methane pyrolysis (TCD)",
    "biomass_gasification": "Biomass gasification",
    "biomethane_smr": "Biomethane SMR",
    "ng_smr_ccs": "NG-SMR + CCS",
}

# Columns exported as raw inputs. These are values that enter the hydrogen model
# directly after retrofit changes have been resolved against the chosen BAU
# baseline.
HYDROGEN_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "annual_output_th2",
    "lifetime_years",
    "capex_eur_per_th2",
    "fixed_opex_eur_per_th2",
    "variable_opex_eur_per_th2",
    "fuel_type",
    "natural_gas_consumption_mwh_per_th2",
    "biomethane_consumption_mwh_per_th2",
    "biomass_consumption_mwh_per_th2",
    "electricity_consumption_mwh_per_th2",
    "emissions_tco2_per_th2",
    "gas_price_eur_per_mwh_th",
    "biomethane_price_eur_per_mwh_th",
    "biomass_price_eur_per_mwh_th",
    "electricity_price_eur_per_mwh",
    "hydrogen_price_eur_per_th2",
    "carbon_price_eur_per_t",
    "transport_and_storage_share_of_capture_cost",
)

# Columns exported as processed outputs. These are derived from the raw inputs by
# the cost, cash-flow, and NPV calculations.
HYDROGEN_PROCESSED_OUTPUT_COLUMNS = (
    "run_id",
    "technology",
    "technology_type",
    "retrofit_bau_mode",
    "initial_capex_eur",
    "annual_revenue_eur",
    "annual_fixed_opex_eur",
    "annual_variable_opex_eur",
    "annual_natural_gas_cost_eur",
    "annual_biomethane_cost_eur",
    "annual_biomass_cost_eur",
    "annual_fuel_cost_eur",
    "annual_electricity_cost_eur",
    "capture_cost_excluding_transport_and_storage_eur_per_th2",
    "transport_and_storage_cost_eur_per_th2",
    "annual_transport_and_storage_cost_eur",
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_th2",
    "present_value_total_cost_eur",
    "lcoh_eur_per_th2",
    "levelized_profit_margin_eur_per_th2",
)

# Internal simulation arrays use `run_id`; exported CSVs use `simulation_id`
# because that name is clearer for thesis readers.
EXPORT_SIMULATION_ID_RENAME = {"run_id": "simulation_id"}
EXPORT_SORT_COLUMNS = ("simulation_id", "technology")

HYDROGEN_FINANCIAL_METRIC_OPTIONS = {
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
        "metric_column": "levelized_profit_margin_eur_per_th2",
        "metric_unit": "EUR/tH2",
        "scale": 1.0,
        "summary_column": "levelized_profit_margin_eur_per_th2",
        "axis_label": "Levelized profit margin (EUR/tH2)",
        "title_unit": "EUR/tH2",
        "file_metric": "Levelized_Profit_Margin_per_tH2",
        "ranking_label": "levelized profit margin",
        "higher_is_better": True,
        "color_by_sign": True,
        "zero_baseline": False,
    },
    "LCOX": {
        "metric_column": "lcoh_eur_per_th2",
        "metric_unit": "EUR/tH2",
        "scale": 1.0,
        "summary_column": "lcoh_eur_per_th2",
        "axis_label": "LCOH (EUR/tH2)",
        "title_unit": "EUR/tH2",
        "file_metric": "LCOH",
        "ranking_label": "LCOH",
        "higher_is_better": False,
        "color_by_sign": False,
        "zero_baseline": True,
    },
}

_WORKFLOW = SectorSummaryWorkflow(
    SectorSummaryConfig(
        sector_key="hydrogen",
        sector_name="Hydrogen",
        technology_labels=HYDROGEN_TECHNOLOGY_LABELS,
        raw_input_columns=HYDROGEN_RAW_INPUT_COLUMNS,
        processed_output_columns=HYDROGEN_PROCESSED_OUTPUT_COLUMNS,
        financial_metrics=HYDROGEN_FINANCIAL_METRIC_OPTIONS,
        simulate_results=simulate_hydrogen_results,
        deterministic_results=calculate_deterministic_hydrogen_results,
        default_sample_size=DEFAULT_SAMPLE_SIZE,
        default_random_seed=DEFAULT_RANDOM_SEED,
        default_retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
        retrofit_bau_modes=RETROFIT_BAU_MODES,
        simulation_id_rename=EXPORT_SIMULATION_ID_RENAME,
        export_sort_columns=EXPORT_SORT_COLUMNS,
    )
)

# Compatibility names retained for notebooks and existing command lines.
_hydrogen_financial_metric_config = _WORKFLOW.metric_config
_with_hydrogen_display_labels = _WORKFLOW.with_display_labels
_with_deterministic_retrofit_mode = _WORKFLOW.with_deterministic_retrofit_mode
hydrogen_npv_distribution_summary_million_eur = _WORKFLOW.distribution_summary_million_eur
hydrogen_npv_distribution_summary = _WORKFLOW.distribution_summary
_distribution_stat = _WORKFLOW.distribution_stat
calculate_mean_hydrogen_npv_million_eur = _WORKFLOW.calculate_mean_npv_million_eur
calculate_mean_hydrogen_npv = _WORKFLOW.calculate_mean_npv
calculate_deterministic_hydrogen_npv_million_eur = _WORKFLOW.calculate_deterministic_npv_million_eur
calculate_deterministic_hydrogen_npv = _WORKFLOW.calculate_deterministic_npv
save_hydrogen_mean_npv_figure = _WORKFLOW.save_mean_figure
save_hydrogen_deterministic_npv_figure = _WORKFLOW.save_deterministic_figure
save_hydrogen_mean_npv_outputs = _WORKFLOW.save_mean_outputs
calculate_hydrogen_npv_rankings_from_results = _WORKFLOW.calculate_rankings_from_results
calculate_hydrogen_npv_rankings = _WORKFLOW.calculate_rankings
save_hydrogen_npv_ranking_outputs = _WORKFLOW.save_ranking_outputs
generate_hydrogen_npv_rankings = _WORKFLOW.generate_rankings
save_hydrogen_deterministic_npv_outputs = _WORKFLOW.save_deterministic_outputs
save_hydrogen_npv_outputs = _WORKFLOW.save_all_outputs
save_hydrogen_npv_figures = _WORKFLOW.save_figures


def _project_root() -> Path:
    return _WORKFLOW.project_root()


def parse_args() -> argparse.Namespace:
    return _WORKFLOW.parse_args()


def main() -> None:
    _WORKFLOW.main()


if __name__ == "__main__":
    main()
