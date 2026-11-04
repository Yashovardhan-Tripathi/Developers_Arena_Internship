"""Inspect selected raw inputs without altering source files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_FILES = {
    "sales": [ROOT / "datasets/raw/sales/online_retail_II.xlsx"],
    "healthcare": [
        ROOT / "datasets/raw/healthcare/diabetic_data.csv",
        ROOT / "datasets/raw/healthcare/IDS_mapping.csv",
    ],
    "sports": [
        ROOT / "datasets/raw/sports/nbaallelo.csv",
        ROOT / "datasets/raw/sports/historical_RAPTOR_by_player.csv",
    ],
    "finance": [ROOT / "datasets/raw/finance/prices-split-adjusted.csv"],
    "ecommerce": [ROOT / "datasets/raw/ecommerce/online_shoppers_intention.csv"],
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_file(path: Path) -> None:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        sheets = pd.read_excel(path, sheet_name=None)
        frame = next(iter(sheets.values())).iloc[:0]
        row_count = sum(len(sheet) for sheet in sheets.values())
        null_counts = sum((sheet.isna().sum() for sheet in sheets.values()), start=pd.Series(0, index=frame.columns, dtype="int64"))
        question_mark_counts = sum((sheet.eq("?").sum() for sheet in sheets.values()), start=pd.Series(0, index=frame.columns, dtype="int64"))
    else:
        frame = pd.read_csv(path, nrows=0)
        row_count = 0
        null_counts = pd.Series(0, index=frame.columns, dtype="int64")
        question_mark_counts = pd.Series(0, index=frame.columns, dtype="int64")
        for chunk in pd.read_csv(path, chunksize=100_000, low_memory=False):
            row_count += len(chunk)
            null_counts = null_counts.add(chunk.isna().sum(), fill_value=0)
            question_mark_counts = question_mark_counts.add(chunk.eq("?").sum(), fill_value=0)
    print(f"FILE: {path.relative_to(ROOT)}")
    print(f"SHA256: {sha256_file(path)}")
    print(f"BYTES: {path.stat().st_size}")
    print(f"ROWS: {row_count}")
    print(f"COLUMNS: {list(frame.columns)}")
    print(f"NULL_COUNTS: {null_counts.astype('int64').to_dict()}")
    print(f"QUESTION_MARK_COUNTS: {question_mark_counts.astype('int64').to_dict()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=sorted(RAW_FILES), required=True)
    parser.add_argument("--check-only", action="store_true", help="Inspect source files without writing processed data")
    args = parser.parse_args()
    files = RAW_FILES[args.domain]
    if not files:
        print(f"{args.domain}: source file list is not frozen; see datasets/catalog.csv")
        return 2
    missing = [path for path in files if not path.is_file()]
    if missing:
        for path in missing:
            print(f"MISSING: {path.relative_to(ROOT)}")
        return 2
    for path in files:
        inspect_file(path)
    if not args.check_only:
        print("Inspection only: no domain cleaning pipeline is implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
