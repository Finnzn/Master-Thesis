"""Reusable probability distribution helpers for Monte Carlo simulations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FixedParameter:
    """A deterministic model parameter."""

    value: float
    unit: str
    description: str


@dataclass(frozen=True)
class TriangularDistribution:
    """Parameters for a triangular probability distribution."""

    minimum: float
    mode: float
    maximum: float
    unit: str
    description: str


@dataclass(frozen=True)
class ScaledBetaDistribution:
    """Parameters for a scaled beta distribution over a finite interval."""

    minimum: float
    mean: float
    maximum: float
    alpha: float
    beta: float
    unit: str
    description: str


@dataclass(frozen=True)
class UniformDistribution:
    """Parameters for a uniform probability distribution."""

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
    """Create a scaled beta distribution from minimum, maximum, and mean."""

    if minimum >= maximum:
        raise ValueError("minimum must be smaller than maximum.")
    if not minimum < mean < maximum:
        raise ValueError("mean must be strictly between minimum and maximum.")

    normalized_mean = (mean - minimum) / (maximum - minimum)
    minimum_concentration = max(
        1.0 / normalized_mean,
        1.0 / (1.0 - normalized_mean),
    )
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
