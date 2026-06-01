## 2026-06-01 14:43 — Add CCGT with CCS electricity NPV simulation

### User request

Add CCGT+CCS using the same style as the existing electricity technologies, with average full-load hours, then run a full sanity and logic check across the documents and code.

### Files changed (if needed)

- `src/electricity_parameters.py` — added CCGT+CCS CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added CCGT+CCS gas-price mapping, simulation wrapper, and CCGT+CCS to the default multi-technology simulation.
- `notebooks/deterministic_ccgt_ccs_npv.ipynb` — added deterministic CCGT+CCS NPV notebook.
- `notebooks/plot_ccgt_ccs_npv.ipynb` — added CCGT+CCS Monte Carlo plotting notebook.

### What was implemented

- Added CCGT+CCS technology assumptions:
  - CAPEX: uniform `1,487-2,557 EUR/kW`.
  - Fixed OPEX: triangular `32.0 / 42.0 / 60.2 EUR/kW/year`.
  - Variable OPEX: triangular `4.5 / 6.73 / 7.6 EUR/MWh_e`.
  - Fuel consumption: uniform `1.90-1.94 MWh_th/MWh_e`.
  - Residual direct emissions: uniform `0.0058-0.039 tCO2/MWh_e`.
  - Full-load hours: fixed average `(3,000 + 6,300) / 2 = 4,650 h/year`.
- Added `simulate_ccgt_ccs_npv`.
- Updated `simulate_electricity_technologies_npv` to include `ccgt_ccs` by default.
- Used the existing gas-price distribution and output key `gas_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for CCGT+CCS using the same structure as the other electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `python3 -m json.tool notebooks/deterministic_ccgt_ccs_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_ccgt_ccs_npv.ipynb`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - All notebooks are valid JSON.
  - The deterministic CCGT+CCS notebook executed and returned NPV `-423.526 million EUR`, or `-16.941 EUR/MWh`, with the current assumptions.
  - A 20,000-run CCGT+CCS sanity simulation returned mean NPV `-422.443 million EUR`, or `-16.898 EUR/MWh`.
  - Capacity, CAPEX, fixed OPEX, variable OPEX, fuel cost, emissions cost, annual net cash flow, lifetime-output, and NPV-per-MWh relationships passed for all electricity technologies.
  - Multi-technology results now include `hard_coal`, `ccgt`, `ccgt_ccs`, `nuclear`, `wind_offshore`, `wind_onshore`, `pv`, and `biogas` with aligned run IDs.

### Reproducibility notes

- This adds CCGT+CCS as a new electricity technology and changes the default multi-technology simulation output by including CCGT+CCS.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.
  - `ELECTRICITY_PRICE_DISTRIBUTION` remains defined but unused by the electricity NPV model.
  - CCGT+CCS uses residual direct emissions only; separate CO2 capture rate, captured CO2 mass flow, transport, storage, and CCS chain costs are not explicitly modeled unless already embedded in the user-provided CAPEX/OPEX values.
  - `npv_million_eur_per_mwh` remains a very small unit; `EUR/MWh` or `MEUR/TWh` may be easier to interpret.

### Next suggested step

Decide whether CCS transport and storage costs should be modeled explicitly or treated as already included in the CCGT+CCS CAPEX/OPEX assumptions.

## 2026-06-01 14:31 — Rename fuel-price distribution keys to thermal units

### User request

Change `gas_price_eur_per_mwh` and `coal_price_eur_per_mwh` to include `_th` at the end.

### Files changed (if needed)

- `src/general_parameters.py` — renamed general fuel-price distribution keys to `gas_price_eur_per_mwh_th` and `coal_price_eur_per_mwh_th`.

### What was implemented

- Updated `GENERAL_DISTRIBUTIONS` keys:
  - `gas_price_eur_per_mwh` -> `gas_price_eur_per_mwh_th`.
  - `coal_price_eur_per_mwh` -> `coal_price_eur_per_mwh_th`.
- Kept the underlying gas and coal distribution values unchanged.

### Verification (if needed)

- Commands run:
  - `rg -n '"(gas|coal)_price_eur_per_mwh"|\[("|\\x27)(gas|coal)_price_eur_per_mwh("|\\x27)\]' src notebooks docs data results figures tests README.md AGENT.md 2>/dev/null`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/general_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - The active project files no longer contain exact `gas_price_eur_per_mwh` or `coal_price_eur_per_mwh` keys without `_th`.
  - `GENERAL_DISTRIBUTIONS` now contains `gas_price_eur_per_mwh_th` and `coal_price_eur_per_mwh_th`.

### Reproducibility notes

- This is a naming/unit-clarity change only.
- No parameter values, model equations, simulation outputs, figures, reports, or PDFs were changed.
- Older historical changelog entries were left unchanged according to the repository rule that previous changelog entries must not be rewritten.

### Next suggested step

Use the `_th` suffix consistently for any future thermal fuel-price parameter names.

## 2026-06-01 14:24 — Add biogas electricity NPV simulation

### User request

Add biogas using the same style as the existing electricity technologies, with average full-load hours and a fixed biogas fuel cost of `87.5 EUR/MWh_th`.

### Files changed (if needed)

- `src/general_parameters.py` — added fixed biogas fuel-price parameter.
- `src/electricity_parameters.py` — added biogas CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added biogas fuel-price mapping, simulation wrapper, and biogas to the default multi-technology simulation.
- `notebooks/deterministic_biogas_npv.ipynb` — added deterministic biogas NPV notebook.
- `notebooks/plot_biogas_npv.ipynb` — added biogas Monte Carlo plotting notebook.

### What was implemented

- Added fixed biogas fuel price:
  - Biogas price: `87.5 EUR/MWh_th`.
- Added biogas technology assumptions:
  - CAPEX: uniform `2,894-5,788 EUR/kW`.
  - Fixed OPEX: uniform `92.6-301.0 EUR/kW/year`.
  - Variable OPEX: triangular `3.2 / 4.0 / 5.2 EUR/MWh_e`.
  - Fuel consumption: triangular `2.38 / 2.50 / 2.70 MWh_th/MWh_e`.
  - Fossil direct emissions: fixed `0 tCO2/MWh_e`.
  - Full-load hours: fixed average `(4,300 + 6,300) / 2 = 5,300 h/year`.
- Added `simulate_biogas_npv`.
- Updated `simulate_electricity_technologies_npv` to include `biogas` by default.
- Added deterministic and plotting notebooks for biogas using the same structure as the other electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/general_parameters.py src/electricity_parameters.py src/electricity_model.py`
  - `python3 -m json.tool notebooks/deterministic_biogas_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_biogas_npv.ipynb`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - Biogas simulation returned fixed `5,300 h/year`, fixed fuel price `87.5 EUR/MWh_th`, and zero fossil direct emissions.
  - Biogas normalized capacity for `1,000,000 MWh/year` is `188.679 MW`.
  - A 10,000-run biogas sanity simulation returned mean NPV `-2,615.424 million EUR` and mean normalized NPV `-104.617 EUR/MWh` with the current assumptions.
  - Capacity, fuel cost, emissions cost, lifetime-output, and NPV-per-MWh relationships passed.
  - Multi-technology results now include `hard_coal`, `ccgt`, `nuclear`, `wind_offshore`, `wind_onshore`, `pv`, and `biogas` with aligned run IDs.

