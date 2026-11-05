# Product Requirements Document

Status: Implementation underway; Phase 1 foundation and dataset selection in progress.
Source: User-supplied Complete Data Analysis Portfolio brief.
Last updated: 2026-11-04

## 1. Purpose

Build a professional, reproducible portfolio of at least five end-to-end data analysis projects across business sales, healthcare, sports, finance, and e-commerce. Demonstrate data preparation, statistical reasoning, visual storytelling, predictive analysis where appropriate, and recommendations supported by evidence.

## 2. Audience and outcomes

- Internship evaluators: inspect coverage, methodology, results, and submission quality.
- Recruiters and technical reviewers: navigate notebooks, understand technical decisions, and reproduce results.
- Nontechnical readers: understand the question, key findings, practical recommendations, and limitations.

Success means a reader can navigate the portfolio, reproduce the analyses from documented inputs, and trace each reported finding to an analysis output.

## 3. Required domain projects

| ID | Domain | Questions to investigate | Candidate outputs, subject to available data |
| --- | --- | --- | --- |
| P1 | Business sales | How do sales vary over time? Which products and customers contribute most? | Revenue trends, product contribution, customer behavior, RFM where supported |
| P2 | Healthcare | How do patient characteristics, treatment outcomes, and hospital metrics vary? | Patient distributions, outcome comparisons, cost or readmission analysis where supported |
| P3 | Sports | Which players and teams perform best, and which factors relate to outcomes? | Performance comparisons, team trends, match prediction where suitable |
| P4 | Finance | How do asset prices, returns, and portfolio risks change? | Return trends, volatility, correlation, drawdown, clearly stated portfolio assumptions |
| P5 | E-commerce | Which customer groups and purchase patterns matter? | Segmentation, repeat purchasing, basket or recommendation insights where supported |

Business sales emphasizes commercial performance; e-commerce emphasizes customer and purchase behavior. Keep their questions distinct even if source fields overlap.

## 4. Functional requirements

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| FR-01 | Complete five distinct domain projects | Five executed notebooks with domain-specific questions and findings |
| FR-02 | Use pandas for comprehensive manipulation | Documented filtering, aggregation, joins or reshaping as appropriate |
| FR-03 | Implement reproducible cleaning and preprocessing | Raw inputs preserved; transformation logic and quality results recorded |
| FR-04 | Perform statistical analysis for every dataset | Descriptive statistics and suitable uncertainty estimates or tests, with assumptions and interpretation |
| FR-05 | Produce at least 25 meaningful visualizations overall | Chart inventory with project, purpose, source, and saved artifact; target at least five per project |
| FR-06 | Generate actionable recommendations | Each recommendation links to a finding, proposed action, limitation, and metric to monitor |
| FR-07 | Create five professional project PDF reports | Each includes executive summary, methods, results, visuals, recommendations, and limitations |
| FR-08 | Present key metrics interactively | Proposed unified dashboard covering all five domains; see scope interpretation below |
| FR-09 | Apply predictive analysis where justified | Suitability decision for each project; evaluated model and baseline when implemented |
| FR-10 | Provide unified portfolio navigation | Root README, master notebook, executive summary, and cross-links |
| FR-11 | Prepare presentation and recommendation materials | Presentation artifact and domain recommendation documents |
| FR-12 | Document setup, structure, technical approach, and validation | Dependency file, setup guide, methodology, screenshots, validation evidence |

## 5. Analysis and data standards

