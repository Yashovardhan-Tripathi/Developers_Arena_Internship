"""Small reusable data-quality operations; domain choices remain explicit."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def profile_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Return column-level type, missingness, and uniqueness counts."""
    return pd.DataFrame(
        {
            "dtype": frame.dtypes.astype(str),
            "missing_count": frame.isna().sum(),
            "missing_fraction": frame.isna().mean(),
            "distinct_count": frame.nunique(dropna=True),
        }
    ).rename_axis("column")


def normalize_unknown_tokens(
    frame: pd.DataFrame,
    columns: Sequence[str],
    tokens: Sequence[str] = ("?",),
) -> pd.DataFrame:
    """Copy the frame and convert documented unknown markers to pandas NA."""
    absent = sorted(set(columns) - set(frame.columns))
    if absent:
        raise KeyError(f"Unknown-token columns do not exist: {absent}")
    result = frame.copy()
    result.loc[:, list(columns)] = result.loc[:, list(columns)].replace(list(tokens), pd.NA)
    return result


def remove_exact_duplicates(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Return a copy without exact duplicate rows and the removed-row count."""
    cleaned = frame.drop_duplicates().copy()
    return cleaned, len(frame) - len(cleaned)