### Reproducibility notes

- This adds biogas as a new electricity technology and changes the default multi-technology simulation output by including biogas.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags remain:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.
  - Biogenic emissions are represented as zero fossil direct emissions only; separate biogenic carbon tracking is not yet modeled.

### Next suggested step

Decide whether biogenic emissions or biomass supply constraints should be represented explicitly before comparing biogas directly against fossil and renewable technologies.

## 2026-06-01 14:16 — Add PV electricity NPV simulation

### User request

Add PV using the same style as the existing electricity technologies, with average full-load hours.

### Files changed (if needed)

- `src/electricity_parameters.py` — added PV CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added PV fuel-price mapping, simulation wrapper, and PV to the default multi-technology simulation.
- `notebooks/deterministic_pv_npv.ipynb` — added deterministic PV NPV notebook.
- `notebooks/plot_pv_npv.ipynb` — added PV Monte Carlo plotting notebook.

### What was implemented

- Added PV technology assumptions:
  - CAPEX: uniform `700-900 EUR/kW`.
  - Fixed OPEX: triangular `10.6 / 13.3 / 17.3 EUR/kW/year`.
  - Variable OPEX: fixed `0 EUR/MWh_e`.
  - Fuel consumption: fixed `0 MWh_th/MWh_e`.
  - Direct stack emissions: fixed `0 tCO2/MWh_e`.
  - Full-load hours: fixed average `(935 + 1,280) / 2 = 1,107.5 h/year`.
- Added `simulate_pv_npv`.
- Updated `simulate_electricity_technologies_npv` to include `pv` by default.
- Used the existing no-fuel price placeholder and technology-specific output key `no_fuel_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for PV using the same structure as the other electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/electricity_parameters.py src/electricity_model.py`
  - `python3 -m json.tool notebooks/deterministic_pv_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_pv_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - PV simulation returned fixed `1,107.5 h/year`, zero fuel cost, and zero direct emissions cost.
  - PV normalized capacity for `1,000,000 MWh/year` is `902.935 MW`.
  - A 10,000-run PV sanity simulation returned mean NPV `149.852 million EUR` and mean normalized NPV `5.994 EUR/MWh` with the current assumptions.
  - Capacity, fuel cost, emissions cost, lifetime-output, and NPV-per-MWh relationships passed.
  - Multi-technology results now include `hard_coal`, `ccgt`, `nuclear`, `wind_offshore`, `wind_onshore`, and `pv` with aligned run IDs.

### Reproducibility notes

- This adds PV as a new electricity technology and changes the default multi-technology simulation output by including PV.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags remain:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.

### Next suggested step

Compare PV with wind using technology-specific capture prices or sensitivity cases, because the current fixed-output, fixed-price setup treats every MWh as equally valuable regardless of generation profile.

## 2026-06-01 14:01 — Add onshore wind electricity NPV simulation

### User request

Add onshore wind power using the same style as the existing electricity technologies, with average full-load hours.

### Files changed (if needed)

- `src/electricity_parameters.py` — added onshore wind CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added onshore wind fuel-price mapping, simulation wrapper, and onshore wind to the default multi-technology simulation.
- `notebooks/deterministic_wind_onshore_npv.ipynb` — added deterministic onshore wind NPV notebook.
- `notebooks/plot_wind_onshore_npv.ipynb` — added onshore wind Monte Carlo plotting notebook.

### What was implemented

- Added onshore wind technology assumptions:
  - CAPEX: uniform `1,300-1,900 EUR/kW`.
  - Fixed OPEX: triangular `25.6 / 32 / 41.6 EUR/kW/year`.
  - Variable OPEX: triangular `5.6 / 7 / 9.1 EUR/MWh_e`.
  - Fuel consumption: fixed `0 MWh_th/MWh_e`.
  - Direct stack emissions: fixed `0 tCO2/MWh_e`.
  - Full-load hours: fixed average `(1,800 + 3,200) / 2 = 2,500 h/year`.
- Added `simulate_wind_onshore_npv`.
- Updated `simulate_electricity_technologies_npv` to include `wind_onshore` by default.
- Used the existing no-fuel price placeholder and technology-specific output key `no_fuel_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for onshore wind using the same structure as the offshore wind notebooks.

