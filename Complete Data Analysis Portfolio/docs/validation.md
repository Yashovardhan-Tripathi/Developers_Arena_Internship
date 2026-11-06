# Validation log

## 2026-11-07 — Final artifact review and acceptance checkpoint

### Passed

- `.venv\Scripts\python.exe -m pip check`: no broken requirements found.
- `.venv\Scripts\python.exe -m compileall -q src scripts dashboard`: completed successfully after the final documentation updates.
- `.venv\Scripts\python.exe scripts/validate_artifacts.py --all --submission`: all required paths present; all five metric and chart contracts valid; exit code 0 on the final recheck. This checks paths and schemas, not all visual or runtime acceptance criteria.
- `nbformat.validate` passed for the five domain notebooks and `portfolio_summary.ipynb`; all six contain captured fresh-kernel execution outputs.
- Inventory contains 25 unique chart IDs, and all referenced image files exist.
- All five domain PDFs have valid PDF signatures and seven pages each; `executive_summary.pdf` has a valid signature and three pages. The PowerPoint archive contains eight slides. These are structural checks only.
- Browser review of the local Streamlit app confirmed overview plus all five domain pages render with filters and charts. Observed domain examples: sales gross sales GBP 212,242 under default filters; 100,124 eligible healthcare encounters and 11.3% readmission; 63,157 sports team-game records; 1,762 finance dates; e-commerce session conversion charts.
- E-commerce month ordering now explicitly recognizes the source's full spelling `June`; the domain builder, notebook, and report were refreshed.
- Visual checks caught and corrected overlapping charts in the executive-summary evidence page, footer crowding on its first page, and decimal display for proportion metrics in reports and summary outputs. All five report covers, all 25 report chart pages, all five recommendation/source pages, and all three executive-summary pages were reviewed after rendering; no overlap or clipping remained in those inspected pages.
- Finance dashboard filter behavior was observed: removing one selected symbol changed the selected count from 8 to 7 while retaining all 1,762 observed dates.
- Saved six desktop dashboard screenshots (overview plus five domains) and one 390 × 844 mobile sports screenshot under `docs/screenshots/` after setting the Streamlit theme to the documented light palette. KPI text is readable. At mobile width the document remains 390 pixels wide, cards stack, and chart content is visible after closing the navigation sidebar.
- Keyboard check: Tab focuses the sidebar radio group, then ArrowDown changes the selected page from healthcare to sports and updates its content.
- Local Markdown link check passed for all 19 Markdown files in scope after `docs/diagrams.md` was added.
- PowerPoint structural review confirmed eight slides, slide text extracted for review, and all text boxes within slide bounds. All slides were visually reviewed in PowerPoint's slide sorter; no clipped or out-of-bounds slide content was apparent at review scale.
- The nested fixture check `scripts/verify_notebook_contract.py` passed when run with elevated access: “Nested notebook root and portfolio kernel verified.” The regular restricted invocation had stalled during kernel startup.
- `.venv\Scripts\python.exe scripts/execute_notebooks.py` completed with exit code 0. The five domain notebooks and portfolio summary all executed in the registered `portfolio` kernel, saved their outputs, and rebuilt the final inventory, five reports, executive summary, and eight-slide presentation. Windows emitted a ZeroMQ Proactor-loop warning during startup, but execution succeeded.

### Clean-environment reproduction (2026-11-07)

- Created a separate ignored `venv` from scratch and installed the pinned `requirements.txt`; `pip check` and `compileall -q src scripts dashboard` passed.
- `scripts/build_outputs.py --all` regenerated all five domains from the local raw snapshots. The builders completed for sales (40,077 invoices), healthcare (100,124 encounters), sports (63,157 team-games), finance (851,264 security-date rows), and e-commerce (12,330 sessions).
- `scripts/execute_notebooks.py` executed all five domain notebooks and `portfolio_summary.ipynb` in the clean environment's registered portfolio kernel. `scripts/render_reports.py` regenerated all five reports.
- `scripts/validate_artifacts.py --all --submission` completed with exit code 0 and reported `READY (0 missing paths)`, including valid metric and chart contracts for each domain.
- The narrative source, recommendation findings, five domain slide headline values, and stored headline metrics were reconciled. This identified a half-rounding mismatch for sports holdout accuracy (66.3% versus 66.4%). A shared decimal half-up formatter now yields 66.4% consistently in the sports narrative, executive summary, and presentation. All six notebooks, reports, executive summary, and presentation were refreshed; final validation, compileall, and `pip check` passed.
- Local Markdown link validation scanned 42 Markdown files and found no broken relative links.
- `python -m jupyter kernelspec list` separately raised Windows WinError 623. This did not block the project's execution script: all six kernels launched and notebooks completed. Record this as a system-specific kernelspec listing issue, not a failed reproduction.

### Dashboard filter acceptance (2026-11-07)

- Tested changing and resetting filters on sales, healthcare, sports, finance, and e-commerce. Sports season range changed the team-game count from 63,157 to 62,807; reset restored 63,157.
- Empty selections on sales, healthcare, finance, and e-commerce produced explicit no-match states; reset restored default values.
- Responsive layout checks at 1440 × 900, 1024 × 768, and 390 × 844 CSS pixels found no horizontal page overflow. Mobile KPI cards stack vertically.
- Streamlit AppTest temporarily removed the sports metrics file and confirmed the overview warning and domain recovery error; malformed finance metrics JSON also produced a recoverable domain error. Both files were restored and verified present.
- Keyboard navigation through the sidebar and sports season slider was verified. Direct screen-reader or other assistive-technology assessment was not performed.
- Rendered dashboard palette contrast was calculated against its specified backgrounds: main text 17.06:1, secondary text 7.24:1, primary action 6.70:1, positive status 7.13:1, caution status 7.09:1, and error status 6.47:1. Each exceeds WCAG AA's 4.5:1 normal-text threshold. Focus styling is explicitly defined with a 3-pixel visible outline; dashboard controls expose descriptive names in the browser accessibility tree.

### Follow-up outside required acceptance

- Direct screen-reader assessment was not performed. The specified keyboard, visible-focus, descriptive-label, responsive, and text-contrast checks passed; a screen-reader pass may be useful as an additional human review.

The `python` command in some PowerShell sessions resolves to the shared/base environment, whose package set reports unrelated `watchdog` and `numpy` conflicts. Use `.venv\Scripts\python.exe`; the project's own environment passes `pip check`.

### Handoff boundary

- The portfolio folder has no independent `.git` directory; its parent is the repository root. After authorized escalation, `git status --short -- .` showed modified and untracked files only beneath `Complete Data Analysis Portfolio/`; no sibling internship paths appeared. These are local project changes; nothing was committed or pushed.
- `git diff --check -- 'Complete Data Analysis Portfolio'` completed without whitespace errors. Git printed line-ending notices for files configured to convert LF to CRLF on a future checkout; no normalization change was made.

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
