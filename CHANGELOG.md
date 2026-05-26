## 2026-05-26 11:45 — Add hard coal electricity technology distributions

### User request

Confirm whether the 1 TWh/year and 4,100 h/year hard coal capacity calculation is reasonable, then add the provided hard coal CAPEX, OPEX, fuel consumption, and emissions parameters to the electricity parameter file.

### Files changed (if needed)

- `src/electricity_parameters.py` — added hard coal technology distributions for CAPEX, fixed OPEX, variable OPEX, fuel consumption, and emissions.

### What was implemented

- Added hard coal CAPEX as a uniform distribution because no base value was provided:
  - 1,700 to 2,300 EUR/kW.
- Added triangular hard coal distributions where base values were provided:
  - Fixed OPEX: 29.6 / 37.0 / 48.1 EUR/kW/year.
  - Variable OPEX excluding fuel/electricity: 4.0 / 5.0 / 6.5 EUR/MWh.
  - Fuel consumption: 2.44 / 2.56 / 2.70 MWh_th/MWh_e.
  - Emissions: 0.83 / 0.87 / 0.92 tCO2/MWh_e.
- Added `ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS` and registered the hard coal stochastic parameters under `hard_coal`.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/electricity_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_parameters import ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS; from distributions import sample_triangular, sample_uniform; d=ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS["hard_coal"]; rng=np.random.default_rng(42); print(d["capex_eur_per_kw"].lower_bound, d["capex_eur_per_kw"].upper_bound, sample_uniform(d["capex_eur_per_kw"], 2, rng).shape, d["fixed_opex_eur_per_kw_year"].mode, sample_triangular(d["fixed_opex_eur_per_kw_year"], 2, rng).shape)'`
- Result:
  - Passed.
  - The smoke test confirmed hard coal CAPEX bounds, fixed OPEX mode, and sampling compatibility.

### Reproducibility notes

- This adds hard coal stochastic technology assumptions to the electricity-sector parameter set.
- The hard coal capacity normalization remains reasonable: 1 TWh/year equals about 114.2 MW average output, and with 4,100 h/year the required capacity is about 243.9 MW.
- No simulation outputs, plots, reports, or PDFs were generated.

### Next suggested step

Add a first electricity NPV function that combines normalized capacity, sampled hard coal parameters, coal fuel price, carbon price, electricity revenue, and discounting.

## 2026-05-26 11:42 — Start electricity sector model

### User request

Start the electricity sector setup by adding hard coal parameters from the attached table, adding a configurable electricity output parameter, and creating a model file with the conversion formula between output, FLH, and capacity.

### Files changed (if needed)

- `src/electricity_parameters.py` — added the normalized annual electricity output parameter and the hard coal full-load-hours parameter.
- `src/electricity_model.py` — added reusable capacity conversion functions for annual electricity output and full-load hours.

### What was implemented

- Added `ANNUAL_ELECTRICITY_OUTPUT_MWH` with a default value of 1,000,000 MWh/year, equivalent to 1 TWh/year.
- Added `HARD_COAL_FULL_LOAD_HOURS` with the user-specified value of 4,100 h/year.
- Added `ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS` with hard coal full-load hours.
- Added `calculate_capacity_mw`, using `annual_electricity_output_mwh / full_load_hours_per_year`.
- Added `calculate_capacity_kw`, converting the calculated MW capacity to kW.
- Did not add CAPEX, OPEX, fuel consumption, or emissions distributions because the numeric values in the attached image were not readable enough to extract without risking invented assumptions.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/electricity_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from electricity_parameters import ANNUAL_ELECTRICITY_OUTPUT_MWH, HARD_COAL_FULL_LOAD_HOURS; from electricity_model import calculate_capacity_mw, calculate_capacity_kw; print(round(calculate_capacity_mw(ANNUAL_ELECTRICITY_OUTPUT_MWH.value, HARD_COAL_FULL_LOAD_HOURS.value), 6), round(calculate_capacity_kw(ANNUAL_ELECTRICITY_OUTPUT_MWH.value, HARD_COAL_FULL_LOAD_HOURS.value), 3))'`
- Result:
  - Passed.
  - The default hard coal capacity calculation returned 243.902439 MW, or 243,902.439 kW, for 1 TWh/year and 4,100 h/year.

### Reproducibility notes

