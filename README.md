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
├── figures/              # Plots and figures for reports and presentations
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
- `src/npv_finance.py` contains the sector-independent NPV formula.
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
- Use the command-line summary modules when figures and CSV outputs must be
  regenerated reproducibly.
- Use `sensitivity_dashboard.py` for interactive deterministic
  one-factor-at-a-time sensitivity analysis.

## Sensitivity Dashboard

The Streamlit dashboard provides an interactive deterministic sensitivity
analysis for the cement and electricity sectors. It lets you select a sector,
technology, NPV metric, and scenario inputs, then generates a tornado diagram
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

The dashboard supports total NPV in `MEUR` and normalized NPV in `EUR/t` for
cement or `EUR/MWh` for electricity. Green bars indicate changes that improve
the selected NPV metric, red bars indicate changes that worsen it, and the
`+x%` or `-x%` labels show which input movement caused the impact. Downloaded or
in-app saved dashboard figures can be written to `figures/`.

Each sector tab also contains a **Variables in sensitivity analysis** panel.
Check or uncheck inputs there to control which variables are recalculated and
shown in the tornado diagram.

The dashboard is a deterministic scenario tool. It does not change stored model
assumptions, and it currently varies annual production/generation consistently
with the normalized deterministic plant-size setup rather than holding capacity
fixed.

To regenerate the standardized technology-input sensitivity CSV and heatmaps:

```bash
PYTHONPATH=src python -m sensitivity_deep_dive
```

The heatmaps compare equal relative input changes using specific NPV
(`EUR/t` or `EUR/MWh`). Annual output and product selling prices are excluded
from these cross-technology heatmaps because they are common comparison
assumptions rather than technology-development inputs. Lifetime and discount
rate remain included as common financial assumptions.
The derived sensitivity CSV is written to `data/processed/`; heatmaps are
written to `figures/`.

To regenerate the electricity-sector figures and CSV outputs, run:

```bash
PYTHONPATH=src python -m electricity.electricity_npv_summary_figures
```

For cement:

```bash
PYTHONPATH=src python -m cement.cement_npv_summary_figures
```

Generated figures are written to `figures/`, raw sampled inputs to `data/raw/`,
and processed model outputs to `data/processed/`.

Use `--help` on either module to see options for sample size, random seed, NPV
scale, output type, and cement retrofit baseline mode.

## Generated Data and Version Control

`data/raw/`, `data/processed/`, and `results/` are intentionally ignored by Git.
They can become very large: the current local generated CSVs occupy roughly
1.5 GB. They are reproducible outputs, not the only copy of source assumptions.
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

There is not yet a formal automated test suite. The commands above are the
minimum project smoke checks.
