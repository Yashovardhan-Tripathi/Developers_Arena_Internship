"""Raw-input readers and deterministic processed-output writers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.paths import PROJECT_ROOT, domain_path


def load_raw(domain: str, filename: str, **kwargs: object) -> pd.DataFrame:
    """Read a CSV or Excel input without changing its raw source file."""
    if Path(filename).name != filename:
        raise ValueError("filename must be a single file name within its domain raw folder")
    path = domain_path("datasets/raw", domain, filename)
    if not path.is_file():
        raise FileNotFoundError(f"Raw input is missing: {path.relative_to(PROJECT_ROOT)}")
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, **kwargs)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, **kwargs)
    raise ValueError(f"Unsupported raw input format: {suffix}")


def write_processed(frame: pd.DataFrame, domain: str, filename: str) -> Path:
    """Write a CSV copy under processed data, never over raw input."""
    if Path(filename).name != filename or Path(filename).suffix.lower() != ".csv":
        raise ValueError("filename must be a single .csv file name")
    path = domain_path("datasets/processed", domain, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path
