# Project Handover Guide

This guide is the practical entry point for someone continuing the thesis code.
The README explains the research context and first run; this file explains how
the repository fits together and where mistakes are most likely.

## Mental Model

The project has three layers:

1. `src/general_parameters.py` and the sector parameter modules define model
   assumptions and uncertainty distributions.
2. Deterministic and Monte Carlo modules turn those assumptions into annual
   costs, cash flow, and NPV arrays.
3. Summary modules, notebooks, and the Streamlit dashboard present those
   results.

The core NPV formula is shared in `src/npv_finance.py`. Electricity and cement
should not implement separate finance formulas.

## Where to Change What

| Goal | Primary file |
| --- | --- |
| Change shared carbon price, fuel prices, or discount rate | `src/general_parameters.py` |
| Change electricity technology assumptions | `src/electricity/electricity_parameters.py` |
| Change cement technology assumptions | `src/cement/cement_parameters.py` |
| Change electricity Monte Carlo calculations | `src/electricity/electricity_npv_monte_carlo.py` |
| Change cement Monte Carlo calculations | `src/cement/cement_npv_monte_carlo.py` |
| Change deterministic calculations | the matching `*_npv_deterministic.py` module |
| Change shared NPV summaries or CSV shaping | `src/npv_summary.py` |
| Change shared comparison or ranking figures | `src/npv_summary_plots.py` |
| Change output naming or command-line workflows | the matching `*_npv_summary_figures.py` module |
| Explore one technology | `notebooks/<sector>/plot_*_npv.ipynb` |
| Compare all technologies | the sector `*_summary.ipynb` notebook |
| Run deterministic sensitivity interactively | `sensitivity_dashboard.py` |

## Standard Workflows

All commands below assume the repository root is the current directory and the
Python environment is active.

Quick electricity check:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
```

Quick cement check:

```bash
PYTHONPATH=src python -m cement.cement_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
```

Full default output generation:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures
PYTHONPATH=src python -m cement.cement_npv_summary_figures
```

Interactive sensitivity dashboard:

```bash
PYTHONPATH=src streamlit run sensitivity_dashboard.py
```

Standardized sensitivity heatmaps:

```bash
PYTHONPATH=src python -m sensitivity_deep_dive
```

## Output Contract

- `figures/`: thesis-ready dated PNG files.
- `data/raw/`: sampled or representative inputs exported by a run.
- `data/processed/`: derived costs, cash flow, NPV, and summary CSVs.
- `results/`: reserved for other numerical outputs.

The data and results directories are ignored by Git. A generated CSV is
reproducible only if its source code, assumptions, sample size, random seed, and
mode are recorded. The output modules encode sample size and random seed in the
calculation but not in every filename, so keep the run command with any result
used outside the repository.

The default 100,000-draw runs create large files. Running both NPV scales repeats
many raw and processed values because scaling NPV does not require a new Monte
Carlo draw. Keep only the generated copies needed for analysis or archive them
outside the working repository.

## Important Scientific Conventions

- Higher total NPV and higher levelized net margin are better.
- A value of exactly zero is classified as non-negative.
- Electricity levelized net margin is NPV divided by discounted lifetime
  electricity output and is reported in EUR/MWh.
- Cement levelized net margin is NPV divided by discounted lifetime cement
  output and is reported in EUR/t.
- Summary workflows switch explicitly between total NPV (`NPV`) and levelized
  net margin (`LNM`). LCOX is intentionally not implemented yet.
- Monte Carlo technology rankings compare technologies within the same
  simulation ID, so shared uncertain conditions describe the same sampled
  world.
- The default random seed is 42 and the default sample size is 100,000.
- Cement retrofit technologies use a configurable BAU baseline mode. Check
  `DEFAULT_RETROFIT_BAU_MODE` and the command-line `--retrofit-bau-mode` option
  before interpreting results.
- Deterministic distribution representatives are defined centrally by
  `representative_value()` in `src/npv_summary.py`.

Do not change one of these conventions silently. Update documentation and
regenerate affected results if a convention changes.

## Notebook Guidance

Notebooks add `src/` to `sys.path` by searching upward from the working
directory. Start Jupyter from the repository root for the least surprising
behavior:

```bash
jupyter lab
```

The summary notebooks are the preferred human-readable overview. The many
technology-specific notebooks are useful for inspecting detailed inputs and
distributions, but they duplicate plotting code and should not become the
only implementation of a model rule.

Stored notebook outputs may reflect an older run. When results matter, restart
the kernel and run all cells.

## Current Handover Risks

1. There is no automated test suite. Use compilation plus small-sample sector
   runs as the minimum validation.
2. Dependencies are only lightly constrained. A future dependency release may
   change behavior; record a working environment before long-term archival.
3. The repository uses `PYTHONPATH=src` rather than an installed Python package.
   Commands must be run from the repository root unless the package path is set
   another way.
4. Generated data can consume substantial disk space and is ignored by Git.
5. The individual notebooks contain repeated setup and plotting code. Shared
   scientific logic belongs in `src/`, not in copied notebook cells.
6. Empty `tests/` and `results/` directories are local structure, not tracked
   content. Fresh clones create output directories automatically when the
   workflows run.

## Safe Change Checklist

1. Identify whether the change is an assumption, calculation, summary, or
   plotting change.
2. Change the smallest shared source module that owns that behavior.
3. Run `python -m compileall -q src sensitivity_dashboard.py`.
4. Run both sector workflows with a small sample size if shared code changed.
5. Restart and run affected notebooks when their displayed results are part of
   the deliverable.
6. Check `git status` and do not commit ignored generated data accidentally.
7. Append the change and exact verification commands to `CHANGELOG.md`.
