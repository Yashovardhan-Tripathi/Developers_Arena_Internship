# Complete Data Analysis Portfolio

A reproducible portfolio of five evidence based analyses: business sales, healthcare, sports, finance, and e-commerce. The project follows [`PRD.md`](PRD.md), [`Design.md`](Design.md), [`Phases.md`](Phases.md), and the [construction blueprint](plans/portfolio-blueprint.md).

## Status

All five domain pipelines have produced notebooks, analysis outputs, five charts each, report PDFs, and finding-linked recommendation documents. The integrated dashboard, portfolio notebook, executive summary, and presentation are also generated. Final acceptance remains open: domain notebooks have been executed in-process, but a fresh Jupyter kernel has not yet completed on this Windows environment; dashboard page, accessibility, responsive layout, and screenshot checks are still being completed. See [`docs/acceptance_matrix.md`](docs/acceptance_matrix.md) and [`docs/validation.md`](docs/validation.md) for evidence and limitations.

## Explore

- [Business sales notebook](project1_sales_analysis/analysis.ipynb) · [report](reports/project_sales_report.pdf) · [recommendations](recommendations/sales.md)
- [Healthcare notebook](project2_healthcare_analysis/analysis.ipynb) · [report](reports/project_healthcare_report.pdf) · [recommendations](recommendations/healthcare.md)
- [Sports notebook](project3_sports_analytics/analysis.ipynb) · [report](reports/project_sports_report.pdf) · [recommendations](recommendations/sports.md)
- [Finance notebook](project4_financial_analysis/analysis.ipynb) · [report](reports/project_finance_report.pdf) · [recommendations](recommendations/finance.md)
- [E-commerce notebook](project5_ecommerce_analytics/analysis.ipynb) · [report](reports/project_ecommerce_report.pdf) · [recommendations](recommendations/ecommerce.md)
- [Portfolio summary notebook](portfolio_summary.ipynb) · [executive summary](executive_summary.pdf) · [presentation](presentation/portfolio_presentation.pptx)
- [Chart inventory](visualizations/inventory.csv) · [Methodology](docs/methodology.md) · [Data catalog](datasets/catalog.csv)

## Run locally

Follow [`docs/setup.md`](docs/setup.md), then from the project root:

```powershell
python scripts/build_outputs.py --domain all
python scripts/merge_chart_inventory.py
python scripts/render_reports.py
python scripts/validate_artifacts.py --all --submission
python -m streamlit run dashboard/app.py
```

Raw source snapshots are not redistributed by this repository. See [`datasets/README.md`](datasets/README.md) for attribution, terms, retrieval, and expected local paths. Keep raw data unchanged under ignored `datasets/raw/` folders.

## Project guidance

- [Requirements](PRD.md) · [Architecture](architecture.md) · [Working rules](Rules.md) · [Design](Design.md) · [Phases](Phases.md) · [Project memory](Memory.md)
- [Setup](docs/setup.md) · [Data dictionary](docs/data_dictionary.md) · [Validation record](docs/validation.md) · [Acceptance matrix](docs/acceptance_matrix.md)

Findings describe the selected historical datasets. They do not establish causality, clinical efficacy, current sports forecasts, or expected investment returns.