### Verification (if needed)

- Commands run:
  - `python3 -m json.tool notebooks/deterministic_wind_onshore_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_wind_onshore_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_wind_onshore_npv, simulate_electricity_technologies_npv; wind=simulate_wind_onshore_npv(5, np.random.default_rng(42)); both=simulate_electricity_technologies_npv(5, rng=np.random.default_rng(42)); print(wind["run_id"].tolist()); print(wind["full_load_hours_per_year"].tolist()); print(wind["fuel_consumption_mwh_th_per_mwh_e"].tolist()); print(wind["no_fuel_price_eur_per_mwh_th"].tolist()); print(wind["emissions_tco2_per_mwh_e"].tolist()); print(round(float(wind["capacity_mw"][0]), 6)); print(both.keys()); print(np.array_equal(both["hard_coal"]["run_id"], both["wind_onshore"]["run_id"]))'`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_electricity_technology_npv, simulate_electricity_technologies_npv; techs = ("hard_coal", "ccgt", "nuclear", "wind_offshore", "wind_onshore");\nfor tech in techs:\n    r = simulate_electricity_technology_npv(tech, 20000, np.random.default_rng(42)); checks = {"capacity": np.allclose(r["capacity_mw"], r["annual_output_mwh"] / r["full_load_hours_per_year"]), "fuel": np.allclose(r["annual_fuel_cost_eur"], r["annual_output_mwh"] * r["fuel_consumption_mwh_th_per_mwh_e"] * r["fuel_price_eur_per_mwh_th"]), "emissions": np.allclose(r["annual_emissions_cost_eur"], r["annual_output_mwh"] * r["emissions_tco2_per_mwh_e"] * r["carbon_price_eur_per_t"]), "npv_per_mwh": np.allclose(r["npv_eur_per_mwh"], r["npv_eur"] / r["lifetime_output_mwh"])}; print(tech, checks, round(float(np.mean(r["npv_eur"])/1e6), 3), round(float(np.mean(r["npv_eur_per_mwh"])), 3))\nboth = simulate_electricity_technologies_npv(100, rng=np.random.default_rng(123)); print(tuple(both.keys())); print(all(np.array_equal(both["hard_coal"]["run_id"], both[t]["run_id"]) for t in techs))'`
- Result:
  - Passed.
  - Onshore wind simulation returned fixed `2,500 h/year`, zero fuel consumption, zero fuel price, and zero direct emissions.
  - Onshore wind normalized capacity for `1,000,000 MWh/year` is `400 MW`.
  - Deterministic onshore wind notebook execution returned `152.815628 million EUR` and `6.112625 EUR/MWh` with the current assumptions.
  - All notebooks are valid JSON.
  - Capacity, fuel cost, emissions cost, and NPV-per-MWh relationships passed for hard coal, CCGT, nuclear, offshore wind, and onshore wind.
  - Multi-technology results now include `hard_coal`, `ccgt`, `nuclear`, `wind_offshore`, and `wind_onshore` with aligned run IDs.
- Notes:
  - Running the deterministic notebook emitted sandbox-related PyArrow `sysctlbyname` warnings from pandas, but execution completed successfully.

### Reproducibility notes

- This adds onshore wind as a new electricity technology and changes the default multi-technology simulation output by including onshore wind.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags remain:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.

### Next suggested step

Compare offshore and onshore wind results under capture-price or FLH sensitivity assumptions, because fixed output and uniform CAPEX make wind NPV distributions look mechanically uniform.

## 2026-06-01 13:51 — Add offshore wind electricity NPV simulation

### User request

Add offshore wind power using the same approach as the existing electricity technologies: average full-load hours, technology parameter distributions, matching notebooks, and a full sanity/logic check afterward.

### Files changed (if needed)

- `src/general_parameters.py` — added a fixed zero fuel-price placeholder for non-fuel electricity technologies.
- `src/electricity_parameters.py` — added offshore wind CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added offshore wind fuel-price mapping, simulation wrapper, and offshore wind to the default multi-technology simulation.
- `notebooks/deterministic_wind_offshore_npv.ipynb` — added deterministic offshore wind NPV notebook.
- `notebooks/plot_wind_offshore_npv.ipynb` — added offshore wind Monte Carlo plotting notebook.

