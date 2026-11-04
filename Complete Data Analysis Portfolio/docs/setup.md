# Local setup

## Environment

The existing environment was inspected on 2026-11-04: Python 3.13.9 and the exact package versions in the project-root `requirements.txt` are present. This is an observed workstation environment, not yet a clean-machine reproduction.

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

Run commands from the repository root. Notebooks will use a small root-resolution helper based on locating `PRD.md`, so nested notebooks can import the project package and address data/output directories consistently. The expected kernel is the Python environment used to install `requirements.txt`; kernel metadata and `sys.executable` must be checked during each fresh-kernel run. This contract has not yet been verified with a nested fixture notebook.

## Preparation status

The preparation commands will be documented after the source files and preparation interface exist. Phase 1 is in progress; no analysis outputs or dataset findings are available yet.
