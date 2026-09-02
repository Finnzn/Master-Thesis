# Master Thesis: Technology Development Uncertainty and Carbon Capture Demand

This repository contains the code, data structure, documentation, and analysis for my master thesis project:

**How uncertainty of technology development shapes carbon capture demand uncertainty**

The thesis is supervised by Nour Boulos and Prof. Dr. Giovanni Sansavini at ETH Zurich.

## Project Overview

Carbon capture and storage (CCS) is considered an important technology for reaching net-zero emissions in Europe. However, the large-scale deployment of CCS is still below political targets. One possible reason is that carbon capture competes with alternative decarbonization technologies that emitting plants can adopt.

This thesis investigates under which conditions carbon capture is the most economically viable option for reducing emissions in different industrial sectors. The focus is on applications such as:

- Cement production
- Steel and metal manufacturing
- Chemical production
- Other energy-intensive industrial processes

The project compares carbon capture technologies with alternative non-capture decarbonization options under techno-economic uncertainty.

## Research Objective

The main objective of this thesis is to evaluate how uncertainty in technology development affects the future demand for carbon capture.

The central research question is:

**Which emitting sectors should implement carbon capture, and which should investigate alternative decarbonization technologies?**

## Methodology

The thesis develops a probabilistic, cost-based evaluation framework for comparing decarbonization technology options across different emitting sectors.

The main methodological steps are:

1. Identify decarbonization technology options for each emitting sector.
2. Compare carbon capture technologies with alternative non-capture decarbonization technologies.
3. Develop a cost-based metric to assess the economic viability of each option.
4. Use Monte Carlo analysis to capture uncertainty in techno-economic parameters.
5. Evaluate how uncertainty in technology development affects carbon capture demand.

The Monte Carlo analysis may include uncertainty in parameters such as:

- Capital costs
- Operating costs
- Energy requirements
- Energy prices
- Carbon prices
- Technology learning and cost evolution

## Quick Start