### What was implemented

- Added `NO_FUEL_PRICE_EUR_PER_MWH_TH` as a fixed zero fuel-price placeholder.
- Added offshore wind technology assumptions:
  - CAPEX: uniform `2,200-3,400 EUR/kW`.
  - Fixed OPEX: triangular `31.2 / 39 / 50.7 EUR/kW/year`.
  - Variable OPEX: triangular `6.4 / 8 / 10.4 EUR/MWh_e`.
  - Fuel consumption: fixed `0 MWh_th/MWh_e`.
  - Direct stack emissions: fixed `0 tCO2/MWh_e`.
  - Full-load hours: fixed average `(3,200 + 4,500) / 2 = 3,850 h/year`.
- Added `simulate_wind_offshore_npv`.
- Updated `simulate_electricity_technologies_npv` to include `wind_offshore` by default.
- Added technology-specific no-fuel output as `no_fuel_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for offshore wind using the same structure as the existing electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `python3 -m json.tool notebooks/deterministic_wind_offshore_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_wind_offshore_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_wind_offshore_npv, simulate_electricity_technologies_npv; wind=simulate_wind_offshore_npv(5, np.random.default_rng(42)); both=simulate_electricity_technologies_npv(5, rng=np.random.default_rng(42)); print(wind["run_id"].tolist()); print(wind["full_load_hours_per_year"].tolist()); print(wind["fuel_consumption_mwh_th_per_mwh_e"].tolist()); print(wind["no_fuel_price_eur_per_mwh_th"].tolist()); print(wind["emissions_tco2_per_mwh_e"].tolist()); print(round(float(wind["capacity_mw"][0]), 6)); print(both.keys()); print(np.array_equal(both["hard_coal"]["run_id"], both["wind_offshore"]["run_id"]))'`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_wind_offshore_npv; r = simulate_wind_offshore_npv(10000, np.random.default_rng(42)); print(np.allclose(r["annual_fuel_cost_eur"], 0.0)); print(np.allclose(r["annual_emissions_cost_eur"], 0.0)); print(np.allclose(r["npv_eur_per_mwh"], r["npv_eur"] / r["lifetime_output_mwh"]))'`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_electricity_technology_npv, simulate_electricity_technologies_npv; techs = ("hard_coal", "ccgt", "nuclear", "wind_offshore");\nfor tech in techs:\n    r = simulate_electricity_technology_npv(tech, 20000, np.random.default_rng(42)); print(tech, np.allclose(r["capacity_mw"], r["annual_output_mwh"] / r["full_load_hours_per_year"]), np.allclose(r["annual_fuel_cost_eur"], r["annual_output_mwh"] * r["fuel_consumption_mwh_th_per_mwh_e"] * r["fuel_price_eur_per_mwh_th"]), np.allclose(r["annual_emissions_cost_eur"], r["annual_output_mwh"] * r["emissions_tco2_per_mwh_e"] * r["carbon_price_eur_per_t"]), np.allclose(r["npv_eur_per_mwh"], r["npv_eur"] / r["lifetime_output_mwh"]))\nboth = simulate_electricity_technologies_npv(100, rng=np.random.default_rng(123)); print(tuple(both.keys())); print(all(np.array_equal(both["hard_coal"]["run_id"], both[t]["run_id"]) for t in techs))'`
- Result:
  - Passed.
  - Offshore wind simulation returned fixed `3,850 h/year`, zero fuel consumption, zero fuel price, and zero direct emissions.
  - Offshore wind normalized capacity for `1,000,000 MWh/year` is `259.740260 MW`.
  - Deterministic offshore wind notebook execution returned `83.371163 million EUR` and `3.334847 EUR/MWh` with the current assumptions.
  - All notebooks are valid JSON.
  - Capacity, fuel cost, emissions cost, and NPV-per-MWh relationships passed for hard coal, CCGT, nuclear, and offshore wind.
  - Multi-technology results now include `hard_coal`, `ccgt`, `nuclear`, and `wind_offshore` with aligned run IDs.

### Reproducibility notes

- This adds offshore wind as a new electricity technology and changes the default multi-technology simulation output by including offshore wind.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.

### Next suggested step

Decide whether electricity lifetimes, discount rates, and revenue prices should become technology-specific before using the NPV distributions as final thesis results.

## 2026-06-01 11:07 — Add nuclear electricity NPV simulation

### User request

Add nuclear as the next electricity technology using the same approach as hard coal and CCGT. Use average full-load hours and add a fixed nuclear fuel (uranium) cost of `8 EUR/MWh_th` to the general parameters.

### Files changed (if needed)

- `src/general_parameters.py` — added fixed nuclear fuel price for uranium.
- `src/electricity_parameters.py` — added nuclear CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added nuclear fuel-price mapping, support for fixed technology parameters in sampled inputs, a nuclear simulation wrapper, and nuclear in the default multi-technology simulation.
- `notebooks/deterministic_nuclear_npv.ipynb` — added deterministic nuclear NPV notebook.
- `notebooks/plot_nuclear_npv.ipynb` — added nuclear Monte Carlo plotting notebook.

### What was implemented

