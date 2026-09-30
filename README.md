# Master Thesis Analysis: CCS and Alternative Decarbonization Technologies

This repository contains the models, assumptions, notebooks, and reproducible
workflows for an ETH Zurich master thesis on the economic competitiveness of
carbon capture and storage (CCS) relative to alternative decarbonization
technologies.

The analysis covers five sectors:

- electricity generation;
- cement production;
- steel production;
- ammonia production; and
- hydrogen production.

For each sector, the project compares deterministic results with Monte Carlo
results under uncertainty in technology costs, energy use, fuel and electricity
prices, emissions, and other technical or financial inputs. The main outputs
are net present value, levelized profit margin, levelized cost, marginal
abatement-cost comparisons, and sensitivity analyses.

## Start Here

Choose the workflow that matches your purpose:

| Goal | Recommended entry point | Output location |
| --- | --- | --- |
| Reproduce a complete, auditable result set | `regenerate_all.py` | `results/runs/<run-name>/` |
| Quickly test one sector or metric | `python -m <sector>.<sector>_financial_summary` | `figures/`, `data/raw/`, `data/processed/` |
| Inspect calculations interactively | `notebooks/` | Inline notebook output |
| Explore one-factor-at-a-time sensitivity | `sensitivity_dashboard.py` | Interactive Streamlit view |
| Generate standardized sensitivity heatmaps | `python -m sensitivity_deep_dive` | `figures/`, `data/processed/` |

Use a named run for thesis results or comparisons that must be preserved and
audited. Use the direct sector commands for quick development checks because
their outputs are not isolated from other quick runs.

All commands below assume that the current working directory is the repository
root.

## Installation

Python 3.10 or newer is required. The thesis environment currently uses Python
3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The examples use `.venv/bin/python` explicitly, so they also work after opening
a new terminal without activating the environment. `PYTHONPATH=src` makes the
project modules importable without installing the repository as a package.

Confirm that the main command is available:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py --help
```

## Repository Map

```text
MasterThesis/
├── src/                       Reusable models, assumptions, and workflows
│   ├── electricity/           Electricity technologies and calculations
│   ├── cement/                Cement technologies and calculations
│   ├── steel/                 Steel technologies and calculations
│   ├── ammonia/               Ammonia technologies and calculations
│   ├── hydrogen/              Hydrogen technologies and calculations
│   ├── general_parameters.py  Shared financial, carbon, and energy assumptions
│   ├── distributions.py       Probability-distribution definitions
│   ├── npv_finance.py         Shared discounted-finance calculations
│   └── financial_summary_workflow.py
│                               Shared summary, export, plotting, and CLI logic
├── notebooks/                 Interactive sector and technology analyses
├── figures/                   Tracked reference figures and quick-run plots
├── data/
│   ├── raw/                   Generated Monte Carlo input samples
│   └── processed/             Generated result and ranking tables
├── results/
│   ├── runs/                  Isolated, manifest-backed named runs
│   └── temporary/             Explicitly temporary comparisons
├── regenerate_all.py          Reproducible multi-sector run entry point
├── sensitivity_dashboard.py   Interactive sensitivity application
├── requirements.txt           Python dependencies
└── CHANGELOG.md               Append-only record of project changes
```

`data/raw/`, `data/processed/`, and `results/` are generated and ignored by
Git. The source assumptions are not stored only in those folders: they live in
the tracked parameter modules under `src/`.

## Reproduce Results in an Isolated Run

`regenerate_all.py` is the preferred entry point for final thesis results. It
calls the existing sector workflows, stores every output under one unique run
name, saves command logs, and creates a reproducibility manifest. It does not
contain a separate scientific model.

### Standard financial run

This command generates NPV, LPM, and LCOX results for all five sectors using
the default 100,000 Monte Carlo draws per technology and random seed 42:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results
```

The standard run includes deterministic and Monte Carlo mean figures, ranking
outputs, raw sampled inputs, and processed results. It does not generate
abatement-cost comparisons, sensitivity heatmaps, or executed notebook copies
unless those are requested.

### Complete run

