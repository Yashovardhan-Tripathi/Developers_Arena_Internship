"""Reusable descriptive and uncertainty summaries."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


def describe_numeric(values: Iterable[float]) -> dict[str, float | int]:
    """Summarize finite observations without silently treating missing as zero."""
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    finite = series[np.isfinite(series)]
    if finite.empty:
        raise ValueError("At least one finite numeric observation is required.")
    return {
        "n": int(finite.size),
        "mean": float(finite.mean()),
        "median": float(finite.median()),
        "std_sample": float(finite.std(ddof=1)) if finite.size > 1 else float("nan"),
        "minimum": float(finite.min()),
        "maximum": float(finite.max()),
    }


def bootstrap_mean_interval(
    values: Iterable[float], *, confidence: float = 0.95, resamples: int = 2000, seed: int = 42
) -> tuple[float, float]:
    """Percentile bootstrap interval for a mean; observations must be independent."""
    if not 0 < confidence < 1 or resamples < 100:
        raise ValueError("confidence must be in (0, 1) and resamples must be at least 100")
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    sample = series[np.isfinite(series)].to_numpy(dtype=float)
    if sample.size < 2:
        raise ValueError("At least two finite observations are required.")
    generator = np.random.default_rng(seed)
    means = np.empty(resamples, dtype=float)
    for index in range(resamples):
        means[index] = generator.choice(sample, size=sample.size, replace=True).mean()
    tail = (1 - confidence) / 2
    lower, upper = np.quantile(means, [tail, 1 - tail])
    return float(lower), float(upper)