- Added `NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH` as a fixed parameter with value `8 EUR/MWh_th`.
- Added nuclear technology assumptions:
  - CAPEX: uniform `6,000-16,000 EUR/kW`.
  - Fixed OPEX: triangular `80 / 100 / 130 EUR/kW/year`.
  - Variable OPEX: triangular `5.6 / 7 / 9.1 EUR/MWh_e`.
  - Fuel consumption: triangular `2.70 / 2.85 / 3.03 MWh_th/MWh_e`.
  - Direct stack emissions: fixed `0 tCO2/MWh_e`.
  - Full-load hours: fixed average `(4,300 + 6,300) / 2 = 5,300 h/year`.
- Updated the electricity model to sample fixed parameters and stochastic distributions through the same helper.
- Added `simulate_nuclear_npv`.
- Updated `simulate_electricity_technologies_npv` to include `nuclear` by default alongside `hard_coal` and `ccgt`.
- Added technology-specific nuclear fuel output as `uranium_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for nuclear using the same structure as the existing electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `python3 -m json.tool notebooks/deterministic_nuclear_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_nuclear_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_nuclear_npv, simulate_electricity_technologies_npv; nuclear=simulate_nuclear_npv(5, np.random.default_rng(42)); both=simulate_electricity_technologies_npv(5, rng=np.random.default_rng(42)); print(nuclear["run_id"].tolist()); print(nuclear["full_load_hours_per_year"].tolist()); print(nuclear["uranium_price_eur_per_mwh_th"].tolist()); print(nuclear["emissions_tco2_per_mwh_e"].tolist()); print(round(float(nuclear["capacity_mw"][0]), 6)); print(both.keys()); print(np.array_equal(both["hard_coal"]["run_id"], both["nuclear"]["run_id"]))'`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_nuclear_npv; r = simulate_nuclear_npv(10000, np.random.default_rng(42)); print(np.allclose(r["annual_fuel_cost_eur"], r["annual_output_mwh"] * r["fuel_consumption_mwh_th_per_mwh_e"] * r["fuel_price_eur_per_mwh_th"])); print(np.allclose(r["annual_emissions_cost_eur"], 0.0)); print(np.allclose(r["npv_eur_per_mwh"], r["npv_eur"] / r["lifetime_output_mwh"]))'`
- Result:
  - Passed.
  - Nuclear simulation returned fixed `5,300 h/year`, fixed uranium price `8 EUR/MWh_th`, and fixed direct emissions of `0`.
  - Nuclear normalized capacity for `1,000,000 MWh/year` is `188.679245 MW`.
  - Multi-technology results now include `hard_coal`, `ccgt`, and `nuclear` with aligned run IDs.
  - Nuclear fuel cost, emissions cost, and NPV-per-MWh relationships passed the arithmetic checks.
  - Deterministic nuclear notebook execution returned `-1,590.814704 million EUR` and `-63.632588 EUR/MWh` with the current `80 EUR/tCO2` and `94.07 EUR/MWh` assumptions.
- Notes:
  - Running the deterministic notebook emitted sandbox-related PyArrow `sysctlbyname` warnings from pandas, but execution completed successfully.

### Reproducibility notes

- This adds nuclear as a new electricity technology and changes the default multi-technology simulation output by including nuclear.
- No generated result files, figures, reports, or PDFs were written.
- Existing hard coal and CCGT interfaces are preserved.

### Next suggested step

Run the nuclear plotting notebook and compare nuclear, CCGT, and hard coal under the aligned multi-technology runs.

## 2026-06-01 10:22 — Use average CCGT full-load hours

### User request

Use the average full-load-hours value for CCGT, as done for hard coal, instead of sampling CCGT full-load hours from a distribution.

### Files changed (if needed)

- `src/electricity_parameters.py` — changed CCGT full-load hours from a uniform distribution over `3,000-6,300 h/year` to a fixed average value of `4,650 h/year`.

### What was implemented

- Replaced `CCGT_FULL_LOAD_HOURS_DISTRIBUTION` with `CCGT_FULL_LOAD_HOURS`.
- Set the fixed CCGT full-load-hours assumption to `(3,000 + 6,300) / 2 = 4,650 h/year`.
- Updated the electricity technology fixed-parameter mapping so CCGT full-load hours are handled like hard coal full-load hours.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_ccgt_npv, simulate_electricity_technologies_npv; ccgt=simulate_ccgt_npv(5, np.random.default_rng(42)); both=simulate_electricity_technologies_npv(5, rng=np.random.default_rng(42)); print(ccgt["full_load_hours_per_year"].tolist()); print(round(float(ccgt["capacity_mw"][0]), 6)); print(np.array_equal(both["hard_coal"]["run_id"], both["ccgt"]["run_id"]))'`
- Result:
  - Passed.
  - CCGT full-load hours returned `[4650.0, 4650.0, 4650.0, 4650.0, 4650.0]`.
  - The normalized CCGT capacity for `1,000,000 MWh/year` is `215.053763 MW`.
  - Multi-technology `run_id` arrays remain aligned.

### Reproducibility notes

- This changes the CCGT capacity and fixed OPEX calculation relative to the immediately previous CCGT implementation because FLH is no longer sampled.
- No generated result files, figures, reports, or PDFs were changed.

### Next suggested step

