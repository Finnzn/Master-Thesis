"""Reusable helpers for sector NPV summaries and CSV exports.

Simulation modules return dictionaries of arrays because that format is compact
and easy to calculate with NumPy. This module turns those arrays into the tables
used for figures, CSV exports, and technology rankings. The helpers are
sector-agnostic so electricity and later sectors can share one output workflow.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
)


ParameterSpec = FixedParameter | ScaledBetaDistribution | TriangularDistribution | UniformDistribution


def representative_value(parameter: ParameterSpec) -> float:
    """Return the deterministic representative value for a parameter.

    Deterministic runs are used as a one-point comparison against the Monte Carlo
    results. For each uncertainty type, this function defines which single value
    stands in for the whole distribution.
    """

    # Fixed parameters already have a single value. For distributions, use the
    # value that best represents the source assumption: mean for scaled beta,
    # mode for triangular, and midpoint for uniform ranges.
    if isinstance(parameter, FixedParameter):
        return parameter.value
    if isinstance(parameter, ScaledBetaDistribution):
        return parameter.mean
    if isinstance(parameter, TriangularDistribution):
        return parameter.mode
    if isinstance(parameter, UniformDistribution):
        return (parameter.lower_bound + parameter.upper_bound) / 2

    raise TypeError(f"Unsupported parameter type: {type(parameter)!r}")


def mean_npv_million_eur(
    results_by_item: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str],
    npv_column: str = "npv_eur",
) -> dict[str, float]:
    """Calculate mean NPV in million EUR from sector result mappings.

    The raw model stores NPV in EUR. Figures and thesis tables are easier to
    read in million EUR, so this function performs that conversion once in the
    shared summary layer.
    """

    values: dict[str, float] = {}
    for item, results in results_by_item.items():
        if npv_column not in results:
            raise KeyError(f"{item!r} results do not contain {npv_column!r}.")
        values[labels.get(item, item)] = float(np.mean(results[npv_column]) / 1_000_000)

    return values


def mean_metric(
    results_by_item: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str],
    metric_column: str,
    scale: float = 1.0,
) -> dict[str, float]:
    """Calculate mean values for a selected metric column.

    `scale` converts stored model units into display units. For example,
    `npv_eur` uses `scale=1_000_000` for million EUR, while normalized
    `npv_eur_per_mwh` and `npv_eur_per_t` use `scale=1`.
    """

    if scale == 0:
        raise ValueError("scale must not be zero.")

    values: dict[str, float] = {}
    for item, results in results_by_item.items():
        if metric_column not in results:
            raise KeyError(f"{item!r} results do not contain {metric_column!r}.")
        values[labels.get(item, item)] = float(np.mean(results[metric_column]) / scale)

    return values


def deterministic_npv_million_eur(
    results_by_item: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str],
    npv_column: str = "npv_eur",
) -> dict[str, float]:
    """Calculate deterministic NPV in million EUR from one-row result mappings."""

    values: dict[str, float] = {}
    for item, results in results_by_item.items():
        if npv_column not in results:
            raise KeyError(f"{item!r} results do not contain {npv_column!r}.")
        values[labels.get(item, item)] = float(
            np.asarray(results[npv_column]).item() / 1_000_000
        )

    return values


def deterministic_metric(
    results_by_item: Mapping[str, Mapping[str, object]],
    labels: Mapping[str, str],
    metric_column: str,
    scale: float = 1.0,
) -> dict[str, float]:
    """Calculate deterministic values for a selected one-row metric column."""

    if scale == 0:
        raise ValueError("scale must not be zero.")

    values: dict[str, float] = {}
    for item, results in results_by_item.items():
        if metric_column not in results:
            raise KeyError(f"{item!r} results do not contain {metric_column!r}.")
        values[labels.get(item, item)] = float(
            np.asarray(results[metric_column]).item() / scale
        )

    return values


def dated_csv_path(
    output_dir: Path,
    stem: str,
    run_date: date,
) -> Path:
    """Build a dated CSV path such as YYYY-MM-DD-Mean_NPV_Electricity_raw.csv."""

    return output_dir / f"{run_date.isoformat()}-{stem}.csv"


def results_to_dataframe(
    results_by_item: Mapping[str, Mapping[str, object]],
    columns: Sequence[str],
    rename_columns: Mapping[str, str] | None = None,
    sort_by: Sequence[str] = (),
) -> pd.DataFrame:
    """Combine selected result columns from multiple items into one DataFrame.

    `results_by_item` is usually keyed by technology. The caller chooses which
    columns belong in a raw-input export or a processed-output export, and this
    helper stacks all technologies into one long table.
    """

    frames = []
    for item, results in results_by_item.items():
        missing_columns = [column for column in columns if column not in results]
        if missing_columns:
            raise KeyError(f"{item!r} results are missing columns: {missing_columns}")

        # Each result mapping already stores equal-length arrays for one technology,
        # so a DataFrame can be built directly from the selected columns.
        frame = pd.DataFrame({column: results[column] for column in columns})
        frames.append(frame)

    if not frames:
        dataframe = pd.DataFrame(columns=columns)
    else:
        dataframe = pd.concat(frames, ignore_index=True)

    if rename_columns:
        dataframe = dataframe.rename(columns=dict(rename_columns))
    if sort_by:
        missing_sort_columns = [column for column in sort_by if column not in dataframe]
        if missing_sort_columns:
            raise KeyError(f"dataframe is missing sort columns: {missing_sort_columns}")
        dataframe = dataframe.sort_values(list(sort_by)).reset_index(drop=True)

    return dataframe


def npv_ranking_dataframe(
    results_by_item: Mapping[str, Mapping[str, object]],
    sector: str,
    simulation_id_column: str = "run_id",
    technology_column: str = "technology",
    npv_column: str = "npv_eur",
) -> pd.DataFrame:
    """Rank technologies by NPV within each Monte Carlo simulation.

    A single Monte Carlo simulation ID represents one shared uncertain world.
    Ranking within each ID answers: under this draw of uncertain parameters,
    which technology has the highest NPV?
    """

    frames = []
    for item, results in results_by_item.items():
        missing_columns = [
            column
            for column in (simulation_id_column, npv_column)
            if column not in results
        ]
        if missing_columns:
            raise KeyError(f"{item!r} results are missing columns: {missing_columns}")

        # Some callers store technology explicitly; otherwise the mapping key is used.
        technology_values = (
            results[technology_column]
            if technology_column in results
            else np.full(len(results[simulation_id_column]), item)
        )
        frame = pd.DataFrame(
            {
                "simulation_id": results[simulation_id_column],
                "sector": sector,
                "technology": technology_values,
                "npv": results[npv_column],
            }
        )
        frames.append(frame)

    if not frames:
        return pd.DataFrame(
            columns=["simulation_id", "sector", "technology", "npv", "rank"]
        )

    ranking = pd.concat(frames, ignore_index=True)
    # Rank 1 is the highest NPV within a simulation and sector. `method="min"`
    # gives tied technologies the same best rank rather than forcing an arbitrary
    # ordering.
    ranking["rank"] = ranking.groupby(["sector", "simulation_id"])["npv"].rank(
        method="min",
        ascending=False,
    )
    return (
        ranking[["simulation_id", "sector", "technology", "npv", "rank"]]
        .sort_values(["sector", "simulation_id", "rank", "technology"])
        .reset_index(drop=True)
    )


def summarize_npv_rankings(ranking: pd.DataFrame) -> pd.DataFrame:
    """Summarize NPV ranks by sector and technology.

    The raw ranking table is long and simulation-level. This summary collapses
    it into interpretable indicators: average rank, probability of being rank 1,
    probability of being in the top 3, and the full rank-count distribution.
    """

    required_columns = {"sector", "technology", "rank", "simulation_id"}
    missing_columns = sorted(required_columns - set(ranking.columns))
    if missing_columns:
        raise KeyError(f"ranking is missing columns: {missing_columns}")

    if ranking.empty:
        return pd.DataFrame(
            columns=[
                "sector",
                "technology",
                "average_rank",
                "median_rank",
                "std_rank",
                "probability_rank_1",
                "probability_top_3",
                "n_simulations",
            ]
        )

    # Keep explicit rank-count columns so CSV outputs show the full rank distribution,
    # not just aggregate probabilities. This is useful when one technology is often
    # either very good or very bad rather than consistently average.
    rank_count_columns = {
        rank: f"rank_{rank}_count"
        for rank in sorted(ranking["rank"].astype(int).unique())
    }
    rank_counts = (
        ranking.assign(rank_number=ranking["rank"].astype(int))
        .groupby(["sector", "technology", "rank_number"])
        .size()
        .unstack(fill_value=0)
        .rename(columns=rank_count_columns)
        .reset_index()
    )
    summary = (
        ranking.assign(
            is_rank_1=ranking["rank"].eq(1),
            is_top_3=ranking["rank"].le(3),
        )
        .groupby(["sector", "technology"], as_index=False)
        .agg(
            average_rank=("rank", "mean"),
            median_rank=("rank", "median"),
            std_rank=("rank", "std"),
            probability_rank_1=("is_rank_1", "mean"),
            probability_top_3=("is_top_3", "mean"),
            n_simulations=("simulation_id", "nunique"),
        )
        .sort_values(["sector", "average_rank", "technology"])
        .reset_index(drop=True)
    )
    return summary.merge(rank_counts, on=["sector", "technology"], how="left")


def save_results_csv(
    results_by_item: Mapping[str, Mapping[str, object]],
    columns: Sequence[str],
    output_path: Path,
    rename_columns: Mapping[str, str] | None = None,
    sort_by: Sequence[str] = (),
) -> Path:
    """Save selected result columns as a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_to_dataframe(
        results_by_item=results_by_item,
        columns=columns,
        rename_columns=rename_columns,
        sort_by=sort_by,
    ).to_csv(output_path, index=False)
    return output_path


def save_dataframe_csv(dataframe: pd.DataFrame, output_path: Path) -> Path:
    """Save a DataFrame as a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return output_path