Use `--full` for financial summaries, deterministic and simulated
abatement-cost comparisons, sensitivity heatmaps, and non-destructive
execution of all notebooks:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results_full --full
```

This is resource-intensive: the default simulation size is 100,000 and all
project notebooks are executed. Use a smaller dry run or focused run first when
testing changes.

### Focused run

Limit the financial and sensitivity work by sector, metric, and sample size:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name electricity_cement_npv_check \
  --sectors electricity cement \
  --metrics NPV \
  --sample-size 1000
```

Valid sectors are `electricity`, `cement`, `steel`, `ammonia`, and `hydrogen`.
Valid metrics are `NPV`, `LPM`, and `LCOX`.

### Add optional analyses

The optional analyses can be selected independently:

```bash
# Add deterministic and Monte Carlo mean abatement-cost comparisons.
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results_abatement_comparison \
  --abatement-comparison-mode both

# Add standardized sensitivity CSVs and heatmaps.
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results_heatmaps --include-heatmaps

# Add non-destructive execution of every project notebook.
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name thesis_results_notebooks --verify-notebooks
```

These flags add work to the standard financial run. In particular,
`--verify-notebooks` does not execute notebooks by themselves: the normal
financial summaries are still generated first. Notebook verification always
executes all notebooks, even if `--sectors` limits the financial steps. The
executed copies are stored in the run directory; the source notebooks are not
overwritten.

### Preview before running

`--dry-run` prints the exact commands and active shared assumptions without
creating a directory or running calculations:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name preview --full --dry-run
```

This is the safest way to check the selected sectors, metrics, simulation
settings, carbon price, and output paths before a large run.

### Important run options

| Option | Purpose |
| --- | --- |
| `--run-name NAME` | Names the isolated result directory; a timestamp is used if omitted |
| `--sectors ...` | Selects one or more sectors |
| `--metrics ...` | Selects `NPV`, `LPM`, and/or `LCOX` |
| `--sample-size N` | Sets Monte Carlo draws per technology |
| `--random-seed N` | Sets the top-level reproducibility seed |
| `--retrofit-bau-mode sampled\|deterministic` | Selects the Monte Carlo parent baseline for retrofit technologies |
| `--abatement-comparison-mode deterministic\|simulated\|both` | Adds sector abatement-cost comparisons; electricity has no corresponding module |
| `--include-heatmaps` | Adds standardized sensitivity tables and heatmaps |
| `--sensitivity-variation-percent N` | Sets the heatmap movement in percent; default is 20 |
| `--verify-notebooks` | Adds execution copies of all notebooks |
| `--notebook-timeout SECONDS` | Sets the maximum execution time per notebook |
| `--output-root PATH` | Changes the parent directory for named runs |
| `--dry-run` | Prints the plan without creating outputs |

Run names are never reused. If `results/runs/<run-name>/` already exists, the
workflow stops instead of overwriting it.

### Named-run output structure

```text
results/runs/<run-name>/
├── manifest.json
├── logs/
├── financial/<sector>/<metric>/
│   ├── figures/
│   ├── raw/
│   └── processed/
├── abatement_comparison/<sector>/<deterministic|simulated>/
│   ├── figures/
│   └── processed/
├── heatmaps/<metric>/
│   ├── figures/
│   └── processed/
└── notebook_verification/
```

Only requested optional folders are created. `manifest.json` records the run
status, active global assumptions, selected options, Git state, environment,
dependency versions, commands, logs, and SHA-256 hashes of generated files.
When comparing runs, check the manifests first rather than relying only on the
folder names.

## Run One Sector Quickly

Every sector uses the same financial-summary interface. Replace `electricity`
in this example with `cement`, `steel`, `ammonia`, or `hydrogen`:

```bash
PYTHONPATH=src .venv/bin/python \
  -m electricity.electricity_financial_summary \
  --metric NPV --sample-size 1000
