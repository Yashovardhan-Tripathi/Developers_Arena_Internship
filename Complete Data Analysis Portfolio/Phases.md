# Project Phases

Status: Phases 1–9 complete for local delivery; direct screen-reader assessment was not performed.
Last updated: 2026-11-07

## Execution model

The brief suggests six weeks: one per domain and a final integration week. The phases below provide more detailed checkpoints within that indicative schedule. Durations depend on dataset suitability and review; they are not promised completion dates.

Each phase records inputs, work, deliverables, and exit criteria. A phase starts after its dependencies are satisfied and user authorization covers the work. Routine work within an authorized phase should proceed without repeated confirmation.

| Phase | Scope | Dependency | Initial status |
| --- | --- | --- | --- |
| 0 | Planning baseline | Supplied brief | Complete |
| 1 | Dataset selection and project foundation | User instruction received 2026-11-04 | Complete; sources, contracts, root resolution, and clean-environment integration verified |
| 2 | Sales analysis | Phase 1 and suitable sales data | Complete; analysis, outputs, notebook, report, and recommendations validated |
| 3 | Healthcare analysis | Phase 1 and suitable healthcare data | Complete; analysis, outputs, notebook, report, and recommendations validated |
| 4 | Sports analysis | Phase 1 and suitable sports data | Complete; analysis, outputs, notebook, report, and recommendations validated |
| 5 | Financial analysis | Phase 1 and suitable finance data | Complete; analysis, outputs, notebook, report, and recommendations validated |
| 6 | E-commerce analysis | Phase 1 and suitable e-commerce data | Complete; analysis, outputs, notebook, report, and recommendations validated |
| 7 | Unified dashboard | Stable derived data contracts | Complete; filters, reset, no-match/error recovery, keyboard, and responsive checks passed. Direct screen-reader evaluation is optional follow-up. |
| 8 | Portfolio reports and presentation | Validated domain results | Complete; all report and slide pages visually reviewed; selected headline and recommendation cross-check passed |
| 9 | Final validation and handoff | All deliverables prepared | Complete; clean rebuild, artifact/link checks, project-scoped Git status, diff check, and handoff evidence recorded. No publication occurred. |

## Phase 0 — Planning baseline

Inputs: supplied project requirements and user authorization to begin implementation on 2026-11-04.

Work: capture scope, resolve brief inconsistencies through explicit assumptions, propose architecture and UI, establish boundaries, and record project state.

