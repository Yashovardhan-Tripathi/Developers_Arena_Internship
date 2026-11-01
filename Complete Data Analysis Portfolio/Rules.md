# Project Working Rules

Status: Active documentation baseline.
Last updated: 2026-10-31

## 1. Authorization and scope

1. The current authorized task covers the six planning documents, Archify planning diagrams, and an ECC Blueprint construction plan with review. It permits local documentation, diagram candidates, generated HTML, and verification receipts. Do not start dataset acquisition, application coding, dependency installation, analysis, dashboard development, or report generation until the user instructs implementation to begin.
2. A later instruction to begin an agreed phase authorizes its ordinary reversible work. Do not repeatedly ask for permission already provided.
3. Follow the user's latest explicit boundaries. Surface material changes to agreed scope before carrying out dependent work.
4. Keep work within this project directory unless the user authorizes another location.
5. Do not modify sibling internship projects, parent documentation, remotes, or account ownership as part of this project.
6. Do not commit, push, deploy, publish, send messages, or use paid services without appropriate user authorization.
7. Inspect existing content before editing. Preserve user changes and do not overwrite unrelated work.
8. Do not delete source data, reset Git history, or perform broad cleanup without explicit authorization.

## 2. Requirement and decision control

- Use `PRD.md` as the requirement baseline and `Phases.md` as the execution sequence.
- Treat `architecture.md` and `Design.md` as proposed specifications until implemented and validated.
- Record material choices and deviations in `Memory.md`, then update affected planning documents.
- Resolve contradictions openly. Current planning assumptions are 25+ charts, all five domains, and one unified local dashboard.
- Do not present a proposed file, tool, feature, or result as already implemented.
- Use small, reviewable changes. Avoid unrelated refactoring and unnecessary frameworks.

## 3. Data handling

- Record provenance and usage terms before downloading or redistributing a dataset.
- Preserve raw input files. Write cleaned data to separate processed paths.
- Never fabricate observations or silently replace real data with simulated data.
- Label synthetic data, sampling, imputation, exclusions, and coverage limitations.
- Do not include identifiable patient information, credentials, access tokens, or other sensitive records in repository artifacts or screenshots.
- Record units, date coverage, row counts, keys, and data-quality decisions.
- Do not claim a source is licensed for redistribution until its terms have been checked.

## 4. Analysis integrity

- Define each question, metric, denominator, and aggregation level before interpreting results.
- Choose statistical methods based on the data and assumptions. Report uncertainty, effect size, and multiple-comparison treatment where relevant.
- Describe associations accurately; do not claim causation from observational data alone.
- Separate training and evaluation before fitting learned preprocessing. Address temporal and entity leakage.
- Compare models against a suitable baseline and disclose weak or negative results.
- Do not reproduce sample output figures from the brief as actual findings.
- Do not report arbitrary overall analysis accuracy, actionability percentages, or savings without a defensible calculation and evidence.
- Recommendations must cite findings and distinguish measured outcomes from hypothetical benefits.

## 5. Implementation conventions once authorized

- Use project-relative paths, clear names, small reusable functions, and documented dependencies.
- Keep domain calculations reusable between notebook outputs and dashboard inputs.
- Keep notebooks readable: question, source, cleaning, analysis, statistics, prediction suitability, findings, recommendations, and limitations.
- Use appropriate deterministic seeds for stochastic procedures and record data snapshots.
- Explain domain decisions; avoid comments that merely restate obvious code.
- Validate important logic with focused tests. Do not create tests that only mirror trivial implementation details.
- Keep large artifacts and caches out of version control when unsuitable; document how to regenerate them.

## 6. UI and reporting rules

- Follow `Design.md` for navigation, typography, color, chart labeling, and interaction states.
- Show data coverage and source context near results. Never show missing data as a measured zero.
- Use neutral language for healthcare and finance findings; this portfolio is an analytical demonstration.
- Keep implementation diagnostics out of normal dashboard flows; present understandable recovery guidance.
- Use consistent metric names and values across notebooks, dashboards, PDFs, and slides.

## 7. Verification and completion

- Run checks appropriate to the changed behavior, and record actual results.
- Distinguish local verification from cloud, production, security, or live-service claims.
- Mark a phase complete only when its exit criteria have evidence; do not mark completion based on generated filenames alone.
- At a handoff, state what changed, what was checked, what remains, and the next authorized action.
- Keep `Memory.md` concise and current at meaningful milestones once implementation is authorized.

## 8. Continuity boundary

`Memory.md` is a project-local progress record. It is not an instruction to modify global Codex memory or other projects. Project rules do not override explicit user instructions or host safety and approval requirements.
