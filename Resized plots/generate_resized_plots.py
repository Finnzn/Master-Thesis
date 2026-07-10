"""Generate the six midterm plots with all visible text at least 14 pt."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cement.cement_npv_monte_carlo import (  # noqa: E402
    DEFAULT_RANDOM_SEED as CEMENT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE as CEMENT_SAMPLE_SIZE,
    simulate_cement_results,
)
from cement.cement_npv_summary_figures import (  # noqa: E402
    _distribution_stat as cement_distribution_stat,
    _with_cement_display_labels,
    calculate_cement_npv_rankings_from_results,
    calculate_deterministic_cement_npv,
    cement_npv_distribution_summary,
)
from electricity.electricity_npv_monte_carlo import (  # noqa: E402
    DEFAULT_RANDOM_SEED as ELECTRICITY_RANDOM_SEED,
    DEFAULT_SAMPLE_SIZE as ELECTRICITY_SAMPLE_SIZE,
    simulate_electricity_results,
)
from electricity.electricity_npv_summary_figures import (  # noqa: E402
    _distribution_stat as electricity_distribution_stat,
    _with_electricity_display_labels,
    calculate_deterministic_electricity_npv,
    calculate_electricity_npv_rankings_from_results,
    electricity_npv_distribution_summary,
)
from npv_summary_plots import (  # noqa: E402
    dated_figure_path,
    plot_average_rank_bars,
    plot_mean_npv_technology_bars,
)


OUTPUT_DIR = ROOT / "Resized plots"
PLOT_FONT_SIZE = 14.0


def _plot_kwargs() -> dict[str, float]:
    return {
        "base_font_size": PLOT_FONT_SIZE,
        "minimum_font_size": PLOT_FONT_SIZE,
    }


def _save_cement_specific_ranking(run_date: date) -> Path:
    results = simulate_cement_results(
        sample_size=CEMENT_SAMPLE_SIZE,
        random_seed=CEMENT_RANDOM_SEED,
        retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
    )
    _, ranking_summary = calculate_cement_npv_rankings_from_results(
        results=results,
        npv_scale="EUR/t",
    )
    return plot_average_rank_bars(
        ranking_summary=_with_cement_display_labels(ranking_summary),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Average_NPV_Rank_per_t_Cement_14pt",
            run_date=run_date,
        ),
        title="Monte Carlo NPV per tonne Ranking",
        random_seed=CEMENT_RANDOM_SEED,
        **_plot_kwargs(),
    )


def _save_electricity_specific_ranking(run_date: date) -> Path:
    results = simulate_electricity_results(
        sample_size=ELECTRICITY_SAMPLE_SIZE,
        random_seed=ELECTRICITY_RANDOM_SEED,
    )
    _, ranking_summary = calculate_electricity_npv_rankings_from_results(
        results=results,
        npv_scale="EUR/MWh",
    )
    return plot_average_rank_bars(
        ranking_summary=_with_electricity_display_labels(ranking_summary),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Average_NPV_Rank_per_MWh_Electricity_14pt",
            run_date=run_date,
        ),
        title="Monte Carlo NPV per MWh Ranking",
        random_seed=ELECTRICITY_RANDOM_SEED,
        **_plot_kwargs(),
    )


def _save_cement_mean_npv(run_date: date) -> Path:
    results = simulate_cement_results(
        sample_size=CEMENT_SAMPLE_SIZE,
        random_seed=CEMENT_RANDOM_SEED,
        retrofit_bau_mode=DEFAULT_RETROFIT_BAU_MODE,
    )
    summary = cement_npv_distribution_summary(results, npv_scale="EUR/t")
    return plot_mean_npv_technology_bars(
        values_million_eur=cement_distribution_stat(summary, "mean"),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Mean_NPV_per_t_Cement_14pt",
            run_date=run_date,
        ),
        title="Monte Carlo mean NPV per tonne by cement technology",
        median_values_million_eur=cement_distribution_stat(summary, "median"),
        lower_values_million_eur=cement_distribution_stat(summary, "p05"),
        upper_values_million_eur=cement_distribution_stat(summary, "p95"),
        sample_size=CEMENT_SAMPLE_SIZE,
        random_seed=CEMENT_RANDOM_SEED,
        x_axis_label="NPV (EUR/t)",
        **_plot_kwargs(),
    )


def _save_cement_deterministic_npv(run_date: date) -> Path:
    return plot_mean_npv_technology_bars(
        values_million_eur=calculate_deterministic_cement_npv(npv_scale="EUR/t"),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Deterministic_NPV_per_t_Cement_14pt",
            run_date=run_date,
        ),
        title="Deterministic NPV per tonne (EUR/t)",
        x_axis_label="NPV (EUR/t)",
        **_plot_kwargs(),
    )


def _save_electricity_mean_npv(run_date: date) -> Path:
    results = simulate_electricity_results(
        sample_size=ELECTRICITY_SAMPLE_SIZE,
        random_seed=ELECTRICITY_RANDOM_SEED,
    )
    summary = electricity_npv_distribution_summary(results, npv_scale="EUR/MWh")
    return plot_mean_npv_technology_bars(
        values_million_eur=electricity_distribution_stat(summary, "mean"),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Mean_NPV_per_MWh_Electricity_14pt",
            run_date=run_date,
        ),
        title="Monte Carlo mean NPV per MWh by electricity technology",
        median_values_million_eur=electricity_distribution_stat(summary, "median"),
        lower_values_million_eur=electricity_distribution_stat(summary, "p05"),
        upper_values_million_eur=electricity_distribution_stat(summary, "p95"),
        sample_size=ELECTRICITY_SAMPLE_SIZE,
        random_seed=ELECTRICITY_RANDOM_SEED,
        x_axis_label="NPV (EUR/MWh)",
        **_plot_kwargs(),
    )


def _save_electricity_deterministic_npv(run_date: date) -> Path:
    return plot_mean_npv_technology_bars(
        values_million_eur=calculate_deterministic_electricity_npv(npv_scale="EUR/MWh"),
        output_path=dated_figure_path(
            OUTPUT_DIR,
            "Deterministic_NPV_per_MWh_Electricity_14pt",
            run_date=run_date,
        ),
        title="Deterministic NPV per MWh (EUR/MWh)",
        x_axis_label="NPV (EUR/MWh)",
        **_plot_kwargs(),
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_date = date.today()
    output_paths = (
        _save_cement_specific_ranking(run_date),
        _save_electricity_specific_ranking(run_date),
        _save_cement_mean_npv(run_date),
        _save_cement_deterministic_npv(run_date),
        _save_electricity_mean_npv(run_date),
        _save_electricity_deterministic_npv(run_date),
    )
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
