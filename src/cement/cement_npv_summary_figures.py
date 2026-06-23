"""Generate cement-sector NPV comparison figures and CSV outputs.

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
    mean_metric,
    mean_npv_million_eur,
    npv_ranking_dataframe,
    save_dataframe_csv,
    save_results_csv,
    summarize_npv_rankings,
)
from npv_summary_plots import (
    dated_figure_path,
    plot_average_rank_bars,
    plot_mean_npv_technology_bars,
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
    "annual_net_cash_flow_eur",
    "npv_eur",
    "lifetime_output_t",
    "npv_eur_per_t",
)

# Internal simulation arrays use `run_id`; exported CSVs use `simulation_id`
# because that name is clearer for thesis readers.
EXPORT_SIMULATION_ID_RENAME = {"run_id": "simulation_id"}
EXPORT_SORT_COLUMNS = ("simulation_id", "technology")

CEMENT_NPV_SCALE_OPTIONS = {
    "MEUR": {
        "metric_column": "npv_eur",
        "metric_unit": "EUR",
        "scale": 1_000_000.0,
        "summary_column": "npv_m_eur",
        "axis_label": "NPV (million EUR)",
        "title_unit": "MEUR",
        "file_suffix": "",
        "ranking_label": "NPV",
    },
    "EUR/t": {
        "metric_column": "npv_eur_per_t",
        "metric_unit": "EUR/t",
        "scale": 1.0,
        "summary_column": "npv_eur_per_t",
        "axis_label": "NPV (EUR/t)",
        "title_unit": "EUR/t",
        "file_suffix": "_per_t",
        "ranking_label": "NPV per tonne",
    },
}


def _cement_npv_scale_config(npv_scale: str) -> Mapping[str, object]:
    """Return display/export settings for one cement NPV scale."""

    if npv_scale not in CEMENT_NPV_SCALE_OPTIONS:
        valid_scales = ", ".join(CEMENT_NPV_SCALE_OPTIONS)
        raise ValueError(f"Unknown npv_scale {npv_scale!r}. Use one of: {valid_scales}.")

    return CEMENT_NPV_SCALE_OPTIONS[npv_scale]


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
        }
    return summary


def cement_npv_distribution_summary(
    results_by_technology: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str] = CEMENT_TECHNOLOGY_LABELS,
    npv_scale: str = "MEUR",
) -> dict[str, dict[str, float]]:
    """Calculate mean, median, and percentile NPV summaries for one scale."""

    config = _cement_npv_scale_config(npv_scale)
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
    npv_scale: str = "MEUR",
) -> dict[str, float]:
    """Calculate mean simulated NPV by cement technology for one scale."""

    config = _cement_npv_scale_config(npv_scale)
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
    npv_scale: str = "MEUR",
) -> dict[str, float]:
    """Calculate deterministic NPV by cement technology for one scale."""

    config = _cement_npv_scale_config(npv_scale)
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
    npv_scale: str = "MEUR",
) -> Path:
    """Save the simulated mean NPV comparison figure for cement."""

    config = _cement_npv_scale_config(npv_scale)
    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    summary = cement_npv_distribution_summary(results, npv_scale=npv_scale)
    values = _distribution_stat(summary, "mean")
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Mean_NPV{config['file_suffix']}_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title=f"Monte Carlo mean {config['ranking_label']} by cement technology",
        median_values_million_eur=_distribution_stat(summary, "median"),
        lower_values_million_eur=_distribution_stat(summary, "p05"),
        upper_values_million_eur=_distribution_stat(summary, "p95"),
        sample_size=sample_size,
        random_seed=random_seed,
        x_axis_label=str(config["axis_label"]),
    )


def save_cement_deterministic_npv_figure(
    output_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Cement",
    npv_scale: str = "MEUR",
) -> Path:
    """Save the deterministic NPV comparison figure for cement."""

    config = _cement_npv_scale_config(npv_scale)
    values = calculate_deterministic_cement_npv(npv_scale=npv_scale)
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Deterministic_NPV{config['file_suffix']}_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title=f"Deterministic {config['ranking_label']} ({config['title_unit']})",
        x_axis_label=str(config["axis_label"]),
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
    npv_scale: str = "MEUR",
) -> tuple[Path, ...]:
    """Save mean NPV figure plus raw-input, processed-output, and ranking outputs."""

    output_date = run_date or date.today()
    config = _cement_npv_scale_config(npv_scale)
    stem = f"Mean_NPV{config['file_suffix']}_{sector_name}"
    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    summary = cement_npv_distribution_summary(results, npv_scale=npv_scale)
    values = _distribution_stat(summary, "mean")
    figure_path = plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title=f"Monte Carlo mean {config['ranking_label']} by cement technology",
        median_values_million_eur=_distribution_stat(summary, "median"),
        lower_values_million_eur=_distribution_stat(summary, "p05"),
        upper_values_million_eur=_distribution_stat(summary, "p95"),
        sample_size=sample_size,
        random_seed=random_seed,
        x_axis_label=str(config["axis_label"]),
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
            npv_scale=npv_scale,
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
                npv_scale=npv_scale,
            )
        )

    return tuple(output_paths)


def calculate_cement_npv_rankings_from_results(
    results: Mapping[str, Mapping[str, object]],
    sector_name: str = "Cement",
    npv_scale: str = "MEUR",
):
    """Calculate raw and summary NPV rank tables from cement results."""

    config = _cement_npv_scale_config(npv_scale)
    ranking = npv_ranking_dataframe(
        results_by_item=results,
        sector=sector_name,
        npv_column=str(config["metric_column"]),
        metric_column=str(config["metric_column"]),
        metric_unit=str(config["metric_unit"]),
    )
    ranking_summary = summarize_npv_rankings(ranking)
    return ranking, ranking_summary


def calculate_cement_npv_rankings(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    npv_scale: str = "MEUR",
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
        npv_scale=npv_scale,
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
    npv_scale: str = "MEUR",
) -> tuple[Path, ...]:
    """Save cement NPV ranking CSVs and/or plots."""

    output_date = run_date or date.today()
    config = _cement_npv_scale_config(npv_scale)
    output_paths: list[Path] = []
    if save_ranking_csv:
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking,
                output_path=dated_csv_path(
                    output_dir=raw_data_dir,
                    stem=f"NPV_Ranking{config['file_suffix']}_{sector_name}_raw",
                    run_date=output_date,
                ),
            )
        )
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking_summary,
                output_path=dated_csv_path(
                    output_dir=processed_data_dir,
                    stem=f"NPV_Ranking{config['file_suffix']}_{sector_name}_summary",
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
                    stem=f"Average_NPV_Rank{config['file_suffix']}_{sector_name}",
                    run_date=output_date,
                ),
                title=f"Monte Carlo {config['ranking_label']} Ranking",
                random_seed=random_seed,
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
    npv_scale: str = "MEUR",
):
    """Return cement NPV ranking DataFrames and optionally save outputs."""

    ranking, ranking_summary = calculate_cement_npv_rankings(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
        sector_name=sector_name,
        retrofit_bau_mode=retrofit_bau_mode,
        npv_scale=npv_scale,
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
            npv_scale=npv_scale,
        )

    return ranking, ranking_summary, output_paths


def save_cement_deterministic_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Cement",
    npv_scale: str = "MEUR",
) -> tuple[Path, Path, Path]:
    """Save deterministic NPV figure plus raw-input and processed-output CSVs."""

    output_date = run_date or date.today()
    config = _cement_npv_scale_config(npv_scale)
    stem = f"Deterministic_NPV{config['file_suffix']}_{sector_name}"
    results = _with_deterministic_retrofit_mode(
        calculate_deterministic_cement_results()
    )
    values = deterministic_metric(
        results_by_item=results,
        labels=CEMENT_TECHNOLOGY_LABELS,
        metric_column=str(config["metric_column"]),
        scale=float(config["scale"]),
    )
    figure_path = plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title=f"Deterministic {config['ranking_label']} ({config['title_unit']})",
        x_axis_label=str(config["axis_label"]),
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
    npv_scale: str = "MEUR",
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
            npv_scale=npv_scale,
        ),
        *save_cement_deterministic_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            run_date=run_date,
            sector_name=sector_name,
            npv_scale=npv_scale,
        ),
    )


def save_cement_npv_figures(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Cement",
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
    npv_scale: str = "MEUR",
) -> tuple[Path, Path]:
    """Save both simulated mean and deterministic cement NPV figures."""

    return (
        save_cement_mean_npv_figure(
            output_dir=output_dir,
            sample_size=sample_size,
            random_seed=random_seed,
            run_date=run_date,
            sector_name=sector_name,
            retrofit_bau_mode=retrofit_bau_mode,
            npv_scale=npv_scale,
        ),
        save_cement_deterministic_npv_figure(
            output_dir=output_dir,
            run_date=run_date,
            sector_name=sector_name,
            npv_scale=npv_scale,
        ),
    )


def _project_root() -> Path:
    """Return the repository root when this module is executed as a script."""

    return Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    """Parse command-line options for regenerating cement outputs."""

    parser = argparse.ArgumentParser(
        description="Generate cement-sector NPV comparison figures."
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
        help="Monte Carlo sample size for the mean NPV figure.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed for the mean NPV figure.",
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
        help="Which Monte Carlo NPV ranking outputs to save.",
    )
    parser.add_argument(
        "--npv-scale",
        choices=tuple(CEMENT_NPV_SCALE_OPTIONS),
        default="MEUR",
        help="NPV scale used for comparison figures and ranking outputs.",
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
                npv_scale=args.npv_scale,
            )
        elif args.kind == "mean":
            output_paths = (
                save_cement_mean_npv_figure(
                    output_dir=args.output_dir,
                    sample_size=args.sample_size,
                    random_seed=args.random_seed,
                    sector_name=args.sector_name,
                    retrofit_bau_mode=args.retrofit_bau_mode,
                    npv_scale=args.npv_scale,
                ),
            )
        else:
            output_paths = (
                save_cement_deterministic_npv_figure(
                    output_dir=args.output_dir,
                    sector_name=args.sector_name,
                    npv_scale=args.npv_scale,
                ),
            )

        if args.kind in ("all", "mean") and save_ranking_outputs:
            ranking, ranking_summary = calculate_cement_npv_rankings(
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
                retrofit_bau_mode=args.retrofit_bau_mode,
                npv_scale=args.npv_scale,
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
                    npv_scale=args.npv_scale,
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
            npv_scale=args.npv_scale,
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
            npv_scale=args.npv_scale,
        )
    else:
        output_paths = save_cement_deterministic_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sector_name=args.sector_name,
            npv_scale=args.npv_scale,
        )

    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