- This adds a new electricity-sector normalization assumption: default annual output is 1 TWh/year.
- No simulation outputs, plots, reports, or PDFs were generated.
- Hard coal CAPEX, OPEX, fuel consumption, and emissions still need to be added once the source values are provided in readable text form.

### Next suggested step

Paste the hard coal CAPEX, fixed OPEX, variable OPEX, fuel consumption, and emissions ranges so they can be added as triangular or uniform distributions.

## 2026-05-26 11:24 — Add electricity price distribution

### User request

Add a triangular electricity price distribution to the general parameters, similar to the existing coal and gas distributions, using minimum 74.8 EUR/MWh, maximum 255.2 EUR/MWh, and average 183.7 EUR/MWh.

### Files changed (if needed)

- `src/general_parameters.py` — added the electricity price triangular distribution and included it in `GENERAL_DISTRIBUTIONS`.

### What was implemented

- Added `ELECTRICITY_PRICE_DISTRIBUTION` with minimum 74.8, mode 183.7, and maximum 255.2 EUR/MWh.
- Registered the distribution under `electricity_price_eur_per_mwh`.
- Used the provided average value as the triangular distribution mode to match the existing low/mid/high parameter structure.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/general_parameters.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from general_parameters import ELECTRICITY_PRICE_DISTRIBUTION, GENERAL_DISTRIBUTIONS; print(ELECTRICITY_PRICE_DISTRIBUTION.minimum, ELECTRICITY_PRICE_DISTRIBUTION.mode, ELECTRICITY_PRICE_DISTRIBUTION.maximum, "electricity_price_eur_per_mwh" in GENERAL_DISTRIBUTIONS)'`
- Result:
  - Passed.

### Reproducibility notes

- This changes a shared model input assumption by adding an electricity price uncertainty distribution.
- No simulation outputs, plots, reports, or PDFs were regenerated.

### Next suggested step

Use `electricity_price_eur_per_mwh` in downstream Monte Carlo sampling wherever electricity price uncertainty should be represented.

## 2026-05-21 15:59 — Split sector parameters and centralize datatypes

### User request

Move `FixedParameter` into the distribution/datatype file and create separate cement and electricity parameter files containing the parameters from the general file that belong to those sectors.

### Files changed (if needed)

- `src/distributions.py` — added `FixedParameter` so fixed and stochastic parameter datatypes are defined in one place.
- `src/general_parameters.py` — removed the local `FixedParameter` datatype and imports cement/electricity sector parameters from their dedicated modules.
- `src/cement_parameters.py` — added cement-sector lifetime and retail price fixed parameters.
- `src/electricity_parameters.py` — added electricity-sector lifetime and retail price fixed parameters.

### What was implemented

- Centralized `FixedParameter`, `TriangularDistribution`, and `UniformDistribution` in `src/distributions.py`.
- Moved cement-specific fixed parameters into `CEMENT_FIXED_PARAMETERS`.
- Moved electricity-specific fixed parameters into `ELECTRICITY_FIXED_PARAMETERS`.
- Kept `GENERAL_FIXED_PARAMETERS` available by importing the sector parameters into `general_parameters.py` for compatibility with existing code.
- Preserved existing parameter values, including the current `INTEREST_RATE` value in the working tree.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/cement_parameters.py src/electricity_parameters.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from distributions import FixedParameter, TriangularDistribution, UniformDistribution; from cement_parameters import CEMENT_FIXED_PARAMETERS; from electricity_parameters import ELECTRICITY_FIXED_PARAMETERS; from general_parameters import GENERAL_FIXED_PARAMETERS, GENERAL_DISTRIBUTIONS; print(len(CEMENT_FIXED_PARAMETERS), len(ELECTRICITY_FIXED_PARAMETERS), len(GENERAL_FIXED_PARAMETERS), len(GENERAL_DISTRIBUTIONS))'`
- Result:
  - Passed.

### Reproducibility notes

- No model parameter values, simulation outputs, plots, reports, or PDFs were changed.
- The change reorganizes where parameter definitions live so sector-specific modules can be extended later.

### Next suggested step

Add sector-specific uncertain parameters to `cement_parameters.py` and `electricity_parameters.py` as the model assumptions are defined.

## 2026-05-21 11:01 — Add uniform distribution helper

### User request

Add the same reusable distribution setup for uniform distributions that currently exists for triangular distributions, using only lower and upper bounds.

