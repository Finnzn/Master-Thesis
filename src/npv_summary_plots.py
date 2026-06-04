"""Reusable plotting helpers for NPV technology comparisons."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt


def dated_figure_path(
    output_dir: Path,
    stem: str,
    run_date: date | None = None,
    extension: str = "png",
) -> Path:
    """Build a dated figure path such as YYYY-MM-DD-Mean_NPV_Electricity.png."""

    figure_date = run_date or date.today()
    suffix = extension.lstrip(".")
    return output_dir / f"{figure_date.isoformat()}-{stem}.{suffix}"


def plot_mean_npv_technology_bars(
    values_million_eur: Mapping[str, float],
    output_path: Path,
    title: str = "Mean NPV (MEUR)",
) -> Path:
    """Save a horizontal positive/negative NPV bar chart.

    The helper is sector-agnostic: callers provide display labels and NPV values
    in million EUR. It can therefore be reused for electricity, cement, or other
    sectors once they produce the same summary mapping.
    """

    if not values_million_eur:
        raise ValueError("values_million_eur must contain at least one value.")

    sorted_items = sorted(
        values_million_eur.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    labels = [label for label, _ in sorted_items]
    values = [value for _, value in sorted_items]
    colors = ["#4EA72E" if value >= 0 else "#FF0F0F" for value in values]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure_height = max(4.6, 0.48 * len(values) + 1.5)
    fig, ax = plt.subplots(figsize=(7.5, figure_height), dpi=160)
    y_positions = range(len(labels))
    ax.barh(y_positions, values, color=colors, height=0.38)

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=9, color="#5a5a5a")
    ax.invert_yaxis()
    ax.axvline(0, color="#c8c8c8", linewidth=1.2)
    ax.set_title(title, fontsize=15, color="#555555", pad=14)

    max_abs_value = max(abs(value) for value in values)
    margin = max(25.0, 0.16 * max_abs_value)
    ax.set_xlim(min(values) - margin, max(values) + margin)

    for y_position, value in zip(y_positions, values):
        label = f"{value:.0f}"
        if value >= 0:
            ax.text(
                value + margin * 0.12,
                y_position,
                label,
                va="center",
                ha="left",
                fontsize=9,
                color="#333333",
            )
        else:
            ax.text(
                value - margin * 0.12,
                y_position,
                label,
                va="center",
                ha="right",
                fontsize=9,
                color="#333333",
            )

    ax.tick_params(axis="x", bottom=False, labelbottom=False)
    ax.tick_params(axis="y", left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.patch.set_facecolor("white")
    fig.patch.set_edgecolor("#d0d0d0")
    fig.patch.set_linewidth(1.0)
    ax.set_facecolor("white")
    fig.tight_layout(pad=1.2)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return output_path