Rerun the CCGT and multi-technology summaries so any reported CCGT capacity or NPV values use fixed average full-load hours.

## 2026-06-01 10:20 — Add CCGT electricity NPV simulation

### User request

Add combined-cycle gas turbine (CCGT) as the next electricity technology using the same distribution rules as hard coal: triangular distributions where the source table gives a base value and uniform distributions where no base value is given. Also allow technologies to be sampled over aligned Monte Carlo runs.

### Files changed (if needed)

- `src/electricity_parameters.py` — added CCGT CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added a generic electricity-technology NPV simulation helper, CCGT simulation wrapper, and multi-technology aligned-run simulation wrapper.

### What was implemented

- Added CCGT technology assumptions:
  - CAPEX: uniform `900-1,300 EUR/kW`.
  - Fixed OPEX: triangular `16 / 20 / 26 EUR/kW/year`.
  - Variable OPEX: triangular `4 / 5 / 6.5 EUR/MWh_e`.
  - Fuel consumption: triangular `1.61 / 1.66 / 1.72 MWh_th/MWh_e`.
  - Direct emissions: triangular `0.326 / 0.337 / 0.348 tCO2/MWh_e`.
  - Full-load hours: uniform `3,000-6,300 h/year` because no base value was provided.
- Added `simulate_electricity_technology_npv` to share the NPV calculation across electricity technologies.
- Kept `simulate_hard_coal_npv` as a backwards-compatible wrapper around the generic helper.
- Added `simulate_ccgt_npv` for CCGT-only simulations.
- Added `simulate_electricity_technologies_npv`, returning results by technology with the same `run_id` sequence for each technology.
- Added a generic `fuel_price_eur_per_mwh_th` output and technology-specific fuel-price aliases:
  - hard coal keeps `coal_price_eur_per_mwh_th`.
  - CCGT adds `gas_price_eur_per_mwh_th`.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_hard_coal_npv, simulate_ccgt_npv, simulate_electricity_technologies_npv; rng=np.random.default_rng(42); hard=simulate_hard_coal_npv(5, rng); ccgt=simulate_ccgt_npv(5, rng); both=simulate_electricity_technologies_npv(5, rng=np.random.default_rng(42)); print(hard["run_id"].tolist(), round(float(hard["capacity_mw"][0]), 6), "coal_price_eur_per_mwh_th" in hard); print(ccgt["run_id"].tolist(), round(float(ccgt["full_load_hours_per_year"].min()), 3), round(float(ccgt["full_load_hours_per_year"].max()), 3), "gas_price_eur_per_mwh_th" in ccgt); print(both.keys()); print(np.array_equal(both["hard_coal"]["run_id"], both["ccgt"]["run_id"]))'`
- Result:
  - Passed.
  - Source files compiled successfully.
  - Hard coal retained its expected `243.902439 MW` capacity for the fixed `4,100 h/year` assumption.
  - CCGT sampled full-load hours within the requested range and returned the gas-price alias.
  - The multi-technology wrapper returned `hard_coal` and `ccgt` results with aligned `run_id` arrays.

### Reproducibility notes

- This adds CCGT as a new electricity-technology option but does not generate result files, figures, reports, or PDFs.
- Existing hard coal notebooks should continue to run because `simulate_hard_coal_npv` and `coal_price_eur_per_mwh_th` are preserved.
- The worktree already contained the user change setting the carbon price to `80 EUR/tCO2`; this change was preserved.

### Next suggested step

Run a CCGT notebook or summary script and compare CCGT NPV against hard coal under the same run IDs.

## 2026-05-26 17:05 — Clarify scaled beta notebook rerun

### User request

Fix the fuel-price plotting notebook error where an open notebook session still referenced the old triangular plotting function and `.mode` attribute after market prices were changed to scaled beta distributions.

### Files changed (if needed)

- `notebooks/plot_fuel_price_distributions.ipynb` — added a note to restart the kernel and rerun all cells so stale triangular plotting functions are cleared from memory.

### What was implemented

- Confirmed the notebook on disk already uses `sample_scaled_beta`, `scaled_beta_pdf`, and `distribution.mean`.
- Confirmed there are no remaining references to `triangular_pdf`, `distribution.mode`, `sample_triangular`, `Continuous triangular`, or `Most likely` in the notebook.
- Added an explicit top-of-notebook note explaining that stale in-memory notebook cells require a kernel restart and full rerun.

### Verification (if needed)

- Commands run:
  - `python3 -m json.tool notebooks/plot_fuel_price_distributions.ipynb`
  - `rg -n "triangular_pdf|distribution.mode|sample_triangular|Continuous triangular|Most likely" notebooks/plot_fuel_price_distributions.ipynb`
- Result:
  - Passed.
  - Notebook JSON is valid.
  - The search returned no stale triangular plotting references.

### Reproducibility notes

- No model assumptions, simulation outputs, figures, reports, or PDFs were changed.
- This only clarifies the notebook rerun procedure after the scaled beta distribution update.

### Next suggested step

Restart the notebook kernel and run all cells in `plot_fuel_price_distributions.ipynb`.

## 2026-05-26 16:16 — Preserve market-price means with scaled beta distributions

### User request

