# Local setup

## Environment

The existing environment was inspected on 2026-11-04: Python 3.13.9 and the exact package versions in the project-root `requirements.txt` are present. The project kernel dependency is pinned as well.

For a separate environment, from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Do not install packages into the shared/base environment. Confirm `python --version` and `python -m pip freeze` for a final reproducibility record.

## Data

Read [`../datasets/README.md`](../datasets/README.md) and `../datasets/catalog.csv`. Download the documented sources with `python scripts/download_sources.py --domain all`, preserve originals under `datasets/raw/<domain>/`, and record snapshot metadata before preparing processed copies. The finance source is retrieved from a public raw-file mirror; its origin and license are recorded in the catalog.

## Project root and notebooks

Run commands from the repository root. Notebooks use a root-resolution helper based on locating `PRD.md`, so nested notebooks can import the project package and address data/output directories consistently. The expected kernel is the Python environment used to install `requirements.txt`; kernel metadata and `sys.executable` must be checked during each fresh-kernel run. The current Windows environment has not yet completed a fresh-kernel notebook execution; see [`validation.md`](validation.md).

## Preparation status

The package set is installed and checked in the project-local `.venv` using Python 3.13.9. The portfolio kernel is registered under `.venv/share/jupyter/kernels/portfolio`. Domain builders have produced the current portfolio outputs; they were also called by notebook code cells in-process. This is useful execution evidence but does not replace the pending fresh-kernel check.

## Dashboard

Run `python -m streamlit run dashboard/app.py` from the project root. The overview and five domain views read the generated `outputs/` and `visualizations/` artifacts. Browser review is recorded in [`acceptance_matrix.md`](acceptance_matrix.md); complete keyboard and responsive review before marking the UI fully accepted.
