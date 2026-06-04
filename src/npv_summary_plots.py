"""Reusable plotting helpers for NPV technology comparisons."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd


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


def plot_average_rank_bars(
    ranking_summary: pd.DataFrame,
    output_path: Path,
    title: str = "Monte Carlo NPV Ranking",
) -> Path:
    """Save an average-rank chart with rank-frequency counts."""

    required_columns = {
        "technology",
        "average_rank",
        "probability_rank_1",
        "probability_top_3",
    }
    missing_columns = sorted(required_columns - set(ranking_summary.columns))
    if missing_columns:
        raise KeyError(f"ranking_summary is missing columns: {missing_columns}")
    if ranking_summary.empty:
        raise ValueError("ranking_summary must contain at least one row.")

    sorted_summary = ranking_summary.sort_values(
        ["average_rank", "technology"],
    )
    label_column = "display_label" if "display_label" in sorted_summary else "technology"
    labels = sorted_summary[label_column].astype(str).tolist()
    average_ranks = sorted_summary["average_rank"].astype(float).tolist()
    probability_rank_1 = sorted_summary["probability_rank_1"].astype(float).tolist()
    probability_top_3 = sorted_summary["probability_top_3"].astype(float).tolist()
    n_simulations = int(sorted_summary["n_simulations"].max())
    rank_count_columns = sorted(
        [
            column
            for column in sorted_summary.columns
            if column.startswith("rank_") and column.endswith("_count")
        ],
        key=lambda column: int(column.removeprefix("rank_").removesuffix("_count")),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure_height = max(5.6, 0.58 * len(labels) + 2.2)
    if rank_count_columns:
        fig, (ax, count_ax) = plt.subplots(
            1,
            2,
            figsize=(14.0, figure_height),
            dpi=160,
            gridspec_kw={"width_ratios": [1.65, 1.45], "wspace": 0.12},
        )
    else:
        fig, ax = plt.subplots(figsize=(8.2, figure_height), dpi=160)
        count_ax = None

    y_positions = range(len(labels))
    bar_color = "#4472C4"
    ax.barh(y_positions, average_ranks, color=bar_color, height=0.42)

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=9, color="#5a5a5a")
    ax.invert_yaxis()
    ax.set_title("Average rank", fontsize=12, color="#4d4d4d", pad=10)
    ax.set_xlabel("Mean rank across simulations (1 = highest NPV)", fontsize=9, color="#5a5a5a")

    max_rank = max(max(average_ranks), len(rank_count_columns))
    label_space = 3.8
    ax.set_xlim(0, max_rank + label_space)
    ax.set_xticks(range(1, int(max_rank) + 1))
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)

    for y_position, rank, rank_1, top_3 in zip(
        y_positions,
        average_ranks,
        probability_rank_1,
        probability_top_3,
    ):
        label = f"avg {rank:.2f} | rank 1 {rank_1:.1%} | top 3 {top_3:.1%}"
        ax.text(
            rank + 0.22,
            y_position,
            label,
            va="center",
            ha="left",
            fontsize=8.5,
            color="#333333",
        )

    ax.tick_params(axis="x", colors="#7a7a7a", labelsize=8)
    ax.tick_params(axis="y", left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.patch.set_facecolor("white")
    fig.patch.set_edgecolor("#d0d0d0")
    fig.patch.set_linewidth(1.0)
    ax.set_facecolor("white")

    if count_ax is not None:
        rank_numbers = [
            int(column.removeprefix("rank_").removesuffix("_count"))
            for column in rank_count_columns
        ]
        rank_counts = sorted_summary[rank_count_columns].astype(int)
        count_cmap = LinearSegmentedColormap.from_list(
            "rank_counts_blue",
            ["#f7f9fc", "#d9e5f6", bar_color],
        )
        count_ax.imshow(rank_counts, aspect="auto", cmap=count_cmap)
        count_ax.set_title("Number of simulations by rank", fontsize=12, color="#4d4d4d", pad=10)
        count_ax.set_xticks(range(len(rank_numbers)))
        count_ax.set_xticklabels(
            [
                f"{rank}\n(best)" if rank == 1 else f"{rank}\n(worst)" if rank == max(rank_numbers) else str(rank)
                for rank in rank_numbers
            ],
            fontsize=8,
            color="#5a5a5a",
        )
        count_ax.set_yticks(list(y_positions))
        count_ax.set_yticklabels([])
        count_ax.tick_params(axis="both", length=0)
        count_ax.set_xlabel("Rank reached in a simulation", fontsize=9, color="#5a5a5a")

        max_count = int(rank_counts.to_numpy().max())
        for y_position, row in enumerate(rank_counts.to_numpy()):
            for x_position, count in enumerate(row):
                text_color = "white" if max_count and count > max_count * 0.55 else "#333333"
                count_ax.text(
                    x_position,
                    y_position,
                    f"{count:,}",
                    ha="center",
                    va="center",
                    fontsize=7.2,
                    color=text_color,
                )

        for spine in count_ax.spines.values():
            spine.set_visible(False)
        count_ax.set_facecolor("white")

    fig.suptitle(title, fontsize=15, color="#444444", y=0.98)
    fig.text(
        0.012,
        0.025,
        (
            f"Ranks are calculated within each Monte Carlo simulation by NPV "
            f"(rank 1 = highest NPV, rank {int(max_rank)} = lowest NPV). "
            f"Sample size: {n_simulations:,} simulations."
        ),
        fontsize=8.5,
        color="#5a5a5a",
    )
    fig.subplots_adjust(
        left=0.12,
        right=0.985,
        top=0.86,
        bottom=0.14,
        wspace=0.12,
    )
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)

    return output_path
