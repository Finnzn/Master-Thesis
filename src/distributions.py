"""Reusable probability distribution helpers for Monte Carlo simulations.

The thesis model stores uncertain inputs as small dataclass objects instead of
sampling them immediately. This keeps assumptions traceable: parameter modules
can list the minimum/mode/maximum, unit, and description, while simulation
modules decide how many samples to draw and which random seed to use.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FixedParameter:
    """A deterministic model parameter.

    Use this when a value is treated as fixed in the current model setup rather
    than sampled in the Monte Carlo run.
    """

    value: float
    unit: str
    description: str


@dataclass(frozen=True)
class TriangularDistribution:
    """Parameters for a triangular probability distribution.

    This is used for inputs where the source gives a lower estimate, most likely
    value, and upper estimate. The `mode` is also used as the deterministic
    representative value in one-point calculations.
    """

    minimum: float
    mode: float
    maximum: float
    unit: str
    description: str


@dataclass(frozen=True)
class ScaledBetaDistribution:
    """Parameters for a scaled beta distribution over a finite interval.

    The beta distribution is sampled on [0, 1] and then rescaled to the original
    unit range. Storing alpha and beta here makes the final sampled distribution
    reproducible from the source minimum, mean, and maximum.
    """

    minimum: float
    mean: float
    maximum: float
    alpha: float
    beta: float
    unit: str
    description: str


@dataclass(frozen=True)
class UniformDistribution:
    """Parameters for a uniform probability distribution.

    This is used when the thesis assumption treats every value between the lower
    and upper bound as equally plausible.
    """

    lower_bound: float
    upper_bound: float
    unit: str
    description: str


def create_scaled_beta_distribution(
    minimum: float,
    mean: float,
    maximum: float,
    unit: str,
    description: str,
) -> ScaledBetaDistribution:
    """Create a scaled beta distribution from minimum, maximum, and mean.

    The source tables often provide a bounded range and an expected value but no
    full probability distribution. This helper converts those three values into
    beta parameters with enough concentration that the requested mean is inside
    the interval and the distribution remains bounded by the source range.
    """

    if minimum >= maximum:
        raise ValueError("minimum must be smaller than maximum.")
    if not minimum < mean < maximum:
        raise ValueError("mean must be strictly between minimum and maximum.")

    # The beta distribution itself lives on [0, 1], so the source mean must first
    # be expressed as a fraction of the source min-max interval.
    normalized_mean = (mean - minimum) / (maximum - minimum)
    minimum_concentration = max(
        1.0 / normalized_mean,
        1.0 / (1.0 - normalized_mean),
    )
    # The concentration factor is the thesis model's `k` choice. It is set high
    # enough to keep alpha and beta above 1, which gives a dome-shaped beta
    # distribution instead of a U-shaped one while preserving the requested mean.
    concentration = 2.0 * minimum_concentration

    return ScaledBetaDistribution(
        minimum=minimum,
        mean=mean,
        maximum=maximum,
        alpha=normalized_mean * concentration,
        beta=(1.0 - normalized_mean) * concentration,
        unit=unit,
        description=description,
    )


def sample_triangular(
    distribution: TriangularDistribution,
    size: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Draw samples from a triangular distribution specification."""

    generator = rng if rng is not None else np.random.default_rng()
    return generator.triangular(
        left=distribution.minimum,
        mode=distribution.mode,
        right=distribution.maximum,
        size=size,
    )


def sample_scaled_beta(
    distribution: ScaledBetaDistribution,
    size: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Draw samples from a scaled beta distribution specification."""

    generator = rng if rng is not None else np.random.default_rng()
    normalized_samples = generator.beta(
        a=distribution.alpha,
        b=distribution.beta,
        size=size,
    )
    return distribution.minimum + normalized_samples * (
        distribution.maximum - distribution.minimum
    )


def sample_uniform(
    distribution: UniformDistribution,
    size: int,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Draw samples from a uniform distribution specification."""

    generator = rng if rng is not None else np.random.default_rng()
    return generator.uniform(
        low=distribution.lower_bound,
        high=distribution.upper_bound,
        size=size,
    )
