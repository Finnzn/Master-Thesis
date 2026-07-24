"""Generate cement-sector financial-metric figures and CSV outputs.

This module mirrors the electricity NPV summary workflow for the cement sector:
it runs deterministic and Monte Carlo cement NPV calculations, writes raw and
processed CSV files, and saves comparison and ranking figures.

The output split is intentional:
- raw CSVs contain sampled or representative model inputs;
- processed CSVs contain derived costs, cash flow, and NPV;
- figures summarize those outputs for interpretation.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Mapping

import numpy as np

from cement.cement_npv_deterministic import calculate_deterministic_cement_results
from cement.cement_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    RETROFIT_BAU_MODES,
    simulate_cement_results,
)
from npv_summary import (
    dated_csv_path,
    deterministic_metric,
    deterministic_npv_million_eur,
    financial_metric_ranking_dataframe,
    mean_metric,
    mean_npv_million_eur,
    save_dataframe_csv,
    save_results_csv,
    summarize_financial_metric_rankings,
    summarize_metric_signs,
)
from npv_summary_plots import (
    dated_figure_path,
    fixed_financial_metric_bar_axis_config,
    plot_average_rank_bars,
    plot_financial_metric_technology_bars,
)


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
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_t",
    "present_value_total_cost_eur",
    "lcoc_eur_per_t",
    "levelized_net_margin_eur_per_t",
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
    "LNM": {
        "metric_column": "levelized_net_margin_eur_per_t",
        "metric_unit": "EUR/t",
        "scale": 1.0,
        "summary_column": "levelized_net_margin_eur_per_t",
        "axis_label": "Levelized net margin (EUR/t cement)",
        "title_unit": "EUR/t",
        "file_metric": "Levelized_Net_Margin_per_t",
        "ranking_label": "levelized net margin",
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


def _cement_financial_metric_config(financial_metric: str) -> Mapping[str, object]:
    """Return display and export settings for one cement financial metric."""

    if financial_metric not in CEMENT_FINANCIAL_METRIC_OPTIONS:
        valid_metrics = ", ".join(CEMENT_FINANCIAL_METRIC_OPTIONS)
        raise ValueError(
            f"Unknown financial_metric {financial_metric!r}. "
            f"Use one of: {valid_metrics}."
        )

    return CEMENT_FINANCIAL_METRIC_OPTIONS[financial_metric]


def _with_cement_display_labels(ranking_summary):
    """Return a ranking summary copy with human-readable technology labels."""

    return ranking_summary.assign(
        display_label=ranking_summary["technology"].map(CEMENT_TECHNOLOGY_LABELS).fillna(
            ranking_summary["technology"]
        )
    )


def _with_deterministic_retrofit_mode(
    results_by_technology: Mapping[str, Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    """Add the cement MC retrofit-mode column to deterministic export rows.

    The deterministic cement model does not need `retrofit_bau_mode` internally,
    but raw and processed cement CSV exports should keep the same column schema as
    Monte Carlo outputs.
    """

    export_results: dict[str, dict[str, object]] = {}
    for technology, results in results_by_technology.items():
        result_copy = dict(results)
        if "retrofit_bau_mode" not in result_copy:
            technology_type = str(np.asarray(result_copy["technology_type"]).item())
            mode = "deterministic" if technology_type == "retrofit" else "not_applicable"
            result_copy["retrofit_bau_mode"] = [mode]
        export_results[technology] = result_copy
    return export_results


def cement_npv_distribution_summary_million_eur(
    results_by_technology: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str] = CEMENT_TECHNOLOGY_LABELS,
) -> dict[str, dict[str, float]]:
    """Calculate mean, median, and percentile NPV summaries in million EUR."""

    summary: dict[str, dict[str, float]] = {}
    for technology, results in results_by_technology.items():
        if "npv_eur" not in results:
            raise KeyError(f"{technology!r} results do not contain 'npv_eur'.")
        label = labels.get(technology, technology)
        npv_million_eur = np.asarray(results["npv_eur"], dtype=float) / 1_000_000
        summary[label] = {
            "mean": float(npv_million_eur.mean()),
            "median": float(np.median(npv_million_eur)),
            "p05": float(np.percentile(npv_million_eur, 5)),
            "p95": float(np.percentile(npv_million_eur, 95)),
            **summarize_metric_signs(npv_million_eur),
        }
    return summary


def cement_npv_distribution_summary(
    results_by_technology: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str] = CEMENT_TECHNOLOGY_LABELS,
    financial_metric: str = "NPV",
) -> dict[str, dict[str, float]]:
    """Calculate mean, median, and percentile financial-metric summaries."""

    config = _cement_financial_metric_config(financial_metric)
    metric_column = str(config["metric_column"])
    scale = float(config["scale"])

    summary: dict[str, dict[str, float]] = {}
    for technology, results in results_by_technology.items():
        if metric_column not in results:
            raise KeyError(f"{technology!r} results do not contain {metric_column!r}.")
        label = labels.get(technology, technology)
        values = np.asarray(results[metric_column], dtype=float) / scale
        summary[label] = {
            "mean": float(values.mean()),
            "median": float(np.median(values)),
            "p05": float(np.percentile(values, 5)),
            "p95": float(np.percentile(values, 95)),
            **summarize_metric_signs(values),
        }
    return summary


def _distribution_stat(
    summary: Mapping[str, Mapping[str, float]],
    statistic: str,
) -> dict[str, float]:
    """Extract one statistic from the nested distribution summary."""

    return {label: values[statistic] for label, values in summary.items()}


def calculate_mean_cement_npv_million_eur(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> dict[str, float]:
    """Calculate mean simulated NPV by cement technology in million EUR."""

    return mean_npv_million_eur(
        results_by_item=simulate_cement_results(
            sample_size=sample_size,
            random_seed=random_seed,
            technologies=technologies,
            retrofit_bau_mode=retrofit_bau_mode,
        ),
        labels=CEMENT_TECHNOLOGY_LABELS,
    )


def calculate_mean_cement_npv(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    financial_metric: str = "NPV",
) -> dict[str, float]:
    """Calculate a mean simulated financial metric by cement technology."""

    config = _cement_financial_metric_config(financial_metric)
    return mean_metric(
        results_by_item=simulate_cement_results(
            sample_size=sample_size,
            random_seed=random_seed,
            technologies=technologies,
            retrofit_bau_mode=retrofit_bau_mode,
        ),
        labels=CEMENT_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )


def calculate_deterministic_cement_npv_million_eur(
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate deterministic NPV by cement technology in million EUR."""

    return deterministic_npv_million_eur(
        results_by_item=calculate_deterministic_cement_results(
            technologies=technologies
        ),
        labels=CEMENT_TECHNOLOGY_LABELS,
    )


