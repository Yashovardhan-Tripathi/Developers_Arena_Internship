# Project diagrams

These diagrams describe the implemented local workflow as of 2026-11-07. They are source-mapped to the current repository; they do not imply cloud hosting, publication, or production services.

## Architecture

```mermaid
flowchart LR
    Raw[Preserved raw datasets] --> Prep[Preparation and domain builders]
    Prep --> Proc[Processed tables and metrics]
    Prep --> Charts[Chart figures and manifests]
    Proc --> NB[Five domain notebooks]
    Proc --> Dash[Streamlit dashboard]
    Charts --> Dash
    NB --> Reports[PDF reports and recommendations]
    Proc --> Summary[Portfolio notebook and executive summary]
    Reports --> Slides[Presentation]
    Summary --> Slides
    Catalog[Dataset catalog and methodology] --> NB
    Catalog --> Dash
```

**Source mapping:** `datasets/raw/` and `datasets/catalog.csv`; `scripts/prepare_data.py`, `src/domains/`, and `scripts/build_outputs.py`; `outputs/`; `visualizations/`; `project*/analysis.ipynb`; `dashboard/app.py`; `reports/`; `recommendations/`; `portfolio_summary.ipynb`; `scripts/render_executive_summary.py`; `scripts/render_presentation.py`.

## Reproduction workflow

```mermaid
flowchart TD
    A[Install project requirements] --> B[Retrieve documented source snapshots]
    B --> C[Profile and prepare each domain]
    C --> D[Build domain outputs]
    D --> E[Merge chart inventory]
    E --> F[Execute notebooks in portfolio kernel]
    F --> G[Render reports, summary, and deck]
    G --> H[Validate paths and metric/chart contracts]
    H --> I[Run local dashboard]
```

**Source mapping:** `docs/setup.md`; `scripts/download_sources.py`; `scripts/prepare_data.py`; `scripts/build_outputs.py`; `scripts/merge_chart_inventory.py`; `scripts/execute_notebooks.py`; `scripts/render_reports.py`; `scripts/render_executive_summary.py`; `scripts/render_presentation.py`; `scripts/validate_artifacts.py`; `dashboard/app.py`.

## Data flow

```mermaid
flowchart LR
    Sources[Versioned public source snapshots] --> Raw[Raw files, preserved unchanged]
    Raw --> Loader[src.data_io]
    Loader --> Builder[src.domains domain builder]
    Builder --> Tables[Processed tables and metrics.json]
    Builder --> Figures[Figures and per-domain manifest]
    Tables --> Notebook[Domain notebook]
    Tables --> Dashboard[Filtered dashboard views]
    Figures --> Dashboard
    Tables --> Narrative[Report narrative and recommendations]
    Narrative --> PDF[Domain PDF report]
    PDF --> Portfolio[Executive summary and slide deck]
```

**Source mapping:** loaders are in `src/data_io.py`; domain transformations are in `src/domains/{sales,healthcare,sports,finance,ecommerce}.py`; output helpers are in `src/domains/common.py`; contracts are in `src/contracts.py`; dashboard consumers are in `dashboard/app.py`; report rendering is in `scripts/render_reports.py`.

## Domain analysis execution

```mermaid
sequenceDiagram
    participant User
    participant Notebook as Domain notebook
    participant Builder as src.domains.*.build
    participant Data as Raw and processed files
    participant Outputs as Metrics, tables, figures, reports
    User->>Notebook: Execute with portfolio kernel
    Notebook->>Builder: Call shared domain builder
    Builder->>Data: Load and transform source snapshot
    Builder->>Outputs: Write metrics, tables, figures, narrative, recommendation
    Builder-->>Notebook: Return headline, metrics, chart count
    Notebook-->>User: Display captured analysis summary
```

**Source mapping:** the domain notebooks call the builders in `src/domains/`; root resolution is defined in each notebook cell; `scripts/execute_notebooks.py` executes the five notebooks and `portfolio_summary.ipynb`.

## Dashboard interaction

```mermaid
sequenceDiagram
    participant Reader
    participant UI as Streamlit page
    participant Data as Validated outputs
    participant Chart as Plotly and static figures
    Reader->>UI: Select a portfolio page
    UI->>Data: Load metrics, processed table, and manifest
    Reader->>UI: Change supported page filter
    UI->>Data: Filter domain rows for selected values
    Data-->>UI: Filtered rows and updated metric values
    UI->>Chart: Render updated interactive charts
    UI-->>Reader: Show source coverage and limitations
```

**Source mapping:** page navigation, filters, loading, empty states, downloads, and charts are implemented in `dashboard/app.py`. The dashboard reads local files under `outputs/`, `datasets/processed/`, and `visualizations/`; it does not query a remote service.