```

By default, a direct sector run writes:

- date-stamped plots to `figures/`;
- sampled Monte Carlo inputs to `data/raw/`; and
- calculated results and rankings to `data/processed/`.

These locations are shared by quick runs. Use a named run when outputs from
different assumptions or scenarios must remain separated.

### Useful financial-summary options

```bash
# Deterministic result only; save the figure but no CSV files or rankings.
PYTHONPATH=src .venv/bin/python \
  -m steel.steel_financial_summary \
  --metric LCOX --kind deterministic --no-data --ranking-output none

# Monte Carlo mean and deterministic plots with a smaller test sample.
PYTHONPATH=src .venv/bin/python \
  -m ammonia.ammonia_financial_summary \
  --metric LPM --sample-size 100 --ranking-output plots

# Put a quick check in explicit temporary output directories.
PYTHONPATH=src .venv/bin/python \
  -m hydrogen.hydrogen_financial_summary \
  --metric NPV --sample-size 100 \
  --output-dir results/quick_check/figures \
  --raw-data-dir results/quick_check/raw \
  --processed-data-dir results/quick_check/processed
```

The most useful options are:

| Option | Values | Meaning |
| --- | --- | --- |
| `--metric` | `NPV`, `LPM`, `LCOX` | Financial measure to calculate and plot |
| `--kind` | `all`, `mean`, `deterministic` | Which main comparison figures to create |
| `--sample-size` | positive integer | Monte Carlo draws per technology |
| `--random-seed` | integer | Reproducibility seed |
| `--ranking-output` | `both`, `plots`, `csv`, `none` | Which ranking outputs to save |
| `--no-data` | flag | Suppresses raw and processed CSV exports |
| `--retrofit-bau-mode` | `sampled`, `deterministic` | Parent inputs used for Monte Carlo retrofits |

Use the module help for the complete current interface:

```bash
PYTHONPATH=src .venv/bin/python \
  -m cement.cement_financial_summary --help
```

## Generate Technology Abatement-Cost Comparisons

Technology abatement-cost comparisons are available for cement, steel,
ammonia, and hydrogen. Electricity has no corresponding module in this
project.

```bash
# Deterministic cement abatement-cost comparison.
PYTHONPATH=src .venv/bin/python -m cement.cement_abatement_comparison

# Monte Carlo mean steel abatement-cost comparison.
PYTHONPATH=src .venv/bin/python -m steel.steel_abatement_comparison \
  --simulated --sample-size 1000
```

These direct commands write figures to `figures/` and tables to
`data/processed/` unless output directories are supplied. Add `--simulated`
to use aligned Monte Carlo means. Steel, ammonia, and hydrogen commands also
accept `--retrofit-bau-mode`; cement does not need that option in this
interface.

Each bar compares one technology independently with the sector reference at
the same annual output:

- bar height: annualized incremental resource cost per tonne of direct CO2
  avoided relative to the reference technology;
- bar width: that technology's individual annual direct emissions avoided;
- horizontal order: increasing abatement cost.

Carbon payments and product revenue are excluded from the cost numerator.
Because the technologies are alternative full-output routes, their widths are
not additive. The figure supports a direct cost-versus-avoided-emissions
comparison, but it is not a cumulative sector deployment curve and does not
represent an optimal technology portfolio.

The reference technologies are BAU cement, BF-BOF BAU steel, NG-SMR + HB
ammonia, and NG-SMR hydrogen. Options without positive direct emissions
abatement relative to their reference are omitted.

## Run Sensitivity Analyses

### Standardized heatmaps

Generate one-factor-at-a-time sensitivity results for all sectors:

```bash
PYTHONPATH=src .venv/bin/python -m sensitivity_deep_dive \
  --metric LPM --variation 0.20
```

Limit the run when needed:

```bash
PYTHONPATH=src .venv/bin/python -m sensitivity_deep_dive \
  --metric NPV --variation 0.10 --sectors cement steel
```

The direct sensitivity command expresses `--variation` as a fraction, so
`0.20` means 20%. By contrast, `regenerate_all.py` uses
`--sensitivity-variation-percent 20`. Direct outputs go to `figures/` and
`data/processed/` unless explicit output directories are provided.

Each heatmap cell is a one-factor-at-a-time recalculation. Downstream equations
are evaluated again, but grouped cells such as fuel, electricity, or emissions
report the larger constituent effect rather than varying multiple inputs
together.

### Interactive dashboard

Start the Streamlit dashboard from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m streamlit run sensitivity_dashboard.py
```

