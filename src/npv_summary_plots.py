"""Reusable plotting helpers for NPV technology comparisons.

The calculation modules produce dictionaries and DataFrames; this module turns
those summaries into thesis-ready figures. It does not calculate NPV or rankings
itself, which keeps visual styling separate from model logic.
"""

from __future__ import annotations

from datetime import date
import math
from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd


def _plot_font_size(
    base_size: float,
    scale: float,
    minimum_font_size: float | None,
) -> float:
    """Scale one plot font size while optionally enforcing a minimum."""

    scaled_size = base_size * scale
    if minimum_font_size is None:
        return scaled_size
    return max(minimum_font_size, scaled_size)


def shared_axis_limits(
    *value_mappings: Mapping[str, float],
    relative_margin: float = 0.12,
    minimum_margin: float = 5.0,
) -> tuple[float, float]:
    """Return common x-axis limits for related value mappings."""

    values = [
        float(value)
        for value_mapping in value_mappings
        for value in value_mapping.values()
    ]
    if not values:
        raise ValueError("At least one value is required for shared axis limits.")

    lower = min(values)
    upper = max(values)
    max_abs_value = max(abs(lower), abs(upper))
    margin = max(minimum_margin, relative_margin * max_abs_value)
    if lower == upper:
        margin = max(margin, abs(lower) * 0.2, 1.0)
    return lower - margin, upper + margin


def shared_axis_ticks(
    axis_limits: tuple[float, float],
    target_intervals: int = 5,
) -> tuple[float, ...]:
    """Return readable tick positions for shared axis limits."""

    lower, upper = axis_limits
    if lower >= upper:
        raise ValueError("axis_limits must be an increasing (min, max) tuple.")
    span = upper - lower
    rough_step = span / target_intervals
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    if normalized <= 1:
        step = magnitude
    elif normalized <= 2:
        step = 2 * magnitude
    elif normalized <= 5:
        step = 5 * magnitude
    else:
        step = 10 * magnitude

    first_tick = math.ceil(lower / step) * step
    ticks: list[float] = []
    tick = first_tick
    while tick <= upper:
        ticks.append(round(tick, 10))
        tick += step
    if 0 not in ticks and lower < 0 < upper:
        ticks.append(0.0)
        ticks.sort()
    return tuple(ticks)


def fixed_financial_metric_bar_axis_config(
    sector: str,
    financial_metric: str,
    distribution_summary: Mapping[str, Mapping[str, float]],
    deterministic_values: Mapping[str, float],
) -> tuple[tuple[float, float], tuple[float, ...]]:
    """Return presentation axis limits and ticks for financial-metric chart pairs."""

    sector_key = sector.lower()
    p05_minimum = min(
        min(values["p05"] for values in distribution_summary.values()),
        min(deterministic_values.values()),
    )

    if sector_key == "cement" and financial_metric == "LNM":
        lower = -300 if p05_minimum < -200 else -200
        return (float(lower), 50.0), tuple(float(value) for value in range(lower, 51, 50))
    if sector_key == "electricity" and financial_metric == "LNM":
        return (-150.0, 50.0), (-150.0, -100.0, -50.0, 0.0, 50.0)
    if sector_key == "cement" and financial_metric == "NPV":
        lower = math.floor(p05_minimum / 200) * 200
        first_major_tick = math.ceil(lower / 1000) * 1000
        return (float(lower), 2000.0), tuple(
            float(value) for value in range(int(first_major_tick), 2001, 1000)
        )
    if sector_key == "electricity" and financial_metric == "NPV":
        lower = math.floor(p05_minimum / 1000) * 1000
        return (float(lower), 1000.0), tuple(
            float(value) for value in range(int(lower), 1001, 1000)
        )

    x_axis_limits = shared_axis_limits(
        {label: values["p05"] for label, values in distribution_summary.items()},
        {label: values["p95"] for label, values in distribution_summary.items()},
        deterministic_values,
    )
    return x_axis_limits, shared_axis_ticks(x_axis_limits)


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


