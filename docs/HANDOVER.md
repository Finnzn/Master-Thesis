# Project Handover Guide

This guide is the practical entry point for someone continuing the thesis code.
The README explains the research context and first run; this file explains how
the repository fits together and where mistakes are most likely.

## Mental Model

The project has four layers:

1. `src/general_parameters.py` and the sector parameter modules define model
   assumptions and uncertainty distributions.
2. Each `<sector>_npv_deterministic.py` chooses representative inputs and each
   `<sector>_npv_monte_carlo.py` samples input arrays.
3. Each `<sector>_npv_model.py` resolves absolute technology inputs and turns
   them into sector costs and financial-result arrays. Both input providers
   call this one sector model.
4. Summary modules, notebooks, and the Streamlit dashboard present those
   results.

The core NPV, levelized-profit-margin, discounted-cost, and LCOX formulas are
shared in `src/npv_finance.py`. All five sectors call this shared finance layer.

## Where to Change What

| Goal | Primary file |
| --- | --- |
| Change shared carbon price, fuel prices, or discount rate | `src/general_parameters.py` |
| Change electricity technology assumptions | `src/electricity/electricity_parameters.py` |
| Change cement technology assumptions | `src/cement/cement_parameters.py` |
| Change steel technology assumptions | `src/steel/steel_parameters.py` |
| Change ammonia technology assumptions | `src/ammonia/ammonia_parameters.py` |
| Change hydrogen technology assumptions | `src/hydrogen/hydrogen_parameters.py` |
| Change a sector's technology resolution, physical costs, or result assembly | the matching `src/<sector>/<sector>_npv_model.py` module |
| Change Monte Carlo sampling or alignment | the matching `src/<sector>/<sector>_npv_monte_carlo.py` module |
| Change deterministic representative-input selection | the matching `src/<sector>/<sector>_npv_deterministic.py` module |
| Change shared NPV summaries or CSV shaping | `src/npv_summary.py` |
| Change shared comparison or ranking figures | `src/npv_summary_plots.py` |
| Change output naming or command-line workflows | the matching `*_financial_summary.py` module |
| Change a sector MACC | the matching `src/<sector>/<sector>_macc.py` module |
| Explore one technology | `notebooks/<sector>/plot_*_npv.ipynb` |
| Compare all technologies | the sector `*_summary.ipynb` notebook |
| Explore a marginal abatement cost curve | the sector `*_macc.ipynb` notebook |
| Run deterministic cross-sector scenarios | `notebooks/scenario_analysis.ipynb` |
| Compare deterministic and probabilistic LCOX | the matching sector `*_summary.ipynb` or `*_financial_summary --metric LCOX` |
| Run deterministic sensitivity interactively | `sensitivity_dashboard.py` |
| Regenerate an isolated, reproducible result set | `regenerate_all.py` |

## Standard Workflows

All commands below assume the repository root is the current directory and the
Python environment is active.

Quick electricity check:

```bash
PYTHONPATH=src python -m electricity.electricity_financial_summary \
  --sample-size 100 --no-data --ranking-output none
```

The electricity command defaults to sampled BAU inputs for the hard-coal and
CCGT CCS retrofits. Append `--retrofit-bau-mode deterministic` when a diagnostic
run should hold those BAU technical inputs at expected values.

Quick cement check:

```bash
PYTHONPATH=src python -m cement.cement_financial_summary \
  --sample-size 100 --no-data --ranking-output none
```

Standard financial-summary generation for all five sectors and all three
financial metrics:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py --run-name thesis_results
```

Complete generation—including both deterministic and simulated MACCs, all
selected sensitivity heatmaps, and non-destructive execution copies of all
notebooks—is available through one preset:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results_full --full
```

Use `--macc-mode deterministic|simulated|both`, `--include-heatmaps`, and
`--verify-notebooks` to select those additions independently. Use `--sectors`,
`--metrics`, `--sample-size`, `--random-seed`, and `--retrofit-bau-mode` to
control scope and simulations, or `--dry-run` to inspect the exact plan. Run
`.venv/bin/python regenerate_all.py --help` for all options and examples. The
script refuses to reuse a run directory.

Interactive five-sector sensitivity dashboard:

```bash
PYTHONPATH=src streamlit run sensitivity_dashboard.py
```

Standardized sensitivity heatmaps:

```bash
PYTHONPATH=src python -m sensitivity_deep_dive
```

## Output Contract

- `figures/`: thesis-ready dated PNG files.
- `data/raw/`: sampled or deterministic expected inputs exported by a run.
- `data/processed/`: derived costs, cash flow, NPV, LPM, LCOX, and summary CSVs.
- `results/`: optional numerical outputs.
- `results/runs/<run-name>/`: isolated regeneration outputs, command logs, and
  the run's `manifest.json`.
- `results/runs/<run-name>/heatmaps/`: optional sensitivity CSVs and heatmap
  figures created with `--include-heatmaps` or `--full`.

Raw-input CSVs hold normalized model inputs; derived resolved T&S unit costs are
in processed outputs. The one direct BECCS T&S draw is retained as
`transport_and_storage_cost_input_eur_per_mwh` in electricity raw inputs.

The data and results directories are ignored by Git. Prefer
`regenerate_all.py` for final result sets: its manifest records the active
carbon price and discount rate, source revision and dirty state, sample size,
random seed, retrofit mode, environment, commands, and output hashes. Individual
sector commands remain useful for development but do not create that manifest.

The default 100,000-draw runs create large files. Running multiple financial
metrics repeats many raw and processed values because changing the reported
metric does not require a new Monte Carlo draw. Keep only the generated copies
needed for analysis or archive them outside the working repository.

