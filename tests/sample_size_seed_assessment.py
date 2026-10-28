"""Reproduce the thesis LPM sample-size and seed assessment using current inputs.

Run: .venv/bin/python tests/sample_size_seed_assessment.py
Override seeds: append --seeds 42 123 2026 31415 27182

Seed 42 covers all sample sizes; the five-seed assessment uses 100k and 200k.
The intermediate sample sizes below can be edited if original settings differ.
Each (size, seed) is simulated separately, rather than slicing a larger run.
Probability differences are expressed in percentage points (pp).
"""

import argparse
from importlib import import_module
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

SAMPLE_SIZES = (1_000, 5_000, 10_000, 50_000, 100_000, 200_000)
DEFAULT_SEEDS = (42, 123, 2026, 31415, 27182)
SECTORS = {
    "electricity": ("mwh", "EUR/MWh"),
    "cement": ("t", "EUR/t cement"),
    "steel": ("tcs", "EUR/t crude steel"),
    "ammonia": ("tnh3", "EUR/t NH3"),
    "hydrogen": ("th2", "EUR/t H2"),
}


def summarize(results, metric):
    """Summarize aligned draws, matching the project's minimum-rank tie rule."""
    values = pd.DataFrame({tech: result[metric] for tech, result in results.items()})
    ranks = values.rank(axis=1, ascending=False, method="min")
    return pd.DataFrame({
        "mean_lpm": values.mean(),
        "first_pp": ranks.eq(1).mean() * 100,
        "top_three_pp": ranks.le(3).mean() * 100,
    })


def leaders(values):
    """Keep all co-leaders so a tie cannot appear as a unique, stable leader."""
    return ", ".join(sorted(values.index[values.eq(values.max())]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs=5, default=DEFAULT_SEEDS)
    args = parser.parse_args()
    if len(set(args.seeds)) != 5 or min(args.seeds) < 0:
        parser.error("provide five distinct, nonnegative seeds")

    print(f"Seed 42 sample sizes: {SAMPLE_SIZES}; retrofit BAU: sampled")
    print(f"Seeds at 100k and 200k: {args.seeds}")
    consistency, convergence, stability = [], [], []
    probability_changes, seed_ranges = [], []
    for sector, (suffix, unit) in SECTORS.items():
        metric = f"levelized_profit_margin_eur_per_{suffix}"
        simulate = getattr(import_module(f"{sector}.{sector}_npv_monte_carlo"),
                           f"simulate_{sector}_results")
        deterministic = getattr(import_module(f"{sector}.{sector}_npv_deterministic"),
                                f"calculate_deterministic_{sector}_results")()
        expected = pd.Series({tech: result[metric][0]
                              for tech, result in deterministic.items()})
        runs = {}
        for size in SAMPLE_SIZES:
            seeds = tuple(dict.fromkeys((42, *args.seeds))) if size >= 100_000 else (42,)
            for seed in seeds:
                runs[size, seed] = summarize(simulate(
                    sample_size=size, random_seed=seed, retrofit_bau_mode="sampled"
                ), metric)

        reference = runs[100_000, 42]
        changes = pd.concat([(runs[100_000, seed] - runs[200_000, seed]).abs()
                             for seed in args.seeds]).max()
        consistency.append({
            "sector": sector, "unit": unit,
            "deterministic–MC": (reference.mean_lpm - expected).abs().max(),
            "100k–200k": changes.mean_lpm,
        })
        probability_changes.append(changes[["first_pp", "top_three_pp"]])
        across_seeds = pd.concat([runs[100_000, seed] for seed in args.seeds])
        grouped = across_seeds.groupby(level=0)
        seed_ranges.append((grouped.max() - grouped.min()).max())

        for size in SAMPLE_SIZES:
            deviations = (runs[size, 42] - runs[200_000, 42]).abs().max()
            convergence.append({"sector": sector, "size": size, **deviations})
        large_runs = [runs[size, seed] for size in (100_000, 200_000)
                      for seed in args.seeds]
        mean_leaders = {leaders(run.mean_lpm) for run in large_runs}
        first_leaders = {leaders(run.first_pp) for run in large_runs}
        stability.append({
            "sector": sector,
            "mean LPM leader(s)": " / ".join(sorted(mean_leaders)),
            "first-place leader(s)": " / ".join(sorted(first_leaders)),
            "stable across all seeds and both sizes":
                len(mean_leaders) == len(first_leaders) == 1,
        })

    for title, rows in [("Numerical consistency (sector units)", consistency),
                        ("Seed 42: max absolute difference from 200k run "
                         "(LPM in sector units; probabilities in pp)", convergence),
                        ("Leading routes at 100k and 200k", stability)]:
        print(f"\n{title}\n{pd.DataFrame(rows).to_string(index=False, float_format='%.2f')}")
    print("\nLargest 100k–200k probability changes (pp):")
    print(pd.DataFrame(probability_changes).max().to_string(float_format="%.2f"))
    print("\nLargest ranges across seeds at 100k (pp):")
    print(pd.DataFrame(seed_ranges)[["first_pp", "top_three_pp"]]
          .max().to_string(float_format="%.2f"))


if __name__ == "__main__":
    main()
