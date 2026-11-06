"""Execute all portfolio notebooks with the registered project kernel."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


NOTEBOOKS = (
    "project1_sales_analysis/analysis.ipynb",
    "project2_healthcare_analysis/analysis.ipynb",
    "project3_sports_analytics/analysis.ipynb",
    "project4_financial_analysis/analysis.ipynb",
    "project5_ecommerce_analytics/analysis.ipynb",
    "portfolio_summary.ipynb",
)


def execute(relative_path: str) -> None:
    path = ROOT / relative_path
    notebook = nbformat.read(path, as_version=4)
    processor = ExecutePreprocessor(
        timeout=600,
        startup_timeout=120,
        kernel_name="portfolio",
        allow_errors=False,
    )
    executed, _ = processor.preprocess(notebook, {"metadata": {"path": str(path.parent)}})
    nbformat.write(executed, path)
    print(f"EXECUTED {relative_path} in portfolio kernel", flush=True)


def main() -> int:
    for notebook in NOTEBOOKS:
        execute(notebook)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
