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