The source code requires Python 3.10 or newer. Python 3.12 is used in the
current thesis environment.

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run a small smoke check before starting a large simulation:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
PYTHONPATH=src python -m cement.cement_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
```

The default Monte Carlo sample size is 100,000 per technology. Start with a
smaller value while testing changes.

## Repository Structure

```text
MasterThesis/
├── src/                  # Main Python source code
├── notebooks/            # Jupyter notebooks for exploration and analysis
├── data/                 # Input data and assumptions
│   ├── raw/              # Raw data, usually not tracked by Git
│   └── processed/        # Cleaned or processed data
├── results/              # Simulation results, usually not tracked by Git
├── figures/              # Plots and figures for reports
├── docs/                 # Handover and workflow documentation
├── tests/                # Reserved for automated tests
├── sensitivity_dashboard.py # Streamlit sensitivity analysis dashboard
├── README.md             # Project overview
├── requirements.txt      # Python dependencies
└── .gitignore            # Files and folders ignored by Git
```

For a practical map of the model, generated files, assumptions, and known
handover risks, read [`docs/HANDOVER.md`](docs/HANDOVER.md).

## Source Code Guide

The reusable Python code is organized around sector-independent helpers and
sector-specific calculations.

- `src/distributions.py` defines deterministic parameters and probability
  distribution specifications used by Monte Carlo simulations.
- `src/general_parameters.py` stores shared assumptions such as carbon price,
  discount rate, and fuel-price distributions.
- `src/npv_finance.py` contains the sector-independent NPV, levelized net
  margin, and LCOX formulas.
- `src/sensitivity_analysis.py` contains deterministic one-factor-at-a-time
  sensitivity calculations and tornado-chart plotting for the dashboard.
- `src/npv_summary.py` converts simulation outputs into summary tables, rankings,
  and CSV files.
- `src/npv_summary_plots.py` contains reusable plotting functions for NPV bar
  charts and ranking figures.
- `src/electricity/` contains electricity-sector assumptions, deterministic NPV
  calculations, Monte Carlo simulations, and output-generation scripts.
- `src/cement/` contains cement-sector assumptions, deterministic NPV
  calculations, Monte Carlo simulations, and output-generation scripts.

## Which Notebook or Script Should I Use?

- Use `notebooks/electricity/electricity_summary.ipynb` or
  `notebooks/cement/cement_summary.ipynb` for an inline overview of all
  technologies. Their Monte Carlo tables include mean, median, percentiles, and
  counts of non-negative versus negative NPV simulations.
- Use `notebooks/<sector>/plot_*_npv.ipynb` to inspect one technology's Monte
  Carlo inputs and NPV distribution. Each notebook reports the count and share
  of non-negative versus negative NPV simulations.
- Use `notebooks/<sector>/deterministic_*_npv.ipynb` to inspect one
  representative deterministic calculation.
- Use `notebooks/scenario_analysis.ipynb` for the deterministic FLH, lifetime,
  renewable value-factor, CO2-price, and discount-rate scenarios.
- Use the command-line summary modules when figures and CSV outputs must be
  regenerated reproducibly.
- Use `sensitivity_dashboard.py` for interactive deterministic
  one-factor-at-a-time sensitivity analysis.

## BECCS Electricity Assumptions

BECCS follows the same normalized-output, deterministic, Monte Carlo, NPV, LNM,
and LCOE pipeline as the other electricity technologies. Its assumptions are:

| Input | BECCS assumption |
| --- | --- |
| CAPEX | Uniform, 2,454-4,239 EUR/kW |
| Fixed OPEX | Uniform, 128.4-229.1 EUR/kW/year |
| Variable OPEX excluding fuel | Uniform, 1.16-2.31 EUR/MWh |
| CO2 transport and storage | Uniform, 22-29 EUR/MWh_e |
| Biomass consumption | Uniform, 2.42-3.27 MWh_th/MWh_e |
| Net emissions | Uniform, -1.33 to -1.01 tCO2/MWh_e |
| Full-load hours | Fixed at 7,665 h/year, the average of 7,446-7,884 |
| Biomass price | Triangular, 17.36 / 28.93 / 46.28 EUR/MWh_th |
| Lifetime | 25 years, assumed equal to the existing biogas lifetime |

The supplied negative-emissions range is multiplied by the common carbon price.
This produces a negative carbon-cost term, which becomes carbon-removal revenue
when subtracted in the shared cash-flow formula. The same negative term reduces
LCOE because the established LCOX boundary includes carbon costs and credits.

## Retrofit BAU Baseline Modes

Cement retrofit technologies and the electricity technologies `hard_coal_ccs`
and `ccgt_ccs` are modelled as changes relative to a BAU technology. The two
electricity retrofits use `hard_coal` and `ccgt`, respectively, as their BAU
parents.

Monte Carlo workflows expose `retrofit_bau_mode` with two choices:

- `sampled` is the default. BAU technical inputs are sampled once per simulation
  ID and reused for the matching BAU result and retrofit, so each comparison uses
  one shared uncertain baseline.
- `deterministic` holds the retrofit's BAU technical inputs at their representative
  values while continuing to sample incremental retrofit and other stochastic
  inputs. This isolates retrofit uncertainty for diagnostic runs.

Incremental costs are added to BAU costs. Fuel use, electricity use where
applicable, and emissions follow `BAU value * (1 - reduction fraction)`. Positive
fractions therefore reduce the BAU value, while negative reduction fractions
represent increases. Deterministic calculations always use representative BAU
and retrofit values; the selectable mode controls Monte Carlo calculations.

CCS transport and storage (T&S) adds 18.7% of the levelized incremental capture
cost, defined as `(BAU + CCS) - BAU` across CAPEX, OPEX, and fuel/electricity
costs before carbon-price effects and before T&S. This applies to hard-coal CCS,
CCGT CCS, and cement CCS. BECCS instead uses its independent 22-29 EUR/MWh_e
uniform T&S cost range. The capture-share calculation is evaluated from the
current inputs rather than stored as a fixed surcharge: changing CAPEX, OPEX,
fuel or electricity inputs, full-load hours, lifetime, or discount rate therefore
also updates T&S wherever those inputs enter the incremental capture cost.

## Renewable Electricity Value Factors

PV, onshore wind, and offshore wind use triangular value-factor distributions
in `src/electricity/electricity_parameters.py`. The supplied base is the mode
and deterministic representative value:

| Technology | Minimum | Base / mode | Maximum |
| --- | ---: | ---: | ---: |
| Onshore wind | 0.80 | 0.90 | 1.00 |
| Offshore wind | 0.85 | 0.95 | 1.00 |
| Solar PV | 0.80 | 0.90 | 1.00 |

The value factor scales the model's existing electricity sales-price proxy to a
captured price. The parameter names remain `VF_PV`, `VF_Wind_onshore`, and
`VF_windoffshore`:

```text
captured electricity price = electricity sales-price proxy * value factor
annual electricity revenue = annual generation * captured electricity price
```

It does not change generation, required capacity, costs, discounted output, or
LCOE. The separate renewable plot in `notebooks/scenario_analysis.ipynb`
compares the minimum, base, and maximum factors for PV and both wind
technologies. Value factor is also included for these three technologies in the
electricity sensitivity heatmap.

## Sensitivity Dashboard

The Streamlit dashboard provides an interactive deterministic sensitivity
analysis for the cement and electricity sectors. It lets you select a sector,
technology, financial metric, and scenario inputs, then generates a tornado diagram
showing one-factor-at-a-time impacts.

To run the dashboard from the repository root:

```bash
PYTHONPATH=src streamlit run sensitivity_dashboard.py
```

If you use the thesis Conda environment directly:

```bash
/opt/anaconda3/envs/master-thesis/bin/streamlit run sensitivity_dashboard.py
```

The path above is specific to the original development machine. On another
machine, activate the environment created in the quick start and use the first
command.

The dashboard uses the same `NPV`, `LNM`, and `LCOX` selector as the summary and
scenario notebooks. Green bars indicate changes that improve the selected
metric and red bars indicate changes that worsen it; for LCOX, a lower value is
treated as better. The `+x%` or `-x%` labels show which input movement caused
the impact. Downloaded or in-app saved dashboard figures can be written to
`figures/`.

Each sector tab also contains a **Variables in sensitivity analysis** panel.
Check or uncheck inputs there to control which variables are recalculated and
shown in the tornado diagram. For hard-coal CCS, CCGT CCS, and cement CCS the
dashboard exposes the T&S share of capture cost; for BECCS it exposes the direct
T&S cost. The same assumptions appear in the standardized heatmaps as `T&S`.

The dashboard is a deterministic scenario tool. It does not change stored model
assumptions, and it currently varies annual production/generation consistently
with the deterministic plant-size setup rather than holding capacity
fixed.

To regenerate the standardized technology-input sensitivity CSV and heatmaps:

```bash
PYTHONPATH=src python -m sensitivity_deep_dive
```

The heatmaps compare equal relative input changes using the selected `NPV`,
`LNM`, or `LCOX` metric. Annual output and product selling prices are excluded
from these cross-technology heatmaps because they are common comparison
assumptions rather than technology-development inputs. Lifetime and discount
rate remain included as common financial assumptions. Every row is a
one-factor-at-a-time calculation, but all downstream equations are evaluated:
for example full-load hours resize electricity capacity, value factor changes
captured revenue, and capture-share T&S follows its current capture-cost basis.
Grouped `Fuel`, `Electricity`, and `Emissions` heatmap cells show the larger of
their two constituent one-at-a-time impacts; they do not vary both inputs jointly
or estimate interaction effects.
The derived sensitivity CSV is written to `data/processed/`; heatmaps are
written to `figures/`.

To regenerate electricity-sector total NPV figures and CSV outputs, run:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures --metric NPV
```

