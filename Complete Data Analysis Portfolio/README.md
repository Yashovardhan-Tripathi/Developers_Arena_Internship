# Complete Data Analysis Portfolio

A reproducible portfolio of five evidence based analyses: business sales, healthcare, sports, finance, and e-commerce. The project follows [`PRD.md`](PRD.md), [`Design.md`](Design.md), [`Phases.md`](Phases.md), and the [construction blueprint](plans/portfolio-blueprint.md).

## Status

The five domain analyses, notebooks, chart inventory, recommendations, PDF reports, unified dashboard, portfolio summary, executive summary, and presentation are complete. A clean environment reproduced the full build and all six notebooks; final artifact validation reported READY. All report, summary, and presentation pages were visually reviewed. Dashboard filters, reset, no-match, and missing/malformed-input recovery were checked; selected findings and recommendations were reconciled across outputs. A direct screen-reader assessment was not performed. See [`docs/acceptance_matrix.md`](docs/acceptance_matrix.md) and [`docs/validation.md`](docs/validation.md) for evidence and limitations.

## Explore

- [Business sales notebook](project1_sales_analysis/analysis.ipynb) · [report](reports/project_sales_report.pdf) · [recommendations](recommendations/sales.md)
- [Healthcare notebook](project2_healthcare_analysis/analysis.ipynb) · [report](reports/project_healthcare_report.pdf) · [recommendations](recommendations/healthcare.md)
- [Sports notebook](project3_sports_analytics/analysis.ipynb) · [report](reports/project_sports_report.pdf) · [recommendations](recommendations/sports.md)
- [Finance notebook](project4_financial_analysis/analysis.ipynb) · [report](reports/project_finance_report.pdf) · [recommendations](recommendations/finance.md)
- [E-commerce notebook](project5_ecommerce_analytics/analysis.ipynb) · [report](reports/project_ecommerce_report.pdf) · [recommendations](recommendations/ecommerce.md)
- [Portfolio summary notebook](portfolio_summary.ipynb) · [executive summary](executive_summary.pdf) · [presentation](presentation/portfolio_presentation.pptx)
- [Chart inventory](visualizations/inventory.csv) · [Methodology](docs/methodology.md) · [Data catalog](datasets/catalog.csv)
- [Dashboard screenshots](docs/screenshots/README.md)

## Run locally

Follow [`docs/setup.md`](docs/setup.md), then from the project root:

```powershell
python scripts/build_outputs.py --domain all
python scripts/merge_chart_inventory.py
python scripts/execute_notebooks.py
python scripts/render_reports.py
python scripts/validate_artifacts.py --all --submission
python -m streamlit run dashboard/app.py
```

Raw source snapshots are not redistributed by this repository. See [`datasets/README.md`](datasets/README.md) for attribution, terms, retrieval, and expected local paths. Keep raw data unchanged under ignored `datasets/raw/` folders.

## Project guidance

- [Requirements](PRD.md) · [Architecture](architecture.md) · [Working rules](Rules.md) · [Design](Design.md) · [Phases](Phases.md) · [Project memory](Memory.md)
- [Setup](docs/setup.md) · [Data dictionary](docs/data_dictionary.md) · [Validation record](docs/validation.md) · [Acceptance matrix](docs/acceptance_matrix.md)

Findings describe the selected historical datasets. They do not establish causality, clinical efficacy, current sports forecasts, or expected investment returns.
