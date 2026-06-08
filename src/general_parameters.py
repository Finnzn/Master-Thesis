"""General Monte Carlo parameters shared across sector modules.

This module contains global assumptions that are not specific to one sector.
Sector modules can import these constants and combine them with their own
technology or sector-specific parameter distributions.

Values in this file affect several technologies at once. For that reason, they
are kept separate from sector files such as `electricity_parameters.py`, where a
future reader should expect only sector-specific assumptions.
"""

from __future__ import annotations

from typing import Mapping

from distributions import (
    FixedParameter,
    ScaledBetaDistribution,
    UniformDistribution,
    create_scaled_beta_distribution,
)

# Carbon price is applied to direct stack emissions in the NPV cash-flow model.
CARBON_PRICE_EUR_PER_T = FixedParameter(
    value=80.0,
    unit="EUR/tCO2",
    description="Carbon price used in the general setup.",
)

# The same discount rate is used when future annual cash flows are converted to NPV.
INTEREST_RATE = FixedParameter(
    value=0.08,
    unit="fraction/year",
    description="Annual interest rate.",
)

NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH = FixedParameter(
    value=8.0,
    unit="EUR/MWh_th",
    description="Nuclear fuel price for uranium.",
)

BIOGAS_PRICE_EUR_PER_MWH_TH = FixedParameter(
    value=87.5,
    unit="EUR/MWh_th",
    description="Biogas fuel price.",
)

NO_FUEL_PRICE_EUR_PER_MWH_TH = FixedParameter(
    value=0.0,
    unit="EUR/MWh_th",
    description="Fuel price placeholder for non-fuel electricity technologies.",
)

# Market-price distributions preserve source-table minimum, maximum, and mean.
# They are shared by technologies that use the same fuel, so gas-fired plants
# draw from the same gas-price uncertainty and coal-fired plants draw from the
# same coal-price uncertainty.
GAS_PRICE_DISTRIBUTION = create_scaled_beta_distribution(
    minimum=12.5,
    mean=39.3,
    maximum=89.7,
    unit="EUR/MWh_th",
    description="Scaled beta distribution for gas price.",
)

COAL_PRICE_DISTRIBUTION = create_scaled_beta_distribution(
    minimum=8.14,
    mean=12.11,
    maximum=24.17,
    unit="EUR/MWh_th",
    description="Scaled beta distribution for coal price.",
)

ELECTRICITY_PRICE_DISTRIBUTION = create_scaled_beta_distribution(
    minimum=74.8,
    mean=183.7,
    maximum=255.2,
    unit="EUR/MWh",
    description="Scaled beta distribution for electricity price.",
)

BIOFUEL_PRICE_DISTRIBUTION = UniformDistribution(
    lower_bound=5.4,
    upper_bound=32.4,
    unit="EUR/MWh_th",
    description="Uniform distribution for biofuel price converted from 1.5-9 EUR/GJ.",
)

GENERAL_FIXED_PARAMETERS: Mapping[str, FixedParameter] = {
    "carbon_price_eur_per_t": CARBON_PRICE_EUR_PER_T,
    "interest_rate": INTEREST_RATE,
    "nuclear_fuel_price_eur_per_mwh_th": NUCLEAR_FUEL_PRICE_EUR_PER_MWH_TH,
    "biogas_price_eur_per_mwh_th": BIOGAS_PRICE_EUR_PER_MWH_TH,
    "no_fuel_price_eur_per_mwh_th": NO_FUEL_PRICE_EUR_PER_MWH_TH,
}

GENERAL_DISTRIBUTIONS: Mapping[str, ScaledBetaDistribution | UniformDistribution] = {
    "gas_price_eur_per_mwh_th": GAS_PRICE_DISTRIBUTION,
    "coal_price_eur_per_mwh_th": COAL_PRICE_DISTRIBUTION,
    "electricity_price_eur_per_mwh": ELECTRICITY_PRICE_DISTRIBUTION,
    "biofuel_price_eur_per_mwh_th": BIOFUEL_PRICE_DISTRIBUTION,
}
