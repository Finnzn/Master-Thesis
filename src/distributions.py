"""Reusable probability distribution helpers for Monte Carlo simulations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TriangularDistribution:
    """Parameters for a triangular probability distribution."""

    minimum: float
    mode: float
    maximum: float
    unit: str
    description: str


@dataclass(frozen=True)
class UniformDistribution:
    """Parameters for a uniform probability distribution."""

    lower_bound: float
    upper_bound: float
    unit: str
    description: str


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