### Files changed (if needed)

- `src/distributions.py` — added `UniformDistribution` and `sample_uniform`.

### What was implemented

- Added a frozen `UniformDistribution` dataclass with `lower_bound`, `upper_bound`, `unit`, and `description`.
- Added `sample_uniform`, matching the existing triangular sampling pattern with `size` and optional NumPy random generator support.
- Left the existing triangular distribution code unchanged.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from distributions import TriangularDistribution, UniformDistribution, sample_triangular, sample_uniform; rng=np.random.default_rng(42); tri=TriangularDistribution(1.0, 2.0, 4.0, "unit", "test"); uni=UniformDistribution(10.0, 20.0, "unit", "test"); print(sample_triangular(tri, 3, rng).shape, sample_uniform(uni, 3, rng).shape)'`
- Result:
  - Passed.

### Reproducibility notes

- No model parameters, simulation outputs, plots, reports, or PDFs were changed.
- The new helper only adds reusable sampling functionality for future parameter definitions.

### Next suggested step

Use `UniformDistribution` in sector-specific parameter modules where only lower and upper uncertainty bounds are available.

## 2026-05-20 14:00 — Split reusable distribution sampling

### User request

Remove general distribution sampling from the general parameters module and create a reusable `distributions.py` module for triangular sampling, while keeping the general fixed parameters unchanged.

### Files changed (if needed)

- `src/general_parameters.py` — removed sampling helpers and imported the triangular distribution specification from the reusable distributions module.
- `src/distributions.py` — added the reusable triangular distribution specification and triangular sampling helper.

### What was implemented

- Kept `GENERAL_FIXED_PARAMETERS` unchanged.
- Kept gas and coal triangular distribution definitions in `general_parameters.py` as general model input definitions.
- Removed `sample_general_distributions` because the model should not have a general-only sampling wrapper at this stage.
- Moved reusable triangular sampling into `src/distributions.py` so future sector modules can use the same helper.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/general_parameters.py src/distributions.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from general_parameters import GENERAL_FIXED_PARAMETERS, GENERAL_DISTRIBUTIONS; from distributions import sample_triangular; sample_triangular(GENERAL_DISTRIBUTIONS["gas_price_eur_per_mwh"], 3); print(len(GENERAL_FIXED_PARAMETERS), len(GENERAL_DISTRIBUTIONS))'`
- Result:
  - Passed.

### Reproducibility notes

- No simulation outputs, plots, reports, or PDFs were generated.
- No parameter values or scientific assumptions were changed.

### Next suggested step

Create sector-specific parameter modules that import shared fixed parameters from `general_parameters.py` and reusable sampling helpers from `distributions.py`.

## 2026-05-20 13:57 — Add general Monte Carlo parameters

### User request

Create a reusable general parameter setup file for the Monte Carlo simulation, including fixed global parameters and gas/coal triangular price distributions from the attached table.

### Files changed (if needed)

- `src/general_parameters.py` — added deterministic parameter specs, triangular distribution specs, and sampling helpers for shared Monte Carlo inputs.

### What was implemented

- Added documented fixed parameters for cement lifetime, electricity lifetime, cement retail price, electricity retail price, carbon price, and interest rate.
- Added gas and coal price triangular distributions using the attached low/mid/high values:
  - Gas: 12.5 / 39.3 / 89.7 EUR/MWh
  - Coal: 8.14 / 12.11 / 24.17 EUR/MWh
- Added mappings for fixed parameters and stochastic distributions so sector modules can extend or combine them later.
- Added sampling helpers compatible with NumPy's random generator API.

### Verification (if needed)

- Commands run:
  - `python -m compileall src`
  - `python3 -B -m py_compile src/general_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache python3 -m py_compile src/general_parameters.py`
- Result:
  - Passed with `python3` after redirecting Python's bytecode cache to `/private/tmp`.
- Notes:
  - `python` was not available on PATH.
  - `python3 -B -m py_compile` attempted to write to Apple's default cache directory under `~/Library`, which is blocked by the sandbox.

### Reproducibility notes

- No simulation outputs, plots, reports, or PDFs were generated.
- The only scientific values added are the user-specified fixed parameters and the fuel-price distribution values extracted from the attached table.

### Next suggested step

Create the first sector-specific parameter module and import the shared general parameters from `src/general_parameters.py`.
