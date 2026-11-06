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

Run commands from the repository root. Notebooks use a root-resolution helper based on locating `PRD.md`, so nested notebooks can import the project package and address data/output directories consistently. The expected kernel is the Python environment used to install `requirements.txt`; kernel metadata and `sys.executable` must be checked during each fresh-kernel run. All six project notebooks have executed with the registered kernel; see [`validation.md`](validation.md) for the clean-environment reproduction result and any system-specific launch limitation.

## Preparation status

The pinned package set was installed and checked in both the project-local `.venv` and a separate clean `venv` using Python 3.13.9. The clean environment reproduced all five domain builds, all six notebook executions, five PDFs, and the final artifact validation. See [`validation.md`](validation.md) for the Windows kernelspec listing limitation observed alongside successful execution.

## Dashboard

Run `python -m streamlit run dashboard/app.py` from the project root. The overview and five domain views read the generated `outputs/` and `visualizations/` artifacts. The dashboard uses the light palette in `.streamlit/config.toml`, matching `Design.md`. Browser review and screenshots are recorded in [`acceptance_matrix.md`](acceptance_matrix.md) and [`screenshots/README.md`](screenshots/README.md). Filter reset was exercised on all five domain pages; no-match states were exercised on four. Missing required files and malformed metrics were exercised with Streamlit AppTest and produced recovery messages. Keyboard paths were checked for page navigation and the sports slider; direct screen-reader assessment remains open.

## Fresh-kernel notebook execution

After installing the project environment and preparing the documented local datasets, run `python scripts/execute_notebooks.py` from the project root. This executes the five domain notebooks and `portfolio_summary.ipynb` with the registered `portfolio` kernel, saves execution outputs back into the notebooks, and stops on the first notebook error.
