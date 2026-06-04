"""Reusable helpers for sector NPV summaries and CSV exports."""

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
    """Return the deterministic representative value for a parameter."""

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
    """Calculate mean NPV in million EUR from sector result mappings."""

    values: dict[str, float] = {}
    for item, results in results_by_item.items():
        if npv_column not in results:
            raise KeyError(f"{item!r} results do not contain {npv_column!r}.")
        values[labels.get(item, item)] = float(np.mean(results[npv_column]) / 1_000_000)

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
) -> pd.DataFrame:
    """Combine selected result columns from multiple items into one DataFrame."""

    frames = []
    for item, results in results_by_item.items():
        missing_columns = [column for column in columns if column not in results]
        if missing_columns:
            raise KeyError(f"{item!r} results are missing columns: {missing_columns}")

        frame = pd.DataFrame({column: results[column] for column in columns})
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=columns)

    return pd.concat(frames, ignore_index=True)


def npv_ranking_dataframe(
    results_by_item: Mapping[str, Mapping[str, object]],
    sector: str,
    simulation_id_column: str = "run_id",
    technology_column: str = "technology",
    npv_column: str = "npv_eur",
) -> pd.DataFrame:
    """Rank technologies by NPV within each Monte Carlo simulation."""

    frames = []
    for item, results in results_by_item.items():
        missing_columns = [
            column
            for column in (simulation_id_column, npv_column)
            if column not in results
        ]
        if missing_columns:
            raise KeyError(f"{item!r} results are missing columns: {missing_columns}")

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
    ranking["rank"] = ranking.groupby(["sector", "simulation_id"])["npv"].rank(
        method="min",
        ascending=False,
    )
    return ranking[["simulation_id", "sector", "technology", "npv", "rank"]]


def summarize_npv_rankings(ranking: pd.DataFrame) -> pd.DataFrame:
    """Summarize NPV ranks by sector and technology."""

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
    return summary


def save_results_csv(
    results_by_item: Mapping[str, Mapping[str, object]],
    columns: Sequence[str],
    output_path: Path,
) -> Path:
    """Save selected result columns as a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_to_dataframe(results_by_item=results_by_item, columns=columns).to_csv(
        output_path,
        index=False,
    )
    return output_path


def save_dataframe_csv(dataframe: pd.DataFrame, output_path: Path) -> Path:
    """Save a DataFrame as a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    return output_path