## Important Scientific Conventions

- Higher total NPV and higher levelized profit margin are better; lower LCOX is
  better.
- A value of exactly zero is classified as non-negative.
- Electricity levelized profit margin is NPV divided by discounted lifetime
  electricity output and is reported in EUR/MWh.
- Cement levelized profit margin is NPV divided by discounted lifetime cement
  output and is reported in EUR/t.
- Electricity LCOX is LCOE in EUR/MWh; cement LCOX is LCOC in EUR/t cement.
- LCOX includes year-zero CAPEX and discounted fixed OPEX, variable OPEX, fuel,
  energy, and carbon cost. It excludes product sales revenue.
- Summary workflows switch explicitly between total NPV (`NPV`), levelized
  profit margin (`LPM`), and levelized cost (`LCOX`).
- PV and onshore wind sample triangular value factors of 0.80/0.90/1.00, while
  offshore wind samples 0.85/0.95/1.00. Deterministic runs use the analytical
  triangular means: 0.90, 0.933, and 0.90, respectively.
  Captured electricity price is the model sales-price proxy multiplied by the
  technology value factor; only electricity revenue, NPV, and LPM change. VF is
  included for these three technologies in the electricity sensitivity heatmap.
- Under the current constant-price and constant-output models, captured
  electricity price minus LCOE equals electricity LPM, while cement price minus
  LCOC equals cement LPM.
- BECCS is registered as an electricity technology with uniformly sampled
  techno-economic ranges, a triangular biomass price of
  17.36/28.93/46.28 EUR/MWh_th, fixed full-load hours of 7,665 h/year, and an
  explicit 25-year lifetime assumption aligned with biogas.
- BECCS emissions are negative. The common emissions-cost calculation therefore
  produces a negative cost that acts as carbon-removal revenue in NPV/LPM and
  as a carbon credit in LCOE.
- Monte Carlo technology rankings compare technologies within the same
  simulation ID, so shared uncertain conditions describe the same sampled
  world. Rank 1 is the highest NPV/LPM or the lowest LCOX.
- The default random seed is 42 and the default sample size is 100,000.
- Cement retrofit technologies, hard-coal CCS, and CCGT CCS use a configurable
  BAU baseline mode. Electricity CCS uses hard coal or CCGT, respectively, as
  the parent BAU technology.
- `retrofit_bau_mode="sampled"` is the Monte Carlo default. It samples BAU
  technical inputs once per simulation ID and reuses them for the matching BAU
  result and retrofit. `"deterministic"` instead fixes the retrofit's BAU
  technical inputs at expected values while other stochastic inputs remain
  sampled.
- Retrofit cost changes are added to BAU costs. Physical reductions resolve as
  `BAU value * (1 - reduction fraction)`, so positive fractions are reductions
  and negative reduction fractions are increases.
- Hard-coal CCS, CCGT CCS, and cement CCS add T&S at 18.7% of their levelized
  incremental capture cost relative to BAU, excluding carbon-price effects.
  BECCS instead samples T&S uniformly from 22-29 EUR/MWh_e.
- Sensitivity and deterministic scenario calculations recompute capture-share
  T&S from the current CAPEX, OPEX, energy, full-load-hour, lifetime, and
  discount-rate inputs. The heatmap varies the 18.7% share for the three
  BAU-relative CCS technologies and the direct T&S unit cost for BECCS.
- Heatmap `Fuel`, `Electricity`, and `Emissions` groups display the larger
  constituent one-factor-at-a-time effect, not a joint perturbation or an
  interaction index. Use a global method such as Sobol analysis for interactions.
- The cement, steel, ammonia, and hydrogen MACCs include T&S through annual
  total technology cost and then remove carbon payments from their resource-cost
  boundary. Product revenue is also excluded. Their respective references are
  cement BAU, BF-BOF BAU, NG-SMR + Haber-Bosch, and NG-SMR. Routes without
  positive direct abatement are omitted, and same-sector route widths represent
  alternatives rather than additive abatement potential.
- Check `DEFAULT_RETROFIT_BAU_MODE` and the summary command's
  `--retrofit-bau-mode` option before interpreting Monte Carlo results. The
  deterministic models always use expected BAU and retrofit input values.
- Deterministic runs use each uncertain input distribution's analytical mean:
  stored mean for scaled beta, `(minimum + mode + maximum) / 3` for triangular,
  midpoint for uniform, and the stored value for fixed parameters. This policy
  is defined centrally by `representative_value()` in `src/npv_summary.py`.

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

1. Dependencies are only lightly constrained. A future dependency release may
   change behavior; record a working environment before long-term archival.
2. The repository uses `PYTHONPATH=src` rather than an installed Python package.
   Commands must be run from the repository root unless the package path is set
   another way.
3. Generated data can consume substantial disk space and is ignored by Git.
4. The individual notebooks contain repeated setup and plotting code. Shared
   scientific logic belongs in `src/`, not in copied notebook cells.
5. Most literature-derived values have descriptive metadata but no
   machine-readable citation field. The original source table must be retained
   outside the generated data folders until provenance is migrated.

## Safe Change Checklist

1. Identify whether the change is an assumption, calculation, summary, or
   plotting change.
2. Change the smallest shared source module that owns that behavior.
3. Run `python -m compileall -q src sensitivity_dashboard.py`.
4. Restart and run affected notebooks when their displayed results are part of
   the deliverable.
5. Check `git status` and do not commit ignored generated data accidentally.
6. Append the change and exact verification commands to `CHANGELOG.md`.
