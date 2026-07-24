"""Generate the thesis technology-input financial sensitivity analysis.

The analysis is deliberately narrow: every included input is changed one at a
time by the same relative amount (20% by default), and the resulting change in
levelized net margin is recorded. It does not perform Monte Carlo
uncertainty-range or correlation analysis.

Levelized net margin (EUR/t cement or EUR/MWh electricity) divides NPV by
discounted lifetime output. Product selling price and annual output are excluded
from the cross-technology heatmap because they are common comparison assumptions.
Lifetime and discount rate remain included as common financial assumptions.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
import pandas as pd

from sensitivity_analysis import (
    METRIC_LEVELIZED_NET_MARGIN,
    METRIC_TOTAL,
    available_technologies,
    base_inputs,
    build_sensitivity_table,
    calculate_metric_value,
    display_label,
)


TECHNOLOGY_LABELS = {
    "bau": "BAU",
    "ccs": "CCS",
    "ccgt": "CCGT",
    "ccgt_ccs": "CCGT with CCS",
    "hard_coal_ccs": "Hard coal with CCS",
    "pv": "PV",
    "beccs": "BECCS",
}

# Inputs retained for the first thesis step. Product selling price and annual
# output do not help distinguish technology uncertainty. Lifetime and discount
# rate are included to show sensitivity to common financial assumptions.
SENSITIVITY_SCOPE: Mapping[str, tuple[str, ...]] = {
    "cement": (
        "capex",
        "lifetime_years",
        "discount_rate",
        "fixed_opex",
        "variable_opex",
        "fuel_consumption",
        "fuel_price",
        "electricity_consumption",
        "electricity_price",
        "emissions",
        "carbon_price",
    ),
    "electricity": (
        "capex",
        "full_load_hours",
        "lifetime_years",
        "discount_rate",
        "fixed_opex",
        "variable_opex",
        "fuel_consumption",
        "fuel_price",
        "emissions",
        "carbon_price",
    ),
}

HEATMAP_PARAMETER_GROUPS: Mapping[str, Mapping[str, str]] = {
    "cement": {
        "Fuel use": "Fuel",
        "Fuel price": "Fuel",
        "Electricity use": "Electricity",
        "Electricity price": "Electricity",
        "Direct emissions": "Emissions",
        "Carbon price": "Emissions",
    },
    "electricity": {
        "Fuel use": "Fuel",
        "Fuel price": "Fuel",
        "Direct emissions": "Emissions",
        "Carbon price": "Emissions",
    },
}


def _technology_label(technology: str) -> str:
    """Return a publication-friendly technology name."""

    return TECHNOLOGY_LABELS.get(technology, display_label(technology))


def standardized_sensitivity(
    sector: str,
    variation_fraction: float,
    metric: str = METRIC_LEVELIZED_NET_MARGIN,
) -> pd.DataFrame:
    """Calculate equal-percentage NPV sensitivity for all technologies."""

    frames = []
    for technology in available_technologies(sector):
        inputs = base_inputs(sector, technology)
        table = build_sensitivity_table(
            sector=sector,
            inputs=inputs,
            variation_fraction=variation_fraction,
            metric=metric,
            included_attributes=SENSITIVITY_SCOPE[sector],
        ).copy()
        table.insert(0, "technology", technology)
        table.insert(0, "sector", sector)
        table["metric"] = metric
        table["base_metric_value"] = calculate_metric_value(
            sector,
            inputs,
            metric,
        )
        # Round away floating-point noise so mathematically identical product
        # terms (for example fuel use and fuel price) receive the same rank.
        ranking_impact = table["max_abs_impact"].round(12)
        table["rank"] = ranking_impact.rank(
            method="min",
            ascending=False,
        ).astype(int)
        table["relative_impact_percent"] = (
            table["max_abs_impact"]
            / table["max_abs_impact"].max()
            * 100.0
        ).fillna(0.0)
        frames.append(table)
    return pd.concat(frames, ignore_index=True)


def plot_sensitivity_heatmap(
    standardized: pd.DataFrame,
    sector: str,
    variation_fraction: float,
    output_path: Path,
    metric: str = METRIC_LEVELIZED_NET_MARGIN,
) -> Path:
    """Save a within-technology relative sensitivity heatmap for one sector."""

    fig = build_sensitivity_heatmap_figure(
        standardized=standardized,
        sector=sector,
        variation_fraction=variation_fraction,
        metric=metric,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
    return output_path


def build_sensitivity_heatmap_figure(
    standardized: pd.DataFrame,
    sector: str,
    variation_fraction: float,
    metric: str = METRIC_LEVELIZED_NET_MARGIN,
) -> plt.Figure:
    """Build a within-technology relative sensitivity heatmap for one sector."""

    sector_data = standardized.loc[standardized["sector"] == sector].copy()
    sector_data["heatmap_parameter"] = sector_data["parameter"].map(
        HEATMAP_PARAMETER_GROUPS.get(sector, {})
    ).fillna(sector_data["parameter"])
    sector_data = (
        sector_data.sort_values(["technology", "rank"])
        .groupby(["technology", "heatmap_parameter"], as_index=False)
        .agg(
            relative_impact_percent=("relative_impact_percent", "max"),
            rank=("rank", "min"),
        )
    )
    technologies = list(available_technologies(sector))
    parameters = list(
        dict.fromkeys(
            sector_data.sort_values(["technology", "rank"])[
                "heatmap_parameter"
            ].tolist()
        )
    )
    relative = (
        sector_data.pivot(
            index="technology",
            columns="heatmap_parameter",
            values="relative_impact_percent",
        )
        .reindex(index=technologies, columns=parameters)
        .fillna(0.0)
    )

    fig_width = max(9.0, 0.85 * len(parameters) + 3.2)
    fig_height = max(5.0, 0.55 * len(technologies) + 2.2)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=180)
    image = ax.imshow(
        relative.to_numpy(),
        cmap="YlOrRd",
        vmin=0.0,
        vmax=100.0,
        aspect="auto",
    )

    for row_index, technology in enumerate(technologies):
        for column_index, parameter in enumerate(parameters):
            value = relative.loc[technology, parameter]
            ax.text(
                column_index,
                row_index,
                f"{value:.0f}",
                ha="center",
                va="center",
                fontsize=8,
                color="white" if value >= 60 else "#263238",
            )

    ax.set_xticks(range(len(parameters)))
    ax.set_xticklabels(parameters, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(technologies)))
    ax.set_yticklabels(
        [_technology_label(technology) for technology in technologies],
        fontsize=8,
    )
    variation_percent = variation_fraction * 100.0
    metric_label = _metric_title_label(metric)
    ax.set_title(
        f"{sector.title()} technology-input sensitivity "
        f"({metric_label}, ±{variation_percent:.0f}%)",
        loc="left",
        fontsize=13,
        color="#26345d",
        pad=12,
    )
    ax.set_xlabel("Sensitivity variable", fontsize=9)
    ax.set_ylabel("Technology", fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.025)
    colorbar.set_label(
        "Impact relative to the largest driver in each technology (%)",
        fontsize=8,
    )
    colorbar.ax.tick_params(labelsize=7)
    fig.text(
        0.01,
        0.01,
        "100 = largest absolute change in levelized net margin for that technology. "
        "A value of 17 means 17% of that row's largest impact.",
        fontsize=8,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def generate_deep_dive(
    project_root: Path,
    output_dir: Path | None = None,
    variation_fraction: float = 0.20,
    metric: str = METRIC_LEVELIZED_NET_MARGIN,
) -> tuple[Path, ...]:
    """Save one standardized CSV and one heatmap per sector."""

    standardized = pd.concat(
        [
            standardized_sensitivity(sector, variation_fraction, metric=metric)
            for sector in ("cement", "electricity")
        ],
        ignore_index=True,
    )

    processed_dir = output_dir or project_root / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    prefix = date.today().isoformat()
    metric_suffix = _metric_filename_suffix(metric)
    variation_suffix = _variation_filename_suffix(variation_fraction)
    csv_path = processed_dir / (
        f"{prefix}-Sensitivity_standardized_{metric_suffix}_{variation_suffix}.csv"
    )
    standardized.to_csv(csv_path, index=False)

    figure_dir = project_root / "figures"
    figure_paths = tuple(
        plot_sensitivity_heatmap(
            standardized,
            sector=sector,
            variation_fraction=variation_fraction,
            output_path=figure_dir
            / (
                f"{prefix}-Sensitivity_Heatmap_Standardized_"
                f"{metric_suffix}_{variation_suffix}_{sector.title()}.png"
            ),
            metric=metric,
        )
        for sector in ("cement", "electricity")
    )
    return (csv_path, *figure_paths)


def _metric_title_label(metric: str) -> str:
    """Return a concise plot-title label for a sensitivity metric."""

    if metric == METRIC_LEVELIZED_NET_MARGIN:
        return "levelized net margin"
    if metric == METRIC_TOTAL:
        return "total NPV"
    raise ValueError(f"Unknown sensitivity metric: {metric!r}.")


def _metric_filename_suffix(metric: str) -> str:
    """Return a filename-safe label for a sensitivity metric."""

    if metric == METRIC_LEVELIZED_NET_MARGIN:
        return "Levelized_Net_Margin"
    if metric == METRIC_TOTAL:
        return "Total"
    raise ValueError(f"Unknown sensitivity metric: {metric!r}.")


def _variation_filename_suffix(variation_fraction: float) -> str:
    """Return a filename-safe percentage label for an input variation."""

    variation_percent = variation_fraction * 100.0
    label = f"{variation_percent:g}".replace(".", "p")
    return f"{label}pct"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate standardized technology-input NPV sensitivity outputs."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--variation",
        type=float,
        default=0.20,
        help="Equal relative one-at-a-time input movement.",
    )
    parser.add_argument(
        "--metric",
        choices=(METRIC_LEVELIZED_NET_MARGIN, METRIC_TOTAL),
        default=METRIC_LEVELIZED_NET_MARGIN,
        help="Financial metric used for the one-at-a-time sensitivity calculation.",
    )
    args = parser.parse_args()
    paths = generate_deep_dive(
        project_root=args.project_root,
        output_dir=args.output_dir,
        variation_fraction=args.variation,
        metric=args.metric,
    )
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
