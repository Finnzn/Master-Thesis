"""Generate electricity-sector financial-metric figures and CSV outputs.

This module is the bridge between model calculations and thesis artefacts. It
runs deterministic and Monte Carlo electricity NPV calculations, writes raw and
processed CSV files, and saves comparison figures.

The output split is intentional:
- raw CSVs contain sampled or representative model inputs;
- processed CSVs contain derived quantities such as capacity, costs, cash flow,
  and NPV;
- figures summarize those outputs for interpretation.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Mapping

import numpy as np

from electricity.electricity_npv_deterministic import (
    calculate_deterministic_electricity_results
)
from electricity.electricity_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_SAMPLE_SIZE,
    simulate_electricity_results,
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
}

# Columns exported as raw inputs. These are values that enter the model directly:
# sampled techno-economic assumptions, fixed prices, and carbon price.
ELECTRICITY_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
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
    "carbon_price_eur_per_t",
)

# Columns exported as processed outputs. These are derived from the raw inputs by
# the capacity, cost, cash-flow, and NPV calculations.
ELECTRICITY_PROCESSED_OUTPUT_COLUMNS = (
    "run_id",
    "technology",
    "capacity_mw",
    "capacity_kw",
    "initial_capex_eur",
    "annual_revenue_eur",
    "annual_fixed_opex_eur",
    "annual_variable_opex_eur",
    "annual_fuel_cost_eur",
    "annual_emissions_cost_eur",
    "annual_total_cost_eur",
    "annual_net_cash_flow_eur",
    "npv_eur",
    "discounted_lifetime_output_mwh",
    "present_value_total_cost_eur",
    "lcoe_eur_per_mwh",
    "levelized_net_margin_eur_per_mwh",
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
    "LNM": {
        "metric_column": "levelized_net_margin_eur_per_mwh",
        "metric_unit": "EUR/MWh",
        "scale": 1.0,
        "summary_column": "levelized_net_margin_eur_per_mwh",
        "axis_label": "Levelized net margin (EUR/MWh)",
        "title_unit": "EUR/MWh",
        "file_metric": "Levelized_Net_Margin_per_MWh",
        "ranking_label": "levelized net margin",
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


def _electricity_financial_metric_config(
    financial_metric: str,
) -> Mapping[str, object]:
    """Return display and export settings for one electricity financial metric."""

    if financial_metric not in ELECTRICITY_FINANCIAL_METRIC_OPTIONS:
        valid_metrics = ", ".join(ELECTRICITY_FINANCIAL_METRIC_OPTIONS)
        raise ValueError(
            f"Unknown financial_metric {financial_metric!r}. "
            f"Use one of: {valid_metrics}."
        )

    return ELECTRICITY_FINANCIAL_METRIC_OPTIONS[financial_metric]


def _with_electricity_display_labels(ranking_summary):
    """Return a ranking summary copy with human-readable technology labels.

    CSV outputs keep stable technology codes such as `hard_coal_ccs`, while
    plots use display labels that are easier to read.
    """

    return ranking_summary.assign(
        display_label=ranking_summary["technology"].map(
            ELECTRICITY_TECHNOLOGY_LABELS
        ).fillna(ranking_summary["technology"])
    )


def electricity_npv_distribution_summary_million_eur(
    results_by_technology: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str] = ELECTRICITY_TECHNOLOGY_LABELS,
) -> dict[str, dict[str, float]]:
    """Calculate mean, median, and percentile NPV summaries in million EUR.

    The mean is used for the bar length in the Monte Carlo figure. The median
    and 5th/95th percentiles are shown as markers and whiskers so the figure
    communicates both central value and uncertainty.
    """

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


def electricity_npv_distribution_summary(
    results_by_technology: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str] = ELECTRICITY_TECHNOLOGY_LABELS,
    financial_metric: str = "NPV",
) -> dict[str, dict[str, float]]:
    """Calculate mean, median, and percentile financial-metric summaries."""

    config = _electricity_financial_metric_config(financial_metric)
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
    """Extract one statistic from the nested distribution summary.

    Plotting helpers expect a simple mapping from label to value, so this keeps
    the summary calculation separate from the figure call.
    """

    return {label: values[statistic] for label, values in summary.items()}


def calculate_mean_electricity_npv_million_eur(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate mean simulated NPV by electricity technology in million EUR.

    This is a lightweight programmatic helper for notebooks or quick checks when
    the caller only needs the mean NPV values and not CSV or figure outputs.
    """

    return mean_npv_million_eur(
        results_by_item=simulate_electricity_results(
            sample_size=sample_size,
            random_seed=random_seed,
            technologies=technologies,
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )


def calculate_mean_electricity_npv(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    financial_metric: str = "NPV",
) -> dict[str, float]:
    """Calculate a mean simulated financial metric by electricity technology."""

    config = _electricity_financial_metric_config(financial_metric)
    return mean_metric(
        results_by_item=simulate_electricity_results(
            sample_size=sample_size,
            random_seed=random_seed,
            technologies=technologies,
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )


def calculate_deterministic_electricity_npv_million_eur(
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate deterministic NPV by electricity technology in million EUR.

    This mirrors the Monte Carlo mean helper but uses representative parameter
    values instead of random draws.
    """

    return deterministic_npv_million_eur(
        results_by_item=calculate_deterministic_electricity_results(
            technologies=technologies
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )


def calculate_deterministic_electricity_npv(
    technologies: tuple[str, ...] | None = None,
    financial_metric: str = "NPV",
) -> dict[str, float]:
    """Calculate a deterministic financial metric by electricity technology."""

    config = _electricity_financial_metric_config(financial_metric)
    return deterministic_metric(
        results_by_item=calculate_deterministic_electricity_results(
            technologies=technologies
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )


def save_electricity_mean_npv_figure(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
) -> Path:
    """Save the simulated mean NPV comparison figure for electricity.

    This figure-only helper does not write CSVs. Use
    `save_electricity_mean_npv_outputs` when the raw and processed data exports
    should be regenerated together with the plot.
    """

    # Simulate once and reuse the same result arrays for all plot statistics.
    results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    config = _electricity_financial_metric_config(financial_metric)
    summary = electricity_npv_distribution_summary(results, financial_metric=financial_metric)
    values = _distribution_stat(summary, "mean")
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Mean_{config['file_metric']}_{sector_name}",
        run_date=run_date,
    )
    return plot_financial_metric_technology_bars(
        values=values,
        output_path=output_path,
        title=f"Monte Carlo mean {config['ranking_label']} by electricity technology",
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


def save_electricity_deterministic_npv_figure(
    output_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
) -> Path:
    """Save the deterministic NPV comparison figure for electricity."""

    config = _electricity_financial_metric_config(financial_metric)
    values = calculate_deterministic_electricity_npv(financial_metric=financial_metric)
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


def save_electricity_mean_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save mean NPV figure plus raw-input, processed-output, and ranking outputs.

    The same Monte Carlo result arrays are reused for the figure, raw input CSV,
    processed output CSV, and optional ranking outputs. This is important: all
    artefacts from one call describe the same simulation run.
    """

    output_date = run_date or date.today()
    config = _electricity_financial_metric_config(financial_metric)
    stem = f"Mean_{config['file_metric']}_{sector_name}"
    # Generate the Monte Carlo results once. Reusing this object prevents the
    # figure and CSVs from accidentally representing different random draws.
    results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    summary = electricity_npv_distribution_summary(results, financial_metric=financial_metric)
    values = _distribution_stat(summary, "mean")
    figure_path = plot_financial_metric_technology_bars(
        values=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title=f"Monte Carlo mean {config['ranking_label']} by electricity technology",
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
        columns=ELECTRICITY_RAW_INPUT_COLUMNS,
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
        columns=ELECTRICITY_PROCESSED_OUTPUT_COLUMNS,
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
        # Rankings are calculated from the same Monte Carlo draw as the mean-NPV plot.
        ranking, ranking_summary = calculate_electricity_npv_rankings_from_results(
            results=results,
            sector_name=sector_name,
            financial_metric=financial_metric,
        )
        output_paths.extend(
            save_electricity_npv_ranking_outputs(
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


def calculate_electricity_npv_rankings_from_results(
    results: Mapping[str, Mapping[str, object]],
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
):
    """Calculate raw and summary NPV rank tables from electricity results.

    Pass existing results here when rankings should correspond exactly to an
    already generated Monte Carlo run. This is how the mean-NPV output function
    keeps rankings aligned with the figure and CSVs.
    """

    config = _electricity_financial_metric_config(financial_metric)
    ranking = financial_metric_ranking_dataframe(
        results_by_item=results,
        sector=sector_name,
        metric_column=str(config["metric_column"]),
        metric_unit=str(config["metric_unit"]),
        higher_is_better=bool(config["higher_is_better"]),
    )
    ranking_summary = summarize_financial_metric_rankings(ranking)
    return ranking, ranking_summary


def calculate_electricity_npv_rankings(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
):
    """Run electricity Monte Carlo simulations and return NPV ranking tables.

    This convenience function is useful when rankings are needed on their own.
    It creates a fresh simulation using the supplied sample size and seed.
    """

    results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
    )
    return calculate_electricity_npv_rankings_from_results(
        results=results,
        sector_name=sector_name,
        financial_metric=financial_metric,
    )


def save_electricity_npv_ranking_outputs(
    ranking,
    ranking_summary,
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    random_seed: int | None = None,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save electricity NPV ranking CSVs and/or plots.

    The raw ranking CSV stores every technology in every simulation. The summary
    CSV aggregates that table into probabilities and rank counts. The plot uses
    the summary CSV structure.
    """

    output_date = run_date or date.today()
    config = _electricity_financial_metric_config(financial_metric)
    output_paths: list[Path] = []
    if save_ranking_csv:
        # Raw ranking stores one row per technology and simulation, so it can be
        # audited back to individual NPV draws.
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
        # Summary ranking aggregates the raw ranking table by technology for
        # interpretation and plotting.
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
                ranking_summary=_with_electricity_display_labels(ranking_summary),
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


def generate_electricity_npv_rankings(
    figure_dir: Path | None = None,
    raw_data_dir: Path | None = None,
    processed_data_dir: Path | None = None,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
):
    """Return electricity NPV ranking DataFrames and optionally save outputs.

    Notebooks can call this to inspect rankings in memory, while scripts can set
    the save flags to persist CSVs and plots in the standard project folders.
    """

    ranking, ranking_summary = calculate_electricity_npv_rankings(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
        sector_name=sector_name,
        financial_metric=financial_metric,
    )
    output_paths: tuple[Path, ...] = ()
    if save_ranking_outputs and (save_ranking_csv or save_ranking_plots):
        root = _project_root()
        output_paths = save_electricity_npv_ranking_outputs(
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


def save_electricity_deterministic_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
) -> tuple[Path, Path, Path]:
    """Save deterministic NPV figure plus raw-input and processed-output CSVs.

    Deterministic exports use the same raw/processed column split as Monte Carlo
    exports, but each technology has only one representative row.
    """

    output_date = run_date or date.today()
    config = _electricity_financial_metric_config(financial_metric)
    stem = f"Deterministic_{config['file_metric']}_{sector_name}"
    results = calculate_deterministic_electricity_results()
    values = deterministic_metric(
        results_by_item=results,
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
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
        columns=ELECTRICITY_RAW_INPUT_COLUMNS,
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
        columns=ELECTRICITY_PROCESSED_OUTPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=processed_data_dir,
            stem=f"{stem}_processed_outputs",
            run_date=output_date,
        ),
        rename_columns=EXPORT_SIMULATION_ID_RENAME,
        sort_by=EXPORT_SORT_COLUMNS,
    )

    return figure_path, raw_csv_path, processed_csv_path


def save_electricity_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
    financial_metric: str = "NPV",
) -> tuple[Path, ...]:
    """Save simulated mean and deterministic electricity NPV outputs.

    This is the main all-in-one output function used by the CLI when `--kind all`
    and data exports are enabled.
    """

    return (
        *save_electricity_mean_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            sample_size=sample_size,
            random_seed=random_seed,
            run_date=run_date,
            sector_name=sector_name,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=financial_metric,
        ),
        *save_electricity_deterministic_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            run_date=run_date,
            sector_name=sector_name,
            financial_metric=financial_metric,
        ),
    )


def save_electricity_npv_figures(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    financial_metric: str = "NPV",
) -> tuple[Path, Path]:
    """Save both simulated mean and deterministic electricity NPV figures.

    This is used for figure-only runs, especially when `--no-data` is supplied.
    """

    config = _electricity_financial_metric_config(financial_metric)
    output_date = run_date or date.today()
    simulated_results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    simulated_summary = electricity_npv_distribution_summary(
        simulated_results,
        financial_metric=financial_metric,
    )
    mean_values = _distribution_stat(simulated_summary, "mean")
    deterministic_values = calculate_deterministic_electricity_npv(
        financial_metric=financial_metric
    )
    x_axis_limits, x_axis_ticks = fixed_financial_metric_bar_axis_config(
        sector="electricity",
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
        title=f"Monte Carlo mean {config['ranking_label']} by electricity technology",
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
    """Parse command-line options for regenerating electricity outputs."""

    parser = argparse.ArgumentParser(
        description="Generate electricity-sector financial-metric comparison figures."
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
        "--kind",
        choices=("all", "mean", "deterministic"),
        default="all",
        help="Which figure to generate.",
    )
    parser.add_argument(
        "--sector-name",
        default="Electricity",
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
        choices=tuple(ELECTRICITY_FINANCIAL_METRIC_OPTIONS),
        default="NPV",
        help="Financial metric used for comparison figures and ranking outputs.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the electricity output workflow selected from the command line."""

    args = parse_args()
    if args.sample_size <= 0:
        raise ValueError("--sample-size must be positive.")

    # `--no-data` suppresses CSV exports but still allows ranking plots. This is
    # useful when only figures need to be refreshed for a report or notebook.
    save_ranking_outputs = args.ranking_output != "none"
    save_ranking_csv = args.ranking_output in ("csv", "both") and not args.no_data
    save_ranking_plots = args.ranking_output in ("plots", "both")

    if args.no_data:
        if args.kind == "all":
            output_paths = save_electricity_npv_figures(
                output_dir=args.output_dir,
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
                financial_metric=args.metric,
            )
        elif args.kind == "mean":
            output_paths = (
                save_electricity_mean_npv_figure(
                    output_dir=args.output_dir,
                    sample_size=args.sample_size,
                    random_seed=args.random_seed,
                    sector_name=args.sector_name,
                    financial_metric=args.metric,
                ),
            )
        else:
            output_paths = (
                save_electricity_deterministic_npv_figure(
                    output_dir=args.output_dir,
                    sector_name=args.sector_name,
                    financial_metric=args.metric,
                ),
            )

        if args.kind in ("all", "mean") and save_ranking_outputs:
            ranking, ranking_summary = calculate_electricity_npv_rankings(
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
                financial_metric=args.metric,
            )
            output_paths = (
                *output_paths,
                *save_electricity_npv_ranking_outputs(
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
        output_paths = save_electricity_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            sector_name=args.sector_name,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=args.metric,
        )
    elif args.kind == "mean":
        output_paths = save_electricity_mean_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            sector_name=args.sector_name,
            save_ranking_outputs=save_ranking_outputs,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
            financial_metric=args.metric,
        )
    else:
        output_paths = save_electricity_deterministic_npv_outputs(
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