The dashboard provides sector tabs, technology and metric selection, editable
scenario inputs, and tornado diagrams. It is a deterministic exploration tool:
changes made in the interface do not alter the stored source assumptions.
Restart it after editing `src/general_parameters.py` or sector parameter files.

## Use the Notebooks

Start Jupyter Lab from the repository root:

```bash
PYTHONPATH=src .venv/bin/python -m jupyter lab
```

Notebook organization is consistent across sectors:

- `notebooks/<sector>/<sector>_summary.ipynb` compares all technologies in a
  sector using deterministic and Monte Carlo results.
- `notebooks/<sector>/deterministic_*_npv.ipynb` explains one deterministic
  technology calculation and its inputs.
- `notebooks/<sector>/plot_*_npv.ipynb` explores one technology's Monte Carlo
  inputs, financial distribution, and cost components.
- `notebooks/<sector>/<sector>_abatement_comparison.ipynb` presents that
  sector's technology abatement-cost comparison for cement, steel, ammonia,
  and hydrogen.
- `notebooks/scenario_analysis.ipynb` contains selected deterministic scenario
  comparisons.
- `notebooks/sensitivity_heatmap.ipynb` presents standardized sensitivity
  heatmaps.
- `notebooks/plot_fuel_elec_price_distributions.ipynb` inspects shared price
  distributions.

Notebook figures are displayed inline. The notebooks do not contain separate
save-output switches. For a non-destructive verification of every notebook,
use `regenerate_all.py --verify-notebooks`; it saves executed copies under the
named run and leaves the source notebooks unchanged.

## How the Model Is Organized

The main calculation path is:

```text
shared and sector parameters
        ↓
deterministic expected inputs or Monte Carlo samples
        ↓
sector technology model
        ↓
shared discounted-finance functions
        ↓
summary tables, rankings, figures, abatement-cost comparisons, and sensitivities
```

For each sector, the reusable modules have the same responsibilities:

| Module | Responsibility |
| --- | --- |
| `<sector>_parameters.py` | Final technology and sector assumptions |
| `<sector>_npv_deterministic.py` | Builds the expected-input case |
| `<sector>_npv_monte_carlo.py` | Samples uncertain inputs with aligned simulation IDs |
| `<sector>_npv_model.py` | Resolves technology inputs and calculates sector results |
| `<sector>_financial_summary.py` | Configures figures, tables, rankings, units, and CLI behavior |
| `<sector>_abatement_comparison.py` | Calculates deterministic or simulated technology abatement-cost comparisons where available |

Shared logic lives in:

- `src/general_parameters.py` for assumptions used across sectors, including
  carbon price, discount rate, CCS transport and storage, and energy prices;
- `src/distributions.py` for fixed, uniform, triangular, and scaled-beta input
  definitions;
- `src/npv_finance.py` for discounted cash flow, NPV, LPM, and LCOX;
- `src/financial_summary_workflow.py` for the common simulation-to-output
  workflow;
- `src/npv_summary.py` and `src/npv_summary_plots.py` for reusable summaries,
  rankings, and plots; and
- `src/sensitivity_analysis.py` and `src/sensitivity_deep_dive.py` for
  deterministic sensitivity calculations and heatmaps.

## Financial Metrics and Units

The same metric selectors are used in all sectors:

| Selector | Meaning | Interpretation |
| --- | --- | --- |
| `NPV` | Total project net present value | Higher is better; figures report million EUR |
| `LPM` | Levelized profit margin | Higher is better; positive values create value |
| `LCOX` | Levelized cost of the sector product | Lower is better; product-specific unit |

`LCOX` is displayed with a sector-specific name:

| Sector | Displayed metric | Unit |
| --- | --- | --- |
| Electricity | LCOE | EUR/MWh |
| Cement | LCOC | EUR/t cement |
| Steel | LCOS | EUR/t crude steel |
| Ammonia | LCOA | EUR/tNH3 |
| Hydrogen | LCOH | EUR/tH2 |

The shared relationships are:

```text
discounted lifetime output = Σ output_t / (1 + r)^t
discounted lifetime cost   = CAPEX at t=0 + Σ annual cost_t / (1 + r)^t
LCOX                       = discounted lifetime cost / discounted lifetime output
LPM                        = NPV / discounted lifetime output
LPM                        = levelized revenue - LCOX
```

Product sales revenue is excluded from LCOX. Technology costs, fuel and
purchased electricity where relevant, and direct carbon costs or credits are
included according to each sector model. Cross-sector LCOX values must not be
placed in one ranking because the products and functional units differ.

## Important Modeling Conventions

- Technology cost assumptions in the sector parameter modules are the final
  model values. Costs that required CEPCI conversion have been normalized to
  2024 values before being entered into the active model.
- The active carbon price is defined in `src/general_parameters.py`; there is
  no carbon-price command-line override. Change it deliberately in that file
  and use a new run name. Every named-run manifest records the value actually
  used.
- The carbon price is applied to modeled direct operational emissions. Negative
  direct emissions, such as BECCS, therefore create a carbon-credit term in the
  financial calculation.
- Deterministic cases use analytical expected inputs: the stored mean for a
  scaled-beta distribution, `(minimum + mode + maximum) / 3` for a triangular
  distribution, the midpoint for a uniform distribution, and the stored value
  for a fixed parameter.
- A deterministic expected-input result need not equal the Monte Carlo output
  mean when later equations are nonlinear.
- The default Monte Carlo setup uses 100,000 draws per technology and random
  seed 42. Use smaller samples for development, but use and record an
  appropriate final sample size for thesis results.
- `retrofit_bau_mode=sampled` is the default. A retrofit and its parent reuse
  the same sampled BAU inputs for each simulation ID. The `deterministic` mode
  fixes the parent at expected inputs while sampling the retrofit increments;
  it is mainly useful for diagnostics.
- Applicable CCS routes add transport and storage as 18.7% of the levelized
  incremental capture cost before carbon-price effects. BECCS uses its direct
  transport-and-storage cost input instead.
- Model outputs cover the system boundaries encoded in the source modules.
  Do not infer upstream life-cycle emissions, infrastructure constraints, or
  market deployment potential unless they are explicitly represented.

Always inspect the relevant parameter and model modules before changing an
assumption. After a change, make a small direct run first and then create a new
named result run so old and new assumptions remain distinguishable.

## Generated Files and Version Control

- `data/raw/` contains generated, unit-resolved Monte Carlo input samples. It
  does not contain the only copy of source assumptions.
- `data/processed/` contains generated technology results, summary statistics,
  rankings, abatement-comparison tables, and sensitivity tables.
- `results/runs/` contains isolated named runs, logs, executed notebook copies,
  and manifests.
- `results/temporary/` is reserved for explicitly temporary comparison work.
- `figures/` contains tracked reference figures. Quick commands create new
  date-stamped figures rather than silently replacing older dates.

The generated data and result directories can become very large and are
ignored by Git. Do not place hand-edited assumptions or irreplaceable work only
inside an ignored directory.

## Basic Validation

Compile the source files after editing code:

```bash
.venv/bin/python -m compileall -q src regenerate_all.py \
  sensitivity_dashboard.py
```

Preview the full workflow without creating files:

```bash
PYTHONPATH=src .venv/bin/python regenerate_all.py \
  --run-name validation_preview --full --dry-run
```

Run a small sector check before a large simulation:

```bash
PYTHONPATH=src .venv/bin/python \
  -m electricity.electricity_financial_summary \
  --metric NPV --sample-size 100 \
  --output-dir results/validation/figures \
  --raw-data-dir results/validation/raw \
  --processed-data-dir results/validation/processed
```

For the authoritative options of any command, use `--help`. The README explains
the intended workflow; the command-line help reflects the exact current
interface.