def calculate_deterministic_cement_npv(
    technologies: tuple[str, ...] | None = None,
    financial_metric: str = "NPV",
) -> dict[str, float]:
    """Calculate a deterministic financial metric by cement technology."""

    config = _cement_financial_metric_config(financial_metric)
    return deterministic_metric(
        results_by_item=calculate_deterministic_cement_results(
            technologies=technologies
        ),
        labels=CEMENT_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )


def save_cement_mean_npv_figure(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    financial_metric: str = "NPV",
) -> Path:
    """Save the simulated mean NPV comparison figure for cement."""

    config = _cement_financial_metric_config(financial_metric)
    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    summary = cement_npv_distribution_summary(results, financial_metric=financial_metric)
    values = _distribution_stat(summary, "mean")
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Mean_{config['file_metric']}_{sector_name}",
        run_date=run_date,
    )
    return plot_financial_metric_technology_bars(
        values=values,
        output_path=output_path,
        title=f"Monte Carlo mean {config['ranking_label']} by cement technology",
        median_values=_distribution_stat(summary, "median"),
        lower_values=_distribution_stat(summary, "p05"),
        upper_values=_distribution_stat(summary, "p95"),
        sample_size=sample_size,
        random_seed=random_seed,
        x_axis_label=str(config["axis_label"]),
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )


def save_cement_deterministic_npv_figure(
    output_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Cement",
    financial_metric: str = "NPV",
) -> Path:
    """Save the deterministic NPV comparison figure for cement."""

    config = _cement_financial_metric_config(financial_metric)
    values = calculate_deterministic_cement_npv(financial_metric=financial_metric)
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Deterministic_{config['file_metric']}_{sector_name}",
        run_date=run_date,
    )
    return plot_financial_metric_technology_bars(
        values=values,
        output_path=output_path,
        title=f"Deterministic {config['ranking_label']} ({config['title_unit']})",
        x_axis_label=str(config["axis_label"]),
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )


