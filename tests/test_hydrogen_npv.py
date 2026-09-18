"""Financial and retrofit consistency checks for the hydrogen sector."""

from __future__ import annotations

import unittest

import numpy as np

from general_parameters import BIOGAS_PRICE_EUR_PER_MWH_TH, INTEREST_RATE
from hydrogen.hydrogen_npv_deterministic import (
    HYDROGEN_TECHNOLOGIES,
    calculate_deterministic_hydrogen_results,
)
from hydrogen.hydrogen_npv_monte_carlo import simulate_hydrogen_results
from hydrogen.hydrogen_parameters import ANNUAL_HYDROGEN_OUTPUT_TH2
from npv_finance import calculate_level_cash_flow_present_value_factor


class HydrogenNpvTests(unittest.TestCase):
    def test_deterministic_financial_identities(self) -> None:
        results = calculate_deterministic_hydrogen_results()
        self.assertEqual(set(results), set(HYDROGEN_TECHNOLOGIES))
        factor = calculate_level_cash_flow_present_value_factor(25, INTEREST_RATE.value)
        for technology, result in results.items():
            with self.subTest(technology=technology):
                output = result["annual_output_th2"][0]
                self.assertEqual(output, ANNUAL_HYDROGEN_OUTPUT_TH2.value)
                self.assertAlmostEqual(
                    result["npv_eur"][0],
                    -result["initial_capex_eur"][0]
                    + result["annual_net_cash_flow_eur"][0] * factor,
                    places=5,
                )
                self.assertAlmostEqual(
                    result["lcoh_eur_per_th2"][0]
                    + result["levelized_net_margin_eur_per_th2"][0],
                    result["hydrogen_price_eur_per_th2"][0],
                    places=8,
                )

    def test_fuel_switch_and_ccs_accounting(self) -> None:
        results = simulate_hydrogen_results(sample_size=32, random_seed=42)
        parent = results["ng_smr"]
        biomethane = results["biomethane_smr"]
        ccs = results["ng_smr_ccs"]

        np.testing.assert_allclose(biomethane["natural_gas_consumption_mwh_per_th2"], 0)
        np.testing.assert_allclose(biomethane["biomethane_consumption_mwh_per_th2"], 43.89)
        np.testing.assert_allclose(biomethane["emissions_tco2_per_th2"], 0)
        np.testing.assert_allclose(biomethane["annual_transport_and_storage_cost_eur"], 0)
        np.testing.assert_allclose(
            biomethane["annual_biomethane_cost_eur"],
            ANNUAL_HYDROGEN_OUTPUT_TH2.value * 43.89 * BIOGAS_PRICE_EUR_PER_MWH_TH.value,
        )

        np.testing.assert_allclose(
            ccs["natural_gas_consumption_mwh_per_th2"]
            - parent["natural_gas_consumption_mwh_per_th2"],
            4.33,
        )
        np.testing.assert_allclose(
            ccs["electricity_consumption_mwh_per_th2"]
            - parent["electricity_consumption_mwh_per_th2"],
            1.05,
        )
        np.testing.assert_allclose(
            ccs["emissions_tco2_per_th2"],
            parent["emissions_tco2_per_th2"] * 0.1,
        )
        np.testing.assert_allclose(
            ccs["transport_and_storage_cost_eur_per_th2"],
            ccs["capture_cost_excluding_transport_and_storage_eur_per_th2"] * 0.187,
        )

    def test_reproducible_aligned_simulations(self) -> None:
        first = simulate_hydrogen_results(sample_size=16, random_seed=7)
        second = simulate_hydrogen_results(sample_size=16, random_seed=7)
        for technology in HYDROGEN_TECHNOLOGIES:
            np.testing.assert_array_equal(first[technology]["npv_eur"], second[technology]["npv_eur"])
            np.testing.assert_array_equal(
                first[technology]["gas_price_eur_per_mwh_th"],
                first["ng_smr"]["gas_price_eur_per_mwh_th"],
            )
        np.testing.assert_array_equal(
            first["ng_smr_ccs"]["bau_capex_eur_per_th2"],
            first["ng_smr"]["capex_eur_per_th2"],
        )
        np.testing.assert_array_equal(
            first["biomethane_smr"]["bau_capex_eur_per_th2"],
            first["ng_smr"]["capex_eur_per_th2"],
        )


if __name__ == "__main__":
    unittest.main()