For electricity levelized net margin, use:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures --metric LNM
```

For LCOE, use the same electricity workflow with `LCOX`:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures --metric LCOX
```

Electricity Monte Carlo summaries use sampled BAU values for the coal and CCGT
CCS retrofits by default. To hold those BAU inputs at representative values, add
the electricity summary flag:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures \
  --metric LCOX --retrofit-bau-mode deterministic
```

For cement, use the same `--metric NPV`, `--metric LNM`, or `--metric LCOX`
switch. In the cement model, `LCOX` is reported as LCOC:

```bash
PYTHONPATH=src python -m cement.cement_npv_summary_figures --metric LCOX
```

Generated figures are written to `figures/`, raw sampled inputs to `data/raw/`,
and processed model outputs to `data/processed/`.

Use `--help` on either module to see options for sample size, random seed,
financial metric, output type, and retrofit BAU baseline mode.

## Financial Metrics

The reporting workflows can switch between:

- `NPV`: total project net present value, displayed in million EUR.
- `LNM`: levelized net margin, displayed in EUR/MWh of electricity or EUR/t of
  cement.
- `LCOX`: levelized cost of the sector product. This is displayed as LCOE in
  EUR/MWh for electricity and LCOC in EUR/t cement for cement.

All three metrics use the same project lifetime, discount rate, and cash-flow
timing:

```text
LNM = NPV / discounted lifetime output
LCOX = discounted lifetime cost / discounted lifetime output
discounted lifetime output = sum(output_t / (1 + r)^t)
discounted lifetime cost = CAPEX at t=0 + sum(annual cost_t / (1 + r)^t)
```

For the current level annual-output models, discounted lifetime output equals
annual output multiplied by the level cash-flow present-value factor. Positive
LNM creates value, zero is break-even, and negative LNM destroys value under the
stated assumptions. Lower LCOX is preferable. The LCOX boundary includes CAPEX,
fixed OPEX, variable OPEX, fuel, cement electricity consumption, and carbon
cost; product sales revenue is excluded. Under the current constant-price and
constant-output assumptions:

```text
electricity captured price - LCOE = electricity LNM
cement price - LCOC = cement LNM
```

The general deterministic and probabilistic LCOX analysis is in
`notebooks/lcox_summary.ipynb`. It keeps electricity and cement charts separate
because LCOE and LCOC measure different products in different units.

The cement MACC annualizes CAPEX and uses all annual technology costs, including
CCS transport and storage, while excluding carbon payments and product revenue.
Its bar heights therefore measure resource cost per tonne of direct CO2 avoided.

## Generated Data and Version Control

`data/raw/`, `data/processed/`, and `results/` are intentionally ignored by Git.
They can become very large: the current local generated CSVs occupy roughly
3 GB. They are reproducible outputs, not the only copy of source assumptions.
Do not place hand-edited inputs or irreplaceable results only in these ignored
folders.

The dated PNG files in `figures/` are tracked selectively. Regenerating a
workflow creates new date-stamped files rather than overwriting older figures.

## Basic Validation

Before handing over a change:

```bash
python -m compileall -q src sensitivity_dashboard.py
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
PYTHONPATH=src python -m cement.cement_npv_summary_figures \
  --sample-size 100 --no-data --ranking-output none
```

Compilation and the two small-sample workflow commands are the minimum smoke
checks for the output pipeline.