def save_cement_mean_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save mean NPV figure plus raw-input, processed-output, and ranking outputs."""

    output_date = run_date or date.today()
    config = _cement_financial_metric_config(financial_metric)
    stem = f"Mean_{config['file_metric']}_{sector_name}"
    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    summary = cement_npv_distribution_summary(results, financial_metric=financial_metric)
    values = _distribution_stat(summary, "mean")
    figure_path = plot_financial_metric_technology_bars(
        values=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title=f"Monte Carlo mean {config['ranking_label']} by cement technology",
        median_values=_distribution_stat(summary, "median"),
        lower_values=_distribution_stat(summary, "p05"),
        upper_values=_distribution_stat(summary, "p95"),
        sample_size=sample_size,
        random_seed=random_seed,
        x_axis_label=str(config["axis_label"]),
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )
    raw_csv_path = save_results_csv(
        results_by_item=results,
        columns=CEMENT_RAW_INPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=raw_data_dir,
            stem=f"{stem}_raw_inputs",
            run_date=output_date,
        ),
        rename_columns=EXPORT_SIMULATION_ID_RENAME,
        sort_by=EXPORT_SORT_COLUMNS,
    )
    processed_csv_path = save_results_csv(
        results_by_item=results,
        columns=CEMENT_PROCESSED_OUTPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=processed_data_dir,
            stem=f"{stem}_processed_outputs",
            run_date=output_date,
        ),
        rename_columns=EXPORT_SIMULATION_ID_RENAME,
        sort_by=EXPORT_SORT_COLUMNS,
    )

    output_paths: list[Path] = [figure_path, raw_csv_path, processed_csv_path]
    if save_ranking_outputs:
        ranking, ranking_summary = calculate_cement_npv_rankings_from_results(
            results=results,
            sector_name=sector_name,
            financial_metric=financial_metric,
        )
        output_paths.extend(
            save_cement_npv_ranking_outputs(
                ranking=ranking,
                ranking_summary=ranking_summary,
                figure_dir=figure_dir,
                raw_data_dir=raw_data_dir,
                processed_data_dir=processed_data_dir,
                run_date=output_date,
                sector_name=sector_name,
                random_seed=random_seed,
                save_ranking_csv=save_ranking_csv,
                save_ranking_plots=save_ranking_plots,
                financial_metric=financial_metric,
            )
        )

    return tuple(output_paths)


def calculate_cement_npv_rankings_from_results(
    results: Mapping[str, Mapping[str, object]],
    sector_name: str = "Cement",
    financial_metric: str = "NPV",
):
    """Calculate raw and summary NPV rank tables from cement results."""

    config = _cement_financial_metric_config(financial_metric)
    ranking = financial_metric_ranking_dataframe(
        results_by_item=results,
        sector=sector_name,
        metric_column=str(config["metric_column"]),
        metric_unit=str(config["metric_unit"]),
        higher_is_better=bool(config["higher_is_better"]),
    )
    ranking_summary = summarize_financial_metric_rankings(ranking)
    return ranking, ranking_summary


def calculate_cement_npv_rankings(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    financial_metric: str = "NPV",
):
    """Run cement Monte Carlo simulations and return NPV ranking tables."""

    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    return calculate_cement_npv_rankings_from_results(
        results=results,
        sector_name=sector_name,
        financial_metric=financial_metric,
    )


def save_cement_npv_ranking_outputs(
    ranking,
    ranking_summary,
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Cement",
    random_seed: int | None = None,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save cement NPV ranking CSVs and/or plots."""

    output_date = run_date or date.today()
    config = _cement_financial_metric_config(financial_metric)
    output_paths: list[Path] = []
    if save_ranking_csv:
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking,
                output_path=dated_csv_path(
                    output_dir=raw_data_dir,
                    stem=f"{config['file_metric']}_Ranking_{sector_name}_raw",
                    run_date=output_date,
                ),
            )
        )
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking_summary,
                output_path=dated_csv_path(
                    output_dir=processed_data_dir,
                    stem=f"{config['file_metric']}_Ranking_{sector_name}_summary",
                    run_date=output_date,
                ),
            )
        )
    if save_ranking_plots:
        output_paths.append(
            plot_average_rank_bars(
                ranking_summary=_with_cement_display_labels(ranking_summary),
                output_path=dated_figure_path(
                    output_dir=figure_dir,
                    stem=f"Average_{config['file_metric']}_Rank_{sector_name}",
                    run_date=output_date,
                ),
                title=f"Monte Carlo {config['ranking_label']} Ranking",
                metric_label=str(config["ranking_label"]),
                random_seed=random_seed,
                higher_is_better=bool(config["higher_is_better"]),
            )
        )

    return tuple(output_paths)