Replace triangular distributions for coal, gas, and electricity market prices with scaled beta distributions because the middle source-table values are arithmetic means, not true modes. Add beta sampling support and update affected notebooks.

### Files changed (if needed)

- `src/distributions.py` — added a scaled beta distribution datatype, constructor, and sampling helper.
- `src/general_parameters.py` — replaced gas, coal, and electricity price triangular distributions with mean-preserving scaled beta distributions.
- `src/electricity_model.py` — updated hard coal NPV sampling to use scaled beta sampling for coal price.
- `notebooks/plot_fuel_price_distributions.ipynb` — updated the fuel-price visualization notebook for scaled beta sampling and PDFs.
- `notebooks/deterministic_hard_coal_npv.ipynb` — updated deterministic coal price selection to use the market-price mean.
- `notebooks/plot_hard_coal_npv.ipynb` — cleared stale outputs so the notebook reruns against the updated model assumptions.

### What was implemented

- Added `ScaledBetaDistribution` with minimum, mean, maximum, alpha, beta, unit, and description.
- Added `create_scaled_beta_distribution`, using:
  - `mu = (mean - minimum) / (maximum - minimum)`
  - `k_min = max(1 / mu, 1 / (1 - mu))`
  - `k = 2 * k_min`
  - `alpha = mu * k`
  - `beta = (1 - mu) * k`
- Added `sample_scaled_beta`, sampling from NumPy beta and scaling samples to the parameter interval.
- Replaced gas, coal, and electricity market-price distributions with scaled beta distributions preserving their source-table means.
- Kept hard coal technology parameters as triangular distributions where the provided middle value is a base value.
- Updated the hard coal NPV simulation so coal price is sampled using the scaled beta helper.
- Updated notebooks to avoid stale triangular terminology and outputs.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_model.py src/electricity_parameters.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from general_parameters import GAS_PRICE_DISTRIBUTION, COAL_PRICE_DISTRIBUTION, ELECTRICITY_PRICE_DISTRIBUTION; dists=[GAS_PRICE_DISTRIBUTION, COAL_PRICE_DISTRIBUTION, ELECTRICITY_PRICE_DISTRIBUTION];\nfor d in dists:\n    theoretical=d.minimum+(d.alpha/(d.alpha+d.beta))*(d.maximum-d.minimum)\n    print(d.unit, round(d.alpha, 6), round(d.beta, 6), round(theoretical, 6), d.mean)'`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from distributions import sample_scaled_beta; from general_parameters import COAL_PRICE_DISTRIBUTION; from electricity_model import simulate_hard_coal_npv; rng=np.random.default_rng(42); samples=sample_scaled_beta(COAL_PRICE_DISTRIBUTION, 200000, rng); result=simulate_hard_coal_npv(10, np.random.default_rng(42)); print(round(float(samples.mean()), 3), COAL_PRICE_DISTRIBUTION.mean); print(result["coal_price_eur_per_mwh_th"].shape, result["npv_eur"].shape)'`
  - `python3 -m json.tool notebooks/plot_fuel_price_distributions.ipynb`
  - `python3 -m json.tool notebooks/plot_hard_coal_npv.ipynb`
  - `python3 -m json.tool notebooks/deterministic_hard_coal_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'from electricity_model import calculate_capacity_kw, calculate_capacity_mw, calculate_level_cash_flow_present_value_factor; from electricity_parameters import ANNUAL_ELECTRICITY_OUTPUT_MWH, HARD_COAL_CAPEX_DISTRIBUTION, HARD_COAL_EMISSIONS_DISTRIBUTION, HARD_COAL_FIXED_OPEX_DISTRIBUTION, HARD_COAL_FUEL_CONSUMPTION_DISTRIBUTION, HARD_COAL_FULL_LOAD_HOURS, HARD_COAL_VARIABLE_OPEX_DISTRIBUTION, LIFETIME_ELECTRICITY_YEARS, RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH; from general_parameters import CARBON_PRICE_EUR_PER_T, COAL_PRICE_DISTRIBUTION, INTEREST_RATE; output=ANNUAL_ELECTRICITY_OUTPUT_MWH.value; flh=HARD_COAL_FULL_LOAD_HOURS.value; cap_kw=calculate_capacity_kw(output, flh); capex=(HARD_COAL_CAPEX_DISTRIBUTION.lower_bound+HARD_COAL_CAPEX_DISTRIBUTION.upper_bound)/2; revenue=output*RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value; fixed=cap_kw*HARD_COAL_FIXED_OPEX_DISTRIBUTION.mode; variable=output*HARD_COAL_VARIABLE_OPEX_DISTRIBUTION.mode; fuel=output*HARD_COAL_FUEL_CONSUMPTION_DISTRIBUTION.mode*COAL_PRICE_DISTRIBUTION.mean; emissions=output*HARD_COAL_EMISSIONS_DISTRIBUTION.mode*CARBON_PRICE_EUR_PER_T.value; net=revenue-fixed-variable-fuel-emissions; pvf=calculate_level_cash_flow_present_value_factor(int(LIFETIME_ELECTRICITY_YEARS.value), INTEREST_RATE.value); npv=-cap_kw*capex+net*pvf; print(round(calculate_capacity_mw(output, flh), 6), round(revenue/1e6, 3), round(net/1e6, 3), round(npv/1e6, 3))'`
- Result:
  - Passed.
  - Theoretical scaled beta means match the source-table means exactly for gas, coal, and electricity prices.
  - A 200,000-sample coal price smoke test returned a sample mean of 12.107 versus the target mean of 12.11.
  - The hard coal simulation returned the expected coal-price and NPV array shapes.
  - Notebook JSON validation passed.
  - The deterministic hard coal NPV check remains 26.442 million EUR.
- Notes:
  - `jupyter nbconvert --clear-output --inplace ...` was attempted but `jupyter` was not available on PATH, so notebook outputs were cleared with a small JSON rewrite instead.

### Reproducibility notes

- This changes the market-price uncertainty assumption for gas, coal, and electricity prices.
- Existing NPV distributions should be regenerated because sampled coal prices now preserve the source-table arithmetic mean rather than the former triangular-mode interpretation.
- No simulation result files, figures, reports, or PDFs were generated.

### Next suggested step

Rerun the hard coal NPV notebook and compare the new probabilistic mean/median with the deterministic base case.

## 2026-05-26 13:35 — Use fixed retail electricity price in coal NPV

### User request

Change the hard coal electricity NPV simulation so it does not sample electricity price and instead uses the fixed retail electricity price of 94.07 EUR/MWh.

### Files changed (if needed)

- `src/electricity_model.py` — replaced sampled electricity-price revenue with the fixed electricity retail price parameter.

### What was implemented

- Removed electricity price sampling from `simulate_hard_coal_npv`.
- Used `RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value` for annual revenue.
- Kept `electricity_price_eur_per_mwh` in the returned simulation result as a constant array so result tables still show the price assumption used in each run.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/electricity_model.py src/electricity_parameters.py src/general_parameters.py src/distributions.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_hard_coal_npv; r=simulate_hard_coal_npv(4, np.random.default_rng(42)); print(r["electricity_price_eur_per_mwh"]); print(r["annual_revenue_eur"]); print(np.allclose(r["annual_revenue_eur"], r["annual_output_mwh"] * 94.07))'`
- Result:
  - Passed.
  - The simulation returned 94.07 EUR/MWh for all checked runs and revenue matched annual output times 94.07.