- Select public, lawfully usable datasets with traceable origin and usage terms. Simulated data is permitted by the brief but must be clearly labeled.
- Record source URL, retrieval date, version or snapshot, license or usage terms, schema, units, row counts, and relevant time coverage.
- Assess missing values, duplicates, invalid values, type consistency, identifier integrity, and domain constraints before analysis.
- State the unit of analysis and denominator for every rate. Distinguish rows, orders, customers, patients, matches, and assets.
- Document currency, timezone, date boundaries, and any exchange-rate assumptions. Do not assume all datasets use INR.
- Use effect sizes and uncertainty where meaningful. Explain statistical assumptions and avoid causal claims from observational associations.
- Split prediction data before learned preprocessing. Fit imputers, scalers, encoders, and feature selection on training data only.
- Use chronological evaluation for forecasting and other time-dependent predictions; address grouping where repeated entities could leak across splits.
- Compare predictive models to a suitable baseline and use task-specific metrics. Record limitations and random seeds.
- Do not set an arbitrary universal accuracy target or require machine learning when the data does not support a credible predictive question.

## 6. Deliverables

1. Five executed domain analysis notebooks.
2. Five project PDF reports and editable report sources.
3. At least 25 substantive visualizations, with accessible labels and consistent styling.
4. A unified interactive dashboard as the planning assumption.
5. `portfolio_summary.ipynb` and `executive_summary.pdf`.
6. Presentation slides and five business recommendation documents.
7. Organized repository contents, README navigation, dependencies, setup instructions, data documentation, screenshots, and validation evidence.

GitHub publication is a later action requiring an explicit user instruction; preparing repository contents does not authorize pushing.

## 7. Nonfunctional requirements

- Reproducibility: documented commands run from the project root; no machine-specific absolute paths in analysis code.
- Usability: readers can locate each project, its results, source data information, and limitations without inspecting implementation details.
- Accessibility: legible text, adequate contrast, keyboard-accessible controls, and chart descriptions.
- Maintainability: small reusable helpers for repeated tasks, consistent output paths, and no unnecessary framework complexity.
- Integrity: distinguish actual findings, illustrative examples, simulated results, and unverified assumptions.
- Portability: record the Python version and exact dependency versions validated during implementation.
- Performance: measure dashboard startup and filtering on selected datasets before setting performance targets; use cached derived data where appropriate.

## 8. Scope interpretation and open decisions

| Topic | Planning treatment |
| --- | --- |
| 20+ versus 25+ visualizations | Use the stricter 25+ target; repeated exports of the same chart count once |
| Dashboard required versus optional | Include a local unified dashboard; user authorized implementation according to the design on 2026-11-04 |
| Five domains described as options | Treat all five as required because the objective and submission list specify them |
| Sample output numbers | Illustrations only; never copy into findings without computed evidence |
| Dataset size | No mandatory minimum; the sample 5.2 million records is not an acceptance criterion |
| Folder layouts differ in brief | Use domain notebooks with centralized datasets, reports, and visualization artifacts |
| Tools | pandas required; Streamlit and Plotly proposed for dashboard; final stack remains provisional |
| Datasets | Not selected; assess coverage, license, quality, and practical download size first |
| Presentation format | PowerPoint or another user-approved portable slide format; choose before authoring |

## 9. Out of scope unless separately requested

Live trading or investment advice, clinical recommendations, production medical systems, paid APIs, authentication, multi-user databases, live streaming, cloud deployment, and automated external publication.

## 10. Final acceptance

- All functional requirements have linked evidence in a completion matrix.
- Each notebook executes from a fresh kernel using documented inputs.
- Statistical and predictive claims match computed outputs and their limitations.
- Dashboard metrics agree with notebook/report outputs for the same filters and data version.
- All reports, charts, links, screenshots, and presentation artifacts are readable and complete.
- A clean setup and representative end-to-end run are documented with actual results.
- No placeholder findings, invented impact claims, exposed credentials, or unlicensed redistributed datasets remain.

## 11. Planning document map

- [architecture.md](architecture.md): proposed structure, responsibilities, and data flow.
- [Rules.md](Rules.md): authorization and engineering boundaries.
- [Phases.md](Phases.md): staged execution and completion criteria.
- [Design.md](Design.md): dashboard and presentation UI/UX specification.
- [Memory.md](Memory.md): current state, decisions, unresolved items, and handoff record.