def generate_cement_npv_rankings(
    figure_dir: Path | None = None,
    raw_data_dir: Path | None = None,
    processed_data_dir: Path | None = None,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
):
    """Return cement NPV ranking DataFrames and optionally save outputs."""

    ranking, ranking_summary = calculate_cement_npv_rankings(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
        sector_name=sector_name,
        retrofit_bau_mode=retrofit_bau_mode,
        financial_metric=financial_metric,
    )
    output_paths: tuple[Path, ...] = ()
    if save_ranking_outputs and (save_ranking_csv or save_ranking_plots):
        root = _project_root()
        output_paths = save_cement_npv_ranking_outputs(
            ranking=ranking,
            ranking_summary=ranking_summary,
            figure_dir=figure_dir or root / "figures",
            raw_data_dir=raw_data_dir or root / "data" / "raw",
            processed_data_dir=processed_data_dir or root / "data" / "processed",
            run_date=run_date,
            sector_name=sector_name,
            random_seed=random_seed,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=financial_metric,
        )

    return ranking, ranking_summary, output_paths


def save_cement_deterministic_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Cement",
    financial_metric: str = "NPV",
) -> tuple[Path, Path, Path]:
    """Save deterministic NPV figure plus raw-input and processed-output CSVs."""

    output_date = run_date or date.today()
    config = _cement_financial_metric_config(financial_metric)
    stem = f"Deterministic_{config['file_metric']}_{sector_name}"
    results = _with_deterministic_retrofit_mode(
        calculate_deterministic_cement_results()
    )
    values = deterministic_metric(
        results_by_item=results,
        labels=CEMENT_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )
    figure_path = plot_financial_metric_technology_bars(
        values=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title=f"Deterministic {config['ranking_label']} ({config['title_unit']})",
        x_axis_label=str(config["axis_label"]),
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )
    raw_csv_path = save_results_csv(
        results_by_item=results,
        columns=CEMENT_RAW_INPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=raw_data_dir,
            stem=f"{stem}_raw_inputs",
            run_date=output_date,
        ),
        rename_columns=EXPORT_SIMULATION_ID_RENAME,
        sort_by=EXPORT_SORT_COLUMNS,
    )
    processed_csv_path = save_results_csv(
        results_by_item=results,
        columns=CEMENT_PROCESSED_OUTPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=processed_data_dir,
            stem=f"{stem}_processed_outputs",
            run_date=output_date,
        ),
        rename_columns=EXPORT_SIMULATION_ID_RENAME,
        sort_by=EXPORT_SORT_COLUMNS,
    )

    return figure_path, raw_csv_path, processed_csv_path


