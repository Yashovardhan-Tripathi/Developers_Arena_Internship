"""Execute the minimal nested notebook in the selected portfolio kernel."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def main() -> int:
    fixture = PROJECT_ROOT / "docs/fixtures/root_resolution.ipynb"
    notebook = nbformat.read(fixture, as_version=4)
    processor = ExecutePreprocessor(timeout=90, kernel_name="portfolio", allow_errors=False)
    executed, _ = processor.preprocess(notebook, {"metadata": {"path": str(fixture.parent)}})
    outputs = [
        output.get("text", "")
        for cell in executed.cells
        if cell.cell_type == "code"
        for output in cell.get("outputs", [])
    ]
    if not any("Project root and shared imports resolved." in output for output in outputs):
        raise RuntimeError("Nested notebook did not report successful root/import resolution.")
    print("Nested notebook root and portfolio kernel verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
