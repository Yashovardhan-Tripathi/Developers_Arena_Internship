# Complete Data Analysis Portfolio

A reproducible portfolio of five evidence-based analyses: business sales, healthcare, sports, finance, and e-commerce. The project follows [`PRD.md`](PRD.md), [`Design.md`](Design.md), [`Phases.md`](Phases.md), and the reviewed [construction blueprint](plans/portfolio-blueprint.md).

## Current status

Phase 1 (dataset selection and foundation) is underway. All five domain inputs have been downloaded and profiled; the sports domain uses complementary team-game and player-season sources. Source limits and attribution are listed in [`datasets/README.md`](datasets/README.md). Domain findings, reports, and charts do not exist yet; illustrative figures from the original brief are not results.

## Setup and data

See [`docs/setup.md`](docs/setup.md) for the observed Python environment and setup. The public-source download command is `python scripts/download_sources.py --domain all`; it writes only to ignored `datasets/raw/` folders and refuses to replace existing files. The finance input is a roughly 50 MB split-adjusted historical file retrieved from a public mirror of the documented CC0 source.

## Navigation

- Requirements: [`PRD.md`](PRD.md)
- Architecture: [`architecture.md`](architecture.md)
- Working rules: [`Rules.md`](Rules.md)
- Experience design: [`Design.md`](Design.md)
- Phases and current gate: [`Phases.md`](Phases.md)
- Dataset catalog: [`datasets/catalog.csv`](datasets/catalog.csv)
- Current progress and decisions: [`Memory.md`](Memory.md)
