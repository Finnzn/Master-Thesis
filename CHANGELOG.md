## 2026-07-13 15:16 — Set scenario notebook to specific NPV with shared panel scales

### User request

Update the deterministic scenario analysis so it again uses specific NPV, and
make the x-axis scales the same across the scenario panels for each sector.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — changed the default metric to
  specific NPV and added shared x-axis limits across scenario panels.
- `CHANGELOG.md` — documented the scenario notebook adjustment.

### What was implemented

- Set `NPV_METRIC = METRIC_SPECIFIC` in the notebook settings cell.
- Kept the existing option to switch back to `METRIC_TOTAL` if needed.
- Updated the plotting helper to calculate one symmetric x-axis range from all
  NPV values in the sector summary and apply it to both scenario panels.

### Verification (if needed)

- Commands run:
  - Notebook code-cell compile check for
    `notebooks/co2_discount_rate_scenarios.ipynb`.
  - `MPLBACKEND=Agg PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - Notebook code cells compiled successfully.
  - Direct notebook code execution confirmed the selected metric is `specific`.
  - The scenario variables remained electricity full-load hours/lifetime and
    cement CO2 price/discount rate.
- Notes:
  - The verification emitted expected Matplotlib Agg warnings because terminal
    execution used a non-interactive plotting backend.

### Reproducibility notes

- No model parameters, generated figures, raw data, or numerical outputs were
  changed.
- The shared x-axis scaling is applied at plot time and does not change the
  deterministic scenario values.

### Next suggested step

Rerun `notebooks/co2_discount_rate_scenarios.ipynb` interactively and inspect
that each sector's two scenario panels now use matching x-axis scales.

## 2026-07-13 14:55 — Update deterministic sector scenario analysis

### User request

Update the scenario analysis so electricity scenarios examine full-load hours
and lifetime, cement scenarios examine discount rate and carbon price, and all
scenario cases use deterministic base inputs instead of Monte Carlo simulation.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — replaced the Monte Carlo
  revaluation workflow with deterministic sector-specific scenarios.
- `CHANGELOG.md` — documented the scenario-analysis update.

### What was implemented

- Removed notebook imports and settings for Monte Carlo sample size, random
  seed, and cement retrofit BAU sampling mode.
- Loaded deterministic base inputs through the shared sensitivity-analysis
  helpers.
- Added electricity scenario panels for full-load hours and lifetime using
  editable low / medium / high multipliers around each technology's deterministic
  base value.
- Kept cement scenario panels for carbon price and discount rate using editable
  absolute low / medium / high values.
- Updated tables and plot labels from Monte Carlo means and percentiles to
  deterministic NPV and change from the medium/base case.

### Verification (if needed)

- Commands run:
  - Notebook code-cell compile check for
    `notebooks/co2_discount_rate_scenarios.ipynb`.
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --to notebook --execute notebooks/co2_discount_rate_scenarios.ipynb --stdout >/tmp/co2_discount_rate_scenarios.executed.ipynb`
  - Deterministic calculation-only scenario check in the thesis conda
    environment.
- Result:
  - Notebook code cells compiled successfully.
  - The notebook executed successfully with nbconvert.
  - The deterministic check produced 54 electricity rows for full-load hours and
    lifetime, and 54 cement rows for CO2 price and discount rate.
- Notes:
  - A separate direct Python execution check was interrupted because macOS
    matplotlib blocks on `plt.show()` outside Jupyter; this does not affect
    notebook execution.

### Reproducibility notes

- No raw data, generated figures, model parameters, or Monte Carlo outputs were
  changed.
- Electricity low/high scenario multipliers are explicit notebook assumptions
  and can be edited in the settings cell.
- Cement carbon-price and discount-rate scenarios remain explicit notebook
  assumptions and do not modify `src/general_parameters.py`.

### Next suggested step

Run `notebooks/co2_discount_rate_scenarios.ipynb` interactively and inspect the
new deterministic electricity and cement scenario plots.

## 2026-07-13 13:38 — Group duplicated sensitivity heatmap drivers

### User request

Combine sensitivity heatmap variables that carry the same linear information,
specifically fuel use/fuel price, electricity use/electricity price, and
emissions/carbon price.

### Files changed (if needed)

- `src/sensitivity_deep_dive.py` — grouped duplicate linear drivers only in the
  heatmap display layer.
- `figures/2026-06-24-Sensitivity_Heatmap_Standardized_Cement.png` — regenerated
  with grouped Fuel, Electricity, and Emissions columns.
- `figures/2026-06-24-Sensitivity_Heatmap_Standardized_Electricity.png` —
  regenerated with grouped Fuel and Emissions columns.
- `CHANGELOG.md` — documented the heatmap update.

### What was implemented

- Added sector-specific heatmap parameter groups:
  Fuel, Electricity, and Emissions.
- Kept the underlying one-at-a-time sensitivity table unchanged, so the raw
  calculation still evaluates each original model input separately.
- Collapsed grouped heatmap cells using the maximum relative impact within each
  technology and group, which preserves the shared signal from linear product
  terms.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/sensitivity_deep_dive.py`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - The source file compiled successfully.
  - The grouped cement and electricity heatmaps regenerated successfully.
  - A sanity check confirmed grouped heatmap labels for cement and electricity.
- Notes:
  - The default system `python3` lacks `matplotlib`, so figure regeneration used
    the thesis conda environment.

### Reproducibility notes

- No model parameters or scientific assumptions were changed.
- Regenerate the full current dated outputs with:
  `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python src/sensitivity_deep_dive.py`

### Next suggested step

Inspect the regenerated heatmap PNGs in `figures/` and confirm the grouped
columns match the intended thesis presentation.

## 2026-07-10 14:16 — Remove Excel plot export workflow

### User request

Delete all Excel plot related things because they are no longer needed.

### Files changed (if needed)

- `src/export_npv_chart_workbook.py` — removed the Excel workbook exporter.
- `Excel plots/` — deleted the generated Excel plot workbook folder.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Removed the Excel-specific source module.
- Removed the generated Excel workbook artifacts.
- Confirmed no active Excel plot/export references remain outside historical `CHANGELOG.md` entries.

### Verification (if needed)

- Commands run:
  - `find . -maxdepth 3 \( -iname '*excel*' -o -iname '*NPV_chart_data*' \) -print`
  - `rg -n "Excel plots|export_npv_chart_workbook|NPV_chart_data|editable Excel|Excel workbook|Cement specific ranking|Electricity specific ranking" . --glob '!CHANGELOG.md'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m compileall -q src`
- Result:
  - Passed.
- Notes:
  - Previous changelog entries mentioning Excel were intentionally left unchanged to preserve project history.

### Reproducibility notes

- The standard PNG figure workflow remains unchanged.
- The Excel workbook export workflow is no longer available.

## 2026-07-10 13:58 — Extend cement specific NPV axis to show full whisker

### User request

Change the cement specific NPV charts so the x-axis goes down to `-300 EUR/t`, because the uncertainty whisker is not shown correctly at `-250 EUR/t`. Do not change notebooks.

### Files changed (if needed)

- `src/npv_summary_plots.py` — changed the fixed cement specific lower axis bound from `-250` to `-300 EUR/t` when the electrolysis uncertainty whisker requires the wider range.
- `figures/2026-07-10-Mean_NPV_per_t_Cement.png` — regenerated with the wider cement specific axis.
- `figures/2026-07-10-Deterministic_NPV_per_t_Cement.png` — regenerated with the same cement specific axis.
- `Excel plots/2026-07-10-NPV_chart_data.xlsx` — regenerated so the editable `Cement EUR per t` sheet uses `-300` to `+50` with `50` as the major unit.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Cement specific Monte Carlo mean and deterministic charts now share an x-axis from `-300` to `+50 EUR/t`.
- The Excel workbook now records:
  - minimum: `-300`
  - maximum: `50`
  - major unit: `50`
  - ticks: `-300, -250, -200, -150, -100, -50, 0, 50`
- No notebooks were changed.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m compileall -q src`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/t`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`
  - `openpyxl` workbook validation for the `Cement EUR per t` axis values.
- Result:
  - Passed.
- Notes:
  - Visual inspection confirmed that the cement electrolysis uncertainty whisker is visible within the `-300` to `+50 EUR/t` axis.

### Reproducibility notes

- Regenerate the cement specific PNGs with:
  - `PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/t`
- Regenerate the Excel workbook with:
  - `PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`

## 2026-07-10 13:54 — Apply fixed midterm NPV axes and Excel ranking exports

### User request

Use the thesis workflow skill. Apply explicit x-axis bounds for the midterm NPV plots: electricity specific charts from `-150` to `+50 EUR/MWh`, cement specific charts from `-250` or `-200` to `+50 EUR/t` depending on the electrolysis uncertainty whisker, cement total charts with `200`-unit scale guidance and visible `+2000 MEUR`, and electricity total charts with `1000`-unit scale guidance and visible `+1000 MEUR`. Use the same scaling for deterministic charts. Check whether notebooks use the shared plotting before changing them. Create a separate Excel plot folder and include the specific ranking plots in the Excel workbook, without the ranking matrix if needed.

### Files changed (if needed)

- `src/npv_summary_plots.py` — added fixed presentation axis configuration for the NPV bar-chart pairs.
- `src/cement/cement_npv_summary_figures.py` — applied the fixed cement axes to both Monte Carlo mean and deterministic figure-only exports.
- `src/electricity/electricity_npv_summary_figures.py` — applied the fixed electricity axes to both Monte Carlo mean and deterministic figure-only exports.
- `src/export_npv_chart_workbook.py` — exports the editable Excel workbook to `Excel plots/`, records axis limits/units, and adds specific ranking chart sheets.
- `Excel plots/2026-07-10-NPV_chart_data.xlsx` — regenerated workbook with four NPV chart sheets plus two specific ranking sheets.
- `figures/2026-07-10-*.png` — regenerated eight standard, non-resized NPV bar charts.
- `Resized plots/` — removed the obsolete resized-output workflow from disk.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Fixed electricity specific axes at `-150` to `+50 EUR/MWh` for both Monte Carlo mean and deterministic charts.
- Fixed cement specific axes at `-250` to `+50 EUR/t` for both Monte Carlo mean and deterministic charts because the electrolysis uncertainty whisker falls below `-200`.
- Fixed total cement axes to show through `+2000 MEUR`; the workbook records `200` as the suggested Excel major unit, while PNG labels use readable `1000` intervals to avoid overlap.
- Fixed total electricity axes to show through `+1000 MEUR` with `1000`-unit ticks.
- Added native Excel ranking sheets for specific NPV:
  - `Cement specific ranking`
  - `Electricity specific ranking`
- Omitted the ranking matrix from the Excel ranking sheets, keeping average rank, probability rank 1, and probability top 3.
- Checked notebooks before editing:
  - `notebooks/cement/cement_summary.ipynb` and `notebooks/electricity/electricity_summary.ipynb` import the shared plotting helper.
  - The individual technology notebooks use local `matplotlib` plotting cells, so no notebook-local plotting was changed.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m compileall -q src`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale MEUR`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/t`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m electricity.electricity_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale MEUR`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m electricity.electricity_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/MWh`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`
  - Workbook validation with `openpyxl` for sheet names, axis limits, major units, and chart counts.
- Result:
  - Passed.
- Notes:
  - Workbook sheets are `Cement MEUR`, `Cement EUR per t`, `Electricity MEUR`, `Electricity EUR per MWh`, `Cement specific ranking`, and `Electricity specific ranking`.
  - Visual inspection confirmed the specific charts and the cement total chart use the requested bounds without the previous unreadable dense tick labels.

### Reproducibility notes

- Regenerate the PNG figures with the sector figure CLIs using `--no-data --ranking-output none --kind all`.
- Regenerate the editable Excel workbook with:
  - `PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`
- Notebook-local plotting remains unchanged until explicitly approved.

## 2026-07-10 13:45 — Regenerate standard NPV plots and replace resized workflow with Excel chart workbook

### User request

Regenerate the non-resized deterministic and Monte Carlo mean NPV plots for both specific and non-specific NPV in both sectors, so the x-axis scales can be checked. Then scrap the resized-plot workflow because the resized images looked bad, and provide a way to resize/edit the figures more easily, preferably via PowerPoint or Excel-native plotting.

### Files changed (if needed)

- `src/npv_summary_plots.py` — added a reusable shared tick helper and kept shared x-axis limit/tick support for NPV bar charts.
- `src/cement/cement_npv_summary_figures.py` — changed the standard figure-only cement workflow so Monte Carlo mean and deterministic NPV figures share one x-axis range and tick set for each NPV scale.
- `src/electricity/electricity_npv_summary_figures.py` — changed the standard figure-only electricity workflow so Monte Carlo mean and deterministic NPV figures share one x-axis range and tick set for each NPV scale.
- `src/export_npv_chart_workbook.py` — added an Excel workbook exporter with source values and editable Excel bar charts.
- `figures/2026-07-10-*.png` — regenerated eight standard, non-resized NPV bar charts.
- `figures/2026-07-10-NPV_chart_data.xlsx` — added an Excel workbook with four sheets and two editable charts per sheet.
- `Resized plots/` — removed the previous resized-plot workflow and generated resized figures.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Regenerated these standard figures in `figures/`:
  - `2026-07-10-Mean_NPV_Cement.png`
  - `2026-07-10-Deterministic_NPV_Cement.png`
  - `2026-07-10-Mean_NPV_per_t_Cement.png`
  - `2026-07-10-Deterministic_NPV_per_t_Cement.png`
  - `2026-07-10-Mean_NPV_Electricity.png`
  - `2026-07-10-Deterministic_NPV_Electricity.png`
  - `2026-07-10-Mean_NPV_per_MWh_Electricity.png`
  - `2026-07-10-Deterministic_NPV_per_MWh_Electricity.png`
- For each sector and scale, the Monte Carlo mean and deterministic bar charts now use the same x-axis limits and tick positions.
- Created `figures/2026-07-10-NPV_chart_data.xlsx` with sheets:
  - `Cement MEUR`
  - `Cement EUR per t`
  - `Electricity MEUR`
  - `Electricity EUR per MWh`
- Each Excel sheet includes shared x-axis limits, Monte Carlo mean/median/P05/P95 values, deterministic values, and two editable native Excel bar charts.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m compileall -q src`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale MEUR`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m cement.cement_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/t`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m electricity.electricity_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale MEUR`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m electricity.electricity_npv_summary_figures --no-data --ranking-output none --kind all --npv-scale EUR/MWh`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/bin/python3.12 - <<'PY' ... load workbook and print sheet/chart counts ... PY`
- Result:
  - Passed.
- Notes:
  - The workbook validation found four sheets and two Excel charts per sheet.
  - Visual inspection confirmed the cement specific Monte Carlo and deterministic figures now use matching x-axis tick labels.

### Reproducibility notes

- Regenerate the standard PNGs with the sector figure CLIs using `--no-data --ranking-output none --kind all`.
- Regenerate the Excel chart workbook with:
  - `PYTHONPATH=src /opt/anaconda3/bin/python3.12 -m export_npv_chart_workbook`
- This is a plotting/export correction only; the NPV calculations, assumptions, random seed, and sample size are unchanged.

### Next suggested step

Use `figures/2026-07-10-NPV_chart_data.xlsx` to copy editable Excel charts into PowerPoint, then resize and format them natively in Office.

## 2026-07-10 13:37 — Share x-axis scales across deterministic and Monte Carlo NPV bars

### User request

Make the x-axis scale uniform for the deterministic NPV and Monte Carlo mean NPV bar charts. The scale should be uniform within each sector, but does not need to be uniform between cement and electricity.

### Files changed (if needed)

- `src/npv_summary_plots.py` — added reusable shared-axis-limit support and optional x-axis tick control to the mean/deterministic NPV bar-chart helper.
- `Resized plots/generate_resized_plots.py` — computes one sector-specific x-axis range from Monte Carlo percentile bounds plus deterministic values, then applies that same range and tick set to both bar charts for the sector.
- `Resized plots/*.png` — regenerated the PowerPoint-sized NPV bar-chart PNGs with shared sector scales.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Cement deterministic and Monte Carlo mean NPV bar charts now share the same `EUR/t` x-axis limits and tick labels.
- Electricity deterministic and Monte Carlo mean NPV bar charts now share the same `EUR/MWh` x-axis limits and tick labels.
- The shared ranges include the Monte Carlo `5th-95th` percentile whiskers and the deterministic values so neither plot silently clips relevant values.
- Tick labels were reduced to a readable common subset because the deterministic chart box is narrower and must still keep text at least `14 pt`.

### Verification (if needed)

