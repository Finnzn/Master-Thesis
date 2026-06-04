"""Generate electricity-sector NPV comparison figures."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Mapping

import numpy as np

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    TriangularDistribution,
    UniformDistribution,
)
from electricity_model import (
    calculate_capacity_kw,
    calculate_npv,
    simulate_electricity_technology_npv,
)
from electricity_parameters import (
    ANNUAL_ELECTRICITY_OUTPUT_MWH,
    ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS,
    ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS,
    LIFETIME_ELECTRICITY_YEARS,
    RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH,
)
from general_parameters import (
    BIOGAS_PRICE_EUR_PER_MWH_TH,
    CARBON_PRICE_EUR_PER_T,
    COAL_PRICE_DISTRIBUTION,
    GAS_PRICE_DISTRIBUTION,
    INTEREST_RATE,
    NO_FUEL_PRICE_EUR_PER_MWH_TH,
    NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
)
from npv_summary_plots import dated_figure_path, plot_mean_npv_technology_bars


DEFAULT_SAMPLE_SIZE = 100_000
DEFAULT_RANDOM_SEED = 42

ELECTRICITY_TECHNOLOGY_LABELS: Mapping[str, str] = {
    "hard_coal": "Hard coal",
    "hard_coal_ccs": "Hard coal+CCS",
    "ccgt": "CCGT",
    "ccgt_ccs": "CCGT + CCS",
    "nuclear": "Nuclear",
    "wind_offshore": "Wind Offshore",
    "wind_onshore": "Wind Onshore",
    "pv": "PV",
    "biogas": "Biogas",
}


def representative_value(
    parameter: (
        FixedParameter
        | ScaledBetaDistribution
        | TriangularDistribution
        | UniformDistribution
    ),
) -> float:
    """Return the deterministic value used for a parameter specification."""

    if isinstance(parameter, FixedParameter):
        return parameter.value
    if isinstance(parameter, ScaledBetaDistribution):
        return parameter.mean
    if isinstance(parameter, TriangularDistribution):
        return parameter.mode
    if isinstance(parameter, UniformDistribution):
        return (parameter.lower_bound + parameter.upper_bound) / 2

    raise TypeError(f"Unsupported parameter type: {type(parameter)!r}")


def electricity_fuel_price_parameter(
    technology: str,
) -> FixedParameter | ScaledBetaDistribution:
    """Return the fuel-price parameter used by an electricity technology."""

    fuel_price_by_technology = {
        "hard_coal": COAL_PRICE_DISTRIBUTION,
        "hard_coal_ccs": COAL_PRICE_DISTRIBUTION,
        "ccgt": GAS_PRICE_DISTRIBUTION,
        "ccgt_ccs": GAS_PRICE_DISTRIBUTION,
        "nuclear": NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_offshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "wind_onshore": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "pv": NO_FUEL_PRICE_EUR_PER_MWH_TH,
        "biogas": BIOGAS_PRICE_EUR_PER_MWH_TH,
    }
    if technology not in fuel_price_by_technology:
        raise ValueError(f"No fuel-price parameter configured for {technology!r}.")

    return fuel_price_by_technology[technology]


def calculate_deterministic_electricity_npv_eur(technology: str) -> float:
    """Calculate deterministic electricity NPV from representative values."""

    if technology not in ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS:
        raise ValueError(f"Unknown electricity technology: {technology!r}.")

    distributions = ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS[technology]
    fixed_parameters = ELECTRICITY_TECHNOLOGY_FIXED_PARAMETERS[technology]

    annual_output_mwh = ANNUAL_ELECTRICITY_OUTPUT_MWH.value
    full_load_hours = representative_value(
        fixed_parameters["full_load_hours_per_year"]
    )
    capacity_kw = calculate_capacity_kw(
        annual_electricity_output_mwh=annual_output_mwh,
        full_load_hours_per_year=full_load_hours,
    )

    capex_eur_per_kw = representative_value(distributions["capex_eur_per_kw"])
    fixed_opex_eur_per_kw_year = representative_value(
        distributions["fixed_opex_eur_per_kw_year"]
    )
    variable_opex_eur_per_mwh = representative_value(
        distributions["variable_opex_eur_per_mwh"]
    )
    fuel_consumption_mwh_th_per_mwh_e = representative_value(
        distributions["fuel_consumption_mwh_th_per_mwh_e"]
    )
    emissions_tco2_per_mwh_e = representative_value(
        distributions["emissions_tco2_per_mwh_e"]
    )
    fuel_price_eur_per_mwh_th = representative_value(
        electricity_fuel_price_parameter(technology)
    )

    initial_capex_eur = capacity_kw * capex_eur_per_kw
    annual_revenue_eur = (
        annual_output_mwh * RETAIL_PRICE_ELECTRICITY_EUR_PER_MWH.value
    )
    annual_fixed_opex_eur = capacity_kw * fixed_opex_eur_per_kw_year
    annual_variable_opex_eur = annual_output_mwh * variable_opex_eur_per_mwh
    annual_fuel_cost_eur = (
        annual_output_mwh
        * fuel_consumption_mwh_th_per_mwh_e
        * fuel_price_eur_per_mwh_th
    )
    annual_emissions_cost_eur = (
        annual_output_mwh * emissions_tco2_per_mwh_e * CARBON_PRICE_EUR_PER_T.value
    )
    annual_net_cash_flow_eur = (
        annual_revenue_eur
        - annual_fixed_opex_eur
        - annual_variable_opex_eur
        - annual_fuel_cost_eur
        - annual_emissions_cost_eur
    )

    return float(
        calculate_npv(
            initial_capex_eur=np.array([initial_capex_eur]),
            annual_net_cash_flow_eur=np.array([annual_net_cash_flow_eur]),
            lifetime_years=int(LIFETIME_ELECTRICITY_YEARS.value),
            discount_rate=INTEREST_RATE.value,
        )[0]
    )


def calculate_mean_electricity_npv_million_eur(
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate mean simulated NPV by electricity technology in million EUR."""

    selected_technologies = technologies or tuple(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
    rng = np.random.default_rng(random_seed)
    values: dict[str, float] = {}
    for technology in selected_technologies:
        simulation = simulate_electricity_technology_npv(
            technology=technology,
            size=sample_size,
            rng=rng,
        )
        label = ELECTRICITY_TECHNOLOGY_LABELS.get(technology, technology)
        values[label] = float(np.mean(simulation["npv_eur"]) / 1_000_000)

    return values


def calculate_deterministic_electricity_npv_million_eur(
    technologies: tuple[str, ...] | None = None,
) -> dict[str, float]:
    """Calculate deterministic NPV by electricity technology in million EUR."""

    selected_technologies = technologies or tuple(ELECTRICITY_TECHNOLOGY_DISTRIBUTIONS)
    return {
        ELECTRICITY_TECHNOLOGY_LABELS.get(technology, technology): (
            calculate_deterministic_electricity_npv_eur(technology) / 1_000_000
        )
        for technology in selected_technologies
    }


def save_electricity_mean_npv_figure(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> Path:
    """Save the simulated mean NPV comparison figure for electricity."""

    values = calculate_mean_electricity_npv_million_eur(
        sample_size=sample_size,
        random_seed=random_seed,
    )
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Mean_NPV_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title="Mean NPV (MEUR)",
    )


def save_electricity_deterministic_npv_figure(
    output_dir: Path,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> Path:
    """Save the deterministic NPV comparison figure for electricity."""

    values = calculate_deterministic_electricity_npv_million_eur()
    output_path = dated_figure_path(
        output_dir=output_dir,
        stem=f"Deterministic_NPV_{sector_name}",
        run_date=run_date,
    )
    return plot_mean_npv_technology_bars(
        values_million_eur=values,
        output_path=output_path,
        title="Deterministic NPV (MEUR)",
    )


def save_electricity_npv_figures(
    output_dir: Path,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_seed: int = DEFAULT_RANDOM_SEED,
    run_date: date | None = None,
    sector_name: str = "Electricity",
) -> tuple[Path, Path]:
    """Save both simulated mean and deterministic electricity NPV figures."""

    return (
        save_electricity_mean_npv_figure(
            output_dir=output_dir,
            sample_size=sample_size,
            random_seed=random_seed,
            run_date=run_date,
            sector_name=sector_name,
        ),
        save_electricity_deterministic_npv_figure(
            output_dir=output_dir,
            run_date=run_date,
            sector_name=sector_name,
        ),
    )


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate electricity-sector NPV comparison figures."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_project_root() / "figures",
        help="Directory where figures are saved.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Monte Carlo sample size for the mean NPV figure.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=DEFAULT_RANDOM_SEED,
        help="Random seed for the mean NPV figure.",
    )
    parser.add_argument(
        "--kind",
        choices=("all", "mean", "deterministic"),
        default="all",
        help="Which figure to generate.",
    )
    parser.add_argument(
        "--sector-name",
        default="Electricity",
        help="Sector name used in the output file name.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.sample_size <= 0:
        raise ValueError("--sample-size must be positive.")

    if args.kind == "all":
        output_paths = save_electricity_npv_figures(
            output_dir=args.output_dir,
            sample_size=args.sample_size,
            random_seed=args.random_seed,
            sector_name=args.sector_name,
        )
    elif args.kind == "mean":
        output_paths = (
            save_electricity_mean_npv_figure(
                output_dir=args.output_dir,
                sample_size=args.sample_size,
                random_seed=args.random_seed,
                sector_name=args.sector_name,
            ),
        )
    else:
        output_paths = (
            save_electricity_deterministic_npv_figure(
                output_dir=args.output_dir,
                sector_name=args.sector_name,
            ),
        )

    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()
