"""Shared orchestration for sector financial summaries and exports.

Sector modules define only labels, export columns, metric metadata, and their
deterministic/Monte Carlo entry points.  This module owns the repeated summary,
ranking, CSV, plotting, and command-line workflow.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Mapping, Sequence

import numpy as np

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
    plot_average_rank_bars,
    plot_financial_metric_technology_bars,
    shared_financial_metric_bar_axis_config,
)


Results = Mapping[str, Mapping[str, object]]
SimulationFunction = Callable[..., Results]
DeterministicFunction = Callable[..., Results]


@dataclass(frozen=True)
class SectorSummaryConfig:
    """Everything that legitimately differs between sector summary workflows."""

    sector_key: str
    sector_name: str
    technology_labels: Mapping[str, str]
    raw_input_columns: Sequence[str]
    processed_output_columns: Sequence[str]
    financial_metrics: Mapping[str, Mapping[str, object]]
    simulate_results: SimulationFunction
    deterministic_results: DeterministicFunction
    default_sample_size: int
    default_random_seed: int
    default_retrofit_bau_mode: str
    retrofit_bau_modes: Sequence[str]
    simulation_id_rename: Mapping[str, str]
    export_sort_columns: Sequence[str]


class SectorSummaryWorkflow:
    """Run one configured sector through the common summary workflow."""

    def __init__(self, config: SectorSummaryConfig) -> None:
        self.config = config

    def metric_config(self, financial_metric: str) -> Mapping[str, object]:
        if financial_metric not in self.config.financial_metrics:
            valid_metrics = ", ".join(self.config.financial_metrics)
            raise ValueError(
                f"Unknown financial_metric {financial_metric!r}. "
                f"Use one of: {valid_metrics}."
            )
        return self.config.financial_metrics[financial_metric]

    def with_display_labels(self, ranking_summary):
        return ranking_summary.assign(
            display_label=ranking_summary["technology"]
            .map(self.config.technology_labels)
            .fillna(ranking_summary["technology"])
        )

    @staticmethod
    def with_deterministic_retrofit_mode(
        results_by_technology: Results,
    ) -> dict[str, dict[str, object]]:
        """Align deterministic export metadata with Monte Carlo schemas."""

        export_results: dict[str, dict[str, object]] = {}
        for technology, results in results_by_technology.items():
            result_copy = dict(results)
            if "retrofit_bau_mode" not in result_copy:
                technology_type = str(
                    np.asarray(result_copy["technology_type"]).item()
                )
                mode = (
                    "deterministic"
                    if technology_type == "retrofit"
                    else "not_applicable"
                )
                result_copy["retrofit_bau_mode"] = [mode]
            export_results[technology] = result_copy
        return export_results

    def distribution_summary_million_eur(
        self,
        results_by_technology: Results,
        labels: Mapping[str, str] | None = None,
    ) -> dict[str, dict[str, float]]:
        """Return the legacy NPV-only distribution summary."""

        return self.distribution_summary(
            results_by_technology,
            labels=labels,
            financial_metric="NPV",
        )

    def distribution_summary(
        self,
        results_by_technology: Results,
        labels: Mapping[str, str] | None = None,
        financial_metric: str = "NPV",
    ) -> dict[str, dict[str, float]]:
        config = self.metric_config(financial_metric)
        metric_column = str(config["metric_column"])
        scale = float(config["scale"])
        display_labels = labels or self.config.technology_labels
        summary: dict[str, dict[str, float]] = {}
        for technology, results in results_by_technology.items():
            if metric_column not in results:
                raise KeyError(
                    f"{technology!r} results do not contain {metric_column!r}."
                )
            label = display_labels.get(technology, technology)
            values = np.asarray(results[metric_column], dtype=float) / scale
            summary[label] = {
                "mean": float(values.mean()),
                "median": float(np.median(values)),
                "p05": float(np.percentile(values, 5)),
                "p95": float(np.percentile(values, 95)),
                **summarize_metric_signs(values),
            }
        return summary

    @staticmethod
    def distribution_stat(
        summary: Mapping[str, Mapping[str, float]],
        statistic: str,
    ) -> dict[str, float]:
        return {label: values[statistic] for label, values in summary.items()}

    def _simulate(
        self,
        sample_size: int | None = None,
        random_seed: int | None = None,
        technologies: tuple[str, ...] | None = None,
        retrofit_bau_mode: str | None = None,
    ) -> Results:
        return self.config.simulate_results(
            sample_size=(
                self.config.default_sample_size
                if sample_size is None
                else sample_size
            ),
            random_seed=(
                self.config.default_random_seed
                if random_seed is None
                else random_seed
            ),
            technologies=technologies,
            retrofit_bau_mode=(
                self.config.default_retrofit_bau_mode
                if retrofit_bau_mode is None
                else retrofit_bau_mode
            ),
        )

    def calculate_mean_npv_million_eur(
        self,
        sample_size: int | None = None,
        random_seed: int | None = None,
        technologies: tuple[str, ...] | None = None,
        retrofit_bau_mode: str | None = None,
    ) -> dict[str, float]:
        return mean_npv_million_eur(
            results_by_item=self._simulate(
                sample_size,
                random_seed,
                technologies,
                retrofit_bau_mode,
            ),
            labels=self.config.technology_labels,
        )

    def calculate_mean_npv(
        self,
        sample_size: int | None = None,
        random_seed: int | None = None,
        technologies: tuple[str, ...] | None = None,
        retrofit_bau_mode: str | None = None,
        financial_metric: str = "NPV",
    ) -> dict[str, float]:
        config = self.metric_config(financial_metric)
        return mean_metric(
            results_by_item=self._simulate(
                sample_size,
                random_seed,
                technologies,
                retrofit_bau_mode,
            ),
            labels=self.config.technology_labels,
            metric_column=str(config["metric_column"]),
            scale=float(config["scale"]),
        )

    def calculate_deterministic_npv_million_eur(
        self,
        technologies: tuple[str, ...] | None = None,
    ) -> dict[str, float]:
        return deterministic_npv_million_eur(
            results_by_item=self.config.deterministic_results(
                technologies=technologies
            ),
            labels=self.config.technology_labels,
        )

    def calculate_deterministic_npv(
        self,
        technologies: tuple[str, ...] | None = None,
        financial_metric: str = "NPV",
    ) -> dict[str, float]:
        config = self.metric_config(financial_metric)
        return deterministic_metric(
            results_by_item=self.config.deterministic_results(
                technologies=technologies
            ),
            labels=self.config.technology_labels,
            metric_column=str(config["metric_column"]),
            scale=float(config["scale"]),
        )

    def save_mean_figure(
        self,
        output_dir: Path,
        sample_size: int | None = None,
        random_seed: int | None = None,
        run_date: date | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        financial_metric: str = "NPV",
    ) -> Path:
        sample_size = sample_size or self.config.default_sample_size
        random_seed = (
            self.config.default_random_seed
            if random_seed is None
            else random_seed
        )
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        results = self._simulate(
            sample_size=sample_size,
            random_seed=random_seed,
            retrofit_bau_mode=retrofit_bau_mode,
        )
        summary = self.distribution_summary(
            results,
            financial_metric=financial_metric,
        )
        return plot_financial_metric_technology_bars(
            values=self.distribution_stat(summary, "mean"),
            output_path=dated_figure_path(
                output_dir=output_dir,
                stem=f"Mean_{config['file_metric']}_{sector_name}",
                run_date=run_date,
            ),
            title=(
                f"Monte Carlo mean {config['ranking_label']} by "
                f"{self.config.sector_key} technology"
            ),
            median_values=self.distribution_stat(summary, "median"),
            lower_values=self.distribution_stat(summary, "p05"),
            upper_values=self.distribution_stat(summary, "p95"),
            sample_size=sample_size,
            random_seed=random_seed,
            x_axis_label=str(config["axis_label"]),
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )

    def save_deterministic_figure(
        self,
        output_dir: Path,
        run_date: date | None = None,
        sector_name: str | None = None,
        financial_metric: str = "NPV",
    ) -> Path:
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        return plot_financial_metric_technology_bars(
            values=self.calculate_deterministic_npv(
                financial_metric=financial_metric
            ),
            output_path=dated_figure_path(
                output_dir=output_dir,
                stem=f"Deterministic_{config['file_metric']}_{sector_name}",
                run_date=run_date,
            ),
            title=(
                f"Deterministic {config['ranking_label']} "
                f"({config['title_unit']})"
            ),
            x_axis_label=str(config["axis_label"]),
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )

    def save_mean_outputs(
        self,
        figure_dir: Path,
        raw_data_dir: Path,
        processed_data_dir: Path,
        sample_size: int | None = None,
        random_seed: int | None = None,
        run_date: date | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        save_ranking_outputs: bool = True,
        save_ranking_csv: bool = True,
        save_ranking_plots: bool = True,
        financial_metric: str = "NPV",
    ) -> tuple[Path, ...]:
        output_date = run_date or date.today()
        sample_size = sample_size or self.config.default_sample_size
        random_seed = (
            self.config.default_random_seed
            if random_seed is None
            else random_seed
        )
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        stem = f"Mean_{config['file_metric']}_{sector_name}"
        results = self._simulate(
            sample_size=sample_size,
            random_seed=random_seed,
            retrofit_bau_mode=retrofit_bau_mode,
        )
        summary = self.distribution_summary(
            results,
            financial_metric=financial_metric,
        )
        figure_path = plot_financial_metric_technology_bars(
            values=self.distribution_stat(summary, "mean"),
            output_path=dated_figure_path(figure_dir, stem, output_date),
            title=(
                f"Monte Carlo mean {config['ranking_label']} by "
                f"{self.config.sector_key} technology"
            ),
            median_values=self.distribution_stat(summary, "median"),
            lower_values=self.distribution_stat(summary, "p05"),
            upper_values=self.distribution_stat(summary, "p95"),
            sample_size=sample_size,
            random_seed=random_seed,
            x_axis_label=str(config["axis_label"]),
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )
        raw_csv_path = save_results_csv(
            results,
            self.config.raw_input_columns,
            dated_csv_path(raw_data_dir, f"{stem}_raw_inputs", output_date),
            rename_columns=self.config.simulation_id_rename,
            sort_by=self.config.export_sort_columns,
        )
        processed_csv_path = save_results_csv(
            results,
            self.config.processed_output_columns,
            dated_csv_path(
                processed_data_dir,
                f"{stem}_processed_outputs",
                output_date,
            ),
            rename_columns=self.config.simulation_id_rename,
            sort_by=self.config.export_sort_columns,
        )
        output_paths: list[Path] = [figure_path, raw_csv_path, processed_csv_path]
        if save_ranking_outputs:
            ranking, summary_ranking = self.calculate_rankings_from_results(
                results,
                sector_name,
                financial_metric,
            )
            output_paths.extend(
                self.save_ranking_outputs(
                    ranking,
                    summary_ranking,
                    figure_dir,
                    raw_data_dir,
                    processed_data_dir,
                    output_date,
                    sector_name,
                    random_seed,
                    save_ranking_csv,
                    save_ranking_plots,
                    financial_metric,
                )
            )
        return tuple(output_paths)

    def calculate_rankings_from_results(
        self,
        results: Results,
        sector_name: str | None = None,
        financial_metric: str = "NPV",
    ):
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        ranking = financial_metric_ranking_dataframe(
            results_by_item=results,
            sector=sector_name,
            metric_column=str(config["metric_column"]),
            metric_unit=str(config["metric_unit"]),
            higher_is_better=bool(config["higher_is_better"]),
        )
        return ranking, summarize_financial_metric_rankings(ranking)

    def calculate_rankings(
        self,
        sample_size: int | None = None,
        random_seed: int | None = None,
        technologies: tuple[str, ...] | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        financial_metric: str = "NPV",
    ):
        return self.calculate_rankings_from_results(
            self._simulate(
                sample_size,
                random_seed,
                technologies,
                retrofit_bau_mode,
            ),
            sector_name,
            financial_metric,
        )

    def save_ranking_outputs(
        self,
        ranking,
        ranking_summary,
        figure_dir: Path,
        raw_data_dir: Path,
        processed_data_dir: Path,
        run_date: date | None = None,
        sector_name: str | None = None,
        random_seed: int | None = None,
        save_ranking_csv: bool = True,
        save_ranking_plots: bool = True,
        financial_metric: str = "NPV",
    ) -> tuple[Path, ...]:
        output_date = run_date or date.today()
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        output_paths: list[Path] = []
        if save_ranking_csv:
            output_paths.extend(
                (
                    save_dataframe_csv(
                        ranking,
                        dated_csv_path(
                            raw_data_dir,
                            f"{config['file_metric']}_Ranking_{sector_name}_raw",
                            output_date,
                        ),
                    ),
                    save_dataframe_csv(
                        ranking_summary,
                        dated_csv_path(
                            processed_data_dir,
                            f"{config['file_metric']}_Ranking_{sector_name}_summary",
                            output_date,
                        ),
                    ),
                )
            )
        if save_ranking_plots:
            output_paths.append(
                plot_average_rank_bars(
                    ranking_summary=self.with_display_labels(ranking_summary),
                    output_path=dated_figure_path(
                        figure_dir,
                        f"Average_{config['file_metric']}_Rank_{sector_name}",
                        output_date,
                    ),
                    title=f"Monte Carlo {config['ranking_label']} Ranking",
                    metric_label=str(config["ranking_label"]),
                    random_seed=random_seed,
                    higher_is_better=bool(config["higher_is_better"]),
                )
            )
        return tuple(output_paths)

    def generate_rankings(
        self,
        figure_dir: Path | None = None,
        raw_data_dir: Path | None = None,
        processed_data_dir: Path | None = None,
        sample_size: int | None = None,
        random_seed: int | None = None,
        technologies: tuple[str, ...] | None = None,
        run_date: date | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        save_ranking_outputs: bool = True,
        save_ranking_csv: bool = True,
        save_ranking_plots: bool = True,
        financial_metric: str = "NPV",
    ):
        sector_name = sector_name or self.config.sector_name
        random_seed = (
            self.config.default_random_seed
            if random_seed is None
            else random_seed
        )
        ranking, ranking_summary = self.calculate_rankings(
            sample_size,
            random_seed,
            technologies,
            sector_name,
            retrofit_bau_mode,
            financial_metric,
        )
        output_paths: tuple[Path, ...] = ()
        if save_ranking_outputs and (save_ranking_csv or save_ranking_plots):
            root = self.project_root()
            output_paths = self.save_ranking_outputs(
                ranking,
                ranking_summary,
                figure_dir or root / "figures",
                raw_data_dir or root / "data" / "raw",
                processed_data_dir or root / "data" / "processed",
                run_date,
                sector_name,
                random_seed,
                save_ranking_csv,
                save_ranking_plots,
                financial_metric,
            )
        return ranking, ranking_summary, output_paths

    def save_deterministic_outputs(
        self,
        figure_dir: Path,
        raw_data_dir: Path,
        processed_data_dir: Path,
        run_date: date | None = None,
        sector_name: str | None = None,
        financial_metric: str = "NPV",
    ) -> tuple[Path, Path, Path]:
        output_date = run_date or date.today()
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        stem = f"Deterministic_{config['file_metric']}_{sector_name}"
        results = self.with_deterministic_retrofit_mode(
            self.config.deterministic_results()
        )
        values = deterministic_metric(
            results,
            self.config.technology_labels,
            str(config["metric_column"]),
            float(config["scale"]),
        )
        figure_path = plot_financial_metric_technology_bars(
            values=values,
            output_path=dated_figure_path(figure_dir, stem, output_date),
            title=(
                f"Deterministic {config['ranking_label']} "
                f"({config['title_unit']})"
            ),
            x_axis_label=str(config["axis_label"]),
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )
        raw_path = save_results_csv(
            results,
            self.config.raw_input_columns,
            dated_csv_path(raw_data_dir, f"{stem}_raw_inputs", output_date),
            rename_columns=self.config.simulation_id_rename,
            sort_by=self.config.export_sort_columns,
        )
        processed_path = save_results_csv(
            results,
            self.config.processed_output_columns,
            dated_csv_path(
                processed_data_dir,
                f"{stem}_processed_outputs",
                output_date,
            ),
            rename_columns=self.config.simulation_id_rename,
            sort_by=self.config.export_sort_columns,
        )
        return figure_path, raw_path, processed_path

    def save_all_outputs(
        self,
        figure_dir: Path,
        raw_data_dir: Path,
        processed_data_dir: Path,
        sample_size: int | None = None,
        random_seed: int | None = None,
        run_date: date | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        save_ranking_outputs: bool = True,
        save_ranking_csv: bool = True,
        save_ranking_plots: bool = True,
        financial_metric: str = "NPV",
    ) -> tuple[Path, ...]:
        return (
            *self.save_mean_outputs(
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
            *self.save_deterministic_outputs(
                figure_dir=figure_dir,
                raw_data_dir=raw_data_dir,
                processed_data_dir=processed_data_dir,
                run_date=run_date,
                sector_name=sector_name,
                financial_metric=financial_metric,
            ),
        )

    def save_figures(
        self,
        output_dir: Path,
        sample_size: int | None = None,
        random_seed: int | None = None,
        run_date: date | None = None,
        sector_name: str | None = None,
        retrofit_bau_mode: str | None = None,
        financial_metric: str = "NPV",
    ) -> tuple[Path, Path]:
        output_date = run_date or date.today()
        sample_size = sample_size or self.config.default_sample_size
        random_seed = (
            self.config.default_random_seed
            if random_seed is None
            else random_seed
        )
        sector_name = sector_name or self.config.sector_name
        config = self.metric_config(financial_metric)
        simulated_summary = self.distribution_summary(
            self._simulate(
                sample_size=sample_size,
                random_seed=random_seed,
                retrofit_bau_mode=retrofit_bau_mode,
            ),
            financial_metric=financial_metric,
        )
        deterministic_values = self.calculate_deterministic_npv(
            financial_metric=financial_metric
        )
        limits, ticks = shared_financial_metric_bar_axis_config(
            distribution_summary=simulated_summary,
            deterministic_values=deterministic_values,
            zero_floor=bool(config["zero_baseline"]),
            tick_step=config.get("axis_tick_step"),
        )
        mean_path = plot_financial_metric_technology_bars(
            values=self.distribution_stat(simulated_summary, "mean"),
            output_path=dated_figure_path(
                output_dir,
                f"Mean_{config['file_metric']}_{sector_name}",
                output_date,
            ),
            title=(
                f"Monte Carlo mean {config['ranking_label']} by "
                f"{self.config.sector_key} technology"
            ),
            median_values=self.distribution_stat(simulated_summary, "median"),
            lower_values=self.distribution_stat(simulated_summary, "p05"),
            upper_values=self.distribution_stat(simulated_summary, "p95"),
            sample_size=sample_size,
            random_seed=random_seed,
            x_axis_label=str(config["axis_label"]),
            x_axis_limits=limits,
            x_axis_ticks=ticks,
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )
        deterministic_path = plot_financial_metric_technology_bars(
            values=deterministic_values,
            output_path=dated_figure_path(
                output_dir,
                f"Deterministic_{config['file_metric']}_{sector_name}",
                output_date,
            ),
            title=(
                f"Deterministic {config['ranking_label']} "
                f"({config['title_unit']})"
            ),
            x_axis_label=str(config["axis_label"]),
            x_axis_limits=limits,
            x_axis_ticks=ticks,
            higher_is_better=bool(config["higher_is_better"]),
            color_by_sign=bool(config["color_by_sign"]),
            zero_baseline=bool(config["zero_baseline"]),
        )
        return mean_path, deterministic_path

    @staticmethod
    def project_root() -> Path:
        return Path(__file__).resolve().parents[1]

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description=(
                f"Generate {self.config.sector_key}-sector "
                "financial-metric comparison figures."
            )
        )
        parser.add_argument("--output-dir", type=Path, default=self.project_root() / "figures")
        parser.add_argument("--raw-data-dir", type=Path, default=self.project_root() / "data" / "raw")
        parser.add_argument("--processed-data-dir", type=Path, default=self.project_root() / "data" / "processed")
        parser.add_argument("--sample-size", type=int, default=self.config.default_sample_size)
        parser.add_argument("--random-seed", type=int, default=self.config.default_random_seed)
        parser.add_argument(
            "--retrofit-bau-mode",
            choices=tuple(self.config.retrofit_bau_modes),
            default=self.config.default_retrofit_bau_mode,
        )
        parser.add_argument("--kind", choices=("all", "mean", "deterministic"), default="all")
        parser.add_argument("--sector-name", default=self.config.sector_name)
        parser.add_argument("--no-data", action="store_true")
        parser.add_argument(
            "--ranking-output",
            choices=("csv", "plots", "both", "none"),
            default="both",
        )
        parser.add_argument(
            "--metric",
            choices=tuple(self.config.financial_metrics),
            default="NPV",
        )
        return parser.parse_args()

    def main(self) -> None:
        args = self.parse_args()
        if args.sample_size <= 0:
            raise ValueError("--sample-size must be positive.")
        save_rankings = args.ranking_output != "none"
        save_csv = args.ranking_output in ("csv", "both") and not args.no_data
        save_plots = args.ranking_output in ("plots", "both")
        common = {
            "sample_size": args.sample_size,
            "random_seed": args.random_seed,
            "sector_name": args.sector_name,
            "retrofit_bau_mode": args.retrofit_bau_mode,
            "financial_metric": args.metric,
        }
        if args.no_data:
            if args.kind == "all":
                paths = self.save_figures(output_dir=args.output_dir, **common)
            elif args.kind == "mean":
                paths = (self.save_mean_figure(output_dir=args.output_dir, **common),)
            else:
                paths = (
                    self.save_deterministic_figure(
                        output_dir=args.output_dir,
                        sector_name=args.sector_name,
                        financial_metric=args.metric,
                    ),
                )
            if args.kind in ("all", "mean") and save_rankings:
                ranking, summary = self.calculate_rankings(**common)
                paths = (
                    *paths,
                    *self.save_ranking_outputs(
                        ranking,
                        summary,
                        args.output_dir,
                        args.raw_data_dir,
                        args.processed_data_dir,
                        sector_name=args.sector_name,
                        random_seed=args.random_seed,
                        save_ranking_csv=save_csv,
                        save_ranking_plots=save_plots,
                        financial_metric=args.metric,
                    ),
                )
        elif args.kind == "all":
            paths = self.save_all_outputs(
                figure_dir=args.output_dir,
                raw_data_dir=args.raw_data_dir,
                processed_data_dir=args.processed_data_dir,
                save_ranking_outputs=save_rankings,
                save_ranking_csv=save_csv,
                save_ranking_plots=save_plots,
                **common,
            )
        elif args.kind == "mean":
            paths = self.save_mean_outputs(
                figure_dir=args.output_dir,
                raw_data_dir=args.raw_data_dir,
                processed_data_dir=args.processed_data_dir,
                save_ranking_outputs=save_rankings,
                save_ranking_csv=save_csv,
                save_ranking_plots=save_plots,
                **common,
            )
        else:
            paths = self.save_deterministic_outputs(
                figure_dir=args.output_dir,
                raw_data_dir=args.raw_data_dir,
                processed_data_dir=args.processed_data_dir,
                sector_name=args.sector_name,
                financial_metric=args.metric,
            )
        for path in paths:
            print(path)
