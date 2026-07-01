# Midterm Deep Dive Findings

Generated from current source code with 100,000 Monte Carlo draws and random seed 42.

## What we built

- A two-sector probabilistic NPV model for electricity and cement.
- Deterministic and Monte Carlo calculations for all modeled technologies.
- Shared run-id logic so rankings compare technologies under common sampled market conditions.
- Total and sector-normalized NPV outputs, ranking probabilities, sign counts, sensitivity heatmaps, scenario analysis, and cement MACC.

## Current electricity findings

| technology | mean_specific | p05_specific | p95_specific | non_negative_share |
| --- | --- | --- | --- | --- |
| pv | 6.56 | 3.75 | 9.40 | 1.00 |
| wind_onshore | 5.84 | 1.41 | 10.29 | 1.00 |
| wind_offshore | 3.10 | -2.57 | 8.74 | 0.75 |
| ccgt | -10.84 | -26.97 | 2.08 | 0.11 |
| nuclear | -13.21 | -25.90 | -0.56 | 0.03 |
| ccgt_ccs | -14.14 | -33.02 | 1.20 | 0.07 |
| hard_coal | -24.28 | -29.08 | -20.13 | 0.00 |
| hard_coal_ccs | -26.15 | -35.63 | -16.79 | 0.00 |
| biogas | -104.64 | -118.40 | -90.80 | 0.00 |

| technology | average_rank | probability_rank_1 | probability_top_3 |
| --- | --- | --- | --- |
| pv | 1.66 | 0.47 | 1.00 |
| wind_onshore | 1.89 | 0.38 | 0.99 |
| wind_offshore | 2.61 | 0.15 | 0.92 |
| ccgt | 4.64 | 0.00 | 0.05 |
| nuclear | 5.27 | 0.00 | 0.02 |
| ccgt_ccs | 5.67 | 0.00 | 0.03 |
| hard_coal | 7.00 | 0.00 | 0.00 |
| hard_coal_ccs | 7.25 | 0.00 | 0.00 |
| biogas | 9.00 | 0.00 | 0.00 |

## Current cement findings

| technology | mean_specific | p05_specific | p95_specific | non_negative_share |
| --- | --- | --- | --- | --- |
| ccs | 20.01 | 6.83 | 31.20 | 1.00 |
| process_heat_integration | 19.03 | 15.95 | 22.11 | 1.00 |
| waste_heat_recovery | 18.85 | 16.19 | 21.36 | 1.00 |
| clinker_substitution | 18.79 | 15.54 | 22.07 | 1.00 |
| alternative_fuels | 18.75 | 15.25 | 22.25 | 1.00 |
| efficiency_improvement | 17.95 | 15.05 | 20.76 | 1.00 |
| bau | 17.44 | 14.52 | 20.36 | 1.00 |
| electrification | -44.64 | -67.38 | -18.60 | 0.00 |
| electrolysis | -163.32 | -251.95 | -86.34 | 0.00 |

| technology | average_rank | probability_rank_1 | probability_top_3 |
| --- | --- | --- | --- |
| process_heat_integration | 2.99 | 0.13 | 0.66 |
| waste_heat_recovery | 3.23 | 0.09 | 0.58 |
| ccs | 3.49 | 0.52 | 0.58 |
| clinker_substitution | 3.51 | 0.12 | 0.53 |
| alternative_fuels | 3.63 | 0.14 | 0.52 |
| efficiency_improvement | 5.00 | 0.00 | 0.12 |
| bau | 6.15 | 0.00 | 0.00 |
| electrification | 8.00 | 0.00 | 0.00 |
| electrolysis | 9.00 | 0.00 | 0.00 |

## Scenario findings

CO2-price scenarios change fossil and directly emitting technologies most. Zero-direct-emission electricity technologies do not move with CO2 price.

Discount-rate scenarios strongly affect capital-heavy technologies such as PV, wind, nuclear, cement CCS, and low-carbon cement routes.

## Current cement MACC

| technology | annual_abatement_tco2 | abatement_cost_eur_per_tco2 |
| --- | --- | --- |
| efficiency_improvement | 6000.00 | -87.91 |
| process_heat_integration | 39000.00 | -8.03 |
| alternative_fuels | 60000.00 | 30.90 |
| clinker_substitution | 75000.00 | 44.03 |
| ccs | 546000.00 | 70.52 |
| electrification | 200000.00 | 811.77 |
| electrolysis | 500000.00 | 922.07 |

| technology | annual_abatement_tco2 | abatement_cost_eur_per_tco2 | abatement_cost_p05_eur_per_tco2 | abatement_cost_p95_eur_per_tco2 |
| --- | --- | --- | --- | --- |
| efficiency_improvement | 6335.56 | -107.82 | -1438.32 | 376.87 |
| process_heat_integration | 41189.41 | -10.39 | -80.17 | 26.36 |
| alternative_fuels | 63350.94 | 31.67 | -29.41 | 147.34 |
| clinker_substitution | 79179.36 | 39.96 | 15.76 | 99.96 |
| ccs | 576407.73 | 69.56 | 25.75 | 118.81 |
| electrification | 233429.03 | 702.85 | 440.39 | 1053.01 |
| electrolysis | 533329.06 | 873.75 | 538.73 | 1276.56 |