def save_cement_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save simulated mean and deterministic cement NPV outputs."""

    return (
        *save_cement_mean_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            sample_size=sample_size,
            random_seed=random_seed,
            run_date=run_date,
            sector_name=sector_name,
            retrofit_bau_mode=retrofit_bau_mode,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=financial_metric,
        ),
        *save_cement_deterministic_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            run_date=run_date,
            sector_name=sector_name,
            financial_metric=financial_metric,
        ),
    )


def save_cement_npv_figures(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    financial_metric: str = "NPV",
) -> tuple[Path, Path]:
    """Save both simulated mean and deterministic cement NPV figures."""

    config = _cement_financial_metric_config(financial_metric)
    output_date = run_date or date.today()
    simulated_results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    simulated_summary = cement_npv_distribution_summary(
        simulated_results,
        financial_metric=financial_metric,
    )
    mean_values = _distribution_stat(simulated_summary, "mean")
    deterministic_values = calculate_deterministic_cement_npv(financial_metric=financial_metric)
    x_axis_limits, x_axis_ticks = fixed_financial_metric_bar_axis_config(
        sector="cement",
        financial_metric=financial_metric,
        distribution_summary=simulated_summary,
        deterministic_values=deterministic_values,
    )

    mean_path = plot_financial_metric_technology_bars(
        values=mean_values,
        output_path=dated_figure_path(
            output_dir=output_dir,
            stem=f"Mean_{config['file_metric']}_{sector_name}",
            run_date=output_date,
        ),
        title=f"Monte Carlo mean {config['ranking_label']} by cement technology",
        median_values=_distribution_stat(simulated_summary, "median"),
        lower_values=_distribution_stat(simulated_summary, "p05"),
        upper_values=_distribution_stat(simulated_summary, "p95"),
        sample_size=sample_size,
        random_seed=random_seed,
        x_axis_label=str(config["axis_label"]),
        x_axis_limits=x_axis_limits,
        x_axis_ticks=x_axis_ticks,
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )
    deterministic_path = plot_financial_metric_technology_bars(
        values=deterministic_values,
        output_path=dated_figure_path(
            output_dir=output_dir,
            stem=f"Deterministic_{config['file_metric']}_{sector_name}",
            run_date=output_date,
        ),
        title=f"Deterministic {config['ranking_label']} ({config['title_unit']})",
        x_axis_label=str(config["axis_label"]),
        x_axis_limits=x_axis_limits,
        x_axis_ticks=x_axis_ticks,
        higher_is_better=bool(config["higher_is_better"]),
        color_by_sign=bool(config["color_by_sign"]),
        zero_baseline=bool(config["zero_baseline"]),
    )
    return mean_path, deterministic_path


def _project_root() -> Path:
    """Return the repository root when this module is executed as a script."""

    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    """Parse command-line options for regenerating cement outputs."""

    parser = argparse.ArgumentParser(
        description="Generate cement-sector financial-metric comparison figures."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_project_root() / "figures",
        help="Directory where figures are saved.",
    )
    parser.add_argument(
        "--raw-data-dir",
        type=Path,
        default=_project_root() / "data" / "raw",
        help="Directory where raw sampled/model inputs are saved.",
    )
    parser.add_argument(
        "--processed-data-dir",
        type=Path,
        default=_project_root() / "data" / "processed",
        help="Directory where derived costs, revenues, and NPVs are saved.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Monte Carlo sample size for the mean comparison figure.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed for the mean comparison figure.",
    )
    parser.add_argument(
        "--retrofit-bau-mode",
        choices=RETROFIT_BAU_MODES,
        default=DEFAULT_RETROFIT_BAU_MODE,
        help="BAU baseline mode for retrofit cement technologies.",
    )
    parser.add_argument(
        "--kind",
        choices=("all", "mean", "deterministic"),
        default="all",
        help="Which figure to generate.",
    )
    parser.add_argument(
        "--sector-name",
        default="Cement",
        help="Sector name used in the output file name.",
    )
    parser.add_argument(
        "--no-data",
        action="store_true",
        help="Only save figures; skip raw-input and processed-output CSV files.",
    )
    parser.add_argument(
        "--ranking-output",
        choices=("csv", "plots", "both", "none"),
        default="both",
        help="Which Monte Carlo financial-metric ranking outputs to save.",
    )
    parser.add_argument(
        "--metric",
        choices=tuple(CEMENT_FINANCIAL_METRIC_OPTIONS),
        default="NPV",
        help="Financial metric used for comparison figures and ranking outputs.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the cement output workflow selected from the command line."""

    args = parse_args()
    if args.sample_size <= 0:
        raise ValueError("--sample-size must be positive.")

    save_ranking_outputs = args.ranking_output != "none"
    save_ranking_csv = args.ranking_output in ("csv", "both") and not args.no_data
    save_ranking_plots = args.ranking_output in ("plots", "both")

    if args.no_data:
        if args.kind == "all":
            output_paths = save_cement_npv_figures(
                output_dir=args.output_dir,
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
                retrofit_bau_mode=args.retrofit_bau_mode,
                financial_metric=args.metric,
            )
        elif args.kind == "mean":
            output_paths = (
                save_cement_mean_npv_figure(
                    output_dir=args.output_dir,
                    sample_size=args.sample_size,
                    random_seed=args.random_seed,
                    sector_name=args.sector_name,
                    retrofit_bau_mode=args.retrofit_bau_mode,
                    financial_metric=args.metric,
                ),
            )
        else:
            output_paths = (
                save_cement_deterministic_npv_figure(
                    output_dir=args.output_dir,
                    sector_name=args.sector_name,
                    financial_metric=args.metric,
                ),
            )

        if args.kind in ("all", "mean") and save_ranking_outputs:
            ranking, ranking_summary = calculate_cement_npv_rankings(
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
                retrofit_bau_mode=args.retrofit_bau_mode,
                financial_metric=args.metric,
            )
            output_paths = (
                *output_paths,
                *save_cement_npv_ranking_outputs(
                    ranking=ranking,
                    ranking_summary=ranking_summary,
                    figure_dir=args.output_dir,
                    raw_data_dir=args.raw_data_dir,
                    processed_data_dir=args.processed_data_dir,
                    sector_name=args.sector_name,
                    random_seed=args.random_seed,
                    save_ranking_csv=save_ranking_csv,
                    save_ranking_plots=save_ranking_plots,
                    financial_metric=args.metric,
                ),
            )
    elif args.kind == "all":
        output_paths = save_cement_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            sector_name=args.sector_name,
            retrofit_bau_mode=args.retrofit_bau_mode,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=args.metric,
        )
    elif args.kind == "mean":
        output_paths = save_cement_mean_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            sector_name=args.sector_name,
            retrofit_bau_mode=args.retrofit_bau_mode,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=args.metric,
        )
    else:
        output_paths = save_cement_deterministic_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sector_name=args.sector_name,
            financial_metric=args.metric,
        )

    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