Deliverables: `PRD.md`, `architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, and `Memory.md`.

Exit: planning documents and reviewed workflow are consistent. The next phase begins after explicit implementation authorization.

## Phase 1 — Dataset selection and foundation

Inputs: implementation authorization received 2026-11-04 and planning baseline.

Work:

1. Inspect current repository state and applicable instructions again.
2. Assess candidate datasets for all five domains: provenance, usage terms, columns, time coverage, quality, and practical size.
3. Choose distinct questions and document unsupported candidate metrics before committing to an analysis.
4. Resolve dashboard scope and proposed tool choices using available user direction.
5. Create the needed folder structure, environment instructions, dependency file, and data catalog.
6. Establish source schemas, shared output contracts, chart inventory, and initial reproducible loading/cleaning helpers.

Progress across implementation: all five domains have downloaded inputs and local schema/quality profiles; sports has separate team-game Elo and player-season RAPTOR sources. SHA-256, byte sizes, row counts, columns, blank/literal-unknown counts, source terms, and limitations are in `datasets/catalog.csv`, `datasets/README.md`, and `docs/data_dictionary.md`. Root resolution, raw/processed I/O, quality/statistics/chart helpers, metric/chart schema validators, and phase-aware build/validation CLIs have been used in the complete build. Both existing and separately recreated environments execute all notebooks. Full evidence is in `docs/validation.md`.

Deliverables: dataset catalog, retrieval guidance, schema notes, initial setup documentation, and working preparation path.

Exit: all five domains have usable inputs or a clearly resolved replacement; setup and a representative data load have been verified. Do not invent findings to compensate for unsuitable data. **Current status:** dataset selection, shared contracts, CLI interfaces, nested root resolution, clean environment setup, and fresh-kernel notebook execution passed; see `docs/validation.md`.

## Common completion checklist for Phases 2–6

- Define the decision question, unit of analysis, metrics, and coverage.
- Profile and clean data with recorded before/after quality results.
- Perform exploratory and statistical analysis with justified assumptions.
- Produce at least five substantive charts with unique questions or analytical purposes.
- Assess predictive suitability; implement a baseline and evaluated model only when justified.
- Write findings, evidence-linked recommendations, and limitations.
- Save reproducible outputs, draft the domain report, and populate its recommendation document.
- Execute the notebook from a fresh kernel; check important metric calculations and artifacts.
- Record domain chart entries in `visualizations/<domain>/manifest.csv` and submit validation evidence to the integrator. The integrator updates shared inventory, acceptance evidence, dependencies, shared helpers, and project memory; domain workers do not edit those files concurrently.

## Phase 2 — Business sales analysis

Indicative slot: Week 1, alongside foundation work where practical.

Analyze temporal sales patterns, category or product contribution, order values, and customer behavior. Use RFM only with suitable customer IDs, order IDs, dates, and purchase values. Calculate profit or retention only if fields and coverage support defensible definitions.

Deliverables: sales notebook, at least five charts, derived tables/metrics, draft report, and recommendations.

Exit: common checklist passes; monetary totals reconcile and transaction grain is explicit.

## Phase 3 — Healthcare analysis

Indicative slot: Week 2.

Analyze patient or encounter characteristics and supported outcomes, utilization, or costs. Define readmission windows if applicable. Consider confounding and group-size differences. Use de-identified public or clearly labeled synthetic data.

Deliverables: healthcare notebook, at least five charts, derived outputs, draft report, and operational recommendations within dataset limits.

Exit: common checklist passes; sensitive identifiers are absent and outcome/denominator definitions are documented. No clinical efficacy or causation claims exceed the evidence.

## Phase 4 — Sports analytics

Indicative slot: Week 3.

Analyze player/team performance and changes across seasons or matches. Account for participation or exposure when comparing performance. If predicting matches, use features available before each match and a suitable evaluation split.

Deliverables: sports notebook, at least five charts, derived outputs, draft report, and recommendations.

Exit: common checklist passes; comparisons state their sample sizes, and any prediction avoids post-match information leakage.

## Phase 5 — Financial analysis

Indicative slot: Week 4.

Analyze prices, returns, volatility, correlations, and drawdowns. State adjusted/unadjusted price choice, observation frequency, missing trading dates, portfolio weights, rebalance rules, and annualization assumptions where used. Evaluate any forecast chronologically against a baseline.

Deliverables: finance notebook, at least five charts, derived outputs, draft report, and analytical recommendations.


Exit: common checklist passes; calculation assumptions are reproducible and results do not imply guaranteed investment performance.

## Phase 6 — E-commerce analytics

Indicative slot: Week 5.

Analyze purchasing behavior, repeat customers, segmentation, and product relationships. Define treatment of returns and cancellations. Fit segmentation transforms appropriately; assess cluster usefulness and stability. Use basket or recommendation analysis only when transaction structure supports it.

Deliverables: e-commerce notebook, at least five charts, derived outputs, draft report, and recommendations distinct from the sales project's focus.

Exit: common checklist passes; segmentation or recommendation claims have validation appropriate to their actual purpose.

## Phase 7 — Unified interactive dashboard

Indicative slot: Week 6; preliminary layout may follow the first stable domain outputs.

Work: implement portfolio overview and five domain views, supported filters, KPI cards, explanatory chart text, source/coverage labels, and required interaction states. Read shared outputs; keep filtered calculations consistent with notebook logic.

Deliverables: locally runnable dashboard, setup instructions, and screenshots.

Exit: all pages render, supported filters update corresponding metrics/charts correctly, empty/missing/error states are handled, keyboard use is checked, and dashboard totals agree with validated outputs. Record actual tested viewport sizes.

## Phase 8 — Reports, integration, and presentation

Indicative slot: Week 6.

Work: finalize five PDF reports, portfolio master notebook, executive summary, five recommendation documents, slides, README navigation, methodology, data dictionaries, and technical documentation. Reconcile figures across all formats.

Deliverables: complete submission artifacts in canonical locations.

Exit: reports and slides have been visually inspected; 25+ unique chart inventory entries exist; sources, limitations, labels, and links are complete; no sample numbers remain as actual findings.

## Phase 9 — Final validation and handoff

Work: reproduce setup, run all notebooks and necessary tests, inspect dashboard flows, verify artifact paths and links, inspect tracked-file boundaries, and map PRD requirements to actual evidence.

Deliverables: completed acceptance matrix, validation log, updated project memory, and handoff notes.

## Current implementation checkpoint — 2026-11-07

- Generated five domain notebooks, metrics, processed tables, chart data, report narratives, five chart files and manifests per domain, recommendation notes, and five domain PDFs .
- Generated the 25-chart inventory, portfolio summary notebook, executive-summary PDF, eight-slide PowerPoint, and Streamlit dashboard.
- Browser-observed the overview and the five domain views; targeted KPI and chart text are recorded in `docs/acceptance_matrix.md` and `docs/validation.md`.
- Refreshed e-commerce month ordering and its notebook/report after recognizing that this dataset spells June in full.
- Clean-environment end-to-end reproduction completed: pinned dependencies installed, five builds, six notebooks, five reports, and artifact validation passed. Filter/reset, no-match/reset, missing/malformed-input recovery, keyboard paths, and responsive checks were exercised. Selected cross-artifact headline and recommendation checks passed after fixing sports percentage rounding. All report and presentation pages have been visually inspected; the 42-file Markdown link scan passed. Direct screen-reader assessment was not performed and is not a release gate.

Exit: every required deliverable is verified or explicitly identified as outstanding. Prepare repository contents for submission. Commit, push, publication, or deployment occurs only when separately authorized.

## Handling blockers and revisions

Record the precise blocker, evidence, impact, and next action in `Memory.md`. Continue independent authorized work where useful. If a dataset or method changes, update source documentation, affected outputs, reports, and acceptance evidence before claiming completion.

## Detailed execution plan

Use [plans/portfolio-blueprint.md](plans/portfolio-blueprint.md) for ten independently reviewable steps and future verification commands. S2–S6 may run independently after S1 under disjoint file ownership. Report drafting may overlap dashboard work; final screenshots and submission packaging require the dashboard completion gate. See [docs/diagrams.md](docs/diagrams.md) for the proposed system flows. This planning extension does not start Phase 1.
