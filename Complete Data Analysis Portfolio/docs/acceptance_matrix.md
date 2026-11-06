# Acceptance matrix

Status is evidence-based as of 2026-11-06. “Generated” means the artifact exists; it does not imply that every runtime or presentation acceptance check passed.

| Requirement | Evidence | Current status | Remaining acceptance work |
| --- | --- | --- | --- |
| FR-01 Five distinct projects | Five domain notebooks, metrics, tables, narratives, reports, and recommendations | Generated; notebook code executed in-process | Execute all notebooks from a fresh Jupyter kernel and inspect outputs |
| FR-02 pandas manipulation | Domain builders under `src/domains/` and captured notebook outputs | Implemented | Fresh-kernel reproduction |
| FR-03 Reproducible preparation | Raw catalog, source hashes, domain builders, preserved raw inputs | Implemented | Re-run documented setup/build from a clean environment |
| FR-04 Statistics per domain | Metrics and narratives: bootstrap intervals, chi-square association, descriptive group analyses, return risk, and forecast scoring where suitable | Implemented; code-level outputs generated | Independently reconcile selected headline values and assumptions |
| FR-05 At least 25 meaningful visualizations | Five per-domain manifests and `visualizations/inventory.csv` | 25 unique entries generated and validated; representative report charts visually inspected | Inspect all 25 figures in context and at presentation size |
| FR-06 Actionable recommendations | `recommendations/{sales,healthcare,sports,finance,ecommerce}.md` | Generated | Cross-check every cited finding against metrics and reports |
| FR-07 Five project PDF reports | `reports/project_*_report.pdf` and editable `reports/source/*.md` | Generated; covers and representative chart pages visually inspected | Inspect remaining chart, recommendation, and source pages |
| FR-08 Interactive metrics | `dashboard/app.py`; portfolio overview and five domain pages | Implemented; overview and all five pages observed in browser | Exercise filter changes, empty states, viewport sizes, and keyboard operation |
| FR-09 Prediction where justified | Suitability and limits in each domain narrative; chronological Elo source-forecast holdout | Addressed; no unsupported general ML claims | Confirm interpretation in notebook/report review |
| FR-10 Portfolio navigation | Root README, portfolio summary notebook, executive summary, cross-linked reports and docs | Generated | Verify all repository-relative links and execute master notebook in fresh kernel |
| FR-11 Presentation and recommendations | `presentation/portfolio_presentation.pptx`, outline, five recommendation documents | Generated | Visually inspect slides and confirm values match current metrics |
| FR-12 Setup, methodology, screenshots, validation | `docs/setup.md`, `docs/methodology.md`, data dictionary, validation log, this matrix | Documentation and structural validation complete; UI screenshot evidence pending | Save dashboard screenshots; complete browser/accessibility evidence and fresh-kernel validation |

## Environment and browser evidence

- The five builders ran and wrote their current outputs. Notebook cells were executed in-process through the same builders. This confirms the analytics code ran in the active interpreter, but it does **not** satisfy fresh-kernel execution.
- On Windows, Jupyter kernel startup remains blocked in `KernelManager.start_kernel` after PATH cleanup and attempted environment adjustments. Keep this requirement open until a real kernel launch and notebook execution complete.
- Browser review confirmed the overview and all five domain pages render. Healthcare showed 100,124 eligible encounters and 11.3% readmission; sports showed 63,157 team-game records; finance showed 1,762 dates and selected-symbol volatility; e-commerce rendered session conversion charts; sales showed GBP sales KPIs and interactive charts. This was a basic render check, not full filter, keyboard, viewport, or error-state acceptance.
- Visual inspection covered all report covers, a representative chart page per domain, and the first two executive-summary pages. Remaining report pages and the presentation slides still need review.
- `docs/screenshots/` exists, but it has no accepted dashboard screenshot files; PDF page previews were stored outside the project workspace.
- No publication or deployment has been performed.
