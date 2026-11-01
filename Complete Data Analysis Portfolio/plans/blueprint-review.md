# Blueprint adversarial review

Review date: 2026-10-31. Reviewed baseline: `portfolio-blueprint.md` version 1.0 (draft), plus all six root planning documents. Scope: planning only; no implementation, dependency installation, data acquisition, or runtime testing performed.

The supplied PRD is the requirements baseline for this review. The original pasted brief was not separately available to this reviewer, so completeness against that brief is assessed through the PRD, not independently asserted.

## Verdict

No critical defect or current implementation-scope violation found. The ten steps cover FR-01–FR-12 and preserve the key assumptions: five domains, 25+ distinct charts, conditional prediction, provisional dashboard, and no invented results. Correct the medium-severity execution ambiguities below before treating the plan as ready for cold-start implementation. These are documentation fixes and do not authorize implementation.

## Findings, ranked by severity

### R1 — Medium: the graph omits the dashboard dependency of final report acceptance

Evidence: blueprint dependency graph and scheduling paragraph; S9 dependencies, verification, and exit criteria.

S9 can draft reports after S7, but its final screenshots and full submission validation need completed S8 artifacts. The prose acknowledges this while the DAG presents S8 and S9 as independent complete steps. A scheduler following the graph alone could attempt to finish S9 too early.

Fix: either add an explicitly labeled S8 -> S9 finalization edge and state that only S9 drafting overlaps, or split S9 into draft/package and finalization steps. Keep the graph, scheduling summary, phase mapping, and diagrams consistent. S10 must depend on the completed finalization gate.

### R2 — Medium: validation scopes do not specify when shared/final artifacts become mandatory

Evidence: CLI conventions, S2–S6 proposed chart entries, S7 inventory integration, S9 `--submission`, and S10 final acceptance records.

The instruction that domain validation must not require unfinished domains is helpful, but does not settle whether it requires the shared inventory finalized in S7. Likewise, “all final artifacts” in `--submission` could include acceptance evidence and handoff records completed in S10, which would make S9's exit depend on its own downstream step. S1 is told to implement all CLI contracts before domain algorithms exist without distinguishing interface availability from full build readiness.

Fix: specify stage-aware checks. Domain validation checks that domain's notebook, output schema, chart manifest, narrative, and recommendations without requiring merged inventory or final PDFs. Integrated validation checks all analyses and merged inventory. Submission validation checks deliverable files/screenshots/links; final acceptance records are independently completed and audited in S10, or use an explicitly separate final gate. In S1, require callable interfaces, fixture tests, and clear incomplete-domain errors; do not require real domain builds before S2–S6. Name a domain-local chart manifest path so contributors and the integrator exchange concrete artifacts.

### R3 — Medium: notebook execution lacks a kernel and working-directory contract

Evidence: root-relative command conventions and nbconvert commands for notebooks in nested project directories; architecture requirement that notebooks import shared `src` metric logic.

Launching nbconvert from the repository root alone does not establish that the execution kernel uses that root as its working directory or that the active Python environment matches notebook kernel metadata. Nested notebooks therefore need an explicit root-resolution/import strategy and verified kernel selection to make the promised commands reproducible on a fresh machine.

Fix: add to S1's exit criteria a documented project-root resolution and kernel/environment strategy, with one minimal nested fixture notebook executed by the same nbconvert command family. Require the five real notebooks to follow that contract. The strategy can use an installed project package, explicit execution configuration, or tested notebook path bootstrap; choose during implementation and update setup instructions. Do not claim the current proposed commands were run.

### R4 — Medium: direct-mode rollback assumes an unspecified recoverable prior version

Evidence: preflight identifies untracked project content and no branch/commit workflow; domain rollback instructions repeatedly say to restore a prior source version.

The boundaries are safe, but no recovery checkpoint is specified for untracked files. An executor cannot reliably restore a prior source version merely from Git in this starting state.

Fix: before each authorized implementation step, capture a project-local, ignored checkpoint or equivalent reviewed backup of that step's existing owned files and a manifest of new paths. Record the checkpoint location and base state. Restoration must preserve intervening user edits and must not automatically remove raw data or newly created files. If a later user-authorized commit provides the recovery base, record that instead. Do not create checkpoints or commits during this planning task.

### R5 — Low: source-document state and parallel ownership need synchronization

Evidence: `architecture.md` says only six planning files exist; `Rules.md` and `Memory.md` describe the current request as six documents only; `Memory.md` still says verification of those six is the next action. `Phases.md` common checklist tells each phase to update shared inventory, acceptance evidence, and project memory, whereas the blueprint assigns these to one integrator.

These statements were accurate for the previous planning baseline, but become stale when this blueprint and diagrams are registered. The shared-file directions are reconcilable, yet a cold-start domain worker could read them as permission to edit common files concurrently.