def plot_financial_metric_technology_bars(
    values: Mapping[str, float],
    output_path: Path | None,
    title: str = "Mean NPV (MEUR)",
    median_values: Mapping[str, float] | None = None,
    lower_values: Mapping[str, float] | None = None,
    upper_values: Mapping[str, float] | None = None,
    sample_size: int | None = None,
    random_seed: int | None = None,
    x_axis_label: str = "NPV (million EUR)",
    base_font_size: float = 9.0,
    minimum_font_size: float | None = None,
    figure_size_inches: tuple[float, float] | None = None,
    dpi: int = 160,
    tight_bbox: bool = True,
    note_text: str | None = None,
    show_legend: bool = True,
    tight_layout_pad: float = 1.2,
    x_axis_limits: tuple[float, float] | None = None,
    x_axis_ticks: tuple[float, ...] | None = None,
) -> Path | None:
    """Plot a horizontal positive/negative financial-metric bar chart.

    The helper is sector-agnostic: callers provide display labels and values in
    the selected metric's display unit.

    For Monte Carlo outputs, callers can also pass median and percentile values.
    In that case the bars still show the mean NPV, while markers and whiskers
    show the distribution behind that mean.
    """

    if not values:
        raise ValueError("values must contain at least one value.")

    sorted_items = sorted(
        values.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    labels = [label for label, _ in sorted_items]
    values = [value for _, value in sorted_items]
    colors = ["#4EA72E" if value >= 0 else "#FF0F0F" for value in values]
    # Uncertainty markers are optional. This lets deterministic and Monte Carlo
    # figures use the same visual style while only Monte Carlo figures show the
    # simulated spread.
    has_uncertainty = (
        median_values is not None
        and lower_values is not None
        and upper_values is not None
    )
    if has_uncertainty:
        missing_uncertainty_labels = [
            label
            for label in labels
            if label not in median_values
            or label not in lower_values
            or label not in upper_values
        ]
        if missing_uncertainty_labels:
            raise KeyError(
                "uncertainty mappings are missing labels: "
                f"{missing_uncertainty_labels}"
            )
        medians = [median_values[label] for label in labels]
        lower_uncertainty_values = [lower_values[label] for label in labels]
        upper_uncertainty_values = [upper_values[label] for label in labels]

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    font_scale = base_font_size / 9.0
    label_font_size = _plot_font_size(9.0, font_scale, minimum_font_size)
    tick_font_size = _plot_font_size(8.0, font_scale, minimum_font_size)
    title_font_size = _plot_font_size(14.0, font_scale, minimum_font_size)
    note_font_size = _plot_font_size(8.5, font_scale, minimum_font_size)
    legend_font_size = _plot_font_size(8.0, font_scale, minimum_font_size)
    figure_height = max(5.0 * font_scale, 0.52 * font_scale * len(values) + 1.7 * font_scale)
    figure_width = (9.5 if has_uncertainty else 7.5) * font_scale
    if figure_size_inches is not None:
        figure_width, figure_height = figure_size_inches
    fig, ax = plt.subplots(figsize=(figure_width, figure_height), dpi=dpi)
    y_positions = list(range(len(labels)))
    ax.barh(y_positions, values, color=colors, height=0.42, label="Mean")

    if has_uncertainty:
        # Percentile whiskers show the simulated 5th-95th percentile range. The
        # median marker is plotted separately so readers can see whether the
        # distribution is skewed relative to the mean.
        ax.errorbar(
            values,
            y_positions,
            xerr=[
                [
                    value - lower
                    for value, lower in zip(values, lower_uncertainty_values)
                ],
                [
                    upper - value
                    for value, upper in zip(values, upper_uncertainty_values)
                ],
            ],
            fmt="none",
            ecolor="#4d4d4d",
            elinewidth=1.1,
            capsize=3,
            label="5th-95th percentile",
        )
        ax.scatter(
            medians,
            y_positions,
            color="white",
            edgecolor="#333333",
            s=26,
            zorder=3,
            label="Median",
        )

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=label_font_size, color="#5a5a5a")
    ax.invert_yaxis()
    ax.axvline(0, color="#bbbbbb", linewidth=1.1)
    if title:
        ax.set_title(title, fontsize=title_font_size, color="#444444", pad=12 * font_scale)
    ax.set_xlabel(x_axis_label, fontsize=label_font_size, color="#5a5a5a")
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)

    if x_axis_limits is not None:
        lower_limit, upper_limit = x_axis_limits
        if lower_limit >= upper_limit:
            raise ValueError("x_axis_limits must be an increasing (min, max) tuple.")
        ax.set_xlim(lower_limit, upper_limit)
        margin = 0.04 * (upper_limit - lower_limit)
    elif has_uncertainty:
        max_abs_value = max(
            max(abs(value) for value in lower_uncertainty_values),
            max(abs(value) for value in upper_uncertainty_values),
        )
        margin = max(60.0, 0.12 * max_abs_value)
        ax.set_xlim(
            min(lower_uncertainty_values) - margin,
            max(upper_uncertainty_values) + margin,
        )
    else:
        max_abs_value = max(abs(value) for value in values)
        margin = max(25.0, 0.16 * max_abs_value)
        ax.set_xlim(min(values) - margin, max(values) + margin)
    if x_axis_ticks is not None:
        ax.set_xticks(x_axis_ticks)

    if has_uncertainty:
        # The note records reproducibility context without putting it in the title.
        # This keeps the figure readable while still documenting the sample size
        # and seed used to create the uncertainty range.
        note_parts = []
        if sample_size is not None:
            note_parts.append(f"Sample size: {sample_size:,}")
        if random_seed is not None:
            note_parts.append(f"random seed: {random_seed}")
        note = "; ".join(note_parts)
        note = f"{note}. " if note else ""
        display_note = (
            note_text
            if note_text is not None
            else f"{note}Bars show the mean; whiskers show simulated 5th-95th percentiles."
        )
        if display_note:
            ax.text(
                0,
                -0.12,
                display_note,
                transform=ax.transAxes,
                fontsize=note_font_size,
                color="#5a5a5a",
            )
        if show_legend:
            ax.legend(
                loc="upper left",
                bbox_to_anchor=(1.01, 1.0),
                fontsize=legend_font_size,
                frameon=False,
            )
    else:
        for y_position, value in zip(y_positions, values):
            label = f"{value:.0f}"
            if value >= 0:
                ax.text(
                    value + margin * 0.12,
                    y_position,
                    label,
                    va="center",
                    ha="left",
                    fontsize=label_font_size,
                    color="#333333",
                )
            else:
                ax.text(
                    value - margin * 0.12,
                    y_position,
                    label,
                    va="center",
                    ha="right",
                    fontsize=label_font_size,
                    color="#333333",
                )

    ax.tick_params(axis="x", colors="#7a7a7a", labelsize=tick_font_size)
    ax.tick_params(axis="y", left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.patch.set_facecolor("white")
    fig.patch.set_edgecolor("#d0d0d0")
    fig.patch.set_linewidth(1.0)
    ax.set_facecolor("white")
    fig.tight_layout(pad=tight_layout_pad)
    if output_path is None:
        return None

    save_kwargs = {"bbox_inches": "tight"} if tight_bbox else {}
    fig.savefig(output_path, **save_kwargs)
    plt.close(fig)
    return output_path


def plot_average_rank_bars(
    ranking_summary: pd.DataFrame,
    output_path: Path | None,
    title: str = "Monte Carlo NPV Ranking",
    metric_label: str = "NPV",
    random_seed: int | None = None,
    base_font_size: float = 9.0,
    minimum_font_size: float | None = None,
    figure_size_inches: tuple[float, float] | None = None,
    dpi: int = 160,
    tight_bbox: bool = True,
    note_text: str | None = None,
    tight_layout_pad: float | None = None,
    show_rank_counts: bool = True,
    show_rank_annotations: bool = True,
) -> Path | None:
    """Plot an average-rank chart with rank-frequency counts.

    The left panel summarizes average rank and top-rank probabilities. If the
    ranking summary contains rank-count columns, the right panel shows how often
    each technology reached every rank, which is useful for spotting unstable
    or polarized ranking behavior.
    """

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
    # Ranking CSVs can include rank_1_count, rank_2_count, ...; plot them if present.
    # The function still works without these columns for older summary tables.
    rank_count_columns = sorted(
        [
            column
            for column in sorted_summary.columns
            if column.startswith("rank_") and column.endswith("_count")
        ],
        key=lambda column: int(column.removeprefix("rank_").removesuffix("_count")),
    )
    if not show_rank_counts:
        rank_count_columns = []

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    font_scale = base_font_size / 9.0
    label_font_size = _plot_font_size(9.0, font_scale, minimum_font_size)
    tick_font_size = _plot_font_size(8.0, font_scale, minimum_font_size)
    panel_title_font_size = _plot_font_size(12.0, font_scale, minimum_font_size)
    annotation_font_size = _plot_font_size(8.5, font_scale, minimum_font_size)
    heatmap_value_font_size = _plot_font_size(7.2, font_scale, minimum_font_size)
    suptitle_font_size = _plot_font_size(15.0, font_scale, minimum_font_size)
    figure_note_font_size = _plot_font_size(8.5, font_scale, minimum_font_size)
    figure_height = max(5.6 * font_scale, 0.58 * font_scale * len(labels) + 2.2 * font_scale)
    if rank_count_columns:
        figure_width = 14.0 * font_scale
        if figure_size_inches is not None:
            figure_width, figure_height = figure_size_inches
        fig, (ax, count_ax) = plt.subplots(
            1,
            2,
            figsize=(figure_width, figure_height),
            dpi=dpi,
            gridspec_kw={"width_ratios": [1.65, 1.45], "wspace": 0.12},
        )
    else:
        figure_width = 8.2 * font_scale
        if figure_size_inches is not None:
            figure_width, figure_height = figure_size_inches
        fig, ax = plt.subplots(figsize=(figure_width, figure_height), dpi=dpi)
        count_ax = None

    y_positions = range(len(labels))
    bar_color = "#4472C4"
    ax.barh(y_positions, average_ranks, color=bar_color, height=0.42)

    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(labels, fontsize=label_font_size, color="#5a5a5a")
    ax.invert_yaxis()
    ax.set_title("Average rank", fontsize=panel_title_font_size, color="#4d4d4d", pad=10 * font_scale)
    ax.set_xlabel(
        f"Mean rank across simulations (1 = highest {metric_label})",
        fontsize=label_font_size,
        color="#5a5a5a",
    )

    max_rank = max(max(average_ranks), len(rank_count_columns))
    if show_rank_annotations and count_ax is None:
        label_space = 7.5 * font_scale
    elif show_rank_annotations:
        label_space = 3.8 * font_scale
    else:
        label_space = 0.5
    ax.set_xlim(0, max_rank + label_space)
    ax.set_xticks(range(1, int(max_rank) + 1))
    ax.grid(axis="x", color="#e6e6e6", linewidth=0.8)
    ax.set_axisbelow(True)

    if show_rank_annotations:
        for y_position, rank, rank_1, top_3 in zip(
            y_positions,
            average_ranks,
            probability_rank_1,
            probability_top_3,
        ):
            label = f"avg {rank:.2f} | #1 {rank_1:.1%} | T3 {top_3:.1%}"
            ax.text(
                rank + 0.22,
                y_position,
                label,
                va="center",
                ha="left",
                fontsize=annotation_font_size,
                color="#333333",
            )

    ax.tick_params(axis="x", colors="#7a7a7a", labelsize=tick_font_size)
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
        # The heatmap shows how often each technology reached each rank. Darker
        # cells mean that technology landed in that rank more often across the
        # Monte Carlo simulations.
        count_cmap = LinearSegmentedColormap.from_list(
            "rank_counts_blue",
            ["#f7f9fc", "#d9e5f6", bar_color],
        )
        count_ax.imshow(rank_counts, aspect="auto", cmap=count_cmap)
        count_ax.set_title("Number of simulations by rank", fontsize=panel_title_font_size, color="#4d4d4d", pad=10 * font_scale)
        count_ax.set_xticks(range(len(rank_numbers)))
        count_ax.set_xticklabels(
            [
                f"{rank}\n(best)" if rank == 1 else f"{rank}\n(worst)" if rank == max(rank_numbers) else str(rank)
                for rank in rank_numbers
            ],
            fontsize=tick_font_size,
            color="#5a5a5a",
        )
        count_ax.set_yticks(list(y_positions))
        count_ax.set_yticklabels([])
        count_ax.tick_params(axis="both", length=0)
        count_ax.set_xlabel("Rank reached in a simulation", fontsize=label_font_size, color="#5a5a5a")

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
                    fontsize=heatmap_value_font_size,
                    color=text_color,
                )

        for spine in count_ax.spines.values():
            spine.set_visible(False)
        count_ax.set_facecolor("white")

    if title:
        fig.suptitle(title, fontsize=suptitle_font_size, color="#444444", y=0.98)
    display_note = (
        note_text
        if note_text is not None
        else (
            f"Ranks are calculated within each Monte Carlo simulation by {metric_label} "
            f"(rank 1 = highest {metric_label}, "
            f"rank {int(max_rank)} = lowest {metric_label}). "
            f"Sample size: {n_simulations:,} simulations"
            f"{f'; random seed: {random_seed}' if random_seed is not None else ''}."
        )
    )
    if display_note:
        fig.text(
            0.012,
            0.025,
            display_note,
            fontsize=figure_note_font_size,
            color="#5a5a5a",
        )
    fig.subplots_adjust(
        left=0.26 if count_ax is None else 0.12,
        right=0.985,
        top=0.86 if title else 0.92,
        bottom=0.14 if display_note else 0.11,
        wspace=0.12,
    )
    if output_path is None:
        return None

    save_kwargs = {"bbox_inches": "tight"} if tight_bbox else {}
    fig.savefig(output_path, **save_kwargs)
    plt.close(fig)
    return output_path
