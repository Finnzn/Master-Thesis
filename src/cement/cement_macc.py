"""Cement marginal abatement cost curve calculations.

The MACC compares each cement technology with the BAU cement baseline. The
abatement potential is direct stack-emissions abatement only:

    BAU direct emissions - technology direct emissions

Carbon-price payments are deliberately excluded from the cost numerator. This
keeps the curve focused on the technology cost of reducing emissions, not on the
financial offset created by the model's carbon-price assumption.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys
from typing import Mapping

import numpy as np
import pandas as pd

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cement.cement_npv_deterministic import calculate_deterministic_cement_results
from cement.cement_npv_monte_carlo import (
    DEFAULT_RANDOM_SEED,
    DEFAULT_RETROFIT_BAU_MODE,
    DEFAULT_SAMPLE_SIZE,
    simulate_cement_results,
)
from general_parameters import INTEREST_RATE
from npv_finance import calculate_level_cash_flow_present_value_factor


CEMENT_MACC_TECHNOLOGY_LABELS = {
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

DEFAULT_MACC_TECHNOLOGIES = tuple(
    technology
    for technology in CEMENT_MACC_TECHNOLOGY_LABELS
    if technology != "bau"
)

MACC_COLUMNS = [
    "technology",
    "label",
    "annual_abatement_tco2",
    "annual_abatement_mtco2",
    "abatement_share_of_bau",
    "incremental_annual_cost_eur",
    "abatement_cost_eur_per_tco2",
    "abatement_cost_p05_eur_per_tco2",
    "abatement_cost_median_eur_per_tco2",
    "abatement_cost_p95_eur_per_tco2",
]


def deterministic_cement_macc(
    technologies: tuple[str, ...] = DEFAULT_MACC_TECHNOLOGIES,
) -> pd.DataFrame:
    """Calculate deterministic cement MACC values relative to BAU."""

    selected_technologies = ("bau", *technologies)
    results = calculate_deterministic_cement_results(
        technologies=selected_technologies,
    )
    return build_cement_macc_table(results)


def simulated_cement_macc(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] = DEFAULT_MACC_TECHNOLOGIES,
    retrofit_bau_mode: str = DEFAULT_RETROFIT_BAU_MODE,
) -> pd.DataFrame:
    """Calculate cement MACC values from aligned Monte Carlo simulations.

    The headline abatement cost is the aggregate ratio of mean incremental cost
    to mean abatement. Draw-level cost quantiles are also reported because
    technologies with very small sampled abatement can have long cost tails.
    """

    selected_technologies = ("bau", *technologies)
    results = simulate_cement_results(
        sample_size=sample_size,
        random_seed=random_seed,
        technologies=selected_technologies,
        retrofit_bau_mode=retrofit_bau_mode,
    )
    return build_cement_macc_table(results)


def build_cement_macc_table(
    results_by_technology: Mapping[str, Mapping[str, object]],
) -> pd.DataFrame:
    """Build a cement MACC table from deterministic or simulated result mappings."""

    if "bau" not in results_by_technology:
        raise ValueError("results_by_technology must include 'bau'.")

    bau = results_by_technology["bau"]
    bau_annual_cost = _annual_cost_excluding_revenue_and_carbon(bau)
    bau_annual_emissions = _annual_direct_emissions(bau)

    rows = []
    for technology, results in results_by_technology.items():
        if technology == "bau":
            continue

        annual_abatement = bau_annual_emissions - _annual_direct_emissions(results)
        incremental_annual_cost = (
            _annual_cost_excluding_revenue_and_carbon(results) - bau_annual_cost
        )
        positive_abatement = annual_abatement > 0
        if not np.any(positive_abatement):
            continue

        abatement_cost = np.divide(
            incremental_annual_cost,
            annual_abatement,
            out=np.full_like(incremental_annual_cost, np.nan, dtype=float),
            where=positive_abatement,
        )
        finite_abatement_cost = abatement_cost[np.isfinite(abatement_cost)]
        bau_emissions_for_share = np.where(
            bau_annual_emissions > 0,
            bau_annual_emissions,
            np.nan,
        )
        abatement_share = annual_abatement / bau_emissions_for_share
        mean_annual_abatement = float(np.nanmean(annual_abatement))
        mean_incremental_annual_cost = float(np.nanmean(incremental_annual_cost))

        rows.append(
            {
                "technology": technology,
                "label": CEMENT_MACC_TECHNOLOGY_LABELS.get(technology, technology),
                "annual_abatement_tco2": mean_annual_abatement,
                "annual_abatement_mtco2": mean_annual_abatement / 1e6,
                "abatement_share_of_bau": float(np.nanmean(abatement_share)),
                "incremental_annual_cost_eur": mean_incremental_annual_cost,
                "abatement_cost_eur_per_tco2": _safe_divide_scalar(
                    mean_incremental_annual_cost,
                    mean_annual_abatement,
                ),
                "abatement_cost_p05_eur_per_tco2": _nanpercentile_or_nan(
                    finite_abatement_cost,
                    5,
                ),
                "abatement_cost_median_eur_per_tco2": _nanpercentile_or_nan(
                    finite_abatement_cost,
                    50,
                ),
                "abatement_cost_p95_eur_per_tco2": _nanpercentile_or_nan(
                    finite_abatement_cost,
                    95,
                ),
            }
        )

    table = pd.DataFrame(rows, columns=MACC_COLUMNS)
    if table.empty:
        return table
    return table.sort_values("abatement_cost_eur_per_tco2").reset_index(drop=True)


def plot_cement_macc(
    macc_table: pd.DataFrame,
    output_path: Path | None = None,
    title: str = "Cement Sector - Marginal Abatement Cost Curve",
) -> object:
    """Plot a cement marginal abatement cost curve."""

    import matplotlib.pyplot as plt

    if macc_table.empty:
        raise ValueError("macc_table must contain at least one abatement option.")

    table = macc_table.sort_values("abatement_cost_eur_per_tco2").reset_index(
        drop=True
    )
    widths = table["annual_abatement_mtco2"].to_numpy(dtype=float)
    heights = table["abatement_cost_eur_per_tco2"].to_numpy(dtype=float)
    left_edges = np.concatenate(([0.0], np.cumsum(widths[:-1])))
    centers = left_edges + widths / 2.0

    colors = plt.get_cmap("tab20").colors
    fig_width = max(10.0, 1.4 * len(table) + 5.0)
    fig, ax = plt.subplots(figsize=(fig_width, 6.4), dpi=160)

    bars = ax.bar(
        left_edges,
        heights,
        width=widths,
        align="edge",
        color=[colors[index % len(colors)] for index in range(len(table))],
        edgecolor="white",
        linewidth=0.8,
    )
    ax.axhline(0.0, color="#222222", linewidth=0.9)

    y_min = min(0.0, float(np.nanmin(heights)))
    y_max = max(0.0, float(np.nanmax(heights)))
    y_span = y_max - y_min if y_max != y_min else 1.0
    label_y = 0.08 * y_span
    y_upper = max(y_max + 0.12 * y_span, label_y + 0.50 * y_span)
    ax.set_ylim(y_min - 0.18 * y_span, y_upper)
    ax.set_xlim(0.0, float(np.sum(widths)) * 1.02)

    for index, bar in enumerate(bars):
        label = table.loc[index, "label"]
        width = widths[index]
        height = heights[index]
        x = centers[index]
        ax.vlines(
            x,
            0.0,
            max(0.0, label_y - 0.012 * y_span),
            color="#222222",
            linewidth=0.7,
        )
        ax.text(
            x,
            label_y,
            label,
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#1f1f1f",
            rotation=90,
        )
        width_label_y = (
            height - 0.04 * y_span
            if height < 0
            else -0.04 * y_span
        )
        ax.text(
            x,
            width_label_y,
            f"{width:.2f}",
            ha="center",
            va="top",
            fontsize=8,
            color="#1f1f1f",
            rotation=35,
        )

    ax.set_title(
        title,
        loc="left",
        fontsize=14,
        fontweight="bold",
        color="#1f2933",
        pad=18,
    )
    ax.set_ylabel("Abatement cost (EUR/tCO2)", fontsize=10, color="#1f2933")
    ax.set_xlabel(
        "Direct abatement potential (MtCO2/year)",
        fontsize=10,
        color="#1f2933",
    )
    ax.grid(axis="y", color="#e2e2e2", linestyle=(0, (2, 5)), linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", labelsize=8, colors="#4b5563")
    ax.tick_params(axis="x", length=0)
    ax.set_xticks([])
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#222222")
    fig.text(
        0.99,
        0.02,
        "Costs exclude carbon payments; widths show annual direct emissions avoided.",
        ha="right",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, bbox_inches="tight")

    return fig


def generate_cement_macc_outputs(
    project_root: Path,
    output_dir: Path | None = None,
    deterministic: bool = True,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> tuple[Path, Path]:
    """Save one cement MACC CSV and PNG figure."""

    table = (
        deterministic_cement_macc()
        if deterministic
        else simulated_cement_macc(sample_size=sample_size, random_seed=random_seed)
    )
    run_date = date.today().isoformat()
    mode = "Deterministic" if deterministic else "Simulated"

    processed_dir = output_dir or project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    csv_path = processed_dir / f"{run_date}-Cement_MACC_{mode}.csv"
    table.to_csv(csv_path, index=False)

    figure_path = project_root / "figures" / f"{run_date}-Cement_MACC_{mode}.png"
    fig = plot_cement_macc(
        table,
        output_path=figure_path,
        title=f"Cement Sector - Marginal Abatement Cost Curve ({mode.lower()})",
    )
    import matplotlib.pyplot as plt

    plt.close(fig)
    return csv_path, figure_path


def _annual_cost_excluding_revenue_and_carbon(
    results: Mapping[str, object],
) -> np.ndarray:
    """Calculate annualized technology cost excluding revenue and carbon payments."""

    lifetime_years = int(_first_value(results["lifetime_years"]))
    present_value_factor = calculate_level_cash_flow_present_value_factor(
        lifetime_years=lifetime_years,
        discount_rate=INTEREST_RATE.value,
    )
    annualized_capex = _array(results["initial_capex_eur"]) / present_value_factor
    return (
        annualized_capex
        + _array(results["annual_fixed_opex_eur"])
        + _array(results["annual_variable_opex_eur"])
        + _array(results["annual_fuel_cost_eur"])
        + _array(results["annual_electricity_cost_eur"])
    )


def _annual_direct_emissions(results: Mapping[str, object]) -> np.ndarray:
    """Calculate annual direct stack emissions in tCO2/year."""

    return _array(results["annual_output_t"]) * _array(
        results["emissions_tco2_per_t"]
    )


def _array(values: object) -> np.ndarray:
    """Return a one-dimensional float array."""

    return np.asarray(values, dtype=float)


def _safe_divide_scalar(numerator: float, denominator: float) -> float:
    """Divide two scalars and return NaN for non-positive abatement."""

    if denominator <= 0 or not np.isfinite(denominator):
        return float("nan")
    return numerator / denominator


def _nanpercentile_or_nan(values: np.ndarray, percentile: float) -> float:
    """Calculate a percentile or NaN when no finite values exist."""

    if values.size == 0:
        return float("nan")
    return float(np.nanpercentile(values, percentile))


def _first_value(values: object) -> float:
    """Return the first numeric value from an array-like object."""

    return float(np.asarray(values, dtype=float).flat[0])


def main() -> None:
    """Run the cement MACC generator from the command line."""

    parser = argparse.ArgumentParser(
        description="Generate a cement marginal abatement cost curve."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--simulated",
        action="store_true",
        help="Use mean Monte Carlo MACC values instead of deterministic values.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
    )
    args = parser.parse_args()

    paths = generate_cement_macc_outputs(
        project_root=args.project_root,
        output_dir=args.output_dir,
        deterministic=not args.simulated,
        sample_size=args.sample_size,
        random_seed=args.random_seed,
    )
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