Fix: update the six-document baseline wording to acknowledge the authorized blueprint/diagram extension, keep implementation unstarted, and link the new planning artifacts. State in the phase checklist that domain workers submit local evidence/manifests and the designated integrator updates shared inventory, acceptance records, dependencies, and project memory. Name concrete domain-specific test paths for parallel work if such tests are added.

## Checklist result

| Area | Result |
| --- | --- |
| Requirement coverage | All twelve PRD functional requirements have owners; no omitted required deliverable found |
| Dependency order | Foundation and integration order sound; R1/R2 require clearer finalization gates |
| Cold-start context | Context briefs, sources, owned paths, and exit criteria present; R2/R3 clarify execution contracts |
| Command feasibility | Properly labeled future contracts; actual runtime feasibility remains unverified because implementation is absent |
| Parallel file ownership | Domain paths mostly disjoint and shared integrator explicit; R5 resolves phase-text ambiguity |
| Rollback | Correctly avoids parent resets/deletion; R4 adds an available recovery base |
| Scope control | Strong: no code, installs, data acquisition, commits, push, or deployment authorized now |
| Assumptions | Dataset, dashboard, statistical method, and presentation choices remain explicit and provisional |
| Source consistency | Requirements align; R5 updates current-state descriptions after registration |
| Review limitation | This is a document review, not proof of dataset suitability, package compatibility, executable analysis, or UI behavior |

## Resolution record

The author should record each fix against R1–R5 in the blueprint review register, then recheck the changed dependency graph, validation contract, setup contract, rollback guidance, and source-document links. No critical findings require escalation. Finalization does not authorize any future implementation step.

## Re-review of version 1.1

Date: 2026-10-31. Verdict: accepted as a construction planning document. No unresolved critical or medium findings remain from this review. Implementation remains unstarted and unauthorized. The findings above preserve the version 1.0 review history; the following dispositions supersede their open status.

| Finding | Disposition and verified change |
| --- | --- |
| R1 | Resolved. The graph explicitly includes S8 -> S9 for final screenshots and submission. Scheduling and S9 dependencies distinguish parallel drafting from completion. |
| R2 | Resolved. Domain, integrated, submission, and final acceptance checks are separated. Domain manifests have concrete paths. Submission validation excludes the S10 acceptance/handoff records. S1 supplies fixture-tested callable interfaces with clear incomplete-domain errors rather than pretending domain analyses exist. |
| R3 | Resolved at planning level. S1 must verify a nested fixture notebook, project-root resolution, shared imports, data/output paths, and actual environment/kernel selection. Exact commands and runtime success remain implementation evidence to obtain later. |
| R4 | Resolved. The recovery contract requires an ignored project-local checkpoint or authorized commit, recorded recovery base, owned-file manifest, comparison with intervening user edits, raw-data preservation, and no automatic deletion of new files. |
| R5 | Resolved for reviewed source instructions. Rules.md acknowledges the planning extension; architecture.md records the Blueprint/diagram scope and domain manifests/tests; Phases.md directs shared updates through the integrator. Memory.md and the diagram guide are undergoing final registration by the author and are not treated as implementation blockers. |

### Independent original-brief coverage check

The re-review read the complete supplied attachment `Pasted text.txt` directly. This supersedes the original review's limitation to PRD-only requirement coverage.

- The objective, five specified domains, pandas, cleaning, statistics per dataset, actionable insights, conditional predictive analysis, reports with executive summaries, and interactive metrics are represented in the PRD and owning construction steps.
- The stricter 25+ chart deliverable reconciles the brief's 20+ technical minimum and 25+ submission target. Five charts in each of five domains meets that target without counting duplicate exports.
- Five notebooks, five PDFs, master notebook, executive summary, slides, recommendation documents, dependencies, README navigation, shared data/report/chart directories, and detailed documentation all have planned locations and owners.
- Documentation coverage includes setup, structure, methodology/technical explanation, actual screenshots, testing evidence, and practical domain recommendations. These are planned deliverables, not completed artifacts.
- The optional-versus-required dashboard inconsistency is explicitly preserved as a scope decision, while the plan includes a unified dashboard. The five-domain interpretation matches the objective, week-by-week guide, and submission structure despite the separate options list.
- The supplied sample code, sample financial/healthcare figures, impact percentages, and 5.2-million-record count are correctly treated as illustrations rather than required implementations or measured results.
- The brief calls for an organized GitHub portfolio. Local preparation is covered; actual publication remains deferred under the user's documentation-only boundary. Final handoff must continue distinguishing local readiness from publication.

No required deliverable was found missing in this independent coverage check. This acceptance concerns plan completeness and consistency only; it does not certify dataset suitability, executable commands, analytical correctness, actual report quality, or dashboard behavior.