### Reproducibility notes

- This changes the hard coal NPV revenue assumption from stochastic electricity prices to a fixed retail electricity price.
- No simulation outputs, plots, reports, or PDFs were generated.

### Next suggested step

Run a larger hard coal NPV sample and inspect how much of the remaining uncertainty comes from CAPEX, OPEX, coal price, fuel consumption, and emissions.

## 2026-05-26 13:33 — Implement hard coal electricity NPV simulation

### User request

Implement the Monte Carlo approach for an electricity-sector NPV distribution, currently only for a hard coal electricity plant, including CAPEX, OPEX, fuel cost, emissions cost, revenue, lifetime, and interest rate.

### Files changed (if needed)

- `src/electricity_model.py` — added reusable NPV helpers and a hard coal Monte Carlo NPV simulation function.

### What was implemented

- Added `calculate_level_cash_flow_present_value_factor` for discounting constant annual cash flows.
- Added `calculate_npv`, using initial CAPEX and discounted annual net cash flow.
- Added `simulate_hard_coal_npv`, which samples hard coal technology parameters, coal price, and electricity price in paired Monte Carlo runs.
- The hard coal annual net cash flow is calculated as:
  - electricity revenue
  - fixed OPEX
  - variable OPEX
  - coal fuel cost
  - emissions cost
- The NPV is calculated as:
  - negative initial CAPEX plus discounted annual net cash flow over the electricity-sector lifetime.
- Returned the NPV distribution together with sampled input values, capacity, annual cost components, annual revenue, and annual net cash flow for each run.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/electricity_model.py src/electricity_parameters.py src/general_parameters.py src/distributions.py`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import simulate_hard_coal_npv; result = simulate_hard_coal_npv(5, np.random.default_rng(42)); print(sorted(result.keys())[-3:]); print(result["npv_eur"].shape, round(float(result["capacity_mw"][0]), 6)); print(round(float(result["npv_eur"].mean()), 2))'`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -c 'import numpy as np; from electricity_model import calculate_level_cash_flow_present_value_factor, calculate_npv; capex=np.array([100.0]); cash=np.array([10.0]); print(round(calculate_level_cash_flow_present_value_factor(2, 0.0), 6), round(float(calculate_npv(capex, cash, 2, 0.0)[0]), 6))'`
- Result:
  - Passed.
  - The hard coal simulation returned an NPV array with the expected shape and the expected normalized capacity of 243.902439 MW.
  - The zero-discount sanity check returned an NPV of -80.0 for 100 EUR initial CAPEX and two years of 10 EUR annual cash flow.

### Reproducibility notes

- This adds the first executable electricity-sector NPV simulation but does not write simulation results to disk.
- The simulation currently uses the existing fixed carbon price, fixed interest rate, fixed lifetime, hard coal technology distributions, coal price distribution, and electricity price distribution.
- Future technologies can be added by extending the same sampled-run structure rather than running separate unrelated Monte Carlo experiments.

### Next suggested step

Create a small script or notebook cell that runs `simulate_hard_coal_npv` for the desired number of runs and plots or summarizes the resulting NPV distribution.

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
