# Validation log

## 2026-11-06 — Integration and submission artifacts

### Passed

- `.venv\Scripts\python.exe -m pip check`: no broken requirements found.
- `.venv\Scripts\python.exe -m compileall -q src scripts dashboard`: completed successfully.
- `python scripts/validate_artifacts.py --all --submission`: all required paths present; all five metric and chart contracts valid; exit code 0. This checks paths and schemas, not all visual or runtime acceptance criteria.
- `nbformat.validate` passed for the five domain notebooks and `portfolio_summary.ipynb`. Each has one code cell with captured in-process execution output.
- Inventory contains 25 unique chart IDs, and all referenced image files exist.
- All five domain PDFs have valid PDF signatures and seven pages each; `executive_summary.pdf` has a valid signature and three pages. The PowerPoint archive contains eight slides. These are structural checks only.
- Browser review of the local Streamlit app confirmed overview plus all five domain pages render with filters and charts. Observed domain examples: sales gross sales GBP 212,242 under default filters; 100,124 eligible healthcare encounters and 11.3% readmission; 63,157 sports team-game records; 1,762 finance dates; e-commerce session conversion charts.
- E-commerce month ordering now explicitly recognizes the source's full spelling `June`; the domain builder, notebook, and report were refreshed.

### Still open

- Fresh-kernel execution: `scripts/verify_notebook_contract.py` continued to hang during Jupyter kernel startup in `.venv`; interrupted after over 70 seconds. Captured outputs come from in-process builder execution and must not be presented as a successful fresh-kernel run.
- Visual inspection covered the five report covers, one representative chart page per domain, and the first two executive-summary pages. Remaining report pages and presentation slides still need review.
- The overview and five domain pages were observed, but filter changes, empty/error states, keyboard-only navigation, and alternate viewport sizes need review.
- There are no accepted dashboard screenshot files yet in `docs/screenshots/`; the inspected PDF page previews were stored outside the project workspace.
- Link consistency and end-to-end reproduction from a clean setup have not been completed.

The `python` command in some PowerShell sessions resolves to the shared/base environment, whose package set reports unrelated `watchdog` and `numpy` conflicts. Use `.venv\Scripts\python.exe`; the project's own environment passes `pip check`.

No publication or deployment was performed.

---

## 2026-11-04 — Phase 1 foundation

### Passed

- Inspected Python 3.13.9 and pinned the verified package versions in `requirements.txt`.
- Created the project `.venv`, installed `requirements.txt`, ran `python -m pip check` (`No broken requirements found`), and imported the analytics, dashboard, and notebook packages.
- Registered the local `portfolio` kernel under `.venv/share/jupyter/kernels/portfolio`.
- Downloaded and profiled selected raw inputs. Exact file hashes, sizes, row counts, columns, blank counts, and literal `?` counts are in `datasets/catalog.csv` and `docs/data_dictionary.md`.
- Loaded the e-commerce source through `src.data_io.load_raw` in `.venv`: 12,330 rows × 18 columns; zero pandas missing values. The generic profile and descriptive summary helpers returned results.
- Ran `python -m compileall -q src scripts` successfully.
- From `docs/fixtures`, executed the notebook bootstrap logic in a normal Python process. It resolved the project root and imported all five domain IDs.

### Incomplete or environment-blocked

- `python -m jupyter kernelspec list` returned Windows `WinError 623` (`Illegal System DLL Relocation`) despite successful local kernelspec registration.
- `scripts/verify_notebook_contract.py` and nbconvert execution did not complete during this session. The nested root logic passed as a normal Python process, but the fresh-kernel contract is not verified.
- Shared metric and chart schema validators were added to `src/contracts.py`, and `scripts/validate_artifacts.py` now invokes them for present outputs. This latest change has not been run against fixture or generated artifacts; its runtime behavior remains unverified.
- `scripts/build_outputs.py --domain sales` reported `NOT READY` because the sales phase has not started. `scripts/validate_artifacts.py --domain sales` reported its five required domain outputs missing. These are expected current-state results, not completed domain validation.
- Git status could not be read: Git reports it cannot change to `G:/Developers_Arena/Developers_Arena_Internship`. Do not infer that the worktree is clean.
- No project test suite was added or run. No domain analysis, reports, dashboard, presentation, publication, or deployment has been completed.

Phase 1 remains open until the notebook kernel/root behavior is verified and the strengthened shared contracts are validated with fixtures or representative artifacts. Domain phases remain gated behind S1.

Microsoft documents error 623 as a system DLL occupying an address reserved for Windows system DLLs; this is an environment-level launch failure, not an analysis result. See [Microsoft's Win32 system error list](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--500-999-).
