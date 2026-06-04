"""Generate electricity-sector NPV comparison figures and CSV outputs."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Mapping

from electricity.electricity_npv_deterministic import (
    calculate_deterministic_electricity_npv_eur,
    calculate_deterministic_electricity_result,
    calculate_deterministic_electricity_results,
)
from electricity.electricity_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_SAMPLE_SIZE,
    simulate_electricity_results,
)
from npv_summary import (
    dated_csv_path,
    deterministic_npv_million_eur,
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


ELECTRICITY_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "hard_coal": "Hard coal",
    "hard_coal_ccs": "Hard coal+CCS",
    "ccgt": "CCGT",
    "ccgt_ccs": "CCGT + CCS",
    "nuclear": "Nuclear",
    "wind_offshore": "Wind Offshore",
    "wind_onshore": "Wind Onshore",
    "pv": "PV",
    "biogas": "Biogas",
}

ELECTRICITY_RAW_INPUT_COLUMNS = (
    "run_id",
    "technology",
    "annual_output_mwh",
    "full_load_hours_per_year",
    "capex_eur_per_kw",
    "fixed_opex_eur_per_kw_year",
    "variable_opex_eur_per_mwh",
    "fuel_consumption_mwh_th_per_mwh_e",
    "emissions_tco2_per_mwh_e",
    "fuel_price_eur_per_mwh_th",
    "electricity_price_eur_per_mwh",
    "carbon_price_eur_per_t",
)

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
    "annual_net_cash_flow_eur",
    "npv_eur",
    "lifetime_output_mwh",
    "npv_eur_per_mwh",
    "npv_million_eur_per_mwh",
)


def calculate_mean_electricity_npv_million_eur(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate mean simulated NPV by electricity technology in million EUR."""

    return mean_npv_million_eur(
        results_by_item=simulate_electricity_results(
            sample_size=sample_size,
            random_seed=random_seed,
            technologies=technologies,
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )


def calculate_deterministic_electricity_npv_million_eur(
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate deterministic NPV by electricity technology in million EUR."""

    return deterministic_npv_million_eur(
        results_by_item=calculate_deterministic_electricity_results(
            technologies=technologies
        ),
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )


def save_electricity_mean_npv_figure(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> Path:
    """Save the simulated mean NPV comparison figure for electricity."""

    values = calculate_mean_electricity_npv_million_eur(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Mean_NPV_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title="Mean NPV (MEUR)",
    )


def save_electricity_deterministic_npv_figure(
    output_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> Path:
    """Save the deterministic NPV comparison figure for electricity."""

    values = calculate_deterministic_electricity_npv_million_eur()
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Deterministic_NPV_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title="Deterministic NPV (MEUR)",
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
) -> tuple[Path, ...]:
    """Save mean NPV figure plus raw-input, processed-output, and ranking outputs."""

    output_date = run_date or date.today()
    stem = f"Mean_NPV_{sector_name}"
    results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    values = mean_npv_million_eur(
        results_by_item=results,
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )
    figure_path = plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title="Mean NPV (MEUR)",
    )
    raw_csv_path = save_results_csv(
        results_by_item=results,
        columns=ELECTRICITY_RAW_INPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=raw_data_dir,
            stem=f"{stem}_raw_inputs",
            run_date=output_date,
        ),
    )
    processed_csv_path = save_results_csv(
        results_by_item=results,
        columns=ELECTRICITY_PROCESSED_OUTPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=processed_data_dir,
            stem=f"{stem}_processed_outputs",
            run_date=output_date,
        ),
    )

    output_paths: list[Path] = [figure_path, raw_csv_path, processed_csv_path]
    if save_ranking_outputs:
        ranking, ranking_summary = calculate_electricity_npv_rankings_from_results(
            results=results,
            sector_name=sector_name,
        )
        output_paths.extend(
            save_electricity_npv_ranking_outputs(
                ranking=ranking,
                ranking_summary=ranking_summary,
                figure_dir=figure_dir,
                processed_data_dir=processed_data_dir,
                run_date=output_date,
                sector_name=sector_name,
                save_ranking_csv=save_ranking_csv,
                save_ranking_plots=save_ranking_plots,
            )
        )

    return tuple(output_paths)


def calculate_electricity_npv_rankings_from_results(
    results: Mapping[str, Mapping[str, object]],
    sector_name: str = "Electricity",
):
    """Calculate detailed and summary NPV rank tables from electricity results."""

    ranking = npv_ranking_dataframe(
        results_by_item=results,
        sector=sector_name,
    )
    ranking_summary = summarize_npv_rankings(ranking)
    return ranking, ranking_summary


def calculate_electricity_npv_rankings(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    sector_name: str = "Electricity",
):
    """Run electricity Monte Carlo simulations and return NPV ranking tables."""

    results = simulate_electricity_results(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
    )
    return calculate_electricity_npv_rankings_from_results(
        results=results,
        sector_name=sector_name,
    )


def save_electricity_npv_ranking_outputs(
    ranking,
    ranking_summary,
    figure_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
) -> tuple[Path, ...]:
    """Save electricity NPV ranking CSVs and/or plots."""

    output_date = run_date or date.today()
    output_paths: list[Path] = []
    if save_ranking_csv:
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking,
                output_path=dated_csv_path(
                    output_dir=processed_data_dir,
                    stem=f"NPV_Ranking_{sector_name}_detailed",
                    run_date=output_date,
                ),
            )
        )
        output_paths.append(
            save_dataframe_csv(
                dataframe=ranking_summary,
                output_path=dated_csv_path(
                    output_dir=processed_data_dir,
                    stem=f"NPV_Ranking_{sector_name}_summary",
                    run_date=output_date,
                ),
            )
        )
    if save_ranking_plots:
        output_paths.append(
            plot_average_rank_bars(
                ranking_summary=ranking_summary,
                output_path=dated_figure_path(
                    output_dir=figure_dir,
                    stem=f"Average_NPV_Rank_{sector_name}",
                    run_date=output_date,
                ),
                title="Average NPV Rank",
            )
        )

    return tuple(output_paths)


def generate_electricity_npv_rankings(
    figure_dir: Path | None = None,
    processed_data_dir: Path | None = None,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
    run_date: date | None = None,
    sector_name: str = "Electricity",
    save_ranking_outputs: bool = True,
    save_ranking_csv: bool = True,
    save_ranking_plots: bool = True,
):
    """Return electricity NPV ranking DataFrames and optionally save outputs."""

    ranking, ranking_summary = calculate_electricity_npv_rankings(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=technologies,
        sector_name=sector_name,
    )
    output_paths: tuple[Path, ...] = ()
    if save_ranking_outputs and (save_ranking_csv or save_ranking_plots):
        root = _project_root()
        output_paths = save_electricity_npv_ranking_outputs(
            ranking=ranking,
            ranking_summary=ranking_summary,
            figure_dir=figure_dir or root / "figures",
            processed_data_dir=processed_data_dir or root / "data" / "processed",
            run_date=run_date,
            sector_name=sector_name,
            save_ranking_csv=save_ranking_csv,
            save_ranking_plots=save_ranking_plots,
        )

    return ranking, ranking_summary, output_paths


def save_electricity_deterministic_npv_outputs(
    figure_dir: Path,
    raw_data_dir: Path,
    processed_data_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> tuple[Path, Path, Path]:
    """Save deterministic NPV figure plus raw-input and processed-output CSVs."""

    output_date = run_date or date.today()
    stem = f"Deterministic_NPV_{sector_name}"
    results = calculate_deterministic_electricity_results()
    values = deterministic_npv_million_eur(
        results_by_item=results,
        labels=ELECTRICITY_TECHNOLOGY_LABELS,
    )
    figure_path = plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=dated_figure_path(
            output_dir=figure_dir,
            stem=stem,
            run_date=output_date,
        ),
        title="Deterministic NPV (MEUR)",
    )
    raw_csv_path = save_results_csv(
        results_by_item=results,
        columns=ELECTRICITY_RAW_INPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=raw_data_dir,
            stem=f"{stem}_raw_inputs",
            run_date=output_date,
        ),
    )
    processed_csv_path = save_results_csv(
        results_by_item=results,
        columns=ELECTRICITY_PROCESSED_OUTPUT_COLUMNS,
        output_path=dated_csv_path(
            output_dir=processed_data_dir,
            stem=f"{stem}_processed_outputs",
            run_date=output_date,
        ),
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
) -> tuple[Path, ...]:
    """Save simulated mean and deterministic electricity NPV outputs."""

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
        ),
        *save_electricity_deterministic_npv_outputs(
            figure_dir=figure_dir,
            raw_data_dir=raw_data_dir,
            processed_data_dir=processed_data_dir,
            run_date=run_date,
            sector_name=sector_name,
        ),
    )


def save_electricity_npv_figures(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> tuple[Path, Path]:
    """Save both simulated mean and deterministic electricity NPV figures."""

    return (
        save_electricity_mean_npv_figure(
            output_dir=output_dir,
            sample_size=sample_size,
            random_seed=random_seed,
            run_date=run_date,
            sector_name=sector_name,
        ),
        save_electricity_deterministic_npv_figure(
            output_dir=output_dir,
            run_date=run_date,
            sector_name=sector_name,
        ),
    )


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate electricity-sector NPV comparison figures."
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
        help="Which Monte Carlo NPV ranking outputs to save.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.sample_size <= 0:
        raise ValueError("--sample-size must be positive.")

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
            )
        elif args.kind == "mean":
            output_paths = (
                save_electricity_mean_npv_figure(
                    output_dir=args.output_dir,
                    sample_size=args.sample_size,
                    random_seed=args.random_seed,
                    sector_name=args.sector_name,
                ),
            )
        else:
            output_paths = (
                save_electricity_deterministic_npv_figure(
                    output_dir=args.output_dir,
                    sector_name=args.sector_name,
                ),
            )

        if args.kind in ("all", "mean") and save_ranking_outputs:
            ranking, ranking_summary = calculate_electricity_npv_rankings(
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
            )
            output_paths = (
                *output_paths,
                *save_electricity_npv_ranking_outputs(
                    ranking=ranking,
                    ranking_summary=ranking_summary,
                    figure_dir=args.output_dir,
                    processed_data_dir=args.processed_data_dir,
                    sector_name=args.sector_name,
                    save_ranking_csv=save_ranking_csv,
                    save_ranking_plots=save_ranking_plots,
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
        )
    else:
        output_paths = save_electricity_deterministic_npv_outputs(
            figure_dir=args.output_dir,
            raw_data_dir=args.raw_data_dir,
            processed_data_dir=args.processed_data_dir,
            sector_name=args.sector_name,
        )

    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