- Commands run:
  - `python3 -m compileall -q src "Resized plots/generate_resized_plots.py"`
  - `"Resized plots/generate_resized_plots.sh"`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache /opt/anaconda3/bin/python3.12 - <<'PY' ... print shared cement/electricity axis limits ... PY`
- Result:
  - Passed.
- Notes:
  - Shared cement limits are approximately `-282.18` to `61.43 EUR/t`.
  - Shared electricity limits are approximately `-132.61` to `24.49 EUR/MWh`.
  - Visual inspection confirmed the deterministic and Monte Carlo bar charts now use matching sector tick labels without overlap.

### Reproducibility notes

- Regenerate the resized figures with:
  - `"Resized plots/generate_resized_plots.sh"`
- This is a plotting-scale correction only; the NPV calculations, assumptions, random seed, and sample size are unchanged.

### Next suggested step

Use each deterministic/Monte Carlo bar-chart pair together only within the same sector, since cement and electricity intentionally keep different units and scales.

## 2026-07-10 13:30 — Restore ranking annotations and add SVG ranking exports

### User request

Improve the PowerPoint-sized ranking plots because removing the descriptions after each ranking bar cut away too much information, and image quality was worse than desired.

### Files changed (if needed)

- `src/npv_summary_plots.py` — compacted ranking annotation text, added more annotation space for single-panel ranking plots, and preserved optional compact-ranking controls.
- `Resized plots/generate_resized_plots.py` — restored ranking annotations for the PowerPoint-sized ranking plots and exported ranking plots as both PNG and SVG.
- `Resized plots/*.png` and `Resized plots/*.svg` — regenerated the PowerPoint-sized ranking plots and refreshed the PNG outputs.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Restored the after-bar ranking descriptions using a compact format:
  - `avg ... | #1 ... | T3 ...`
- Kept the rank-frequency heatmap removed from the PowerPoint-sized ranking plots because it cannot fit at `26.04 x 13.74 cm` with 14 pt cell text without overlap.
- Added SVG ranking exports:
  - `2026-07-10-Average_NPV_Rank_per_t_Cement_14pt.svg`
  - `2026-07-10-Average_NPV_Rank_per_MWh_Electricity_14pt.svg`
- Kept PNG ranking exports for compatibility.

### Verification (if needed)

- Commands run:
  - `python3 -m compileall -q src "Resized plots/generate_resized_plots.py"`
  - `"Resized plots/generate_resized_plots.sh"`
  - `sips -g pixelWidth -g pixelHeight -g dpiWidth -g dpiHeight "Resized plots"/*.png`
  - `grep -n "<svg" "Resized plots/2026-07-10-Average_NPV_Rank_per_t_Cement_14pt.svg" "Resized plots/2026-07-10-Average_NPV_Rank_per_MWh_Electricity_14pt.svg"`
- Result:
  - Passed.
- Notes:
  - Visual inspection confirmed that the ranking annotations fit without clipping in the regenerated PNG previews.
  - The SVG ranking files report dimensions of `738 x 389.28 pt`, matching the requested `26.04 x 13.74 cm`.

### Reproducibility notes

- Regenerate all resized midterm figures with:
  - `"Resized plots/generate_resized_plots.sh"`
- Use the SVG ranking plots in PowerPoint when possible for sharper rendering.
- The underlying NPV calculations, ranking results, random seed, and sample size are unchanged.

### Next suggested step

Use the SVG files for the ranking slides and keep PNGs as fallback only if PowerPoint has trouble with SVG rendering.

## 2026-07-10 13:24 — Resize 14 pt midterm plots to PowerPoint dimensions

### User request

Regenerate the `Resized plots` figures so they insert into PowerPoint at the intended final dimensions without needing to shrink them. The requested sizes were:

- deterministic NPV bar charts: `13.92 cm` wide by `12.22 cm` high
- Monte Carlo NPV bar charts: `17.34 cm` wide by `12.22 cm` high
- ranking charts: `26.04 cm` wide by `13.74 cm` high

### Files changed (if needed)

- `src/npv_summary_plots.py` — added optional exact figure-size, DPI, tight-bounding-box, title/footer, legend, and compact-ranking controls while preserving the existing default plot behavior.
- `Resized plots/generate_resized_plots.py` — converted the requested centimeter dimensions to inches, saved the PowerPoint exports at `300 dpi`, disabled tight bounding boxes, removed internal titles/footers from the slide-sized figures, and used compact ranking charts for readability.
- `Resized plots/*.png` — regenerated the six specific 14 pt PowerPoint-sized figures.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Regenerated the deterministic bar charts at approximately `1644 x 1442 px` with `300 dpi`, matching `13.92 x 12.22 cm`.
- Regenerated the Monte Carlo bar charts at approximately `2048 x 1442 px` with `300 dpi`, matching `17.34 x 12.22 cm`.
- Regenerated the ranking charts at approximately `3075 x 1622 px` with `300 dpi`, matching `26.04 x 13.74 cm`.
- Kept all six figures as specific NPV outputs:
  - cement: `EUR/t`
  - electricity: `EUR/MWh`
- Simplified the PowerPoint ranking charts to average-rank bar charts only. The previous two-panel ranking plot with rank-frequency heatmap cell counts cannot fit into `26.04 x 13.74 cm` with all graph text at `14 pt` without severe label overlap.

### Verification (if needed)

- Commands run:
  - `python3 -m compileall -q src "Resized plots/generate_resized_plots.py"`
  - `"Resized plots/generate_resized_plots.sh"`
  - `sips -g pixelWidth -g pixelHeight -g dpiWidth -g dpiHeight "Resized plots"/*.png`
- Result:
  - Passed.
- Notes:
  - The regenerated PNGs report `300 dpi` metadata.
  - Visual inspection showed the compact ranking charts and bar charts fit at the requested dimensions without the earlier title/footer/heatmap overlap.

### Reproducibility notes

- Regenerate the PowerPoint-sized figures with:
  - `"Resized plots/generate_resized_plots.sh"`
- The generated files remain in `Resized plots/` and do not overwrite `figures/`.
- The underlying NPV calculations, assumptions, random seed, and sample size are unchanged.

### Next suggested step

Insert the PNGs into PowerPoint at their native size; add slide titles and any explanatory legend/caption as PowerPoint text boxes at `14 pt` or larger.

## 2026-07-10 12:44 — Add 14 pt specific-NPV midterm plots

### User request

Delete the obsolete presentation folder and references, then create a separate `Resized plots` folder for quickly regenerating the six midterm figures with all graph text at least 14 pt. The requested figures are the specific Monte Carlo NPV rankings for cement and electricity, plus Monte Carlo mean and deterministic bar charts for both sectors. The user clarified that the bar charts must also use specific NPV units.

### Files changed (if needed)

- `presentations/` — removed obsolete deck scripts, deck files, and copied presentation assets.
- `Resized plots/generate_resized_plots.py` — added a focused generator for the six 14 pt specific-NPV figures.
- `Resized plots/generate_resized_plots.sh` — added a convenience wrapper that uses Python 3.12 when available.
- `src/npv_summary_plots.py` — added optional plot font-size controls while preserving existing default plotting behavior.
- `src/electricity/electricity_npv_summary_figures.py` — updated one comment to remove presentation-specific wording.
- `README.md` and `docs/HANDOVER.md` — removed presentation-specific wording.
- `requirements.txt` — removed deck/PDF dependencies that were only needed by the deleted presentation workflow.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Generated six 14 pt midterm PNG figures in `Resized plots/`:
  - `2026-07-10-Average_NPV_Rank_per_t_Cement_14pt.png`
  - `2026-07-10-Average_NPV_Rank_per_MWh_Electricity_14pt.png`
  - `2026-07-10-Mean_NPV_per_t_Cement_14pt.png`
  - `2026-07-10-Deterministic_NPV_per_t_Cement_14pt.png`
  - `2026-07-10-Mean_NPV_per_MWh_Electricity_14pt.png`
  - `2026-07-10-Deterministic_NPV_per_MWh_Electricity_14pt.png`
- Kept chart content and model assumptions unchanged; only the output unit selection, file names, font sizes, and layout scale were adjusted for the midterm figures.
- Switched all four bar charts to specific NPV units after clarification:
  - cement: `EUR/t`
  - electricity: `EUR/MWh`
- Removed the initially generated total-NPV 14 pt bar-chart PNGs from `Resized plots/`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache /opt/anaconda3/bin/python3.12 "Resized plots/generate_resized_plots.py"`
  - `"Resized plots/generate_resized_plots.sh"`
  - `python3 -m compileall -q src "Resized plots/generate_resized_plots.py"`
  - `sips -g pixelWidth -g pixelHeight "Resized plots"/*.png`
  - `rg -n "presentation|Presentation|presentations|presnetation|python-pptx|pptx|pypdf" .`
- Result:
  - Passed.
- Notes:
  - The system `python3` is Python 3.9.6, which cannot import the project because the source uses Python 3.10+ type-union syntax. The generator wrapper therefore prefers `/opt/anaconda3/bin/python3.12` when available.
  - The six generated figures were visually inspected for obvious clipping, overlap, and layout issues after increasing text size.

### Reproducibility notes

- Regenerate the six midterm figures with:
  - `"Resized plots/generate_resized_plots.sh"`
- The generator uses the project defaults: `100,000` Monte Carlo samples and random seed `42`.
- Existing figures in `figures/` were not overwritten.

### Next suggested step

Insert the specific 14 pt PNGs from `Resized plots/` into the midterm slides at their intended final display size without scaling them down.

## 2026-06-29 11:12 — Add alternative-fuel share to cement fuel costs

### User request

Fix the alternative-fuels cement inconsistency where emissions reductions reflected a `25-60%` alternative-fuel share but fuel costs assumed `100%` alternative fuel use. Implement the share as a uniform distribution and calculate fuel cost as alternative share times alternative-fuel price plus fossil share times fossil-fuel price.

### Files changed (if needed)

- `src/cement/cement_parameters.py` — added `ALTERNATIVE_FUELS_CEMENT_SHARE_DISTRIBUTION` as a uniform `0.25-0.60` fraction and registered it with the alternative-fuels retrofit assumptions.
- `src/cement/cement_npv_monte_carlo.py` — changed alternative-fuels Monte Carlo fuel pricing to use a blended effective price from sampled biofuel and coal prices.
- `src/cement/cement_npv_deterministic.py` — changed deterministic alternative-fuels fuel pricing to use the representative blended price, with the uniform-share midpoint `0.425`.
- `src/cement/cement_npv_summary_figures.py` — added the alternative-fuel share, fossil-fuel share, coal-price, and biofuel-price fields to raw cement CSV exports.
- `notebooks/cement/deterministic_alternative_fuels_npv.ipynb` — refreshed executed outputs and added the fuel-share and component-price fields to displayed input tables.
- `notebooks/cement/plot_alternative_fuels_npv.ipynb` — refreshed executed outputs and added the fuel-share and component-price fields to the retrofit/input summary.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added an explicit alternative-fuel share parameter for the cement alternative-fuels retrofit.
- Kept the existing alternative-fuels emissions-reduction distribution unchanged at `0.03-0.17`, now consistent with partial fuel substitution.
- Updated fuel-price calculations for alternative fuels:
  - `fuel_price_eur_per_mwh_th = alternative_fuel_share_fraction * biofuel_price_eur_per_mwh_th + (1 - alternative_fuel_share_fraction) * coal_price_eur_per_mwh_th`.
- Kept `fuel_price_eur_per_mwh_th` as the effective blended fuel price so existing summaries, sensitivity analysis, and downstream cash-flow code continue to use one fuel-price column.
- Added traceability fields to cement outputs: `alternative_fuel_share_fraction`, `fossil_fuel_share_fraction`, `coal_price_eur_per_mwh_th`, and `biofuel_price_eur_per_mwh_th`. Non-applicable share fields are `NaN` for technologies other than alternative fuels.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src/cement/cement_parameters.py src/cement/cement_npv_deterministic.py src/cement/cement_npv_monte_carlo.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic alternative-fuels blended-price and fuel-cost identity checks ... PY`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... 1,000-draw Monte Carlo share-bounds, blended-price, and fuel-cost identity checks ... PY`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic cement results, 200-draw cement simulation, and standardized cement sensitivity smoke checks ... PY`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic and 100-draw simulated cement MACC smoke checks ... PY`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src MPLCONFIGDIR=/private/tmp/masterthesis_mpl /opt/anaconda3/envs/master-thesis/bin/python -m cement.cement_npv_summary_figures --kind all --sample-size 10 --random-seed 13 --npv-scale EUR/t --ranking-output both --output-dir /private/tmp/masterthesis_alt_fuel_share_check/figures --raw-data-dir /private/tmp/masterthesis_alt_fuel_share_check/raw --processed-data-dir /private/tmp/masterthesis_alt_fuel_share_check/processed`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src MPLCONFIGDIR=/private/tmp/masterthesis_mpl /opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/cement/deterministic_alternative_fuels_npv.ipynb notebooks/cement/plot_alternative_fuels_npv.ipynb --ExecutePreprocessor.timeout=180`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic and Monte Carlo fuel-share, fuel-cost, emissions, and CO2-cost identity checks ... PY`
- Result:
  - Passed.
- Notes:
  - Deterministic alternative-fuels share is `0.425`.
  - Deterministic effective alternative-fuels price is `14.99575 EUR/MWh_th`, matching `0.425 * 18.9 + 0.575 * 12.11`.
  - In the 1,000-draw smoke run, sampled alternative-fuel shares stayed within `0.25-0.60`, fuel and fossil shares summed to `1.0`, and fuel price/cost identities matched.
  - CO2 emissions cost remains calculated from post-retrofit direct emissions: `annual_output_t * emissions_tco2_per_t * carbon_price_eur_per_t`.
  - Deterministic alternative-fuels emissions cost is `43.2 MEUR/year`, matching `1,000,000 t/year * 0.54 tCO2/t * 80 EUR/tCO2`.
  - An initial MACC smoke-check command used an incorrect local function name and then a stale display column name; the corrected `deterministic_cement_macc` and `simulated_cement_macc` checks passed.

### Reproducibility notes

- This is a scientific-assumption correction and changes cement alternative-fuels deterministic, Monte Carlo, sensitivity, MACC, ranking, figure, and CSV results.
- Existing generated cement outputs and executed notebook outputs are stale until regenerated.
- Temporary verification outputs were written only to `/private/tmp/masterthesis_alt_fuel_share_check`.
- Regenerate cement notebooks and summary outputs before interpreting alternative fuels against other cement technologies.

### Next suggested step

Regenerate the cement summary figures, CSV outputs, and alternative-fuels notebooks so stored artifacts match the corrected fuel-share assumption.

## 2026-06-15 10:27 — Correct cement CCS fuel-consumption change range

### User request

Correct the cement CCS fuel-consumption reduction range because CCS should range from `-130%` to `0%`, not from `0%` to `+130%`.

### Files changed (if needed)

- `src/cement/cement_parameters.py` — changed `CCS_CEMENT_FUEL_REDUCTION_DISTRIBUTION` from `0.0` to `1.30` into `-1.30` to `0.0`, and clarified that negative reduction values represent fuel-consumption increases.
- `CHANGELOG.md` — added this scientific-assumption correction entry.

### What was implemented

- Updated the CCS cement fuel-consumption change range to `[-1.30, 0.0]`.
- Kept the existing retrofit formula unchanged:
  - `fuel_consumption = BAU_fuel_consumption * (1 - fuel_consumption_reduction_fraction)`.
- With the corrected range, CCS fuel use is now between `1.0x` and `2.3x` BAU instead of between `-0.3x` and `1.0x` BAU.
- This removes impossible negative CCS fuel-consumption and negative fuel-cost draws.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic CCS before/after checks ... PY`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... 10,000-draw CCS Monte Carlo fuel checks ... PY`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/mpl-cache PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache /opt/anaconda3/envs/master-thesis/bin/python -m cement.cement_npv_summary_figures --kind all --sample-size 10 --random-seed 13 --npv-scale EUR/t --ranking-output both --output-dir /private/tmp/masterthesis_ccs_fuel_check/figures --raw-data-dir /private/tmp/masterthesis_ccs_fuel_check/raw --processed-data-dir /private/tmp/masterthesis_ccs_fuel_check/processed`
- Result:
  - Passed.
- Notes:
  - Deterministic CCS fuel reduction changed from `+0.65` to `-0.65`.
  - Deterministic CCS fuel consumption changed from `0.2135` to `1.0065 MWh_th/t`.
  - Deterministic CCS annual fuel cost changed from `2.585 MEUR/year` to `12.189 MEUR/year`.
  - Deterministic CCS NPV changed from `632.024 MEUR` to `529.512 MEUR`.
  - Deterministic CCS normalized NPV changed from `25.281 EUR/t` to `21.180 EUR/t`.
  - In a 10,000-draw CCS smoke run, fuel consumption and annual fuel cost were always non-negative after the correction.

### Reproducibility notes

- This is a scientific-assumption correction and changes cement CCS deterministic, Monte Carlo, ranking, figure, and CSV results.
- Existing generated cement outputs in `data/`, `figures/`, and cement notebooks are now stale until regenerated.
- Temporary verification outputs were written only to `/private/tmp/masterthesis_ccs_fuel_check`.

### Next suggested step

Regenerate the cement summary outputs and notebooks before interpreting CCS against the other cement technologies.

## 2026-06-15 09:45 — Clean normalized electricity NPV schema and ranking metadata

### User request

Remove the confusing `npv_million_eur_per_mwh` field after checking whether it is needed, add `metric_column` and `metric_unit` to ranking CSVs, and explain possible follow-up cleanups for fuel-price mappings and unit-identity tests.

### Files changed (if needed)

- `src/electricity/electricity_npv_monte_carlo.py` — removed the obsolete `npv_million_eur_per_mwh` result field.
- `src/electricity/electricity_npv_deterministic.py` — removed the obsolete deterministic `npv_million_eur_per_mwh` result field.
- `src/electricity/electricity_npv_summary_figures.py` — removed `npv_million_eur_per_mwh` from processed output exports and added ranking metric metadata for electricity scales.
- `src/cement/cement_npv_summary_figures.py` — added ranking metric metadata for cement scales.
- `src/npv_summary.py` — added `metric_column` and `metric_unit` to raw ranking tables and propagated them into ranking summaries.
- `notebooks/electricity/*.ipynb` — removed stale source/output references to `npv_million_eur_per_mwh`; affected outputs were cleared and can be regenerated by rerunning the notebooks.
- `data/raw/*NPV_Ranking*.csv` and `data/processed/*NPV_Ranking*.csv` — added generated ranking metadata columns in local CSV artifacts.
- `data/processed/*Electricity*processed_outputs.csv` — removed the obsolete generated `npv_million_eur_per_mwh` column in local CSV artifacts.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Confirmed that `npv_million_eur_per_mwh` was not used for calculations or rankings; it was only an exported/displayed derivative of `npv_eur_per_mwh / 1_000_000`.
- Kept the meaningful normalized electricity metric as `npv_eur_per_mwh`.
- Added ranking metadata so generic `npv` ranking values are now explicitly described:
  - total rankings use `metric_column=npv_eur` and `metric_unit=EUR`;
  - electricity normalized rankings use `metric_column=npv_eur_per_mwh` and `metric_unit=EUR/MWh`;
  - cement normalized rankings use `metric_column=npv_eur_per_t` and `metric_unit=EUR/t`.
- Applied the ranking metadata change in the shared ranking helper so electricity and cement stay aligned.

### Verification (if needed)

- Commands run:
  - `rg -n "npv_million_eur_per_mwh" src notebooks data README.md CHANGELOG.md`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/mpl-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... ranking metadata smoke checks ... PY`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... processed output schema check ... PY`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... notebook JSON validity check ... PY`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... ranking CSV metadata header check ... PY`
- Result:
  - Passed.
- Notes:
  - The obsolete field is gone from live source, notebooks, and local data artifacts.
  - Historical changelog entries still mention `npv_million_eur_per_mwh` as audit history.
  - Matplotlib printed font-cache messages during import; setting `MPLCONFIGDIR` to `/private/tmp/mpl-cache` resolved the unwritable default cache issue for the rerun.

### Reproducibility notes

- No economic formulas, parameter values, sampled assumptions, NPV values, or ranking logic were changed.
- Existing local generated CSV artifacts were updated for schema clarity. They can be regenerated with the sector summary CLIs using the desired `--npv-scale` and `--ranking-output` arguments.
- Notebook outputs that contained the removed column were cleared rather than recalculated; rerunning the notebooks will regenerate outputs from the current schema.

### Next suggested step

Add a small unit-identity test suite for the core cost and normalized-NPV equations, then consider extracting the duplicated electricity fuel-price mapping into one shared helper.

## 2026-06-12 12:58 — Verify cross-sector outputs and export cement lifetime

### User request

Run a check that the project still works after the electricity lifetime change, assess whether `lifetime_years` should also be included in cement raw CSV exports for sector consistency, and explain what changed with the new electricity lifetimes.

### Files changed (if needed)

- `src/cement/cement_npv_deterministic.py` — added `lifetime_years` to deterministic cement result rows.
- `src/cement/cement_npv_monte_carlo.py` — added `lifetime_years` to Monte Carlo cement result rows.
- `src/cement/cement_npv_summary_figures.py` — added `lifetime_years` to cement raw-input CSV exports.
- `CHANGELOG.md` — added this verification and consistency entry.

### What was implemented

- Added the existing cement lifetime assumption (`LIFETIME_CEMENT_YEARS = 25`) to cement result dictionaries.
- Added `lifetime_years` to `CEMENT_RAW_INPUT_COLUMNS`, matching the electricity raw CSV export pattern.
- Did not change cement NPV calculations, cement assumptions, or cement figures; the change only makes the existing lifetime input visible in raw CSV exports.
- Rechecked electricity and cement deterministic, Monte Carlo, ranking, and CLI output paths.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cross-sector lifetime, per-output, and ranking invariant checks ... PY`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind all --sample-size 10 --random-seed 13 --npv-scale EUR/MWh --ranking-output both --output-dir /private/tmp/masterthesis_cross_sector_check/electricity/figures --raw-data-dir /private/tmp/masterthesis_cross_sector_check/electricity/raw --processed-data-dir /private/tmp/masterthesis_cross_sector_check/electricity/processed`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m cement.cement_npv_summary_figures --kind all --sample-size 10 --random-seed 13 --npv-scale EUR/t --ranking-output both --output-dir /private/tmp/masterthesis_cross_sector_check/cement/figures --raw-data-dir /private/tmp/masterthesis_cross_sector_check/cement/raw --processed-data-dir /private/tmp/masterthesis_cross_sector_check/cement/processed`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... exported CSV lifetime and normalized ranking metric validation ... PY`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... deterministic old-25-year versus new-lifetime comparison ... PY`
- Result:
  - Passed.
- Notes:
  - Temporary cross-sector outputs were generated in `/private/tmp/masterthesis_cross_sector_check`.
  - Electricity raw exports contain technology-specific lifetimes; cement raw exports now contain 25 years for all cement technologies.
  - Normalized ranking CSVs were checked against `npv_eur_per_mwh` and `npv_eur_per_t` from processed exports.

### Reproducibility notes

- Cement numerical results are unchanged; only the raw export schema now includes the cement lifetime input.
- Electricity results remain changed from the previous entry because electricity now uses technology-specific lifetimes.
- No raw data or project output files in `figures/` or `data/` were changed.

## 2026-06-12 12:40 — Add technology-specific electricity lifetimes

### User request

Use the thesis workflow skill and update the electricity sector so asset lifetime is technology-specific. Use 30 years for PV, coal, CCGT, and CCS variants; 25 years for wind and biogas; and 45 years for nuclear. Keep the change consistent across deterministic, Monte Carlo, plotting, rankings, and CSV exports.

### Files changed (if needed)

- `src/electricity/electricity_parameters.py` — added technology-specific lifetime parameters and registered them with each electricity technology.
- `src/electricity/electricity_npv_deterministic.py` — changed deterministic NPV and lifetime-output calculations to use the selected technology lifetime.
- `src/electricity/electricity_npv_monte_carlo.py` — changed Monte Carlo NPV and lifetime-output calculations to use the selected technology lifetime.
- `src/electricity/electricity_npv_summary_figures.py` — added `lifetime_years` to raw electricity CSV exports.
- `notebooks/electricity/electricity_summary.ipynb` — re-executed the electricity summary notebook with the new lifetime assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Removed the single global electricity lifetime from active calculation paths.
- Added these technology lifetimes:
  - hard coal: 30 years
  - hard coal + CCS: 30 years
  - CCGT: 30 years
  - CCGT + CCS: 30 years
  - nuclear: 45 years
  - offshore wind: 25 years
  - onshore wind: 25 years
  - PV: 30 years
  - biogas: 25 years
- Stored lifetime in `ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS` next to full-load hours.
- Used `lifetime_years` in both:
  - the NPV discount horizon;
  - the `lifetime_output_mwh` denominator used for `npv_eur_per_mwh`.
- Added `lifetime_years` to electricity raw-input CSV exports so generated outputs show which lifetime was used.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/electricity/electricity_parameters.py src/electricity/electricity_npv_deterministic.py src/electricity/electricity_npv_monte_carlo.py src/electricity/electricity_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... lifetime, deterministic, Monte Carlo, and ranking validation ... PY`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind all --sample-size 10 --random-seed 5 --npv-scale EUR/MWh --ranking-output both --output-dir /private/tmp/masterthesis_lifetime_cli/figures --raw-data-dir /private/tmp/masterthesis_lifetime_cli/raw --processed-data-dir /private/tmp/masterthesis_lifetime_cli/processed`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... exported CSV lifetime and ranking metric validation ... PY`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/electricity/electricity_summary.ipynb`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
- Result:
  - Passed.
- Notes:
  - The CLI smoke test generated temporary electricity total/deterministic/ranking outputs in `/private/tmp/masterthesis_lifetime_cli`.
  - The CSV validation confirmed raw exports include `lifetime_years`, processed exports use `annual_output_mwh * lifetime_years`, and `EUR/MWh` ranking CSV values match `npv_eur_per_mwh`.

### Reproducibility notes

- This changes electricity NPV results and electricity normalized NPV results because the discount horizon and lifetime-output denominator are now technology-specific.
- No cement code, raw data, or project output CSV/figure files were changed.
- The electricity summary notebook was refreshed. The individual single-technology electricity notebooks will use the new lifetimes when re-executed, but they were not re-executed in this focused change to avoid a broad notebook-output diff.

## 2026-06-12 12:12 — Add normalized NPV summary and ranking workflows

### User request

Keep the existing total NPV comparison, but add a parallel normalized workflow so figures, rankings, CSV outputs, and summary notebooks can compare electricity in `EUR/MWh` and cement in `EUR/t`. Use the thesis workflow skill and keep the implementation clean and lean.

### Files changed (if needed)

- `src/npv_summary.py` — added generic metric summary helpers for mean and deterministic values.
- `src/npv_summary_plots.py` — added a configurable x-axis label to the NPV bar plot helper.
- `src/electricity/electricity_npv_summary_figures.py` — added electricity NPV scale options, normalized `EUR/MWh` figures, rankings, CSV stems, and CLI support via `--npv-scale`.
- `src/cement/cement_npv_summary_figures.py` — added cement NPV scale options, normalized `EUR/t` figures, rankings, CSV stems, and CLI support via `--npv-scale`.
- `notebooks/electricity/electricity_summary.ipynb` — added `NPV_SCALE = "MEUR"` setting with optional `"EUR/MWh"` mode and re-executed the notebook.
- `notebooks/cement/cement_summary.ipynb` — added `NPV_SCALE = "MEUR"` setting with optional `"EUR/t"` mode and re-executed the notebook.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Preserved `MEUR` as the default total-NPV workflow.
- Added scale metadata per sector so the same result arrays can be summarized by total NPV or normalized NPV without changing model assumptions.
- Added reusable `mean_metric` and `deterministic_metric` helpers for arbitrary result columns and display scales.
- Kept existing million-EUR helper functions for backward compatibility.
- Added per-unit ranking support by passing `npv_eur_per_mwh` or `npv_eur_per_t` into the existing generic ranking helper.
- Added normalized output filenames such as:
  - `Mean_NPV_per_MWh_Electricity`
  - `NPV_Ranking_per_MWh_Electricity`
  - `Mean_NPV_per_t_Cement`
  - `NPV_Ranking_per_t_Cement`
- Added `--npv-scale MEUR|EUR/MWh` to the electricity summary CLI.
- Added `--npv-scale MEUR|EUR/t` to the cement summary CLI.
- Updated the summary notebooks so changing one `NPV_SCALE` variable switches the mean table, deterministic table, mean figure, and ranking calculation together.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/electricity/electricity_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary.py src/npv_summary_plots.py src/electricity/electricity_npv_summary_figures.py src/cement/cement_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... four-scale output smoke test ... PY`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/electricity/electricity_summary.ipynb notebooks/cement/cement_summary.ipynb`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 4 --npv-scale EUR/MWh --output-dir /private/tmp/masterthesis_cli_norm/electricity/figures --raw-data-dir /private/tmp/masterthesis_cli_norm/electricity/raw --processed-data-dir /private/tmp/masterthesis_cli_norm/electricity/processed --ranking-output both`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m cement.cement_npv_summary_figures --kind mean --sample-size 5 --random-seed 4 --npv-scale EUR/t --output-dir /private/tmp/masterthesis_cli_norm/cement/figures --raw-data-dir /private/tmp/masterthesis_cli_norm/cement/raw --processed-data-dir /private/tmp/masterthesis_cli_norm/cement/processed --ranking-output both`
  - `/opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... summary notebook structure and execution validation ... PY`
- Result:
  - Passed.
- Notes:
  - The first notebook execution attempt failed inside the sandbox because Jupyter could not bind local kernel ports. The same command succeeded after approval to run outside the sandbox.
  - The smoke test generated temporary total and normalized outputs for electricity and cement in `/private/tmp`.

### Reproducibility notes

- No raw data, model assumptions, parameter values, or existing project output files in `figures/` or `data/` were changed.
- Existing total-NPV output behavior remains the default because `npv_scale="MEUR"` is used unless another scale is requested.
- Normalized outputs are generated from existing model result columns, so the change affects plotting, ranking metric selection, and export naming, not the underlying NPV calculations.

## 2026-06-09 17:11 — Align cement summary notebook with electricity summary structure

### User request

Make the cement summary notebook match the electricity summary notebook structure by removing the cement-only explanation section or adding an equivalent electricity section.

### Files changed (if needed)

- `notebooks/cement/cement_summary.ipynb` — removed the cement-only quick interpretation section and re-executed the notebook.
- `CHANGELOG.md` — added this consistency correction entry.

### What was implemented

- Removed the `Quick result interpretation` markdown cell from the cement summary notebook.
- Removed the associated interpretation-table code cell.
- Re-executed `notebooks/cement/cement_summary.ipynb` in place.
- Confirmed the cement and electricity summary notebooks now share the same section structure:
  - summary title
  - settings
  - Monte Carlo mean NPV
  - deterministic NPV
  - Monte Carlo NPV ranking

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement summary structure validation ... PY`
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/cement/cement_summary.ipynb`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... executed notebook validation and heading comparison ... PY`
- Result:
  - Passed.

### Reproducibility notes

- No source code, raw data, generated CSVs, project figures, or parameter values were changed.
- The cement notebook still includes the cement-specific `RETROFIT_BAU_MODE` setting because cement retrofits are BAU-relative.

## 2026-06-09 15:51 — Add cement NPV summary notebook

### User request

Add a cement summary notebook consistent with the electricity summary notebook, mark inconsistencies if present, and include quick basic feedback on the cement NPV results.

### Files changed (if needed)

- `notebooks/cement/cement_summary.ipynb` — added executed cement summary notebook with Monte Carlo mean NPV, deterministic NPV, ranking, and quick interpretation table.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Created a cement-sector counterpart to `notebooks/electricity/electricity_summary.ipynb`.
- Mirrored the electricity notebook structure:
  - project/source import setup
  - settings cell
  - Monte Carlo mean NPV figure
  - deterministic NPV figure
  - Monte Carlo NPV ranking table and plot
- Added cement-specific `RETROFIT_BAU_MODE = DEFAULT_RETROFIT_BAU_MODE`.
- Added a quick result interpretation table with Monte Carlo mean NPV, normalized `EUR/t`, deterministic NPV, ranking metrics, and one short explanation per technology.
- Executed the notebook in place so plots and tables are rendered.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... static notebook validation ... PY`
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/cement/cement_summary.ipynb`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... executed notebook validation ... PY`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement summary result extraction ... PY`
  - `rg -n "electricity|Electricity|simulate_electricity|ELECTRICITY" notebooks/cement/cement_summary.ipynb -S`
- Result:
  - Passed.
- Notes:
  - The notebook has six executed code cells with rendered outputs.
  - The `rg` check found only ordinary explanatory uses of the word "electricity" in cement technology explanations, not stale electricity imports or module names.

### Result notes

- CCS has the highest Monte Carlo mean NPV in the current assumptions, because the emissions-cost reduction dominates despite high CAPEX/OPEX and electricity penalties.
- Process heat integration, waste heat recovery, and clinker substitution cluster near each other with strong positive NPVs because they improve BAU fuel, electricity, or emissions intensities without becoming fully new high-CAPEX production routes.
- Efficiency improvement and alternative fuels remain positive but rank lower than the strongest retrofit options because their benefits are more modest or depend on higher fuel-cost assumptions.
- BAU remains positive, mainly due to low CAPEX and the shared cement price assumption, but it ranks below most retrofits once carbon and fuel savings are counted.
- Electrification and electrolysis are strongly negative under current assumptions because high electricity consumption dominates the NPV.

### Review notes

- No avoidable structural inconsistency was found versus the electricity summary notebook.
- The cement notebook necessarily differs by including `RETROFIT_BAU_MODE`, because cement retrofits are BAU-relative while electricity technologies are absolute.

### Reproducibility notes

- No raw data, project figures, generated CSVs, or parameter values were changed.
- The notebook uses `DEFAULT_SAMPLE_SIZE`, `DEFAULT_RANDOM_SEED`, and `DEFAULT_RETROFIT_BAU_MODE` from the cement Monte Carlo source.

## 2026-06-09 15:21 — Add cement NPV summary figures source

### User request

Create the cement equivalent of the electricity NPV summary figures source code, while watching for avoidable inconsistencies and highlighting any that remain.

### Files changed (if needed)

- `src/cement/cement_npv_summary_figures.py` — added cement-sector summary, CSV export, figure, ranking, and CLI workflow.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added cement technology display labels for BAU, alternative technologies, and retrofit technologies.
- Added cement raw-input and processed-output export column schemas.
- Added cement Monte Carlo NPV distribution summaries in million EUR.
- Added helper functions for simulated and deterministic mean NPV values.
- Added cement mean NPV, deterministic NPV, and combined figure/output save functions.
- Added cement NPV ranking calculation, ranking CSV export, and ranking plot functions.
- Added `generate_cement_npv_rankings` for notebook/script use.
- Added a CLI matching the electricity module structure:
  - `--kind all|mean|deterministic`
  - `--sample-size`
  - `--random-seed`
  - `--retrofit-bau-mode sampled|deterministic`
  - `--no-data`
  - `--ranking-output csv|plots|both|none`
- Added an export-only normalization helper for deterministic cement results so deterministic CSV exports include `retrofit_bau_mode`, matching the Monte Carlo cement schema without changing deterministic model logic.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement/cement_npv_summary_figures.py`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement summary smoke test ... PY`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m cement.cement_npv_summary_figures --kind mean --sample-size 10 --random-seed 2 --output-dir /private/tmp/masterthesis_cement_summary_cli/figures --raw-data-dir /private/tmp/masterthesis_cement_summary_cli/raw --processed-data-dir /private/tmp/masterthesis_cement_summary_cli/processed --ranking-output none`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement all-output helper check ... PY`
  - `rg -n "def save_cement|def calculate_cement|def generate_cement|CEMENT_RAW_INPUT_COLUMNS|retrofit_bau_mode|save_cement_npv_outputs|parse_args" src/cement/cement_npv_summary_figures.py`
- Result:
  - Passed.
- Notes:
  - Smoke tests generated mean, deterministic, ranking, raw-input, and processed-output cement artefacts in `/private/tmp`.
  - The CLI generated the expected mean figure plus raw and processed CSVs.
  - The all-output helper generated the expected six paths when ranking outputs were disabled.
  - Matplotlib emitted sandbox-related font-cache warnings, but output files were created successfully.

### Review notes

- Cement differs from electricity because it has `retrofit_bau_mode` and BAU-relative retrofit handling. The new module keeps this difference explicit instead of hiding it.
- Deterministic cement results do not need `retrofit_bau_mode` internally, so the summary module adds it only for export schema consistency.
- No additional source-level inconsistency was found that needed to be fixed in this pass.
- Remaining known cleanup candidate, intentionally left unchanged: normalized NPV fields still include `npv_million_eur_per_mwh` / `npv_million_eur_per_t` in source outputs and deterministic notebooks.

### Reproducibility notes

- No project figures, project data CSVs, raw data, or parameter values were changed.
- The new CLI can generate project outputs with:
  - `PYTHONPATH=src python -m cement.cement_npv_summary_figures`
- Cement retrofit summary outputs default to `retrofit_bau_mode="sampled"` unless `--retrofit-bau-mode deterministic` is provided.

## 2026-06-09 15:08 — Align electricity and cement NPV simulation entry patterns

### User request

Keep the electricity and cement Monte Carlo code/notebook structure consistent, especially around default technology selection and notebook simulation entry points, and review both sectors for avoidable inconsistencies.

### Files changed (if needed)

- `src/electricity/electricity_npv_monte_carlo.py` — changed sector-level technology selection to the registry-driven `None` default pattern used by cement.
- `notebooks/electricity/plot_biogas_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_ccgt_ccs_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_ccgt_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_hard_coal_ccs_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_hard_coal_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_nuclear_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_pv_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_wind_offshore_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/electricity/plot_wind_onshore_npv.ipynb` — switched to the public `simulate_electricity_results` entry point.
- `notebooks/cement/plot_bau_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_electrification_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_electrolysis_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_clinker_substitution_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_alternative_fuels_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_efficiency_improvement_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_waste_heat_recovery_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_ccs_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `notebooks/cement/plot_process_heat_integration_npv.ipynb` — switched to the public `simulate_cement_results` entry point.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Changed `simulate_electricity_technologies_npv` from a hard-coded default technology tuple to `technologies: tuple[str, ...] | None = None`.
- Resolved default electricity technologies from `tuple(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)`, matching the cement registry-driven pattern.
- Simplified `simulate_electricity_results` so it passes the optional `technologies` argument through to the sector-level function, matching cement's public-entry layering.
- Updated all electricity plotting notebooks to call:
  - `simulate_electricity_results(sample_size=SAMPLE_SIZE, random_seed=RANDOM_SEED, technologies=(TECHNOLOGY,))`
- Updated all cement plotting notebooks to call:
  - `simulate_cement_results(sample_size=SAMPLE_SIZE, random_seed=RANDOM_SEED, technologies=(TECHNOLOGY,), retrofit_bau_mode=RETROFIT_BAU_MODE)`
- Removed notebook-level RNG construction from all electricity and cement plotting notebooks so the public result functions own default seed handling.
- Re-executed all 18 plotting notebooks in place.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... plotting notebook entry-point validation ... PY`
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/electricity/plot_biogas_npv.ipynb notebooks/electricity/plot_ccgt_ccs_npv.ipynb notebooks/electricity/plot_ccgt_npv.ipynb notebooks/electricity/plot_hard_coal_ccs_npv.ipynb notebooks/electricity/plot_hard_coal_npv.ipynb notebooks/electricity/plot_nuclear_npv.ipynb notebooks/electricity/plot_pv_npv.ipynb notebooks/electricity/plot_wind_offshore_npv.ipynb notebooks/electricity/plot_wind_onshore_npv.ipynb notebooks/cement/plot_bau_npv.ipynb notebooks/cement/plot_electrification_npv.ipynb notebooks/cement/plot_electrolysis_npv.ipynb notebooks/cement/plot_clinker_substitution_npv.ipynb notebooks/cement/plot_alternative_fuels_npv.ipynb notebooks/cement/plot_efficiency_improvement_npv.ipynb notebooks/cement/plot_waste_heat_recovery_npv.ipynb notebooks/cement/plot_ccs_npv.ipynb notebooks/cement/plot_process_heat_integration_npv.ipynb`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... sector MC defaults, market alignment, and ranking checks ... PY`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... executed plotting notebook validation ... PY`
  - `rg -n "technologies: tuple\\[str, \\.\\.\\.\\] = \\(|simulate_electricity_technology_npv|simulate_cement_technology_npv|np.random.default_rng\\(RANDOM_SEED\\)" src/electricity src/cement notebooks/electricity notebooks/cement -S`
- Result:
  - Passed.
- Notes:
  - Confirmed electricity and cement sector-level MC functions now use registry-driven default technology selection.
  - Confirmed all 18 plotting notebooks use public result entry points and no longer construct notebook-level RNGs.
  - Confirmed electricity coal/gas shared price alignment and cement BAU/market alignment still work.
  - Confirmed NPV ranking helpers still produce expected row counts and simulation counts.

### Review notes

- Fixed avoidable inconsistency: electricity no longer duplicates its default technology list in the MC function signature.
- Fixed avoidable inconsistency: plotting notebooks in both sectors now use the public `simulate_*_results` layer with `SAMPLE_SIZE`, `RANDOM_SEED`, and `technologies=(TECHNOLOGY,)`.
- Remaining cleanup candidate: source outputs and deterministic notebooks still expose `npv_million_eur_per_mwh` / `npv_million_eur_per_t`. This is now consistent across sectors, but it conflicts with the newer plotting convention of displaying normalized NPV as `EUR/MWh` or `EUR/t`.

### Reproducibility notes

- Plotting notebook outputs changed because they now use the public sector result functions, which own seed handling and run-level shared market sampling.
- Single-technology source wrappers remain available for backwards compatibility, but notebooks no longer use them.

## 2026-06-09 14:53 — Standardize electricity plotting notebooks on generic technology selection

### User request

Make the electricity Monte Carlo plotting notebooks consistent with the cement plotting notebooks by choosing the technology through a notebook variable instead of importing one technology-specific simulation wrapper per notebook.

### Files changed (if needed)

- `notebooks/electricity/plot_biogas_npv.ipynb` — switched to `TECHNOLOGY = "biogas"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_ccgt_ccs_npv.ipynb` — switched to `TECHNOLOGY = "ccgt_ccs"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_ccgt_npv.ipynb` — switched to `TECHNOLOGY = "ccgt"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_hard_coal_ccs_npv.ipynb` — switched to `TECHNOLOGY = "hard_coal_ccs"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_hard_coal_npv.ipynb` — switched to `TECHNOLOGY = "hard_coal"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_nuclear_npv.ipynb` — switched to `TECHNOLOGY = "nuclear"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_pv_npv.ipynb` — switched to `TECHNOLOGY = "pv"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_wind_offshore_npv.ipynb` — switched to `TECHNOLOGY = "wind_offshore"` and `simulate_electricity_technology_npv`.
- `notebooks/electricity/plot_wind_onshore_npv.ipynb` — switched to `TECHNOLOGY = "wind_onshore"` and `simulate_electricity_technology_npv`.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Replaced technology-specific wrapper imports such as `simulate_ccgt_npv` with the generic `simulate_electricity_technology_npv` import.
- Added a `TECHNOLOGY` variable to each electricity plotting notebook setup cell.
- Changed each notebook setup call to:
  - `simulate_electricity_technology_npv(technology=TECHNOLOGY, size=SAMPLE_SIZE, rng=rng)`
- Kept `SAMPLE_SIZE = DEFAULT_SAMPLE_SIZE` and `RANDOM_SEED = DEFAULT_RANDOM_SEED` editable in every notebook.
- Re-executed all nine electricity plotting notebooks in place so outputs match the updated cells.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... electricity notebook conversion validation ... PY`
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/electricity/plot_biogas_npv.ipynb notebooks/electricity/plot_ccgt_ccs_npv.ipynb notebooks/electricity/plot_ccgt_npv.ipynb notebooks/electricity/plot_hard_coal_ccs_npv.ipynb notebooks/electricity/plot_hard_coal_npv.ipynb notebooks/electricity/plot_nuclear_npv.ipynb notebooks/electricity/plot_pv_npv.ipynb notebooks/electricity/plot_wind_offshore_npv.ipynb notebooks/electricity/plot_wind_onshore_npv.ipynb`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... executed notebook validation ... PY`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
- Result:
  - Passed.
- Notes:
  - Confirmed all nine notebooks import `simulate_electricity_technology_npv`.
  - Confirmed all nine notebooks define the correct `TECHNOLOGY` string and call `technology=TECHNOLOGY`.
  - Confirmed old technology-specific wrapper names no longer appear in the electricity plotting notebooks.
  - Confirmed all nine notebooks execute and validate as notebooks.

### Reproducibility notes

- No source simulation logic or parameter values were changed in this step.
- The notebook output values remain single-technology simulations; sector-level shared fuel-price behavior is handled by `simulate_electricity_results` / `simulate_electricity_technologies_npv`.

## 2026-06-09 14:33 — Align electricity MC fuel prices by run ID

### User request

Update the electricity Monte Carlo logic so technologies sharing a fuel type, such as CCGT and CCGT+CCS, are compared with consistent fuel-price draws for the same `run_id`.

### Files changed (if needed)

- `src/electricity/electricity_npv_monte_carlo.py` — added shared fuel-price arrays for sector-level electricity Monte Carlo runs.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added an optional `market_values` mapping to `simulate_electricity_technology_npv`.
- In `simulate_electricity_technologies_npv`, sampled fuel prices once per `run_id` for coal, gas, uranium, no-fuel, and biogas assumptions.
- Passed those shared market values into each technology simulation in sector-level runs.
- Kept single-technology simulations unchanged: direct calls without `market_values` still sample their own fuel-price arrays.
- Aligned electricity with the cement MC interpretation that one `run_id` represents one shared uncertain market context for ranking.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... electricity MC consistency checks ... PY`
- Result:
  - Passed.
- Notes:
  - Confirmed that `hard_coal` and `hard_coal_ccs` share identical coal-price arrays for the same `run_id`.
  - Confirmed that `ccgt` and `ccgt_ccs` share identical gas-price arrays for the same `run_id`.
  - Confirmed that electricity NPV ranking still produces the expected number of rows and simulation counts.

### Reproducibility notes

- Sector-level electricity Monte Carlo results will change numerically compared with previous runs because shared fuel-price draws are now sampled before technology-specific parameters.
- Single-technology notebook simulations are not affected unless they call the multi-technology sector simulation.

## 2026-06-09 14:24 — Add cement NPV plotting notebooks and align cement MC run IDs

### User request

Create Monte Carlo plotting notebooks for the cement technologies, then review the NPV code for inconsistencies, logic errors, or other issues.

### Files changed (if needed)

- `notebooks/cement/plot_bau_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for BAU.
- `notebooks/cement/plot_electrification_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for electrification.
- `notebooks/cement/plot_electrolysis_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for electrolysis.
- `notebooks/cement/plot_clinker_substitution_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for clinker substitution.
- `notebooks/cement/plot_alternative_fuels_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for alternative fuels.
- `notebooks/cement/plot_efficiency_improvement_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for efficiency improvement.
- `notebooks/cement/plot_waste_heat_recovery_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for waste heat recovery.
- `notebooks/cement/plot_ccs_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for CCS.
- `notebooks/cement/plot_process_heat_integration_npv.ipynb` — added executed cement Monte Carlo NPV plotting notebook for process heat integration.
- `src/cement/cement_npv_monte_carlo.py` — aligned shared cement market-price draws across technologies in sector-level Monte Carlo runs.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added one cement plotting notebook per cement technology, following the electricity plotting notebook structure.
- Imported `DEFAULT_SAMPLE_SIZE`, `DEFAULT_RANDOM_SEED`, and `DEFAULT_RETROFIT_BAU_MODE` from `cement.cement_npv_monte_carlo` while keeping notebook variables editable for custom plots.
- Used `npv_eur_per_t` for normalized cement NPV plots, with the x-axis labeled `NPV (EUR/t)`.
- Added retrofit input summaries in retrofit notebooks so sampled BAU-relative changes and BAU baseline columns are visible.
- Kept the total NPV distribution in million EUR and annual cost components in million EUR/year.
- Updated sector-level cement Monte Carlo runs so coal, biofuel, and electricity price samples are drawn once per `run_id` and reused across technologies.
- Preserved single-technology notebook behavior: when a notebook simulates one technology directly, it samples its own market prices as before.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/cement/plot_bau_npv.ipynb notebooks/cement/plot_electrification_npv.ipynb notebooks/cement/plot_electrolysis_npv.ipynb notebooks/cement/plot_clinker_substitution_npv.ipynb notebooks/cement/plot_alternative_fuels_npv.ipynb notebooks/cement/plot_efficiency_improvement_npv.ipynb notebooks/cement/plot_waste_heat_recovery_npv.ipynb notebooks/cement/plot_ccs_npv.ipynb notebooks/cement/plot_process_heat_integration_npv.ipynb`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement MC consistency checks ... PY`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ... cement plotting notebook validation ... PY`
  - `rg -n "NPV \\(MEUR/t\\)|MEUR/t|npv_million_eur_per_t|NPV \\(MEUR/MWh\\)|MEUR/MWh" src notebooks/cement notebooks/electricity/plot_*_npv.ipynb -S`
- Result:
  - Passed for source compilation, cement Monte Carlo consistency, and all nine new cement plotting notebooks.
- Notes:
  - The cement MC consistency check confirmed that sampled BAU baseline columns match the BAU result for retrofit runs.
  - The same check confirmed that sector-level cement runs now align coal and electricity prices across technologies for the same `run_id`.
  - All nine cement plotting notebooks validated as JSON notebooks and contain the editable default imports and `EUR/t` normalized plot labels.

### Review notes

- Fixed: sector-level cement MC previously aligned BAU technical values across retrofit technologies but sampled market prices separately by technology. That conflicted with the shared `run_id` ranking interpretation.
- Remaining caveat: deterministic cement notebooks and cement source outputs still expose `npv_million_eur_per_t` / `MEUR/t`. The new plotting notebooks do not use this for normalized plots, but the older deterministic notebooks still show it in their tables.

### Reproducibility notes

- The new cement plotting notebooks can be customized by overriding `SAMPLE_SIZE`, `RANDOM_SEED`, or `RETROFIT_BAU_MODE` in the setup cell.
- For retrofit notebooks, `RETROFIT_BAU_MODE = "sampled"` propagates sampled BAU uncertainty; `"deterministic"` isolates retrofit uncertainty against representative BAU values.
- The sector-level cement MC result now better matches the ranking helper's interpretation of each `run_id` as one shared uncertain world.

## 2026-06-09 14:02 — Update electricity NPV plotting notebook defaults and normalized units

### User request

Update all electricity NPV plotting notebooks to import the Monte Carlo default sample size and random seed while keeping those values editable, and change normalized NPV plots from `MEUR/MWh` to `EUR/MWh`.

### Files changed (if needed)

- `notebooks/electricity/plot_biogas_npv.ipynb` — imported Monte Carlo defaults, made `SAMPLE_SIZE` and `RANDOM_SEED` editable from defaults, and changed normalized NPV output to `EUR/MWh`.
- `notebooks/electricity/plot_ccgt_ccs_npv.ipynb` — same plotting notebook update for CCGT+CCS.
- `notebooks/electricity/plot_ccgt_npv.ipynb` — same plotting notebook update for CCGT.
- `notebooks/electricity/plot_hard_coal_ccs_npv.ipynb` — same plotting notebook update for hard coal+CCS.
- `notebooks/electricity/plot_hard_coal_npv.ipynb` — same plotting notebook update for hard coal.
- `notebooks/electricity/plot_nuclear_npv.ipynb` — same plotting notebook update for nuclear.
- `notebooks/electricity/plot_pv_npv.ipynb` — same plotting notebook update for PV.
- `notebooks/electricity/plot_wind_offshore_npv.ipynb` — same plotting notebook update for offshore wind.
- `notebooks/electricity/plot_wind_onshore_npv.ipynb` — same plotting notebook update for onshore wind.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Imported `DEFAULT_SAMPLE_SIZE` and `DEFAULT_RANDOM_SEED` from `electricity.electricity_npv_monte_carlo` in each electricity plotting notebook.
- Replaced hard-coded `SAMPLE_SIZE = 1000000` and unseeded `np.random.default_rng()` setup with editable notebook variables:
  - `SAMPLE_SIZE = DEFAULT_SAMPLE_SIZE`
  - `RANDOM_SEED = DEFAULT_RANDOM_SEED`
- Kept custom plotting possible because users can still override `SAMPLE_SIZE` and `RANDOM_SEED` in the notebook setup cell.
- Removed the `NPV million EUR/MWh` summary column from the plotting notebooks.
- Changed the normalized NPV histogram to use `npv_eur_per_mwh` and label the x-axis as `NPV (EUR/MWh)`.
- Re-executed all nine plotting notebooks in place so saved outputs match the updated code.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/electricity/plot_biogas_npv.ipynb notebooks/electricity/plot_ccgt_ccs_npv.ipynb notebooks/electricity/plot_ccgt_npv.ipynb notebooks/electricity/plot_hard_coal_ccs_npv.ipynb notebooks/electricity/plot_hard_coal_npv.ipynb notebooks/electricity/plot_nuclear_npv.ipynb notebooks/electricity/plot_pv_npv.ipynb notebooks/electricity/plot_wind_offshore_npv.ipynb notebooks/electricity/plot_wind_onshore_npv.ipynb`
  - `rg -n "NPV million EUR/MWh|NPV \\(million EUR/MWh\\)|npv_million_eur_per_mwh =|SAMPLE_SIZE = 1000000|np.random.default_rng\\(\\)" notebooks/electricity/plot_*_npv.ipynb`
  - `/opt/anaconda3/envs/master-thesis/bin/python -c 'import json; from pathlib import Path; paths=sorted(Path("notebooks/electricity").glob("plot_*_npv.ipynb")); [print(path.name, [c.get("execution_count") for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "code"], sum(len(c.get("outputs", [])) for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "code")) for path in paths]'`
  - `/opt/anaconda3/envs/master-thesis/bin/python -c 'import nbformat; from pathlib import Path; paths=sorted(Path("notebooks/electricity").glob("plot_*_npv.ipynb")); [nbformat.validate(nbformat.read(path, as_version=4)) for path in paths]; print(len(paths), "electricity plotting notebooks validated")'`
- Result:
  - Passed.
- Notes:
  - The `rg` check returned no matches for stale `MEUR/MWh` normalized plotting code, old hard-coded `SAMPLE_SIZE = 1000000`, or unseeded `np.random.default_rng()`.
  - All nine plotting notebooks executed successfully and validated as notebook format version 4.

### Reproducibility notes

- No source code, raw data, generated CSVs, or standalone figure files were changed.
- Saved notebook outputs now use the electricity Monte Carlo module defaults unless `SAMPLE_SIZE` or `RANDOM_SEED` are changed in a notebook.
- The normalized NPV distribution remains normalized by lifetime MWh, but is now displayed in `EUR/MWh`.

### Next suggested step

Apply the same default-import and `EUR/t` normalized plotting convention when cement Monte Carlo plotting notebooks are added.

## 2026-06-09 13:41 — Add cement Monte Carlo NPV simulation

### User request

Implement the cement NPV Monte Carlo file following the electricity equivalent, with a configurable choice for retrofit technologies to use either sampled or deterministic BAU baseline values.

### Files changed (if needed)

- `src/cement/cement_npv_monte_carlo.py` — added the cement-sector Monte Carlo NPV simulation engine with absolute technology handling and BAU-relative retrofit handling.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added `simulate_cement_technology_npv`, `simulate_cement_technologies_npv`, and `simulate_cement_results`, mirroring the electricity Monte Carlo entry-point structure.
- Added one wrapper function for each cement technology: BAU, electrification, electrolysis, clinker substitution, alternative fuels, efficiency improvement, waste heat recovery, CCS, and process heat integration.
- Added `retrofit_bau_mode` with supported values `"sampled"` and `"deterministic"`.
- Set `"sampled"` as the default retrofit BAU mode for full uncertainty propagation.
- In sampled BAU mode, BAU technology parameters are sampled once for the simulation run IDs and reused for the `bau` result and all retrofit technologies.
- In deterministic BAU mode, retrofit technologies use representative BAU values while sampling only their retrofit distributions.
- Added traceability columns for retrofit outputs, including resolved absolute values, sampled retrofit changes/reduction fractions, and `bau_*` baseline values used for each run ID.
- Kept the shared result contract used by sector-agnostic helpers: `run_id`, `technology`, `npv_eur`, `initial_capex_eur`, and `annual_net_cash_flow_eur`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement/cement_npv_monte_carlo.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement.cement_npv_monte_carlo import simulate_cement_results; r=simulate_cement_results(sample_size=5, random_seed=42, retrofit_bau_mode="sampled"); print(sorted(r)); print(r["bau"]["capex_eur_per_t"][:3]); print(r["ccs"]["bau_capex_eur_per_t"][:3]); print((r["bau"]["capex_eur_per_t"] == r["ccs"]["bau_capex_eur_per_t"]).all()); print(r["ccs"]["retrofit_bau_mode"][0]); print(round(float(r["ccs"]["electricity_consumption_mwh_per_t"][0]), 6)); print(round(float(r["ccs"]["npv_eur"][0] / 1_000_000), 3))'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement.cement_npv_monte_carlo import simulate_cement_results, simulate_cement_technology_npv; r=simulate_cement_results(sample_size=5, random_seed=42, retrofit_bau_mode="deterministic"); print(sorted(r)); print(r["ccs"]["bau_capex_eur_per_t"][:3]); print(r["ccs"]["retrofit_bau_mode"][0]); print(round(float(r["ccs"]["bau_emissions_tco2_per_t"][0]), 6)); print(round(float(r["ccs"]["npv_eur"][0] / 1_000_000), 3)); single=simulate_cement_technology_npv("clinker_substitution", size=3, retrofit_bau_mode="deterministic"); print(single["technology_type"][0], single["retrofit_bau_mode"][0])'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement.cement_npv_monte_carlo import simulate_cement_results; from npv_summary import npv_ranking_dataframe; r=simulate_cement_results(sample_size=10, random_seed=7, technologies=("bau", "electrification", "ccs")); ranking=npv_ranking_dataframe(r, sector="cement"); print(ranking.shape); print(sorted(ranking["technology"].unique())); print(ranking.groupby("simulation_id").size().unique().tolist())'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c $'from cement.cement_npv_monte_carlo import simulate_cement_results\ntry:\n    simulate_cement_results(sample_size=1, retrofit_bau_mode="bad")\nexcept ValueError as exc:\n    print(str(exc))'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement.cement_npv_monte_carlo import simulate_cement_results; r=simulate_cement_results(sample_size=3, random_seed=1); assert all(set(len(value) for value in result.values()) == {3} for result in r.values()); print("all lengths ok")'`
  - `awk 'length($0) > 88 { print FNR ":" length($0) ":" $0 }' src/cement/cement_npv_monte_carlo.py`
- Result:
  - Passed.
- Notes:
  - Sampled BAU mode returned identical BAU CAPEX arrays for the `bau` result and the `ccs` retrofit baseline columns.
  - Deterministic BAU mode returned fixed `160 EUR/t` BAU CAPEX and `0.6 tCO2/t` BAU emissions baseline arrays for CCS.
  - The cement Monte Carlo result worked with `npv_summary.npv_ranking_dataframe`.
  - Invalid `retrofit_bau_mode` values raise a clear `ValueError`.

### Reproducibility notes

- No raw data, generated figures, generated CSVs, notebooks, or parameter values were changed.
- Main cement Monte Carlo runs can use `simulate_cement_results(sample_size=..., random_seed=..., retrofit_bau_mode="sampled")`.
- Diagnostic retrofit-only runs can use `retrofit_bau_mode="deterministic"` to isolate retrofit uncertainty from BAU uncertainty.

### Next suggested step

Add cement Monte Carlo summary/export scripts and notebooks that reuse the existing sector-agnostic NPV summary helpers.

## 2026-06-09 11:49 — Add cement source package and deterministic notebooks

### User request

Create a cement folder in `src` like the electricity sector and add deterministic notebooks for all cement technologies in `notebooks/cement`, following the deterministic electricity technology notebooks.

### Files changed (if needed)

- `src/cement/cement_parameters.py` — moved cement parameter definitions into a cement source package.
- `src/cement/cement_npv_deterministic.py` — moved deterministic cement NPV calculations into the cement source package and updated imports to `cement.cement_parameters`.
- `notebooks/cement/deterministic_bau_npv.ipynb` — added executed deterministic BAU cement notebook.
- `notebooks/cement/deterministic_electrification_npv.ipynb` — added executed deterministic electrification cement notebook.
- `notebooks/cement/deterministic_electrolysis_npv.ipynb` — added executed deterministic electrolysis cement notebook.
- `notebooks/cement/deterministic_clinker_substitution_npv.ipynb` — added executed deterministic clinker substitution retrofit notebook.
- `notebooks/cement/deterministic_alternative_fuels_npv.ipynb` — added executed deterministic alternative fuels retrofit notebook.
- `notebooks/cement/deterministic_efficiency_improvement_npv.ipynb` — added executed deterministic efficiency improvement retrofit notebook.
- `notebooks/cement/deterministic_waste_heat_recovery_npv.ipynb` — added executed deterministic waste heat recovery retrofit notebook.
- `notebooks/cement/deterministic_ccs_npv.ipynb` — added executed deterministic CCS retrofit notebook.
- `notebooks/cement/deterministic_process_heat_integration_npv.ipynb` — added executed deterministic process heat integration retrofit notebook.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Created `src/cement/` and moved the cement parameter and deterministic NPV modules into that sector folder, matching the existing `src/electricity/` layout.
- Updated deterministic cement imports so callers use `cement.cement_npv_deterministic` and the module imports `cement.cement_parameters`.
- Created one deterministic notebook for each cement technology in `notebooks/cement/`.
- Mirrored the deterministic electricity notebook structure: project path setup, shared source-code import, summary table, representative input table, and processed output table.
- Added a BAU-relative retrofit input table only for retrofit technologies, so retrofit notebooks show the CAPEX/OPEX changes and reduction fractions used to derive absolute cement values.
- Executed the notebooks in place so each notebook contains rendered deterministic outputs.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement/cement_parameters.py src/cement/cement_npv_deterministic.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement.cement_npv_deterministic import calculate_deterministic_cement_results; results=calculate_deterministic_cement_results(); print(sorted(results)); print(round(results["bau"]["npv_eur"][0] / 1_000_000, 3)); print(round(results["ccs"]["emissions_tco2_per_t"][0], 6))'`
  - `rg -n "from cement_parameters|import cement_parameters|from cement_npv_deterministic|import cement_npv_deterministic|from cement\\.cement_npv_deterministic|from cement\\.cement_parameters" src notebooks -S`
  - `/opt/anaconda3/envs/master-thesis/bin/jupyter nbconvert --execute --inplace notebooks/cement/deterministic_bau_npv.ipynb notebooks/cement/deterministic_electrification_npv.ipynb notebooks/cement/deterministic_electrolysis_npv.ipynb notebooks/cement/deterministic_clinker_substitution_npv.ipynb notebooks/cement/deterministic_alternative_fuels_npv.ipynb notebooks/cement/deterministic_efficiency_improvement_npv.ipynb notebooks/cement/deterministic_waste_heat_recovery_npv.ipynb notebooks/cement/deterministic_ccs_npv.ipynb notebooks/cement/deterministic_process_heat_integration_npv.ipynb`
  - `/opt/anaconda3/envs/master-thesis/bin/python -c 'import json; from pathlib import Path; paths=sorted(Path("notebooks/cement").glob("deterministic_*_npv.ipynb")); print(len(paths)); [print(path.name, len([c for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "code"]), [c.get("execution_count") for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "code"], sum(len(c.get("outputs", [])) for c in json.loads(path.read_text())["cells"] if c["cell_type"] == "code")) for path in paths]'`
  - `/opt/anaconda3/envs/master-thesis/bin/python -c 'import nbformat; from pathlib import Path; paths=sorted(Path("notebooks/cement").glob("deterministic_*_npv.ipynb")); [nbformat.validate(nbformat.read(path, as_version=4)) for path in paths]; print(len(paths), "cement notebooks validated")'`
- Result:
  - Passed.
- Notes:
  - The first in-sandbox notebook execution attempt failed because Jupyter could not bind local kernel ports under the sandbox. The same `nbconvert --execute --inplace` command was rerun with approved elevated permissions and completed successfully.
  - All nine deterministic cement notebooks validated as notebook format version 4.
  - All nine notebooks contain executed code cells and rendered outputs.

### Reproducibility notes

- No raw data, generated figures, generated CSVs, or numerical result files were changed.
- Cement code imports now use the sector package path, for example `from cement.cement_npv_deterministic import calculate_deterministic_cement_result`.
- The deterministic notebooks can be rerun with the same `jupyter nbconvert --execute --inplace notebooks/cement/deterministic_*_npv.ipynb` workflow.

### Next suggested step

Add cement deterministic summary/export scripts that aggregate these technology-level results for comparison figures and CSV outputs.

## 2026-06-09 11:34 — Move cement emissions conversion into parameters

### User request

Move the cement `tCO2` conversion into the parameter section and remove the conversion from deterministic cement NPV calculations.

### Files changed (if needed)

- `src/cement_parameters.py` — converted absolute cement emissions distributions from `kgCO2/t` values to `tCO2/t` values and exposed them under `emissions_tco2_per_t`.
- `src/cement_npv_deterministic.py` — removed the deterministic NPV-layer `kgCO2` to `tCO2` conversion and consumed `emissions_tco2_per_t` directly.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Converted BAU cement emissions from `600-700 kgCO2/t` to `0.600-0.700 tCO2/t`.
- Converted electrification cement emissions from `350-450 kgCO2/t` to `0.350-0.450 tCO2/t`.
- Converted electrolysis cement emissions from `60-140 kgCO2/t` to `0.060-0.140 tCO2/t`.
- Renamed the absolute cement technology registry key from `emissions_kgco2_per_t` to `emissions_tco2_per_t`.
- Updated deterministic retrofit calculations so BAU-relative emissions reductions operate on `tCO2/t` values directly.
- Kept the annual emissions cost and deterministic NPV results numerically unchanged, since this is a unit-boundary cleanup rather than a model-value change.

### Verification (if needed)

- Commands run:
  - `rg -n "emissions_kgco2_per_t|kgCO2/t" src -S`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py src/cement_npv_deterministic.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_TECHNOLOGY_DISTRIBUTIONS; from cement_npv_deterministic import calculate_deterministic_cement_result; bau_params=CEMENT_TECHNOLOGY_DISTRIBUTIONS["bau"]; print(bau_params["emissions_tco2_per_t"].mode, bau_params["emissions_tco2_per_t"].unit); bau=calculate_deterministic_cement_result("bau"); ccs=calculate_deterministic_cement_result("ccs"); print(round(bau["emissions_tco2_per_t"][0], 6)); print(round(ccs["emissions_tco2_per_t"][0], 6)); print("emissions_kgco2_per_t" in bau); print(round(bau["annual_emissions_cost_eur"][0] / 1_000_000, 3))'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_npv_deterministic import calculate_deterministic_cement_results; results=calculate_deterministic_cement_results(); print(sorted(results)); print(round(results["electrolysis"]["emissions_tco2_per_t"][0], 6)); print(round(results["ccs"]["annual_emissions_cost_eur"][0] / 1_000_000, 3)); print(round(results["bau"]["npv_eur"][0] / 1_000_000, 3))'`
- Result:
  - Passed.
- Notes:
  - Source code no longer contains the old `emissions_kgco2_per_t` key or `kgCO2/t` unit.
  - BAU parameters now report `0.6 tCO2/t`.
  - Deterministic BAU annual emissions cost remains `48.0 million EUR`, and deterministic BAU NPV remains `474.262 million EUR`.

### Reproducibility notes

- No raw data, generated figures, generated CSVs, notebooks, or model result files were changed.
- Existing downstream code should use `emissions_tco2_per_t` for absolute cement emissions.

### Next suggested step

Carry the same `emissions_tco2_per_t` convention into future cement Monte Carlo code and export schemas.

## 2026-06-09 11:25 — Add deterministic cement NPV calculations

### User request

Implement deterministic cement NPV values following the structure of the deterministic electricity NPV model, while applying retrofit technologies relative to BAU.

### Files changed (if needed)

- `src/cement_npv_deterministic.py` — added deterministic cement NPV calculation helpers for BAU, alternative cement technologies, and BAU-relative retrofit technologies.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a deterministic cement NPV module that mirrors the electricity deterministic workflow: representative parameter values, normalized annual output, revenue, cost components, annual net cash flow, and discounted NPV.
- Added absolute-value handling for BAU, electrification, and electrolysis using `CEMENT_TECHNOLOGY_DISTRIBUTIONS`.
- Added retrofit handling for clinker substitution, alternative fuels, efficiency improvement, waste heat recovery, CCS, and process heat integration using BAU representative values plus retrofit CAPEX/OPEX changes and BAU-relative reduction fractions.
- Converted cement emissions from `kgCO2/t` to `tCO2/t` before applying the shared carbon price.
- Used the existing coal price distribution as the cement thermal fuel-price source, except for the alternative-fuels retrofit, which uses the existing biofuel price distribution.
- Used the existing electricity price distribution for purchased electricity consumption.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_npv_deterministic.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_npv_deterministic import calculate_deterministic_cement_result, calculate_deterministic_cement_results; results=calculate_deterministic_cement_results(); print(sorted(results)); bau=calculate_deterministic_cement_result("bau"); ccs=calculate_deterministic_cement_result("ccs"); alt=calculate_deterministic_cement_result("alternative_fuels"); print(round(bau["fuel_consumption_mwh_th_per_t"][0], 6), round(ccs["fuel_consumption_mwh_th_per_t"][0], 6)); print(round(bau["electricity_consumption_mwh_per_t"][0], 6), round(ccs["electricity_consumption_mwh_per_t"][0], 6)); print(round(alt["fuel_price_eur_per_mwh_th"][0], 4)); print(round(results["bau"]["npv_eur"][0] / 1_000_000, 3))'`
  - `awk 'length($0) > 88 { print FNR ":" length($0) ":" $0 }' src/cement_npv_deterministic.py`
- Result:
  - Passed.
- Notes:
  - The smoke calculation returned all nine cement technologies.
  - Deterministic CCS resolved from BAU to `0.2135 MWh_th/t` fuel consumption and `0.156 MWh/t` electricity consumption, confirming that negative electricity reduction fractions increase BAU electricity use.
  - Alternative fuels used a deterministic biofuel price of `18.9 EUR/MWh_th`.

### Reproducibility notes

- No raw data, generated figures, generated CSVs, notebooks, or existing parameter values were changed.
- Deterministic cement outputs can be reproduced by importing `calculate_deterministic_cement_results()` from `src/cement_npv_deterministic.py` with `PYTHONPATH=src`.
- The fuel-price mapping is now an explicit modeling assumption in code: cement thermal fuel uses coal price except alternative fuels, which uses biofuel price.

### Next suggested step

Add cement deterministic CSV export and plotting wrappers that reuse the existing sector-agnostic NPV summary helpers.

## 2026-06-08 14:18 — Add annual cement output parameter

### User request

Add an annual cement output parameter equal to one million tonnes.

### Files changed (if needed)

- `src/cement_parameters.py` — added the normalized annual cement output fixed parameter and registered it with cement fixed parameters.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added `ANNUAL_CEMENT_OUTPUT_T` with value `1_000_000.0` and unit `t/year`.
- Registered it under `"annual_cement_output_t"` in `CEMENT_FIXED_PARAMETERS`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import ANNUAL_CEMENT_OUTPUT_T, CEMENT_FIXED_PARAMETERS; print(ANNUAL_CEMENT_OUTPUT_T.value, ANNUAL_CEMENT_OUTPUT_T.unit); print(CEMENT_FIXED_PARAMETERS["annual_cement_output_t"].value)'`
- Result:
  - Passed.

### Reproducibility notes

- Added one fixed cement-sector normalization assumption.
- No generated figures, generated CSVs, notebooks, NPV calculations, or existing technology parameter values were changed.

### Next suggested step

Use `ANNUAL_CEMENT_OUTPUT_T` when implementing cement NPV calculations.

## 2026-06-08 14:02 — Add process heat integration retrofit parameters

### User request

Add the final cement retrofit technology, process heat integration, using the same retrofit parameter structure.

### Files changed (if needed)

- `src/cement_parameters.py` — added process heat integration retrofit CAPEX change, fixed OPEX change, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a uniform process heat integration CAPEX increase distribution over `1-13 EUR/t`.
- Added a uniform fixed OPEX increase distribution over `0-0.5 EUR/t`.
- Added fixed zero variable OPEX change and electricity-consumption reduction.
- Added uniform fuel-consumption and emissions-reduction distributions, converting `3-30%` and `1-12%` to fractions `0.03-0.30` and `0.01-0.12`.
- Registered process heat integration under `"process_heat_integration"` in `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["process_heat_integration"]; print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_change_eur_per_t"].lower_bound, r["capex_change_eur_per_t"].upper_bound); print(r["fixed_opex_change_eur_per_t"].lower_bound, r["fixed_opex_change_eur_per_t"].upper_bound); print(r["variable_opex_change_eur_per_t"].value, r["electricity_consumption_reduction_fraction"].value); print(r["fuel_consumption_reduction_fraction"].lower_bound, r["fuel_consumption_reduction_fraction"].upper_bound); print(r["emissions_reduction_fraction"].lower_bound, r["emissions_reduction_fraction"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector process heat integration assumptions were added from the user-provided table only.
- Retrofit percentage values are stored as fractions for later calculations.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.

### Next suggested step

Implement the cement NPV logic that applies retrofit changes relative to the BAU cement baseline.

## 2026-06-08 13:56 — Add CCS retrofit parameters

### User request

Add the cement retrofit technology CCS using the same retrofit parameter structure.

### Files changed (if needed)

- `src/cement_parameters.py` — added CCS retrofit CAPEX change, fixed OPEX change, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a uniform CCS CAPEX increase distribution over `55-185 EUR/t`.
- Added a uniform fixed OPEX increase distribution over `4-10 EUR/t`.
- Added a uniform variable OPEX increase distribution over `0-3 EUR/t`.
- Added uniform fuel-consumption and emissions-reduction distributions, converting `0-130%` and `88-94%` to fractions `0-1.30` and `0.88-0.94`.
- Added a uniform electricity-consumption signed reduction distribution from `-2.60` to `0.70`, where the negative bound represents a `260%` increase.
- Registered CCS under `"ccs"` in `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["ccs"]; print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_change_eur_per_t"].lower_bound, r["capex_change_eur_per_t"].upper_bound); print(r["fixed_opex_change_eur_per_t"].lower_bound, r["fixed_opex_change_eur_per_t"].upper_bound); print(r["variable_opex_change_eur_per_t"].lower_bound, r["variable_opex_change_eur_per_t"].upper_bound); print(r["fuel_consumption_reduction_fraction"].lower_bound, r["fuel_consumption_reduction_fraction"].upper_bound); print(r["electricity_consumption_reduction_fraction"].lower_bound, r["electricity_consumption_reduction_fraction"].upper_bound); print(r["emissions_reduction_fraction"].lower_bound, r["emissions_reduction_fraction"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector CCS assumptions were added from the user-provided table only.
- Retrofit percentage values are stored as signed fractions for later calculations; positive values reduce BAU values and negative values increase them.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.

### Next suggested step

Add the next cement retrofit row to `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 13:42 — Add waste heat recovery retrofit parameters

### User request

Add the cement retrofit technology waste heat recovery using the same retrofit parameter structure.

### Files changed (if needed)

- `src/cement_parameters.py` — added waste heat recovery retrofit CAPEX change, fixed OPEX change, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a uniform waste heat recovery CAPEX increase distribution over `2-18 EUR/t`.
- Added a uniform fixed OPEX increase distribution over `0.1-0.5 EUR/t`.
- Added fixed zero variable OPEX change, fuel-consumption reduction, and emissions reduction.
- Added a uniform electricity-consumption reduction distribution, converting `17-40%` to fractions `0.17-0.40`.
- Registered waste heat recovery under `"waste_heat_recovery"` in `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["waste_heat_recovery"]; print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_change_eur_per_t"].lower_bound, r["capex_change_eur_per_t"].upper_bound); print(r["fixed_opex_change_eur_per_t"].lower_bound, r["fixed_opex_change_eur_per_t"].upper_bound); print(r["variable_opex_change_eur_per_t"].value, r["fuel_consumption_reduction_fraction"].value); print(r["electricity_consumption_reduction_fraction"].lower_bound, r["electricity_consumption_reduction_fraction"].upper_bound); print(r["emissions_reduction_fraction"].value)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector waste heat recovery assumptions were added from the user-provided table only.
- Retrofit percentage values are stored as fractions for later calculations.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.

### Next suggested step

Add the next cement retrofit row to `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 13:33 — Add efficiency improvement retrofit parameters

### User request

Add the cement retrofit technology efficiency improvement using the same retrofit parameter structure.

### Files changed (if needed)

- `src/cement_parameters.py` — added efficiency improvement retrofit CAPEX change, fixed OPEX change, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a uniform efficiency improvement CAPEX increase distribution over `0-28 EUR/t`.
- Added fixed zero fixed OPEX change and variable OPEX change.
- Added uniform fuel-consumption, electricity-consumption, and emissions-reduction distributions, converting `0-10%`, `0-20%`, and `0-2%` to fractions `0-0.10`, `0-0.20`, and `0-0.02`.
- Registered efficiency improvement under `"efficiency_improvement"` in `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["efficiency_improvement"]; print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_change_eur_per_t"].lower_bound, r["capex_change_eur_per_t"].upper_bound); print(r["fixed_opex_change_eur_per_t"].value, r["variable_opex_change_eur_per_t"].value); print(r["fuel_consumption_reduction_fraction"].lower_bound, r["fuel_consumption_reduction_fraction"].upper_bound); print(r["electricity_consumption_reduction_fraction"].lower_bound, r["electricity_consumption_reduction_fraction"].upper_bound); print(r["emissions_reduction_fraction"].lower_bound, r["emissions_reduction_fraction"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector efficiency improvement assumptions were added from the user-provided table only.
- Retrofit percentage values are stored as fractions for later calculations.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.

### Next suggested step

Add the next cement retrofit row to `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 13:18 — Add alternative fuels retrofit and biofuel price

### User request

Add the cement retrofit technology alternative fuels and add a general biofuel price range from `1.5-9 EUR/GJ`, converted to MWh.

### Files changed (if needed)

- `src/general_parameters.py` — added a uniform biofuel price distribution converted to `5.4-32.4 EUR/MWh_th`.
- `src/cement_parameters.py` — added alternative fuels retrofit CAPEX change, fixed OPEX change, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added `BIOFUEL_PRICE_DISTRIBUTION` as a uniform distribution over `5.4-32.4 EUR/MWh_th`, using `1 MWh = 3.6 GJ`.
- Registered biofuel price under `"biofuel_price_eur_per_mwh_th"` in `GENERAL_DISTRIBUTIONS`.
- Added a uniform alternative fuels CAPEX increase distribution over `0-2 EUR/t`.
- Added fixed zero fixed OPEX change, variable OPEX change, fuel-consumption reduction, and electricity-consumption reduction for alternative fuels.
- Added a uniform emissions-reduction distribution for alternative fuels, converting `3-17%` to fractions `0.03-0.17`.
- Renamed retrofit cost keys in `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS` to `capex_change_eur_per_t` and `fixed_opex_change_eur_per_t` so retrofit cost entries consistently represent changes relative to BAU.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/general_parameters.py src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from general_parameters import BIOFUEL_PRICE_DISTRIBUTION, GENERAL_DISTRIBUTIONS; from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["alternative_fuels"]; c=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["clinker_substitution"]; print(BIOFUEL_PRICE_DISTRIBUTION.lower_bound, BIOFUEL_PRICE_DISTRIBUTION.upper_bound, BIOFUEL_PRICE_DISTRIBUTION.unit); print("biofuel_price_eur_per_mwh_th" in GENERAL_DISTRIBUTIONS); print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_change_eur_per_t"].lower_bound, r["capex_change_eur_per_t"].upper_bound); print(r["fixed_opex_change_eur_per_t"].value, r["variable_opex_change_eur_per_t"].value, r["fuel_consumption_reduction_fraction"].value, r["electricity_consumption_reduction_fraction"].value); print(r["emissions_reduction_fraction"].lower_bound, r["emissions_reduction_fraction"].upper_bound); print(c["capex_change_eur_per_t"].value, c["fixed_opex_change_eur_per_t"].value)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector alternative fuels assumptions and the biofuel price range were added from the user-provided values only.
- The biofuel price conversion is `EUR/MWh_th = EUR/GJ * 3.6`.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.

### Next suggested step

Add the next cement retrofit row to `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 12:58 — Add clinker substitution retrofit parameters

### User request

Start the cement retrofit technologies by adding clinker substitution, treating positive percentages as reductions and negative percentages as increases for later retrofit logic.

### Files changed (if needed)

- `src/cement_parameters.py` — added clinker substitution retrofit CAPEX, fixed OPEX, variable OPEX change, fuel-consumption reduction, electricity-consumption reduction, and emissions-reduction assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added fixed zero CAPEX and fixed zero fixed OPEX for clinker substitution.
- Added a uniform variable OPEX increase distribution over `3.00-6.56 EUR/t`.
- Added uniform fuel-consumption reduction and emissions-reduction distributions, converting `15-25%` and `5-20%` to fractions `0.15-0.25` and `0.05-0.20`.
- Added a fixed zero electricity-consumption reduction.
- Added `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS` so retrofit measures remain separate from BAU and alternative technologies, because retrofit rows define changes relative to BAU rather than absolute technology intensities.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS, CEMENT_TECHNOLOGY_DISTRIBUTIONS; r=CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS["clinker_substitution"]; print(sorted(CEMENT_TECHNOLOGY_DISTRIBUTIONS)); print(sorted(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS)); print(r["capex_eur_per_t"].value, r["fixed_opex_eur_per_t"].value); print(r["variable_opex_change_eur_per_t"].lower_bound, r["variable_opex_change_eur_per_t"].upper_bound); print(r["fuel_consumption_reduction_fraction"].lower_bound, r["fuel_consumption_reduction_fraction"].upper_bound); print(r["electricity_consumption_reduction_fraction"].value, r["emissions_reduction_fraction"].lower_bound, r["emissions_reduction_fraction"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector clinker substitution assumptions were added from the user-provided table only.
- No generated figures, generated CSVs, notebooks, NPV calculations, electricity-sector assumptions, or existing cement technology parameter values were changed.
- Retrofit percentage values are stored as fractions for later calculations.

### Next suggested step

Add the next cement retrofit row to `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 12:52 — Add electricity price distribution to notebook

### User request

Include the electricity scaled beta distribution in the existing notebook that plots continuous and simulated gas and coal beta distributions.

### Files changed (if needed)

- `notebooks/plot_fuel_price_distributions.ipynb` — added electricity price imports, samples, continuous density curve, separate histogram, and overlay histogram.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Imported `ELECTRICITY_PRICE_DISTRIBUTION` from `general_parameters.py`.
- Sampled electricity prices with the same `sample_scaled_beta` helper, sample size, random seed, and RNG stream used for gas and coal.
- Added electricity to the continuous scaled beta plot.
- Expanded the simulated sample subplot layout from two to three panels so gas, coal, and electricity each have one histogram.
- Added electricity to the combined simulated histogram and updated plot titles/text from gas-and-coal wording to gas, coal, and electricity wording.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src MPLCONFIGDIR=/private/tmp/masterthesis_mpl /opt/anaconda3/envs/master-thesis/bin/python -m jupyter nbconvert --to notebook --execute notebooks/plot_fuel_price_distributions.ipynb --inplace --ExecutePreprocessor.timeout=120`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'import json; p="notebooks/plot_fuel_price_distributions.ipynb"; nb=json.load(open(p)); print(len(nb["cells"])); print("ELECTRICITY_PRICE_DISTRIBUTION" in "".join("".join(c.get("source", [])) for c in nb["cells"])); print([len(c.get("outputs", [])) for c in nb["cells"] if c["cell_type"] == "code"]); print("execution_counts", [c.get("execution_count") for c in nb["cells"] if c["cell_type"] == "code"])'`
  - `rg -n "electricity_samples|Electricity|Continuous scaled beta price|Gas, coal, and electricity|1, 3" notebooks/plot_fuel_price_distributions.ipynb -S`
- Result:
  - Passed.
- Notes:
  - The first notebook execution attempt failed inside the sandbox because Jupyter could not bind local kernel ports. The same command passed after rerunning with approved elevated execution.

### Reproducibility notes

- No parameter values, distribution definitions, generated CSVs, model code, or NPV calculations were changed.
- The notebook was executed in place, so its embedded plot outputs now reflect gas, coal, and electricity.

### Next suggested step

Use the updated notebook when visually checking shared market-price assumptions for electricity and cement calculations.

## 2026-06-08 11:26 — Add electrolysis cement parameters

### User request

Add the second alternative cement technology, electrolysis, using the same thesis workflow and cement-parameter structure.

### Files changed (if needed)

- `src/cement_parameters.py` — added electrolysis cement CAPEX, fixed OPEX, variable OPEX, fuel consumption, electricity consumption, and direct emissions assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added triangular distributions for electrolysis CAPEX, fixed OPEX, and variable OPEX using the provided base values as modes.
- Added fixed zero fuel consumption for electrolysis.
- Added uniform distributions for electrolysis electricity consumption and direct emissions because only ranges were provided.
- Registered electrolysis under `"electrolysis"` in the single `CEMENT_TECHNOLOGY_DISTRIBUTIONS` registry.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_TECHNOLOGY_DISTRIBUTIONS; e=CEMENT_TECHNOLOGY_DISTRIBUTIONS["electrolysis"]; print(sorted(CEMENT_TECHNOLOGY_DISTRIBUTIONS)); print(e["capex_eur_per_t"].minimum, e["capex_eur_per_t"].mode, e["capex_eur_per_t"].maximum); print(e["fixed_opex_eur_per_t"].minimum, e["fixed_opex_eur_per_t"].mode, e["fixed_opex_eur_per_t"].maximum); print(e["fuel_consumption_mwh_th_per_t"].value, e["electricity_consumption_mwh_per_t"].lower_bound, e["emissions_kgco2_per_t"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector electrolysis assumptions were added from the user-provided table only.
- No generated figures, generated CSVs, notebooks, NPV calculations, or electricity-sector assumptions were changed.

### Next suggested step

Add the next cement alternative technology row to `CEMENT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 11:22 — Add electrification cement parameters

### User request

Add the first alternative cement technology, electrification, using the same cement-parameter structure and distribution rules as before.

### Files changed (if needed)

- `src/cement_parameters.py` — added electrification cement CAPEX, fixed OPEX, variable OPEX, fuel consumption, electricity consumption, and direct emissions assumptions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added triangular distributions for electrification CAPEX, fixed OPEX, and variable OPEX using the provided base values as modes.
- Added fixed zero fuel consumption for electrification.
- Added uniform distributions for electrification electricity consumption and direct emissions because only ranges were provided.
- Registered electrification under `"electrification"` in the single `CEMENT_TECHNOLOGY_DISTRIBUTIONS` registry.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_TECHNOLOGY_DISTRIBUTIONS; e=CEMENT_TECHNOLOGY_DISTRIBUTIONS["electrification"]; print(sorted(CEMENT_TECHNOLOGY_DISTRIBUTIONS)); print(e["capex_eur_per_t"].minimum, e["capex_eur_per_t"].mode, e["capex_eur_per_t"].maximum); print(e["fuel_consumption_mwh_th_per_t"].value, e["electricity_consumption_mwh_per_t"].lower_bound, e["emissions_kgco2_per_t"].upper_bound)'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector electrification assumptions were added from the user-provided table only.
- No generated figures, generated CSVs, notebooks, NPV calculations, or electricity-sector assumptions were changed.

### Next suggested step

Add the next cement alternative technology row to `CEMENT_TECHNOLOGY_DISTRIBUTIONS`.

## 2026-06-08 11:16 — Align cement registry with electricity pattern

### User request

Clarify whether the extra cement mapping section is needed and keep the cement parameter structure consistent with electricity parameters.

### Files changed (if needed)

- `src/cement_parameters.py` — removed the cement-only BAU, alternative, and retrofit distribution registries and kept one combined technology registry.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Removed `CEMENT_BAU_TECHNOLOGY_DISTRIBUTIONS`, `CEMENT_ALTERNATIVE_TECHNOLOGY_DISTRIBUTIONS`, and `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS`.
- Kept `CEMENT_TECHNOLOGY_DISTRIBUTIONS` as the single registry for cement technologies, matching the electricity parameter module pattern.
- Kept the BAU technology key as `"bau"` so later cement model code can still distinguish BAU from alternatives and retrofits by technology identity.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from cement_parameters import CEMENT_TECHNOLOGY_DISTRIBUTIONS; bau=CEMENT_TECHNOLOGY_DISTRIBUTIONS["bau"]; print(sorted(CEMENT_TECHNOLOGY_DISTRIBUTIONS)); print(bau["capex_eur_per_t"].lower_bound, bau["emissions_kgco2_per_t"].mode)'`
- Result:
  - Passed.

### Reproducibility notes

- No cement parameter values, distributions, generated outputs, notebooks, or electricity-sector assumptions were changed.
- This task only simplified the cement parameter registry structure for consistency with the electricity module.

### Next suggested step

Add the next cement technology assumptions to the single `CEMENT_TECHNOLOGY_DISTRIBUTIONS` registry.

## 2026-06-08 11:11 — Add BAU cement parameters

### User request

Start the cement sector by adding BAU cement technology parameters in the same style as the electricity parameter module, while keeping BAU, alternatives, and retrofits separated for later modelling.

### Files changed (if needed)

- `src/cement_parameters.py` — added BAU cement CAPEX, fixed OPEX, variable OPEX, fuel consumption, electricity consumption, and direct emissions assumptions with cement-specific registries.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a uniform CAPEX distribution for BAU cement using the provided `150-170 EUR/t` range.
- Added triangular distributions for BAU cement fixed OPEX, variable OPEX, fuel consumption, electricity consumption, and emissions where the provided base value is stored as the triangular mode.
- Added separate `CEMENT_BAU_TECHNOLOGY_DISTRIBUTIONS`, `CEMENT_ALTERNATIVE_TECHNOLOGY_DISTRIBUTIONS`, and `CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS` registries, plus a combined `CEMENT_TECHNOLOGY_DISTRIBUTIONS` registry.
- Documented that BAU fuel consumption, electricity consumption, and emissions are absolute intensities, not percentage reductions.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'import numpy as np; from cement_parameters import CEMENT_BAU_TECHNOLOGY_DISTRIBUTIONS, CEMENT_ALTERNATIVE_TECHNOLOGY_DISTRIBUTIONS, CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS, CEMENT_TECHNOLOGY_DISTRIBUTIONS; from distributions import sample_triangular, sample_uniform; bau=CEMENT_BAU_TECHNOLOGY_DISTRIBUTIONS["bau"]; rng=np.random.default_rng(42); print(bau["capex_eur_per_t"].lower_bound, bau["capex_eur_per_t"].upper_bound, sample_uniform(bau["capex_eur_per_t"], 2, rng).shape); print(bau["fuel_consumption_mwh_th_per_t"].mode, sample_triangular(bau["fuel_consumption_mwh_th_per_t"], 2, rng).shape); print(len(CEMENT_ALTERNATIVE_TECHNOLOGY_DISTRIBUTIONS), len(CEMENT_RETROFIT_TECHNOLOGY_DISTRIBUTIONS), sorted(CEMENT_TECHNOLOGY_DISTRIBUTIONS))'`
- Result:
  - Passed.

### Reproducibility notes

- Cement-sector BAU assumptions were added from the user-provided table only.
- No generated figures, generated CSVs, notebooks, NPV calculations, or electricity-sector assumptions were changed.
- Alternative and retrofit cement registries are present but empty until those technology assumptions are provided.

### Next suggested step

Add the cement alternative technology rows next, then connect retrofit technologies to their BAU baseline when the cement NPV model is implemented.

## 2026-06-04 18:15 — Clarify beta-distribution concentration choice

### User request

Confirm whether the comments are sufficient for handover and add a note explaining that the beta-function concentration formula was chosen to achieve dome-shaped rather than U-shaped distributions.

### Files changed (if needed)

- `src/distributions.py` — added a comment explaining that the concentration factor, equivalent to the thesis model's `k` choice, keeps alpha and beta above 1 so the scaled beta distribution is dome-shaped rather than U-shaped.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a focused explanatory comment next to the scaled-beta concentration calculation.
- Kept the existing formula and distribution behavior unchanged.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/distributions.py`
- Result:
  - Passed.

### Reproducibility notes

- No model assumptions, parameter values, formulas, generated figures, generated CSVs, notebooks, or scientific conclusions were changed.
- This task only added explanatory documentation for the existing beta-distribution concentration choice.

### Next suggested step

If the final thesis uses a specific symbol for this concentration factor, align the code comment with that notation.

## 2026-06-04 18:02 — Deepen source-code handover comments

### User request

The first comment pass was too simple; expand the comments so people can understand what was done in the source code after handover.

### Files changed (if needed)

- `src/distributions.py` — expanded module/class/function docstrings to explain how parameter assumptions are stored separately from sampling.
- `src/general_parameters.py` — clarified why shared assumptions such as carbon price, discount rate, and fuel prices live outside sector modules.
- `src/cement_parameters.py` — added context for the current cement-sector parameter module structure.
- `src/npv_finance.py` — expanded NPV docstrings to explain the shared financial structure across sectors.
- `src/npv_summary.py` — expanded comments/docstrings for deterministic representative values, table exports, simulation-level ranking, and rank summaries.
- `src/npv_summary_plots.py` — expanded plotting comments/docstrings to explain mean bars, median markers, percentile whiskers, and rank-count heatmaps.
- `src/electricity/electricity_capacity_calculation.py` — explained why full-load hours determine required installed capacity for a normalized annual output.
- `src/electricity/electricity_parameters.py` — expanded comments around the electricity assumptions catalogue, normalized output, technology blocks, and parameter registries.
- `src/electricity/electricity_npv_monte_carlo.py` — expanded docstrings/comments for the Monte Carlo workflow, sampling, technology sizing, fuel-price mapping, cash-flow construction, result traceability, and run IDs.
- `src/electricity/electricity_npv_deterministic.py` — explained how deterministic calculations mirror Monte Carlo calculations using representative values.
- `src/electricity/electricity_npv_summary_figures.py` — expanded output-workflow documentation for raw versus processed CSVs, plot summaries, ranking outputs, and CLI regeneration behavior.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Replaced or supplemented terse comments with higher-context handover comments.
- Focused explanations on modelling intent, data flow, assumptions, reproducibility, and output interpretation.
- Kept the comments close to the code they explain so future readers can follow the model without searching elsewhere.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_finance.py src/general_parameters.py src/cement_parameters.py src/distributions.py src/npv_summary.py src/npv_summary_plots.py src/electricity/electricity_capacity_calculation.py src/electricity/electricity_parameters.py src/electricity/electricity_npv_monte_carlo.py src/electricity/electricity_npv_deterministic.py src/electricity/electricity_npv_summary_figures.py`
- Result:
  - Passed.

### Reproducibility notes

- No model assumptions, parameter values, random seeds, formulas, generated figures, generated CSVs, notebooks, or scientific conclusions were changed.
- This task only changed explanatory source comments and docstrings.

### Next suggested step

When the thesis text is finalized, align key terms in comments with the final thesis wording for NPV, raw inputs, processed outputs, and ranking probabilities.

## 2026-06-04 17:53 — Improve README and source-code comments

### User request

Update the README if needed and add simple comments across the source code so future readers can understand the implementation after handover.

### Files changed (if needed)

- `README.md` — closed the repository-structure code block and added a source-code guide plus the command for regenerating electricity outputs.
- `src/distributions.py` — added a short comment explaining scaled-beta normalization.
- `src/npv_finance.py` — added comments for the zero-discount case and NPV cash-flow timing.
- `src/npv_summary.py` — added comments for deterministic representative values, result table construction, and ranking semantics.
- `src/npv_summary_plots.py` — added comments for optional uncertainty plotting, reproducibility notes, and rank-count plotting.
- `src/electricity/electricity_npv_monte_carlo.py` — added comments/docstrings for sampling dispatch, output normalization, fuel-price mapping, cash-flow construction, and seeded simulation flow.
- `src/electricity/electricity_npv_deterministic.py` — added comments connecting deterministic calculations to the Monte Carlo structure.
- `src/electricity/electricity_npv_summary_figures.py` — added comments/docstrings for statistic extraction, shared simulation reuse, ranking exports, project-root resolution, and CLI output switches.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Updated the README so new project readers can find the main source modules and rerun the electricity output script.
- Added concise comments at handover-relevant points in the source code.
- Kept existing module docstrings and parameter section comments where they were already clear.
- Avoided line-by-line comments and did not refactor formulas or data flow.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_finance.py src/general_parameters.py src/cement_parameters.py src/distributions.py src/npv_summary.py src/npv_summary_plots.py src/electricity/electricity_capacity_calculation.py src/electricity/electricity_parameters.py src/electricity/electricity_npv_monte_carlo.py src/electricity/electricity_npv_deterministic.py src/electricity/electricity_npv_summary_figures.py`
- Result:
  - Passed.

### Reproducibility notes

- No model assumptions, parameter values, random seeds, formulas, generated figures, generated CSVs, notebooks, or scientific conclusions were changed.
- This task only changed documentation and source comments/docstrings.

### Next suggested step

Review the README source-code guide once more after the next major sector module is added, so it stays aligned with the project structure.

## 2026-06-04 17:42 — Centralize electricity summary notebook plotting

### User request

Move the remaining plotting code out of the electricity summary notebook so the notebook uses shared source plotting functions instead of carrying large local plot helper definitions.

### Files changed (if needed)

- `src/npv_summary_plots.py` — allowed `plot_average_rank_bars` to run in display-only mode with `output_path=None`, matching the mean-NPV plot helper behavior.
- `notebooks/electricity/electricity_summary.ipynb` — removed the helper section entirely, cleared stored execution outputs, and switched all plot rendering to shared plotting helpers.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- The electricity summary notebook now calls:
  - `plot_mean_npv_technology_bars(..., output_path=None)` for Monte Carlo mean NPV.
  - `plot_mean_npv_technology_bars(..., output_path=None)` for deterministic NPV.
  - `plot_average_rank_bars(..., output_path=None)` for ranking.
- Removed the notebook-local helper section entirely.
- Kept only direct per-section data transformations needed to feed the shared plotting functions.
- Removed notebook-local Matplotlib plotting functions for mean, deterministic, and ranking figures.
- Cleared notebook outputs and execution counts so the notebook remains lightweight and rerunnable.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary_plots.py`
  - `python3 -m json.tool notebooks/electricity/electricity_summary.ipynb`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - Passed.
  - The notebook is valid JSON.
  - All notebook code cells executed in memory with the thesis conda environment.
- Notes:
  - The dry run used `MPLBACKEND=Agg`, so Matplotlib reported expected non-interactive `plt.show()` warnings.

### Reproducibility notes

- No model assumptions, parameter values, random seed, sample size, ranking logic, NPV calculations, generated CSVs, or generated repository figures were changed.
- The notebook remains display-only: shared plotting functions are called with `output_path=None`.

### Next suggested step

If the deterministic plot should have a distinct visual style later, add that as another reusable source helper rather than putting plotting code back into the notebook.

## 2026-06-04 17:27 — Add random seed note to ranking plot

### User request

Add the random seed to the Monte Carlo NPV ranking plot, like the mean NPV plot already does.

### Files changed (if needed)

- `src/npv_summary_plots.py` — added an optional `random_seed` argument to the ranking plot helper and included it in the explanatory note.
- `src/electricity/electricity_npv_summary_figures.py` — passed the configured random seed through to the ranking plot helper.
- `figures/2026-06-04-Average_NPV_Rank_Electricity.png` — regenerated the ranking figure with the seed note.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Updated the bottom note of the ranking figure to include the random seed when one is provided.
- Threaded `random_seed` through the electricity ranking-output generation paths, including CLI generation and programmatic generation.
- Kept the ranking calculation and summary values unchanged.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary_plots.py src/electricity/electricity_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --no-data --ranking-output plots`
- Result:
  - Passed.
  - The regenerated ranking plot was visually inspected and now includes `random seed: 42` in the bottom explanatory note.

### Reproducibility notes

- No model assumptions, parameters, sample size, ranking logic, or NPV calculations were changed.
- The regenerated ranking figure uses the default 100,000-simulation electricity run with seed `42`.
- The command used `--no-data`, so no CSV outputs were regenerated.

### Next suggested step

Send the second requested change so it can be handled in the same focused way.

## 2026-06-04 17:16 — Reuse notebook-style uncertainty plot for mean NPV outputs

### User request

Follow the thesis workflow with a changelog entry, change the reusable plotting function to mirror the electricity summary notebook's Monte Carlo mean NPV graph, and update the notebook to use the shared function instead of keeping its own mean-NPV plot helper.

### Files changed (if needed)

- `src/npv_summary_plots.py` — extended `plot_mean_npv_technology_bars` with optional median markers, 5th-95th percentile whiskers, sample-size/seed notes, and display-only use with `output_path=None`.
- `src/electricity/electricity_npv_summary_figures.py` — added electricity NPV distribution-summary helpers and passed mean, median, and percentile values into the reusable plot function for simulated mean NPV figures.
- `notebooks/electricity/electricity_summary.ipynb` — changed the Monte Carlo mean NPV section to import and use `plot_mean_npv_technology_bars` instead of the notebook-local mean-NPV plotting helper.
- `figures/2026-06-04-Mean_NPV_Electricity.png` — regenerated the mean NPV figure with uncertainty whiskers and median markers.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Made the reusable mean-NPV bar plot match the notebook's improved visual structure:
  - Bars show mean NPV.
  - White circle markers show median NPV.
  - Whiskers show the simulated 5th-95th percentile range.
  - A note records sample size and random seed when provided.
- Preserved backwards compatibility: existing callers can still pass only mean values and an output path.
- Added `output_path=None` support so notebooks can display the shared plot inline without saving a figure.
- Updated the electricity summary notebook so the Monte Carlo mean plot uses the shared source function.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary_plots.py src/electricity/electricity_npv_summary_figures.py`
  - `python3 -m json.tool notebooks/electricity/electricity_summary.ipynb`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLBACKEND=Agg MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --no-data --ranking-output none`
- Result:
  - Passed.
  - Source modules compile.
  - The electricity summary notebook is valid JSON.
  - All notebook code cells executed in memory using the thesis conda environment.
  - The regenerated mean NPV figure was visually inspected and the legend no longer overlaps the plotted data.
- Notes:
  - The notebook dry run used `MPLBACKEND=Agg`, so Matplotlib reported expected non-interactive `plt.show()` warnings. These do not occur as a functional problem when running the notebook interactively.

### Reproducibility notes

- No model assumptions, parameter values, random seed, or NPV calculations were changed.
- The regenerated mean NPV figure uses the default 100,000-simulation electricity run with seed `42`.
- The summary notebook still does not save figures or CSV files; it displays the shared mean-NPV plot inline with `output_path=None`.

### Next suggested step

Consider using the same shared display-only pattern for the deterministic and ranking notebook plots if those should also be fully centralized in `src/`.

## 2026-06-04 16:51 — Standardize NPV output IDs and rank raw data location

### User request

Rename the detailed ranking data to raw ranking data, store it in the raw data folder, order the raw mean-NPV simulation data by simulation ID, and keep ID naming uniform so outputs do not mix `run_id` and `simulation_id`.

### Files changed (if needed)

- `src/npv_summary.py` — added optional CSV-export column renaming and sorting while preserving the existing result-combination helper.
- `src/electricity/electricity_npv_summary_figures.py` — exported mean NPV raw/processed CSVs with `simulation_id`, sorted run-level exports by simulation ID and technology, and moved ranking raw output to the raw data directory.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Changed the ranking raw export path from processed `NPV_Ranking_Electricity_detailed.csv` to raw `NPV_Ranking_Electricity_raw.csv`.
- Kept ranking summary output in `data/processed/` because it is aggregated/processed data.
- Sorted mean NPV raw input exports by `simulation_id` and `technology`.
- Also sorted mean NPV processed output exports by `simulation_id` and `technology` for consistency.
- Renamed exported `run_id` columns to `simulation_id` in raw and processed mean-NPV CSV outputs.
- Preserved internal simulation result keys as `run_id` to avoid a broad model refactor; the output layer now standardizes the naming.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary.py src/electricity/electricity_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --ranking-output both`
  - `head -n 12 data/raw/2026-06-04-NPV_Ranking_Electricity_raw.csv`
  - `head -n 12 data/raw/2026-06-04-Mean_NPV_Electricity_raw_inputs.csv`
  - `head -n 12 data/processed/2026-06-04-Mean_NPV_Electricity_processed_outputs.csv`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'import pandas as pd; paths=("data/raw/2026-06-04-Mean_NPV_Electricity_raw_inputs.csv","data/processed/2026-06-04-Mean_NPV_Electricity_processed_outputs.csv","data/raw/2026-06-04-NPV_Ranking_Electricity_raw.csv","data/processed/2026-06-04-NPV_Ranking_Electricity_summary.csv"); [print(p, "first_cols", pd.read_csv(p, nrows=5).columns[:3].tolist(), "has_run_id", "run_id" in pd.read_csv(p, nrows=0).columns, "has_simulation_id", "simulation_id" in pd.read_csv(p, nrows=0).columns) for p in paths]'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'import pandas as pd; checks=[]; paths=("data/raw/2026-06-04-Mean_NPV_Electricity_raw_inputs.csv","data/processed/2026-06-04-Mean_NPV_Electricity_processed_outputs.csv","data/raw/2026-06-04-NPV_Ranking_Electricity_raw.csv"); [checks.append((p, pd.read_csv(p, usecols=["simulation_id"])["simulation_id"].head(20).tolist(), bool(pd.read_csv(p, usecols=["simulation_id"])["simulation_id"].is_monotonic_increasing))) for p in paths]; [print(p, "first_sim_ids", ids, "monotonic", ok) for p, ids, ok in checks]'`
- Result:
  - Passed.
  - Generated outputs now include `data/raw/2026-06-04-NPV_Ranking_Electricity_raw.csv`.
  - Run-level raw and processed exports start with `simulation_id` and do not contain `run_id` in their headers.
  - Run-level raw and processed exports are monotonically ordered by `simulation_id`.
- Notes:
  - The old ignored file `data/processed/2026-06-04-NPV_Ranking_Electricity_detailed.csv` still exists locally from an earlier generation, but the code no longer writes it. It was not deleted because existing generated results should not be removed unless explicitly requested.

### Reproducibility notes

- No model assumptions, parameters, random seed, ranking method, or NPV calculations were changed.
- The output-location and exported-column-name changes affect generated CSV layout only.
- Regenerated CSV outputs use the default 100,000-simulation electricity run with seed `42`.

### Next suggested step

Delete or archive the old ignored `data/processed/2026-06-04-NPV_Ranking_Electricity_detailed.csv` file if you want the local data folder to contain only the current naming convention.

## 2026-06-04 16:39 — Rework electricity NPV rank figure and rank-count summary

### User request

Use the thesis workflow skill and improve the rank graph so all technologies use the same colour, labels clearly explain the ranking numbers, and the outputs show how often each technology reached ranks 1 through 9.

### Files changed (if needed)

- `src/npv_summary.py` — added per-rank count columns to the NPV ranking summary output.
- `src/npv_summary_plots.py` — redesigned the average-rank figure with one consistent bar colour, clearer labels, explanatory notes, and a rank-count heatmap.
- `src/electricity/electricity_npv_summary_figures.py` — passed human-readable electricity technology labels into the rank figure while keeping CSV technology codes unchanged.
- `figures/2026-06-04-Average_NPV_Rank_Electricity.png` — regenerated the electricity rank figure.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Kept the ranking logic unchanged: ranks are still calculated within each Monte Carlo simulation by NPV, with rank 1 meaning highest NPV.
- Added `rank_1_count` through `rank_9_count` columns to the ranking summary table.
- Reworked the rank graph into two coordinated panels:
  - Average rank bars, all using the same blue colour.
  - A same-palette count matrix showing how many simulations each technology reached each rank.
- Replaced terse labels like `P1` and `Top3` with explicit labels such as `rank 1` and `top 3`.
- Added an explanatory note to the figure with the ranking definition and sample size.

### Verification (if needed)

- Commands run:
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary.py src/npv_summary_plots.py src/electricity/electricity_npv_summary_figures.py`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --ranking-output both`
  - `MPLCONFIGDIR=/private/tmp/masterthesis_mpl PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from pathlib import Path; import pandas as pd; from electricity.electricity_npv_summary_figures import ELECTRICITY_TECHNOLOGY_LABELS; from npv_summary_plots import plot_average_rank_bars; summary=pd.read_csv("data/processed/2026-06-04-NPV_Ranking_Electricity_summary.csv"); summary=summary.assign(display_label=summary["technology"].map(ELECTRICITY_TECHNOLOGY_LABELS).fillna(summary["technology"])); print(plot_average_rank_bars(summary, Path("figures/2026-06-04-Average_NPV_Rank_Electricity.png"), title="Monte Carlo NPV Ranking"))'`
  - `PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'import pandas as pd; p="data/processed/2026-06-04-NPV_Ranking_Electricity_summary.csv"; df=pd.read_csv(p); cols=[c for c in df.columns if c.startswith("rank_") and c.endswith("_count")]; ok=(df[cols].sum(axis=1)==df["n_simulations"]).all(); print("counts sum to n_simulations", bool(ok))'`
- Result:
  - Passed.
  - The regenerated summary CSV contains rank-count columns from `rank_1_count` to `rank_9_count`.
  - The rank-count columns sum to `n_simulations` for every technology.
  - The updated figure was visually inspected and no longer uses mixed technology colours.
- Notes:
  - The full regeneration command produced the expected Matplotlib/macOS font setup messages. A redraw from the regenerated summary CSV was used for the final rank PNG and completed without the earlier layout warning.

### Reproducibility notes

- No model assumptions, parameters, random seed, ranking method, or NPV calculations were changed.
- The rank figure and processed ranking summary were regenerated for the 100,000-simulation electricity run with the default seed `42`.
- `data/processed/2026-06-04-NPV_Ranking_Electricity_summary.csv` and related generated data outputs are present locally but are not tracked by git; the tracked regenerated output is `figures/2026-06-04-Average_NPV_Rank_Electricity.png`.

### Next suggested step

Use the rank-count summary table in the thesis text to explain whether a technology is consistently strong or only occasionally reaches a high rank.

## 2026-06-04 14:31 — Move electricity source modules into package folder

### User request

Create a new `src/electricity/` folder and move all electricity-related source code there, while keeping general files and the cement parameter file at the first level of `src/`. Update code and notebook paths/imports accordingly.

### Files changed (if needed)

- `src/electricity/` — added the electricity source package.
- `src/electricity/__init__.py` — added package initialization.
- `src/electricity/electricity_capacity_calculation.py` — moved from `src/electricity_capacity_calculation.py`.
- `src/electricity/electricity_parameters.py` — moved from `src/electricity_parameters.py`.
- `src/electricity/electricity_npv_monte_carlo.py` — moved from `src/electricity_npv_monte_carlo.py` and updated package imports.
- `src/electricity/electricity_npv_deterministic.py` — moved from `src/electricity_npv_deterministic.py` and updated package imports.
- `src/electricity/electricity_npv_summary_figures.py` — moved from `src/electricity_npv_summary_figures.py` and updated package imports.
- `notebooks/electricity/*.ipynb` — updated electricity Monte Carlo and deterministic imports to use the new `electricity.` package path.

### What was implemented

- Grouped all electricity-specific reusable source files under `src/electricity/`.
- Left shared/general modules at first-level `src/`, including `distributions.py`, `general_parameters.py`, `npv_finance.py`, `npv_summary.py`, `npv_summary_plots.py`, and `cement_parameters.py`.
- Updated source imports from top-level electricity modules to explicit package imports, such as `electricity.electricity_npv_monte_carlo`.
- Updated electricity notebooks to import simulation and deterministic functions from the new package path.
- The summary CLI is now run as:
  - `PYTHONPATH=src python -m electricity.electricity_npv_summary_figures ...`

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py src/distributions.py src/general_parameters.py src/npv_finance.py src/npv_summary.py src/npv_summary_plots.py src/electricity/__init__.py src/electricity/electricity_capacity_calculation.py src/electricity/electricity_parameters.py src/electricity/electricity_npv_monte_carlo.py src/electricity/electricity_npv_deterministic.py src/electricity/electricity_npv_summary_figures.py`
  - `python3 -m json.tool notebooks/electricity/plot_pv_npv.ipynb`
  - `python3 -m json.tool notebooks/electricity/deterministic_pv_npv.ipynb`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -c 'from electricity.electricity_npv_monte_carlo import simulate_pv_npv; from electricity.electricity_npv_deterministic import calculate_deterministic_electricity_result; print(simulate_pv_npv(size=3)["technology"].tolist()); print(round(float(calculate_deterministic_electricity_result("pv")["npv_eur"][0]), 2))'`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind all --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-figures-electricity-package --raw-data-dir /private/tmp/mt-data-electricity-package/raw --processed-data-dir /private/tmp/mt-data-electricity-package/processed`
  - `rg -n "from electricity_npv_|import electricity_npv_|from electricity_parameters|import electricity_parameters|from electricity_capacity_calculation|import electricity_capacity_calculation|-m electricity_npv_summary_figures|src/electricity_npv_|src/electricity_parameters|src/electricity_capacity" src notebooks README.md docs -g "*.py" -g "*.ipynb" -g "*.md" -S`
- Result:
  - Passed with the thesis conda environment.
  - Representative notebooks remain valid JSON.
  - Runtime import smoke test returned PV simulation output and deterministic PV NPV.
  - The new package CLI generated test figures and CSVs in `/private/tmp`.
  - No stale top-level electricity import/module-path references remain in live source, notebooks, README, or docs.
- Notes:
  - Plain `python3` in this shell resolves to Python 3.9 and cannot run the project's newer type syntax in `npv_summary.py`; runtime verification used `/opt/anaconda3/envs/master-thesis/bin/python`.

### Reproducibility notes

- No model assumptions, parameter values, data, thesis outputs, or generated repository figures were changed.
- Existing commands that used `python -m electricity_npv_summary_figures` should now use `python -m electricity.electricity_npv_summary_figures`.

### Next suggested step

Update any external run scripts or personal notes outside this repository that still call the old top-level electricity module names.

## 2026-06-04 09:55 — Add reusable NPV technology summary figure generator

### User request

Create non-notebook code that generates and saves technology NPV comparison figures like the provided example, including one simulated mean-NPV version and one deterministic version, with reusable code that can later support sectors beyond electricity if possible.

### Files changed (if needed)

- `src/npv_summary_plots.py` — added sector-agnostic NPV bar-chart plotting helper and dated figure-path helper.
- `src/electricity_npv_summary_figures.py` — added electricity-sector simulated mean and deterministic NPV summary calculations, figure-saving functions, and command-line entry point.
- `figures/2026-06-04-Mean_NPV_Technology.png` — generated simulated mean NPV comparison figure.
- `figures/2026-06-04-Deterministic_NPV_Technology.png` — generated deterministic NPV comparison figure.

### What was implemented

- Added a reusable plotting function that accepts any mapping of display label to NPV value in million EUR.
- Added electricity-sector wrapper functions:
  - `calculate_mean_electricity_npv_million_eur`
  - `calculate_deterministic_electricity_npv_million_eur`
  - `save_electricity_mean_npv_figure`
  - `save_electricity_deterministic_npv_figure`
  - `save_electricity_npv_figures`
- Added a command-line interface:
  - `PYTHONPATH=src python3 -m electricity_npv_summary_figures --kind all --sample-size 100000 --random-seed 42`
- Added a Matplotlib-based plotting path with a Pillow fallback so PNG figures can still be generated in environments where Matplotlib is not installed.
- Saved figures to `figures/` using the requested date-stamped names:
  - `YYYY-MM-DD-Mean_NPV_Technology.png`
  - `YYYY-MM-DD-Deterministic_NPV_Technology.png`

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/npv_summary_plots.py src/electricity_npv_summary_figures.py src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `env PYTHONPATH=src python3 - <<'PY' ...`
  - `env PYTHONPATH=src python3 -m electricity_npv_summary_figures --kind all --sample-size 100000 --random-seed 42`
  - `env PYTHONPATH=src python3 -m electricity_npv_summary_figures --kind deterministic --output-dir /private/tmp/masterthesis_figures_test`
- Result:
  - Passed.
  - Both requested figure files were generated in `figures/`.
  - The deterministic-only command-line path generated a test figure in `/private/tmp/masterthesis_figures_test`.
  - The generated figures were visually inspected and match the requested positive/negative bar-chart style.

### Reproducibility notes

- The simulated mean-NPV figure uses a fixed default seed of `42` and default sample size of `100,000`, both configurable through CLI arguments.
- The plotting helper is sector-agnostic; future cement or other sector models can reuse `plot_mean_npv_technology_bars` once they provide technology labels and NPV values in million EUR.
- No model assumptions or parameter values were changed.

### Next suggested step

When cement NPV model outputs exist, add a small cement-sector wrapper that feeds cement technology NPVs into the same `npv_summary_plots.py` helper.

## 2026-06-04 09:20 — Review electricity NPV model assumptions and logic

### User request

Review the code in depth, checking assumptions, calculations, units, and whether it is plausible that only PV and wind have positive mean NPV under the current assumptions.

### Files changed (if needed)

- `CHANGELOG.md` — added this review entry only.

### What was implemented

- Reviewed the electricity NPV source code, general parameters, technology parameters, distribution helpers, cement parameter placeholder, and notebooks.
- Recomputed a 100,000-run electricity technology cost breakdown under the current assumptions.
- Checked whether the model equations and units are internally consistent.
- Identified model caveats and notebook-output risks for thesis interpretation.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - Source files compile.
  - All notebooks are valid JSON.
  - Cost breakdown confirmed that PV, onshore wind, and offshore wind are the only positive mean-NPV technologies under the current model assumptions.

### Reproducibility notes

- No model code, parameter values, notebooks, generated results, figures, reports, or PDFs were changed.
- The review found reproducibility and interpretation caveats that should be handled before final thesis use, especially unseeded plot notebooks, stale notebook outputs, shared lifetime, fixed electricity price, unused electricity-price distribution, and missing technology-specific capture prices.

### Next suggested step

Decide which model caveats should be fixed in code and which should be documented as limitations before using the current NPV comparison as a thesis result.

## 2026-06-04 09:09 — Add hard coal with CCS electricity NPV simulation

### User request

Add hard coal+CCS using the same style as the existing electricity technologies, with average full-load hours.

### Files changed (if needed)

- `src/electricity_parameters.py` — added hard coal+CCS CAPEX, fixed OPEX, variable OPEX, fuel-consumption, emissions, and full-load-hour assumptions.
- `src/electricity_model.py` — added hard coal+CCS coal-price mapping, simulation wrapper, and hard coal+CCS to the default multi-technology simulation.
- `notebooks/deterministic_hard_coal_ccs_npv.ipynb` — added deterministic hard coal+CCS NPV notebook.
- `notebooks/plot_hard_coal_ccs_npv.ipynb` — added hard coal+CCS Monte Carlo plotting notebook.

### What was implemented

- Added hard coal+CCS technology assumptions:
  - CAPEX: uniform `3,021-5,131 EUR/kW`.
  - Fixed OPEX: triangular `61.3 / 82.2 / 115.9 EUR/kW/year`.
  - Variable OPEX: triangular `8.0 / 10.73 / 15.1 EUR/MWh_e`.
  - Fuel consumption: uniform `3.08-3.24 MWh_th/MWh_e`.
  - Residual direct emissions: uniform `0.010-0.110 tCO2/MWh_e`.
  - Full-load hours: fixed average `(3,000 + 5,200) / 2 = 4,100 h/year`.
- Added `simulate_hard_coal_ccs_npv`.
- Updated `simulate_electricity_technologies_npv` to include `hard_coal_ccs` by default.
- Used the existing coal-price distribution and output key `coal_price_eur_per_mwh_th`.
- Added deterministic and plotting notebooks for hard coal+CCS using the same structure as the other electricity-technology notebooks.

### Verification (if needed)

- Commands run:
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 -m py_compile src/distributions.py src/general_parameters.py src/electricity_parameters.py src/electricity_model.py src/cement_parameters.py`
  - `python3 -m json.tool notebooks/deterministic_hard_coal_ccs_npv.ipynb`
  - `python3 -m json.tool notebooks/plot_hard_coal_ccs_npv.ipynb`
  - `for f in notebooks/*.ipynb; do python3 -m json.tool "$f" >/dev/null || exit 1; done; echo all-notebooks-valid`
  - `env PYTHONPYCACHEPREFIX=/private/tmp/masterthesis_pycache PYTHONPATH=src python3 - <<'PY' ...`
- Result:
  - Passed.
  - All notebooks are valid JSON.
  - The deterministic hard coal+CCS notebook executed and returned NPV `-778.264 million EUR`, or `-31.131 EUR/MWh`, with the current assumptions.
  - A 20,000-run hard coal+CCS sanity simulation returned mean NPV `-794.153 million EUR`, or `-31.766 EUR/MWh`.
  - Capacity, CAPEX, fixed OPEX, variable OPEX, fuel cost, emissions cost, annual net cash flow, lifetime-output, and NPV-per-MWh relationships passed for all electricity technologies.
  - Multi-technology results now include `hard_coal`, `hard_coal_ccs`, `ccgt`, `ccgt_ccs`, `nuclear`, `wind_offshore`, `wind_onshore`, `pv`, and `biogas` with aligned run IDs.

### Reproducibility notes

- This adds hard coal+CCS as a new electricity technology and changes the default multi-technology simulation output by including hard coal+CCS.
- No generated result files, figures, reports, or PDFs were written.
- Sanity check flags remain:
  - Plot notebooks still use `np.random.default_rng()` without a fixed seed, so Monte Carlo summaries are not exactly reproducible.
  - The model still uses one shared electricity lifetime parameter for all technologies.
  - The model still uses one fixed electricity retail-price revenue assumption for all technologies, without technology-specific capture prices.
  - `ELECTRICITY_PRICE_DISTRIBUTION` remains defined but unused by the electricity NPV model.
  - Hard coal+CCS uses residual direct emissions only; separate CO2 capture rate, captured CO2 mass flow, transport, storage, and CCS chain costs are not explicitly modeled unless already embedded in the user-provided CAPEX/OPEX values.

### Next suggested step

Compare hard coal+CCS and CCGT+CCS with explicit CCS transport and storage cost assumptions if those costs are not already embedded in the provided CAPEX/OPEX values.

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
## 2026-06-04 10:27 — Refactor NPV summary outputs

### User request

Review whether the electricity NPV summary figure code can be split into reusable sector-agnostic parts and whether raw/processed data should be saved as CSV files.

### Files changed (if needed)

- `src/npv_summary.py` — added reusable helpers for representative deterministic values, NPV summary aggregation, dated CSV paths, and CSV export.
- `src/electricity_npv_summary_figures.py` — refactored the electricity summary script to use reusable summary/export helpers and to save raw-input and processed-output CSV files.
- `src/npv_summary_plots.py` — updated the dated figure path docstring to reflect sector-based filenames.

### What was implemented

- Split sector-independent summary logic out of the electricity plotting script.
- Kept electricity-specific logic in the electricity adapter: technology labels, fuel-price mapping, deterministic electricity calculation, and raw/processed column definitions.
- Added CSV exports alongside figure generation:
  - Raw-input CSVs go to `data/raw/` by default.
  - Processed-output CSVs go to `data/processed/` by default.
- Added `--raw-data-dir`, `--processed-data-dir`, and `--no-data` CLI options.
- Kept the existing figure-only helper functions available for cases where only plots are needed.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary.py src/npv_summary_plots.py src/electricity_npv_summary_figures.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity_npv_summary_figures --kind all --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-figures --raw-data-dir /private/tmp/mt-data/raw --processed-data-dir /private/tmp/mt-data/processed`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - Passed.
- Notes:
  - The refactor preserved the previous mean and deterministic NPV values for the electricity summary.
  - The small-sample export check produced 45 simulation rows and 9 deterministic rows for each raw/processed split.

### Reproducibility notes

- Running `python -m electricity_npv_summary_figures` now saves figures plus CSV data by default.
- Use `--no-data` to reproduce the earlier figure-only behavior.
- No scientific assumptions or parameter values were changed.

### Next suggested step

When the cement model is added, reuse `src/npv_summary.py` for summary aggregation and CSV export, and only define cement-specific model calculations and column sets.
## 2026-06-04 11:19 — Split electricity NPV calculations

### User request

Create dedicated electricity Monte Carlo and deterministic NPV source files so summary figures and future analyses can reuse the calculation outputs without keeping model logic inside the summary script.

### Files changed (if needed)

- `src/electricity_npv_monte_carlo.py` — added the electricity Monte Carlo entry point and re-exported technology simulation functions from the existing electricity model.
- `src/electricity_npv_deterministic.py` — added deterministic electricity NPV calculations and all deterministic result outputs.
- `src/electricity_npv_summary_figures.py` — refactored the summary script to call the Monte Carlo and deterministic modules instead of containing deterministic model calculations itself.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Separated electricity calculation logic from electricity summary plotting/export logic.
- Kept `electricity_model.py` as the shared low-level calculation and notebook-compatible simulation module.
- Added `simulate_electricity_results()` in the Monte Carlo module for reusable multi-technology simulation outputs.
- Added deterministic result functions in the deterministic module:
  - `calculate_deterministic_electricity_result`
  - `calculate_deterministic_electricity_results`
  - `calculate_deterministic_electricity_npv_eur`
- Preserved existing summary helper names for calculating mean and deterministic NPV in million EUR.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/electricity_npv_monte_carlo.py src/electricity_npv_deterministic.py src/electricity_npv_summary_figures.py src/npv_summary.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity_npv_summary_figures --kind all --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-figures-refactor --raw-data-dir /private/tmp/mt-data-refactor/raw --processed-data-dir /private/tmp/mt-data-refactor/processed`
- Result:
  - Passed.
- Notes:
  - Mean and deterministic electricity summary values remained unchanged after the refactor.
  - Figure and CSV generation still works through the existing CLI.

### Reproducibility notes

- No model assumptions, parameters, generated thesis figures, or data files were changed in the repository.
- The summary CLI can still be run with `PYTHONPATH=src python -m electricity_npv_summary_figures`.
- Future ranking, sensitivity, or thesis table scripts can now consume the dedicated Monte Carlo and deterministic electricity result modules directly.

### Next suggested step

Use the same pattern for future sectors: sector-specific Monte Carlo and deterministic model files feeding reusable summary, ranking, plotting, and CSV export helpers.
## 2026-06-04 11:26 — Remove electricity Monte Carlo overlap

### User request

Clean up overlapping source files so the electricity Monte Carlo calculations are no longer split ambiguously between `electricity_model.py` and `electricity_npv_monte_carlo.py`.

### Files changed (if needed)

- `src/electricity_model.py` — reduced to low-level capacity, present-value-factor, and NPV helper formulas.
- `src/electricity_npv_monte_carlo.py` — moved the electricity Monte Carlo technology simulation logic into this module.
- `notebooks/electricity/plot_*_npv.ipynb` — updated plot notebook imports to use `electricity_npv_monte_carlo` for simulation functions.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Made `electricity_npv_monte_carlo.py` the single source for electricity Monte Carlo simulation runners.
- Kept `electricity_model.py` as the low-level formula module used by deterministic and Monte Carlo calculations.
- Removed the structural overlap where `electricity_npv_monte_carlo.py` merely wrapped simulation functions that still lived in `electricity_model.py`.
- Updated notebook imports so plot notebooks continue to run with the new module split.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/electricity_model.py src/electricity_npv_monte_carlo.py src/electricity_npv_deterministic.py src/electricity_npv_summary_figures.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity_npv_summary_figures --kind all --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-figures-cleanup --raw-data-dir /private/tmp/mt-data-cleanup/raw --processed-data-dir /private/tmp/mt-data-cleanup/processed`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - Passed.
- Notes:
  - Mean and deterministic electricity summary values were unchanged.
  - End-to-end figure and CSV generation still works.
  - Technology-level simulation imports used by the plot notebooks still work.

### Reproducibility notes

- No model assumptions, parameter values, generated thesis figures, or repository data files were changed.
- Monte Carlo simulation functions should now be imported from `electricity_npv_monte_carlo.py`.
- `electricity_model.py` should be treated as a shared formula helper module.

### Next suggested step

Use the same separation for future sectors: low-level formulas, sector Monte Carlo runner, sector deterministic runner, then summary/export code.
## 2026-06-04 11:39 — Refactor deterministic notebooks to source model

### User request

Change the deterministic electricity notebooks so they use the shared source code instead of duplicating the deterministic NPV calculations inside each notebook.

### Files changed (if needed)

- `notebooks/electricity/deterministic_biogas_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_ccgt_ccs_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_ccgt_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_hard_coal_ccs_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_hard_coal_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_nuclear_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_pv_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_wind_offshore_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `notebooks/electricity/deterministic_wind_onshore_npv.ipynb` — replaced duplicated deterministic calculations with a source-model call and overview tables.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Updated all deterministic electricity notebooks to call `calculate_deterministic_electricity_result()` from `src/electricity_npv_deterministic.py`.
- Replaced notebook-local model formulas with compact summary, representative-input, and processed-output tables.
- Cleared stale notebook outputs so old rendered numbers do not conflict with the source-driven calculation.
- Improved notebook source-path detection so the notebooks can find `src/` from nested notebook directories.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `rg "HARD_COAL|CCGT_|NUCLEAR_|WIND_|PV_|BIOGAS_|calculate_level_cash_flow|calculate_capacity" notebooks/electricity/deterministic_*_npv.ipynb`
  - `rg "calculate_deterministic_electricity_result" notebooks/electricity/deterministic_*_npv.ipynb`
- Result:
  - Passed.
- Notes:
  - Each deterministic notebook executed successfully from its code cells.
  - The deterministic NPV values matched the shared source model outputs.
  - No old per-technology parameter imports or duplicated deterministic formula calls remain in the deterministic notebooks.

### Reproducibility notes

- No scientific assumptions or parameter values were changed.
- Existing rendered notebook outputs were cleared and should be regenerated by running the notebooks.
- Deterministic notebook results now depend directly on `src/electricity_npv_deterministic.py`.

### Next suggested step

Use the same source-driven notebook style for any future deterministic sector notebooks.

## 2026-06-04 15:03 — Add Monte Carlo NPV ranking outputs

### User request

Add an NPV-based technology ranking feature to the existing Monte Carlo model, reusing current source structure, output folders, data handling, and plotting style.

### Files changed (if needed)

- `src/npv_summary.py` — added reusable sector-agnostic NPV ranking, ranking summary, and DataFrame CSV export helpers.
- `src/npv_summary_plots.py` — added an average-rank bar plot helper using the existing Matplotlib output style.
- `src/electricity/electricity_npv_summary_figures.py` — wired electricity Monte Carlo results into the ranking helpers and added flexible ranking CSV/plot output controls.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Created detailed ranking tables with `simulation_id`, `sector`, `technology`, `npv`, and `rank`.
- Ranked technologies within each simulation using pandas `rank(method="min", ascending=False)`, so highest NPV receives rank 1 and ties receive the same minimum rank.
- Created per-sector/per-technology ranking summaries with average rank, median rank, rank standard deviation, probability of rank 1, probability of top 3, and simulation count.
- Kept the ranking helpers sector-agnostic by accepting result mappings and sector names rather than hard-coding technology names.
- Added `generate_electricity_npv_rankings(...)` for DataFrame-first usage with `save_ranking_outputs`, `save_ranking_csv`, and `save_ranking_plots` switches.
- Added `--ranking-output {csv,plots,both,none}` to the electricity summary CLI.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/npv_summary.py src/npv_summary_plots.py src/electricity/electricity_npv_summary_figures.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-ranking-figures-both --raw-data-dir /private/tmp/mt-ranking-data-both/raw --processed-data-dir /private/tmp/mt-ranking-data-both/processed --ranking-output both`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-ranking-figures-csv --raw-data-dir /private/tmp/mt-ranking-data-csv/raw --processed-data-dir /private/tmp/mt-ranking-data-csv/processed --ranking-output csv`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-ranking-figures-plots --raw-data-dir /private/tmp/mt-ranking-data-plots/raw --processed-data-dir /private/tmp/mt-ranking-data-plots/processed --ranking-output plots`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-ranking-figures-none --raw-data-dir /private/tmp/mt-ranking-data-none/raw --processed-data-dir /private/tmp/mt-ranking-data-none/processed --ranking-output none`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity.electricity_npv_summary_figures --kind mean --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-ranking-figures-nodata --raw-data-dir /private/tmp/mt-ranking-data-nodata/raw --processed-data-dir /private/tmp/mt-ranking-data-nodata/processed --no-data --ranking-output plots`
- Result:
  - Passed.
- Notes:
  - DataFrame-only ranking returned the expected detailed and summary columns.
  - CSV-only, plot-only, both, none, and no-data plot modes worked with a five-simulation smoke test.
  - Matplotlib printed macOS static font registry messages during plot smoke tests, but output generation succeeded.

### Reproducibility notes

- No scientific assumptions, parameter values, NPV formulas, or random sampling logic were changed.
- Smoke-test outputs were written only to `/private/tmp/...`.
- To generate ranking outputs in the project folders, run the electricity summary script with `--ranking-output both`, `csv`, `plots`, or `none`.

### Next suggested step

Apply the same reusable ranking helpers when cement, aluminium, steel, or other sector Monte Carlo result mappings are added.

## 2026-06-04 15:23 — Fix electricity summary default output root

### User request

Fix the NPV summary output paths so generated figures and CSV files are stored in the repository-level `figures/` and `data/` folders instead of folders inside `src/`.

### Files changed (if needed)

- `src/electricity/electricity_npv_summary_figures.py` — corrected project-root detection for default output paths.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Changed `_project_root()` to resolve to the repository root from `src/electricity/electricity_npv_summary_figures.py`.
- The default CLI output directories now resolve to:
  - `figures/`
  - `data/raw/`
  - `data/processed/`

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/electricity/electricity_npv_summary_figures.py`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `ls -d figures data data/raw data/processed`
- Result:
  - Passed.
- Notes:
  - `_project_root()` now prints `/Users/finn/Desktop/MasterThesis`.
  - The import check printed Matplotlib/font-cache warnings because `MPLCONFIGDIR` was not set for that command, but the path verification completed successfully.

### Reproducibility notes

- No scientific assumptions, parameter values, formulas, or generated thesis results were changed by this code fix.
- Existing generated files under `src/data/` were not deleted or moved.

### Next suggested step

Clean up any accidentally generated `src/data/` or `src/figures/` outputs after deciding whether those files should be kept, moved, or removed.
## 2026-06-04 13:54 — Fix notebook imports and split generic NPV finance

### User request

Fix broken Monte Carlo notebook imports, check notebooks and source code connectivity, and improve the source structure so generic NPV formulas are separated from electricity-specific capacity calculations.

### Files changed (if needed)

- `src/npv_finance.py` — added sector-independent present-value-factor and NPV calculation helpers.
- `src/electricity_capacity_calculation.py` — added electricity-specific capacity calculations based on annual electricity output and FLH.
- `src/electricity_npv_monte_carlo.py` — updated Monte Carlo electricity NPV calculations to import NPV finance helpers from `npv_finance.py`.
- `src/electricity_npv_deterministic.py` — updated deterministic electricity NPV calculations to import electricity capacity helpers and generic NPV finance helpers from the new modules.
- `src/electricity_model.py` — removed the ambiguous legacy module after its functionality was split into generic finance and electricity capacity modules.
- `notebooks/electricity/plot_*_npv.ipynb` — fixed project-root detection so plot notebooks can import `src/` when run from `notebooks/electricity`.
- `notebooks/plot_fuel_price_distributions.ipynb` — fixed project-root detection consistently with the electricity notebooks.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Fixed the `ModuleNotFoundError` caused by plot notebooks resolving `src/` relative to `notebooks/electricity` instead of the repository root.
- Replaced the shallow notebook root detection with a robust upward search for the project directory containing `src/`.
- Split generic NPV finance logic from electricity-specific capacity logic:
  - `npv_finance.py` is sector-independent.
  - `electricity_capacity_calculation.py` is electricity-specific.
- Removed `electricity_model.py` to avoid keeping a misleading or duplicated source file.
- Checked that source imports now point to the intended modules and that notebooks no longer reference `electricity_model.py`.

### Verification (if needed)

- Commands run:
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement_parameters.py src/distributions.py src/electricity_capacity_calculation.py src/electricity_npv_deterministic.py src/electricity_npv_monte_carlo.py src/electricity_npv_summary_figures.py src/electricity_parameters.py src/general_parameters.py src/npv_finance.py src/npv_summary.py src/npv_summary_plots.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python -m electricity_npv_summary_figures --kind all --sample-size 5 --random-seed 42 --output-dir /private/tmp/mt-figures-final-check --raw-data-dir /private/tmp/mt-data-final-check/raw --processed-data-dir /private/tmp/mt-data-final-check/processed`
  - `rg "electricity_model|PROJECT_ROOT = Path.cwd\\(\\)\\.parent|from electricity_npv_monte_carlo import simulate_|from electricity_npv_deterministic import" src notebooks -n`
- Result:
  - Passed.
- Notes:
  - All source modules compiled and imported successfully.
  - All notebook setup/import cells ran successfully from their own notebook directories.
  - Deterministic notebooks executed successfully and returned the expected deterministic NPVs.
  - Monte Carlo technology functions returned expected result structures with small sample sizes.
  - Summary figure and CSV generation still works.
  - A full all-notebook plot execution test was stopped because plot rendering hung in Matplotlib/macOS GUI services; targeted notebook checks were used instead.

### Reproducibility notes

- No scientific assumptions or parameter values were changed.
- Key NPV values stayed unchanged after the refactor:
  - Mean PV NPV: 149.429 MEUR with 100,000 samples and seed 42.
  - Mean hard coal NPV: -715.789 MEUR with 100,000 samples and seed 42.
  - Deterministic PV NPV: 153.635 MEUR.
  - Deterministic hard coal NPV: -707.235 MEUR.
- Future sector NPV models should import `calculate_npv` from `npv_finance.py`.

### Next suggested step

Create the same model separation for future sectors: sector parameter file, sector-specific physical/capacity calculations, sector Monte Carlo runner, sector deterministic runner, and shared summary/export code.
## 2026-06-15 13:20 — Document sensitivity dashboard and stop server

### User request

Update the README and stop the running dashboard.

### Files changed (if needed)

- `README.md` — added the sensitivity dashboard to the repository structure,
  documented the sensitivity helper module, added dashboard launch commands, and
  summarized the dashboard metrics, tornado color meaning, saved-figure behavior,
  and deterministic scenario interpretation.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added a README section explaining how to run `sensitivity_dashboard.py` with
  Streamlit from the repository root or with the thesis Conda environment.
- Documented that the dashboard supports total NPV in `MEUR` and normalized NPV
  in `EUR/t` or `EUR/MWh`.
- Documented that green/red tornado bars indicate better/worse impact on the
  selected NPV metric, while the `+x%` or `-x%` label shows input direction.
- Stopped the Streamlit process that was listening on port `8501`.

### Verification (if needed)

- Commands run:
  - `sed -n '45,150p' README.md`
  - `kill 30823`
  - `lsof -iTCP:8501 -sTCP:LISTEN`
- Result:
  - Passed.
- Notes:
  - `lsof` returned no listener on port `8501` after stopping the dashboard.

### Reproducibility notes

- No model assumptions, calculations, data files, generated figures, or
  numerical results were changed.
- The README now records the command needed to restart the dashboard.

### Next suggested step

When the dashboard design stabilizes, add a short screenshot or example figure
reference to the README so future readers know what the tool produces.

## 2026-06-15 12:28 — Audit and improve dashboard tornado chart

### User request

Check whether the dashboard sensitivity analysis is correct, improve the tornado
plot readability after legend/label overlap, consider additional sensitivity
variables, and think about whether other plot designs would make sense.

### Files changed (if needed)

- `src/sensitivity_analysis.py` — moved the tornado legend below the plot,
  expanded the chart margin for input-change labels, renamed legend entries to
  clarify that colors mean better/worse NPV impact, and added missing technical
  drivers to the one-factor-at-a-time sensitivity list.
- `sensitivity_dashboard.py` — added full-load hours as an editable electricity
  input so electricity capacity sizing can be inspected directly.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Confirmed that the dashboard base-case NPV calculation reproduces the existing
  deterministic model for tested cement and electricity cases.
- Improved the tornado chart layout by moving the legend out of the top-right
  plotting area and giving the `+x%`/`-x%` labels more horizontal room.
- Added sensitivity rows for variables already present in the deterministic
  cash-flow equation:
  - cement: fuel use, electricity use, and direct emissions;
  - electricity: full-load hours, fuel use, and direct emissions.
- Kept green/red as economic direction:
  - green is better for the selected NPV metric;
  - red is worse for the selected NPV metric.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/sensitivity_analysis.py sensitivity_dashboard.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `/opt/anaconda3/envs/master-thesis/bin/streamlit run sensitivity_dashboard.py --server.headless true --server.port 8501`
- Result:
  - Passed.
- Notes:
  - The smoke test asserted that dashboard base-case NPV equals deterministic
    module NPV for cement BAU and electricity hard coal.
  - Expanded total and specific sensitivity plots were generated under
    `/private/tmp` for cement BAU and electricity hard coal.
  - Streamlit is running at `http://localhost:8501` with the refreshed code.

### Reproducibility notes

- No thesis parameter values or deterministic NPV formulas were changed.
- The dashboard remains a deterministic one-factor-at-a-time scenario tool.
- The current annual output sensitivity changes both output and required plant
  size/capacity because this matches the normalized deterministic model setup;
  it is not yet a pure utilization/sales-volume sensitivity with capacity held
  fixed.

### Next suggested step

Add a second sensitivity mode that varies utilization/output while holding
installed capacity fixed, then compare that with the current normalized
plant-size interpretation.

## 2026-06-15 11:59 — Clarify dashboard tornado direction and normalized metrics

### User request

Clarify whether the tornado chart's green and red bars represent `+10%` or
`-10%` input changes, and add a way to view sensitivity results as normalized
`EUR/t` or `EUR/MWh` instead of only total NPV.

### Files changed (if needed)

- `src/sensitivity_analysis.py` — added selectable total/specific NPV metrics,
  explicit tornado input-change labels, and metric-specific axis labels.
- `sensitivity_dashboard.py` — added an NPV metric selector, normalized headline
  metrics, metric-aware graph filenames, and sensitivity-table columns that show
  whether the favorable/unfavorable result came from `+x%` or `-x%`.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Kept the tornado colors as economic direction:
  - green means the changed input improves the selected NPV metric;
  - red means the changed input worsens the selected NPV metric.
- Added `+x%` and `-x%` labels next to each tornado bar so the input movement
  that produced each impact is visible directly on the chart.
- Added a dashboard selector for:
  - total NPV in `MEUR`;
  - specific NPV in `EUR/t` for cement;
  - specific NPV in `EUR/MWh` for electricity.
- Updated the sensitivity table to show favorable and unfavorable input-change
  directions alongside their impacts in the selected unit.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/sensitivity_analysis.py sensitivity_dashboard.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python sensitivity_dashboard.py`
- Result:
  - Passed.
- Notes:
  - The smoke test generated total and specific sensitivity plots for cement
    BAU and electricity PV under `/private/tmp`.
  - The smoke test confirmed direction labels such as `+10%` and `-10%` appear
    in the generated sensitivity tables.
  - Bare-mode Streamlit execution completed successfully; expected Streamlit
    context warnings and sandboxed PyArrow CPU-probe warnings were printed
    outside a real browser session.

### Reproducibility notes

- No thesis parameter values or deterministic NPV formulas were changed.
- Normalized dashboard metrics are calculated as `NPV / lifetime output` for
  the current scenario.
- The running dashboard server is still available at `http://localhost:8501`.

### Next suggested step

Review whether normalized sensitivity for changes to annual output and lifetime
should divide by the changed scenario's lifetime output, as implemented now, or
by the original base-case lifetime output for a pure numerator-only comparison.

## 2026-06-15 11:36 — Add sensitivity analysis dashboard

### User request

Create a sensitivity analysis dashboard with separate cement and electricity tabs,
technology selection, editable prices/lifetime/interest-rate style inputs, and
a savable tornado-style base sensitivity graph.

### Files changed (if needed)

- `src/sensitivity_analysis.py` — added reusable deterministic sensitivity
  calculations, tornado-table generation, and Matplotlib tornado plotting.
- `sensitivity_dashboard.py` — added a Streamlit dashboard with Cement and
  Electricity tabs, technology selectors, scenario input controls, chart
  downloads, saving to `figures/`, and a sensitivity-values table.
- `requirements.txt` — added `streamlit` as the dashboard dependency.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Built an interactive deterministic sensitivity dashboard around the existing
  deterministic NPV models rather than changing sector parameter assumptions.
- Added one-factor-at-a-time tornado analysis using the current scenario as the
  base case and a configurable percentage variation.
- Included editable controls for annual output, lifetime, interest rate, sales
  price, investment cost, OPEX, fuel price/use, emissions, carbon price, and
  cement electricity price/use.
- Added graph download and graph saving to `figures/` for the currently selected
  sector, technology, and scenario.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/sensitivity_analysis.py sensitivity_dashboard.py`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `/opt/anaconda3/envs/master-thesis/bin/python -m pip install streamlit`
  - `/opt/anaconda3/envs/master-thesis/bin/streamlit run sensitivity_dashboard.py --server.headless true --server.port 8501`
  - `env PYTHONPATH=src MPLCONFIGDIR=/private/tmp/matplotlib-cache /opt/anaconda3/envs/master-thesis/bin/python sensitivity_dashboard.py`
- Result:
  - Passed.
- Notes:
  - The smoke test calculated cement BAU and electricity PV sensitivity tables
    and wrote test PNGs under `/private/tmp`.
  - Matplotlib printed font-cache warnings in the sandboxed shell, but the plots
    were generated successfully.
  - The bare-mode Streamlit script execution completed successfully; expected
    Streamlit context warnings and sandboxed PyArrow CPU-probe warnings were
    printed outside a real browser session.
  - Streamlit is running at `http://localhost:8501`.

### Reproducibility notes

- No thesis parameter values or deterministic NPV formulas were changed.
- The dashboard recalculates deterministic scenario NPVs from existing base-case
  inputs and explicit user edits only.
- Saved dashboard figures are written to `figures/` when the in-app save button
  is pressed.

### Next suggested step

Review the tornado input list and decide whether technology-specific parameters
such as full-load hours, capture-rate assumptions, or retrofit reduction
fractions should also be exposed in the dashboard.

## 2026-06-23 12:40 — Remove misleading cement normalized MEUR/t output

### User request

Clarify the cement retrofit interpretation, remove the misleading million-euro-per-ton
cement output if needed, and provide clear project-improvement recommendations.

### Files changed (if needed)

- `src/cement/cement_npv_deterministic.py` — removed `npv_million_eur_per_t`
  from deterministic cement result mappings.
- `src/cement/cement_npv_monte_carlo.py` — removed `npv_million_eur_per_t`
  from Monte Carlo cement result mappings.
- `src/cement/cement_npv_summary_figures.py` — removed
  `npv_million_eur_per_t` from processed cement CSV export columns.
- `CHANGELOG.md` — added this entry.

### What was implemented

- Kept the existing cement retrofit methodology unchanged: retrofit technologies
  are still resolved as whole post-retrofit plant systems by combining sampled
  BAU assumptions with sampled retrofit changes.
- Removed the confusing `npv_million_eur_per_t` field from reusable source-code
  outputs and current cement processed CSV exports. Normalized cement NPV remains
  available as `npv_eur_per_t`.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m py_compile src/cement/cement_npv_deterministic.py src/cement/cement_npv_monte_carlo.py src/cement/cement_npv_summary_figures.py`
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
  - `rg -n "npv_million_eur_per_t" src`
- Result:
  - Passed.

### Reproducibility notes

- No model assumptions, formulas, sampled distributions, or retrofit calculations
  were changed.
- Existing notebooks may still contain old saved outputs or hard-coded references
  to `npv_million_eur_per_t`; reusable source outputs no longer expose it.

## 2026-06-24 — Add isolated CO2-price and discount-rate scenario notebook

### User request

Create a quick notebook following the sector summary-notebook logic, with separate
electricity and cement views for low, medium, and high CO2-price and discount-rate
scenarios, without changing the reusable `src/` code.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — added an isolated Monte Carlo
  scenario notebook with two cross-sector figures and editable scenario values.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Added one CO2-price scenario figure and one discount-rate scenario figure.
- Each figure contains separate electricity and cement panels and compares low,
  medium, and high scenarios for every technology.
- Reused one Monte Carlo simulation per sector across all scenarios so scenario
  differences reflect only the changed CO2 price or discount rate.
- Kept the current shared values of `80 EUR/tCO2` and `8%` as the medium cases.
- Added editable low/high defaults of `40/120 EUR/tCO2` and `4%/12%`, explicitly
  documented as notebook-only sensitivity assumptions.
- Added a switch between total NPV in million EUR and sector-specific NPV in
  EUR/MWh or EUR/t.
- Kept all calculations and plotting logic inside the notebook; no `src/` files
  or generated data/figure folders were changed.

### Verification (if needed)

- Commands run:
  - Notebook JSON validation and code-cell compilation.
  - Executed the notebook with the project Python environment.
- Result:
  - Passed.
- Notes:
  - The executed notebook copy was written only to
    `/private/tmp/masterthesis_scenario_notebook/executed.ipynb`.

### Reproducibility notes

- Rerun `notebooks/co2_discount_rate_scenarios.ipynb` from any directory inside
  the repository.
- The notebook defaults to 10,000 draws with random seed 42 and does not save
  outputs.
- Change only the settings cell to use alternative scenario values or normalized
  NPV units.

### Next suggested step

Review whether the low/high scenario assumptions should be replaced with values
from a cited policy or literature source.

## 2026-06-24 — Improve scenario plot layout and CCS label spacing

### User request

Remove the dash-like marks after technology names, move the low/medium/high
scenario legend out of the plot area, and consistently display spaces around the
plus sign in the hard-coal CCS label.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — removed visible y-axis tick
  marks and moved the shared scenario legend above both sector panels.
- `src/electricity/electricity_npv_summary_figures.py` — changed the shared
  display label from `Hard coal+CCS` to `Hard coal + CCS`.
- `notebooks/electricity/plot_hard_coal_ccs_npv.ipynb` — aligned the notebook
  heading and plot-title source text with the shared label style.
- `CHANGELOG.md` — added this implementation entry.

### What was implemented

- Disabled left-side y ticks so technology labels no longer appear to end in a
  dash.
- Replaced the in-axis legend with one figure-level legend centered above the
  electricity and cement panels.
- Reserved top layout space for the title and legend so neither overlaps the
  plots.
- Standardized the electricity summary display label as `Hard coal + CCS`.

### Verification (if needed)

- Commands run:
  - Notebook JSON validation and Python code-cell compilation.
  - Executed the scenario notebook with the project Python environment.
  - Searched source and notebook code for remaining `Hard coal+CCS` labels.
- Result:
  - Passed.
- Notes:
  - The scenario notebook executed without errors and rendered both figures.
  - Visual inspection confirmed that y-axis tick marks are hidden, the legend is
    outside the axes, and the shared label displays as `Hard coal + CCS`.

### Reproducibility notes

- No model assumptions, simulations, or numerical outputs were changed.
- Existing saved outputs in previously executed notebooks can retain the old
  label until those notebooks are rerun.
- The scenario notebook still writes no figures or data files.

### Next suggested step

Rerun the electricity summary notebook if its stored output cells should display
the updated `Hard coal + CCS` label immediately.

## 2026-06-24 — Analyze sector and technology scenario behavior

### User request

Provide an in-depth interpretation of both sectors and every technology under
the current assumptions and the notebook's CO2-price and discount-rate
scenarios, including why nuclear remains negative at the low discount rate.

### Files changed (if needed)

- `CHANGELOG.md` — documented the completed analytical review.

### What was implemented

- Reproduced the scenario notebook's 10,000-draw, seed-42 Monte Carlo setup.
- Calculated technology-level mean CAPEX, annual revenues and costs, annual net
  cash flow, mean and median NPV, positive-NPV probability, and scenario NPVs.
- Compared cement retrofit whole-plant NPVs against BAU and electricity CCS
  technologies against their unabated counterparts.
- Quantified nuclear's low-discount-rate result and identified its approximate
  mean break-even discount rate and required CAPEX or electricity-price change.

### Verification (if needed)

- Commands run:
  - Temporary Python analysis using the existing electricity and cement
    simulation modules and shared NPV function.
- Result:
  - Passed.
- Notes:
  - Temporary analysis code and outputs were kept under `/private/tmp`.

### Reproducibility notes

- No model code, parameter assumptions, notebooks, figures, or numerical output
  files were changed for this analysis.
- Reported scenario values use 10,000 draws, random seed 42, CO2 prices of
  40/80/120 EUR/tCO2, and discount rates of 4%/8%/12%.
- Each sensitivity changes one variable at a time; the notebook does not model a
  combined low-low or high-high scenario.

### Next suggested step

Add incremental-versus-BAU and incremental-versus-unabated comparison tables to
the scenario notebook so the economic value of retrofit and CCS choices is
visible alongside total plant NPV.

## 2026-06-24 — Add explicit scenario NPV scale selector and assess abatement costs

### User request

Add NPV-scale selection to the scenario notebook and assess whether cement
abatement cost would add useful information beyond NPV for a thesis about how
technology-development uncertainty shapes carbon-capture demand.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — replaced the less visible
  internal NPV mode with an explicit `NPV_SCALE` selector matching the summary
  notebook terminology.
- `CHANGELOG.md` — documented the implementation and analytical assessment.

### What was implemented

- Added `NPV_SCALE_OPTIONS = ("MEUR", "specific")` and an editable `NPV_SCALE`
  setting.
- Kept `MEUR` as the default and retained normalized output as EUR/MWh for
  electricity and EUR/t for cement.
- Displayed the selected scale when the settings cell runs.
- Calculated exploratory levelized direct-abatement costs for cement
  technologies relative to BAU using annualized CAPEX and operating costs,
  excluding carbon payments from the numerator.

### Verification (if needed)

- Commands run:
  - Notebook JSON validation and Python code-cell compilation.
  - Executed the scenario notebook at both supported NPV scales.
  - Temporary 100,000-draw cement abatement-cost analysis with random seed 42.
- Result:
  - Passed.
- Notes:
  - Both `MEUR` and `specific` modes executed without errors and rendered two
    scenario figures each.

### Reproducibility notes

- No source-code assumptions or model formulas were changed.
- Exploratory abatement-cost calculations were not added to the notebook in this
  task; they were used to determine whether the metric adds distinct insight.
- Abatement-cost estimates compare direct stack emissions with BAU and exclude
  indirect electricity emissions.

### Next suggested step

Add a dedicated cement marginal-abatement-cost and abatement-depth section that
reports both EUR/tCO2 avoided and the share of BAU direct emissions avoided.

## 2026-06-24 — Define electricity abatement-cost counterfactuals

### User request

Explain how an electricity-sector abatement-cost curve would be constructed and
whether it requires a BAU reference.

### Files changed (if needed)

- `CHANGELOG.md` — documented the methodological clarification.

### What was implemented

- Distinguished a system-wide electricity marginal abatement cost curve from
  pairwise technology comparisons.
- Identified coal, CCGT, and the grid mix as alternative counterfactuals with
  different interpretations.
- Recommended pairwise `coal + CCS versus coal` and `CCGT + CCS versus CCGT`
  avoided-cost calculations for the thesis's carbon-capture-demand question.

### Verification (if needed)

- Result:
  - Analytical clarification only; no model execution was required.

### Reproducibility notes

- No model assumptions, code, notebooks, figures, or numerical outputs were
  changed.

### Next suggested step

Define whether the electricity analysis should represent plant replacement,
new-build technology choice, or displacement of an observed grid mix before
constructing an electricity abatement curve.

## 2026-06-24 14:51 — Add NPV sign counts and improve project handover

### User request

Add a technology-summary metric counting simulations with NPV greater than or
equal to zero versus negative NPV, assess whether the current source code
supports it, and deep-dive the repository's clarity and usability for future
users.

### Files changed (if needed)

- `src/npv_summary.py` — added reusable, validated simulation sign summaries.
- `src/electricity/electricity_npv_summary_figures.py` — included NPV sign
  counts and non-negative share in electricity distribution summaries.
- `src/cement/cement_npv_summary_figures.py` — included the same metrics in
  cement distribution summaries.
- `notebooks/electricity/electricity_summary.ipynb` — displayed non-negative
  count, negative count, and non-negative share for every technology.
- `notebooks/cement/cement_summary.ipynb` — displayed the same metrics for
  every cement technology.
- `README.md` — added setup, smoke checks, workflow selection, cement output
  generation, generated-data guidance, and basic validation instructions.
- `docs/HANDOVER.md` — added a practical architecture, workflow, output,
  scientific-convention, risk, and safe-change guide.
- `requirements.txt` — documented the Python 3.10 minimum.
- `CHANGELOG.md` — documented this work.

### What was implemented

- Confirmed that each Monte Carlo result mapping retains its full
  simulation-level NPV array, so sign counts require no model or simulation
  changes.
- Classified exactly zero as non-negative, as requested.
- Added `non_negative_npv_count`, `negative_npv_count`, and
  `non_negative_npv_share`; rejected empty or non-finite arrays rather than
  silently producing incomplete counts.
- Reused the same helper in both sectors and both NPV scales. Positive scaling
  does not change an NPV's sign.
- Audited repository structure, runtime assumptions, notebook roles, ignored
  outputs, generated-data volume, validation coverage, and handover risks.
- Documented that the default 100,000-draw workflows can create large outputs
  and that the current ignored generated CSVs occupy roughly 1.5 GB.
- Documented the main remaining risks: no automated test suite, lightly
  constrained dependencies, `PYTHONPATH=src` execution, repeated notebook
  plotting code, and untracked generated outputs.

### Verification (if needed)

- Commands run:
  - `/opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src sensitivity_dashboard.py`
  - Direct helper assertions and 25-draw electricity/cement sign-summary checks.
  - 100-draw electricity and cement CLI smoke runs with temporary output
    directories, `--no-data`, and no ranking outputs.
  - JSON validation and code-cell compilation for both summary notebooks.
  - Full execution of both summary notebooks to temporary notebook files.
  - `git diff --check`
- Result:
  - Passed.
- Notes:
  - The machine's system Python 3.9 cannot import the project because the source
    uses Python 3.10 union type syntax. The thesis Python 3.12 environment
    completed all checks.

### Reproducibility notes

- No NPV formula, technology assumption, probability distribution, sample-size
  default, random seed, or scientific scenario was changed.
- Notebook verification outputs and smoke-test figures were written only under
  `/tmp`; tracked figures and ignored simulation CSVs were not regenerated or
  deleted.
- Stored outputs were cleared from the two modified summary notebooks so their
  previously displayed tables do not contradict the new source until users run
  all cells.
- Existing uncommitted sensitivity-analysis changes and figures were preserved
  and not modified as part of this task.

### Next suggested step

Add a small automated test suite for finance calculations, sign counts, shared
simulation IDs, and deterministic representative values before final archival.

## 2026-06-24 14:57 — Show NPV sign counts in technology notebooks

### User request

Make the non-negative and negative NPV simulation metrics visible in the
technology-specific plotting notebooks as well as the sector summary notebooks.

### Files changed (if needed)

- `notebooks/electricity/plot_*_npv.ipynb` — added the sign-count table to all
  nine electricity technology Monte Carlo notebooks.
- `notebooks/cement/plot_*_npv.ipynb` — added the sign-count table to all nine
  cement technology Monte Carlo notebooks.
- `README.md` — documented that technology notebooks show these metrics.
- `CHANGELOG.md` — documented this extension.

### What was implemented

- Imported the shared `summarize_metric_signs()` helper in every
  technology-specific plotting notebook.
- Added a two-row table for non-negative NPV (`NPV >= 0`) and negative NPV
  (`NPV < 0`), including simulation count and simulation share.
- Used total NPV in million EUR as the sign input. The sign is identical for the
  normalized EUR/MWh or EUR/t metric because those values differ only by a
  positive scale factor.
- Cleared stored notebook outputs so older tables do not remain visible beside
  the new source until the notebooks are rerun.

### Verification (if needed)

- Commands run:
  - JSON validation and code-cell compilation for all 18 technology notebooks.
  - Full temporary execution of `notebooks/electricity/plot_pv_npv.ipynb`.
  - Full temporary execution of `notebooks/cement/plot_ccs_npv.ipynb`.
  - `/opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src`
  - `git diff --check`
- Result:
  - Passed.
- Notes:
  - Both representative executed notebooks displayed the category, count, and
    share columns correctly.

### Reproducibility notes

- No simulation assumptions, NPV formulas, sample-size defaults, or random
  seeds changed.
- Verification notebooks were written under `/tmp`; no data CSVs or figures
  were regenerated.

### Next suggested step

Run all technology notebooks before final archival if stored rendered outputs
are desired in the repository.

## 2026-06-24 15:10 — Assess fuel-use and emissions dependence

### User request

Assess whether independently sampling fuel consumption and direct emissions is
appropriate in the electricity and cement Monte Carlo models.

### Files changed (if needed)

- `CHANGELOG.md` — documented the model-design assessment.

### What was implemented

- Inspected electricity and cement parameter definitions and Monte Carlo
  sampling paths.
- Confirmed that fuel consumption and emissions are sampled independently in
  the current model.
- Recommended deriving unabated fossil-electricity emissions from sampled fuel
  consumption and a fuel-specific carbon factor.
- Recommended deriving CCS residual emissions from gross fuel-related emissions
  and a sampled capture rate, with any capture-rate and energy-penalty
  dependence stated explicitly.
- Recommended decomposing cement emissions into combustion and process
  components instead of imposing one generic correlation coefficient.

### Verification (if needed)

- Commands run:
  - Temporary 10,000-draw electricity and cement simulations using random seed
    42, followed by Pearson correlation checks.
- Result:
  - The sampled fuel-use/emissions correlations were approximately zero for all
    checked technologies, confirming the independent-draw behavior.

### Reproducibility notes

- No source code, parameters, assumptions, notebooks, figures, or simulation
  outputs were changed.
- The diagnostic calculation was run in memory only.

### Next suggested step

Implement and compare a mechanistic emissions model first for hard coal and
CCGT, then quantify its effect on NPV distributions and rankings before
extending the approach to CCS and cement.

## 2026-06-24 15:24 — Clarify independence assumption defensibility

### User request

Assess whether the thesis can retain separate sampling of fuel consumption and
emissions as a simplifying assumption.

### Files changed (if needed)

- `CHANGELOG.md` — documented the methodological guidance.

### What was implemented

- Clarified that separate random draws imply statistical independence, not only
  a computational simplification.
- Assessed the assumption as potentially acceptable when explicitly disclosed,
  justified by data limitations, and tested for material influence on results.
- Distinguished the relatively weak case for independent sampling in unabated
  coal and gas generation from the more defensible simplification in cement,
  where process and combustion emissions are not represented separately.

### Verification (if needed)

- Result:
  - Methodological assessment only; no model execution was required.

### Reproducibility notes

- No model assumptions, source code, notebooks, figures, or numerical outputs
  were changed.

### Next suggested step

Run one coupled-versus-independent sensitivity comparison for coal and CCGT and
report whether technology rankings or positive-NPV probabilities change
materially.

## 2026-06-26 09:45 — Add selectable sensitivity heatmap notebook

### User request

Create a user-friendly notebook for the sensitivity heatmap, similar to the
scenario notebook, with a selectable total-NPV or specific-NPV metric.

### Files changed (if needed)

- `src/sensitivity_deep_dive.py` — added metric selection to the standardized
  heatmap workflow and exposed a notebook-friendly heatmap figure builder.
- `notebooks/sensitivity_heatmap.ipynb` — added an editable notebook for
  calculating, displaying, and optionally saving cement and electricity
  sensitivity heatmaps.
- `CHANGELOG.md` — documented the change.

### What was implemented

- Added `metric` support to `standardized_sensitivity()`, `plot_sensitivity_heatmap()`,
  and `generate_deep_dive()`.
- Preserved specific NPV as the default heatmap metric for existing behavior.
- Added `--metric specific|total` to the sensitivity deep-dive CLI.
- Added inline notebook heatmap display through `build_sensitivity_heatmap_figure()`.
- Added optional notebook saving of the standardized CSV and heatmap PNG files.
- Made saved sensitivity filenames include both the selected NPV metric and the
  selected variation percentage.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/sensitivity_deep_dive.py src/sensitivity_analysis.py`
  - Notebook JSON/code-cell compile check for `notebooks/sensitivity_heatmap.ipynb`
- Result:
  - Source and notebook code cells compiled successfully.
  - Full heatmap execution could not be run in the current bare Python
    environment because `matplotlib` is not installed there.

### Reproducibility notes

- The notebook displays outputs inline by default and writes no CSV or figure
  files unless `SAVE_OUTPUTS = True`.
- No raw data, model parameters, or generated thesis figures were overwritten.

### Next suggested step

Run `notebooks/sensitivity_heatmap.ipynb` in the thesis Jupyter environment once
with `NPV_METRIC = METRIC_SPECIFIC` and once with `NPV_METRIC = METRIC_TOTAL` to
inspect whether the normalized driver rankings differ materially.

## 2026-06-26 09:51 — Align cross-sector notebook NPV metric controls

### User request

Make the NPV metric selection uniform between the scenario and sensitivity
notebooks, while leaving the sector-specific summary notebooks unchanged.

### Files changed (if needed)

- `notebooks/co2_discount_rate_scenarios.ipynb` — replaced the local
  `NPV_SCALE = "MEUR" / "specific"` setting with the shared
  `NPV_METRIC = METRIC_TOTAL / METRIC_SPECIFIC` convention.
- `CHANGELOG.md` — documented the follow-up alignment.

### What was implemented

- Imported `METRIC_TOTAL` and `METRIC_SPECIFIC` from `sensitivity_analysis`.
- Updated the scenario notebook settings cell to use the same metric constants
  as `notebooks/sensitivity_heatmap.ipynb`.
- Updated scenario metric conversion and axis-label logic to read
  `NPV_METRIC`.
- Left the electricity and cement summary notebooks unchanged because their
  sector-specific scale labels remain appropriate there.

### Verification (if needed)

- Commands run:
  - Searched both cross-sector notebooks for leftover `NPV_SCALE` references.
  - Compiled all code cells in `notebooks/co2_discount_rate_scenarios.ipynb`.
  - Compiled all code cells in `notebooks/sensitivity_heatmap.ipynb`.
- Result:
  - No leftover `NPV_SCALE` references were found.
  - Both notebooks' code cells compiled successfully.

### Reproducibility notes

- This is a naming/control alignment only.
- No scenario values, model parameters, raw data, generated figures, or numerical
  outputs were changed.

### Next suggested step

When running cross-sector notebooks, use `NPV_METRIC = METRIC_TOTAL` for total
project NPV and `NPV_METRIC = METRIC_SPECIFIC` for sector-normalized NPV.

## 2026-06-26 10:11 — Add cement marginal abatement cost curve code

### User request

Create cement-specific code for a marginal abatement cost curve, using only
direct technology abatement rather than CO2-price offsets, and explain the
calculation for CCS and clinker substitution.

### Files changed (if needed)

- `src/cement/cement_macc.py` — added deterministic and simulated cement MACC
  table builders, a MACC plotting function, and a CLI output generator.
- `CHANGELOG.md` — documented the change.

### What was implemented

- Added cement MACC calculations relative to the BAU cement baseline.
- Defined abatement potential as annual direct stack-emissions reduction:
  `BAU emissions - technology emissions`.
- Excluded cement revenue and carbon-price payments from the cost numerator.
- Calculated annualized technology cost as annualized CAPEX plus fixed OPEX,
  variable OPEX, fuel cost, and electricity cost.
- Calculated MACC values as incremental annual cost versus BAU divided by annual
  direct emissions avoided versus BAU.
- Added a MACC bar plot where bar width is direct abatement potential and bar
  height is abatement cost in EUR/tCO2.
- Added deterministic and mean Monte Carlo modes.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/cement/cement_macc.py`
  - Attempted deterministic and simulated MACC table smoke tests.
- Result:
  - The new module compiled successfully.
  - Runtime smoke tests could not be completed in the current shell because the
    available `python3` is Python 3.9.6, while the project requires Python >=
    3.10 and existing project modules use Python 3.10 type-union syntax.

### Reproducibility notes

- No raw data, model parameters, generated figures, or numerical outputs were
  changed.
- The MACC generator writes CSV and PNG outputs only when called explicitly.
- The calculation uses the shared thesis discount rate for annualized CAPEX.

### Next suggested step

Run `PYTHONPATH=src python -m cement.cement_macc` in the thesis Python 3.10+
environment to generate the deterministic cement MACC CSV and figure, then run
with `--simulated` if uncertainty bands or simulated mean values are needed.

## 2026-06-26 10:21 — Stabilize simulated cement MACC statistics and labels

### User request

Check why simulated efficiency improvement showed an implausibly large negative
abatement cost, add median/p05/p95 statistics, and improve MACC plot labels.

### Files changed (if needed)

- `src/cement/cement_macc.py` — revised simulated MACC statistics and label
  placement.
- `CHANGELOG.md` — documented the fix.

### What was implemented

- Changed the headline abatement-cost statistic to the aggregate ratio of mean
  incremental annual cost to mean annual direct abatement.
- Added draw-level abatement-cost p05, median, and p95 columns.
- Kept the draw-level quantiles visible so technologies with small-abatement
  tails remain transparent instead of hidden.
- Reworked MACC labels to appear vertically above the zero line with leader
  lines, improving readability for narrow bars.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/cement/cement_macc.py`
- Result:
  - The module compiled successfully.
  - Full runtime checks remain blocked in the current shell because the
    available Python is 3.9.6 and the project requires Python >= 3.10.

### Reproducibility notes

- No raw data, model parameters, or model formulas were changed.
- The simulated efficiency-improvement issue was a summary-statistic problem:
  averaging draw-level ratios allowed near-zero abatement draws to dominate the
  reported mean.

### Next suggested step

Regenerate the simulated MACC output in the thesis Python 3.10+ environment and
inspect the p05/median/p95 columns for technologies with low direct-abatement
potential.

## 2026-06-26 10:38 — Improve cement MACC label placement

### User request

Fix the cement MACC plot labels because they interfered with the title and make
the direct-abatement-potential numbers easier to read.

### Files changed (if needed)

- `src/cement/cement_macc.py` — adjusted MACC plot label and width-number
  placement.
- `CHANGELOG.md` — documented the change.

### What was implemented

- Moved vertical technology labels closer to the zero line instead of placing
  them near the top of the plot.
- Added title padding and additional upper-axis room to prevent label-title
  overlap.
- Rotated the direct-abatement-potential numbers diagonally below the bars.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/cement/cement_macc.py`
- Result:
  - The module compiled successfully.

### Reproducibility notes

- Plot formatting only; no calculations, model assumptions, parameters, raw
  data, or generated outputs were changed by this edit.

### Next suggested step

Regenerate the MACC figure in the thesis Python 3.10+ environment to visually
inspect the updated label spacing.

## 2026-06-26 10:42 — Align cement MACC labels and width values

### User request

Make all cement MACC technology labels equally far from the zero line and place
direct-abatement-potential numbers closer to the zero line or, for negative-cost
bars, closer to the bar.

### Files changed (if needed)

- `src/cement/cement_macc.py` — refined MACC label placement.
- `CHANGELOG.md` — documented the change.

### What was implemented

- Set all technology labels to the same vertical distance above the zero line.
- Kept leader lines from the zero line to each vertical technology label.
- Placed diagonal abatement-potential numbers just below the zero line for
  positive-cost bars.
- Placed diagonal abatement-potential numbers just below negative-cost bars for
  negative-cost bars.

### Verification (if needed)

- Commands run:
  - `python3 -m py_compile src/cement/cement_macc.py`
- Result:
  - The module compiled successfully.

### Reproducibility notes

- Plot formatting only; no calculations, model assumptions, parameters, raw
  data, or generated outputs were changed by this edit.

### Next suggested step

Regenerate the MACC figure in the thesis Python 3.10+ environment to visually
confirm the adjusted label positions.

## 2026-06-26 10:45 — Add cement MACC notebook

### User request

Create a notebook for the cement marginal abatement cost curve that uses the
existing source code.

### Files changed (if needed)

- `notebooks/cement/cement_macc.ipynb` — added a user-friendly notebook wrapper
  around `src/cement/cement_macc.py`.
- `CHANGELOG.md` — documented the notebook addition.

### What was implemented

- Added editable notebook settings for deterministic versus simulated MACC mode.
- Added controls for sample size, random seed, retrofit BAU mode, selected
  technologies, and optional output saving.
- Displayed the MACC table inline.
- Displayed the MACC plot inline using `plot_cement_macc()`.
- Kept file writing optional through `SAVE_OUTPUTS = False` by default.

### Verification (if needed)

- Commands run:
  - Notebook JSON and code-cell compile check for
    `notebooks/cement/cement_macc.ipynb`.
  - `python3 -m py_compile src/cement/cement_macc.py`
- Result:
  - The notebook JSON and code cells compiled successfully.
  - The MACC source module compiled successfully.

### Reproducibility notes

- The notebook uses existing reusable source code rather than duplicating MACC
  formulas.
- No raw data, model parameters, generated figures, or numerical outputs were
  changed by this notebook addition.
- Outputs are written only if `SAVE_OUTPUTS = True`.

### Next suggested step

Run `notebooks/cement/cement_macc.ipynb` in the thesis Python 3.10+ Jupyter
environment and inspect the deterministic and simulated modes.

## 2026-06-29 — Recalculate sector and technology interpretation after parameter updates

### User request

Redo the in-depth analysis of both sectors and all technologies after parameter
updates, including normal conditions and the CO2-price and discount-rate
scenario behavior.

### Files changed (if needed)

- `CHANGELOG.md` — documented the refreshed analytical check.

### What was implemented

- Re-ran the current electricity and cement Monte Carlo models with 100,000
  draws and random seed 42.
- Revalued the simulated cash flows under low, medium, and high CO2 prices and
  discount rates.
- Compared electricity CCS technologies against their unabated counterparts and
  cement technologies against BAU.
- Rechecked the nuclear low-discount-rate behavior under the updated
  parameters.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src:src/electricity:src/cement /opt/anaconda3/envs/master-thesis/bin/python - <<'PY' ...`
- Result:
  - The current models executed successfully and produced refreshed NPV,
    scenario, and incremental-comparison tables.

### Reproducibility notes

- No model code, notebooks, raw data, parameters, figures, or numerical output
  files were changed.
- The analysis used the current normal assumptions: 80 EUR/tCO2 carbon price,
  8% discount rate, 100,000 Monte Carlo draws, random seed 42, and sampled
  cement retrofit BAU mode.

## 2026-07-24 13:28 — Add levelized net margin as a financial metric

### User request

Implement levelized net margin throughout the project, including every affected
notebook, while retaining an explicit switch between total NPV and levelized net
margin. Leave LCOX for a later step.

### Files changed (if needed)

- `src/npv_finance.py` — added shared discounted-output and levelized-net-margin
  calculations.
- `src/electricity/` and `src/cement/` NPV model and summary modules — replaced
  undiscounted NPV-per-output results with discounted-output levelized net
  margin and added `NPV`/`LNM` reporting switches.
- `src/npv_summary.py` and `src/npv_summary_plots.py` — generalized ranking,
  sign-summary, and plot helpers for either financial metric.
- `src/sensitivity_analysis.py`, `src/sensitivity_deep_dive.py`, and
  `sensitivity_dashboard.py` — replaced specific NPV with levelized net margin
  and retained total NPV as the alternative.
- 40 affected notebooks under `notebooks/` — updated result keys, labels,
  plots, settings, and metric switches; cleared stale saved outputs.
- `README.md` and `docs/HANDOVER.md` — documented the formula, units, switches,
  and the explicit deferral of LCOX.
- `CHANGELOG.md` — documented this implementation.

### What was implemented

- Defined levelized net margin as NPV divided by discounted lifetime output,
  using the same lifetime and discount rate as the annual cash-flow present
  value.
- Added auditable discounted-output fields and levelized-net-margin fields in
  electricity (`EUR/MWh`) and cement (`EUR/t`) deterministic and Monte Carlo
  results.
- Replaced the ambiguous NPV-scale CLI with `--metric NPV` and `--metric LNM`.
- Made summary figures, technology rankings, CSV exports, sensitivity analyses,
  dashboard labels, and notebook plots follow the selected metric.
- Kept rank 1 as the highest value for both NPV and levelized net margin.
- Did not implement LCOX and did not generate or change repository figures or
  data outputs.

### Verification (if needed)

- Commands run:
  - `PYTHONPATH=src /opt/anaconda3/envs/master-thesis/bin/python -m compileall -q src sensitivity_dashboard.py`
  - Deterministic and Monte Carlo formula assertions for both sectors.
  - Both sector summary CLIs with reduced samples for `--metric NPV` and
    `--metric LNM`, including ranking plots and CSV exports in temporary
    directories.
  - Code-cell compile checks for every notebook.
  - Reduced-sample execution of all 40 modified notebooks with saving disabled.
  - Repository-wide stale-reference scans and `git diff --check`.
- Result:
  - All checks passed.

### Reproducibility notes

- No model input parameters, raw data, processed data, tracked figures, or
  assumptions other than the reported per-output metric definition changed.
- The previous NPV divided by undiscounted lifetime output fields were removed.
- Existing historical figures remain unchanged; regenerate only the metric and
  sector outputs needed for the thesis.

### Next suggested step

Define the LCOX cost boundary and component treatment, then compare it
analytically with product price minus levelized net margin.

## 2026-07-24 13:45 — Rebuild all outputs and execute all notebooks

### User request

Verify that every notebook path previously using specific or normalized NPV now
uses levelized net margin, clear all figures and generated raw/processed data,
regenerate the complete output set, and rerun every notebook.

### Files changed (if needed)

- `figures/` — removed 24 historical tracked figures and generated 18 current
  NPV, levelized-net-margin, sensitivity, and cement MACC figures.
- `data/raw/` — cleared and regenerated 12 current raw/ranking CSVs.
- `data/processed/` — cleared and regenerated 16 current model, ranking,
  sensitivity, and cement MACC CSVs.
- `notebooks/**/*.ipynb` — executed and saved all 42 notebooks with fresh cell
  outputs.
- `CHANGELOG.md` — documented the full rebuild.

### What was implemented

- Audited all 42 notebook sources. Summary notebooks switch explicitly between
  `NPV` and `LNM`; sensitivity/scenario notebooks switch between total NPV and
  `METRIC_LEVELIZED_NET_MARGIN`; technology notebooks report total NPV and
  levelized net margin together.
- Confirmed no notebook source retains the former specific/normalized NPV keys
  or labels.
- Removed every existing file under `figures/`, `data/raw/`, and
  `data/processed/`.
- Regenerated electricity and cement summary, deterministic, ranking, raw, and
  processed outputs at 100,000 Monte Carlo draws and random seed 42 for both
  total NPV and levelized net margin.
- Regenerated standardized sensitivity heatmaps/CSVs for total NPV and
  levelized net margin.
- Regenerated deterministic and simulated cement MACC figures and CSVs.
- Executed all notebooks using their stored full-size settings and saved their
  current outputs.

### Verification (if needed)

- Commands run:
  - Full electricity summary workflow with `--metric NPV` and `--metric LNM`.
  - Full cement summary workflow with `--metric NPV` and `--metric LNM`.
  - `python -m sensitivity_deep_dive` for `levelized_net_margin` and `total`.
  - `python -m cement.cement_macc` in deterministic and simulated modes.
  - `nbclient` execution of all 42 notebooks without reduced samples.
  - PNG readability, CSV schema/row-count, LNM identity, ranking-metric,
    notebook-error, stale-reference, and `git diff --check` validations.
- Result:
  - All workflows and all 42 notebooks completed successfully.
  - Generated 18 valid PNGs and 28 CSVs containing 10,800,528 lines in total.
  - Sampled processed rows satisfy
    `levelized net margin × discounted lifetime output = NPV`.

### Reproducibility notes

- Current generated outputs are dated `2026-07-24`.
- `data/raw/` is approximately 972 MB and `data/processed/` approximately
  798 MB; both directories remain ignored by Git.
- The old tracked figure files are deleted in the working tree. The 18 new
  current figures are untracked until explicitly added to Git.
- No LCOX calculation was added during this rebuild.

### Next suggested step

Review the regenerated figures for thesis selection, then add only the final
figure set intended for version control.
