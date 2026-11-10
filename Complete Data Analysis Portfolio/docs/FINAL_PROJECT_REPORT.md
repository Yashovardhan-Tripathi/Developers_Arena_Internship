# Complete Data Analysis Portfolio

## Final Project Report and Submission Documentation

**Prepared:** 11 November 2026  
**Project type:** Reproducible data analysis portfolio with a local interactive dashboard  
**Technology:** Python 3.13.9, pandas, NumPy, SciPy, scikit-learn, Matplotlib, Seaborn, Plotly, Streamlit, and Jupyter

## 1. Project overview

The Complete Data Analysis Portfolio demonstrates end-to-end analysis across five domains: business sales, healthcare encounters, basketball analytics, historical financial prices, and e-commerce sessions. Its goals are to show reproducible data preparation, appropriate statistical reasoning, clear visual communication, cautious predictive evaluation where justified, and recommendations that can be traced to evidence.

Each domain has a documented public source, a stated unit of analysis, preparation and analysis code, an executed notebook, a report, visualizations, and a recommendation. A shared Streamlit dashboard presents portfolio and domain views. A portfolio notebook, executive summary, and slide deck bring the five analyses together.

The work is local and reproducible. It does not provide a Django application, REST API, hosted production service, clinical guidance, investment advice, or live sports predictions. The dashboard reads local generated artifacts; no database or backend API is used.

## 2. Objectives and deliverables

- Complete five distinct, evidence-based domain analyses.
- Preserve source data and document provenance, grain, coverage, usage notes, and quality considerations.
- Build reusable Python modules and reproducible scripts for data preparation and analysis.
- Produce six executed notebooks: five domain notebooks and one portfolio summary notebook.
- Create five seven-page PDF domain reports and five editable report narratives.
- Inventory 25 unique visualizations and provide a filterable six-view dashboard (overview plus five domains).
- Provide recommendations, an executive summary PDF, an eight-slide presentation, setup instructions, screenshots, and validation evidence.

## 3. Code structure

The code is grouped by responsibility. Shared Python modules provide data loading, quality checks, statistical helpers, visualization support, and output validation. Five domain modules implement the sales, healthcare, sports, finance, and e-commerce analyses. Separate notebooks explain each analysis. Build scripts prepare data and artifacts, while the Streamlit dashboard reads the generated results. Reports, recommendations, visualizations, and presentation materials are organized as submission outputs.

Raw source files remain local and are not redistributed. The dataset catalog records their origins, terms, retrieval details, and expected local inputs.

## 4. Architecture and data flow

The implementation uses a local Python workflow. Shared loaders handle project-relative inputs, domain builders prepare data and calculate metrics, and output contracts validate metric and chart records. Scripts orchestrate preparation, output generation, notebook execution, report rendering, and artifact validation.

```text
Public source snapshots
        ↓
Preserved raw inputs → quality checks and domain builders
        ↓
Processed tables, metrics, chart data, figures, and manifests
        ├── Executed notebooks and static reports
        ├── Streamlit dashboard (local files only)
        └── Recommendations → executive summary → presentation
```

The dashboard loads the validated local metrics, tables, and chart artifacts. User-selected filters operate on supported detail or aggregate outputs; the app does not train models or query a remote service during interaction. There is no relational database, authentication layer, or public deployment in this project.

## 5. Data sources and analytical methods

| Domain | Source and unit | Main methods | Interpretation limits |
|---|---|---|---|
| Business sales | UCI Online Retail II; invoice line, Dec 2009–Dec 2011 | Cleaning and aggregation by invoice, product, country, and identified customer; invoice-level bootstrap interval for mean order value | GBP gross sales are not profit; cancelled and invalid/non-positive rows are excluded; customer IDs are often missing. |
| Healthcare | UCI Diabetes 130-US Hospitals; eligible encounter, 1999–2008 | Encounter summaries; patient-cluster bootstrap for the 30-day readmission proportion; descriptive group comparisons | Repeated encounters occur per patient; observational historical data supports no causal or clinical conclusion. Identifiers are excluded from exported outputs. |
| Sports | FiveThirtyEight NBA Elo team-game archive and historical RAPTOR player-season file | Chronological holdout assessment of published Elo probabilities on 2013–2015; accuracy and Brier score; separate descriptive player ratings | Elo coverage ends in 2015; RAPTOR ends in 2022 and methodology varies across eras. This is not a newly trained model or current forecast. |
| Finance | Split-adjusted NYSE price snapshot; security-date, 2010–2016 | Daily returns, annualized volatility using 252 trading days, drawdown, and illustrative equal-weight cohort summary | Dividend adjustment is undocumented; survivorship/selection bias applies; no transaction costs or taxes. Not investment advice. |
| E-commerce | UCI Online Shoppers Purchasing Intention; session, one-year sample | Conversion proportion and Wilson interval; visitor-type association via Pearson chi-square; descriptive engagement comparisons | Sessions are not repeat customers or baskets; association is not causation. PageValues is excluded from prediction because timing is uncertain. |

Across domains, the analysis states its denominator and grain, separates descriptive association from causality, and avoids predictive claims where a valid question or temporal basis is lacking. The dataset catalog, data dictionary, and methodology guide record source profiles, exclusions, definitions, and caveats.

## 6. Key findings

- **Sales:** Eligible gross line sales total GBP 20,972,595 across 40,077 invoices. Mean gross order value is GBP 523.31 (95% invoice bootstrap interval GBP 508.96–538.25). This is revenue before costs, not profit.
- **Healthcare:** Of 100,124 eligible encounters from 70,446 patients, 11.3% carry the source `<30` readmission label; median stay is four days. This is a historical descriptive result, not a clinical recommendation.
- **Sports:** The non-copy Elo archive contains 63,157 team-games from 1947–2015. On the final three seasons, published pregame forecast accuracy is 66.4%, with Brier score 0.2082.
- **Finance:** The full-coverage cohort contains 467 symbols over 1,762 dates. An illustrative equal-weight price-return index annualized at 14.4%, with 16.8% annualized volatility and −21.9% maximum drawdown; these historical figures are not a return forecast.
- **E-commerce:** 1,908 of 12,330 sessions converted (15.5%; 95% Wilson interval 14.8%–16.1%). Visitor type and purchase outcome are associated in this sample; this does not establish cause.

Detailed definitions, results, figures, recommendations, and limitations appear in each linked domain PDF and source narrative.

## 7. Setup and run instructions

Use Windows PowerShell from the repository root. Python 3.13.9 and the pinned requirements were verified for this project.

```powershell
cd "G:\Developers_Arena\Developers_Arena_Internship\Complete Data Analysis Portfolio"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name portfolio --display-name "Portfolio (.venv)"
```

Download the documented source snapshots before rebuilding the analyses:

```powershell
python scripts/download_sources.py --domain all
```

Rebuild derived analysis artifacts and launch the dashboard:

```powershell
python scripts/build_outputs.py --domain all
python scripts/merge_chart_inventory.py
python scripts/execute_notebooks.py
python scripts/render_reports.py
python scripts/validate_artifacts.py --all --submission
python -m streamlit run dashboard/app.py
```

Streamlit prints a local address (normally `http://localhost:8501`). Keep the terminal running while using the dashboard; press Ctrl+C there to stop it. Raw data are not included, so a fresh reproduction requires retrieval from the documented public sources.

## 8. User guide

1. Open the dashboard using the Streamlit command above.
2. Use the sidebar to select the portfolio overview or one of the five domain pages.
3. Review the source coverage, headline measures, charts, and interpretation limits shown on each page.
4. Adjust a domain's supported filters to narrow the displayed data. Use the page's reset control to restore defaults; empty filter results show a no-match message.
5. For full methods and static findings, open the matching analysis notebook and PDF report from the project index.
6. Stop the local server with Ctrl+C in its terminal.

## 9. Visual documentation

The following figures show the running dashboard on desktop and mobile. The desktop captures show the initial viewport with default filters at 1803 × 915 pixels. The mobile sports capture is 390 × 844 pixels with the sidebar collapsed; KPI cards stack vertically and the page has no horizontal overflow. Sidebar keyboard navigation was checked. Direct screen-reader assessment and exhaustive keyboard-only filter testing were not completed.

### Portfolio dashboard overview

![Portfolio overview showing the five completed analyses, six source snapshots, and 25 distinct charts](screenshots/dashboard-overview.png)

*Figure 1. Portfolio landing page with cross-domain indicators and navigation.*

### Business sales

![Business sales dashboard with headline measures and sales visualizations](screenshots/dashboard-sales.png)

*Figure 2. Sales analysis dashboard and supported filters.*

### Healthcare encounters

![Healthcare dashboard showing encounter outcomes and group comparisons](screenshots/dashboard-healthcare.png)

*Figure 3. Healthcare encounter dashboard. Results are descriptive and not clinical advice.*

### Sports analytics

![Sports dashboard showing historical NBA analytics](screenshots/dashboard-sports.png)

*Figure 4. Historical team and player analysis dashboard.*

### Financial risk

![Finance dashboard with historical returns and risk measures](screenshots/dashboard-finance.png)

*Figure 5. Historical price-return and risk dashboard. Results are illustrative, not investment advice.*

### E-commerce sessions

![E-commerce dashboard showing session conversion and engagement](screenshots/dashboard-ecommerce.png)

*Figure 6. E-commerce session conversion and engagement dashboard.*

### Mobile dashboard

![Sports dashboard at a mobile viewport showing stacked measures and charts](screenshots/dashboard-sports-mobile.png)

*Figure 7. Sports dashboard at 390 × 844 pixels. Content stacks without horizontal overflow.*

The project also contains 25 unique chart inventory entries across five domains. Each domain report includes charts and recommendations. The report PDFs, executive summary pages, and eight presentation slides were visually reviewed; no clipping or overlap was observed in the reviewed artifacts.

## 10. Testing and validation evidence

The recorded clean-environment reproduction used a newly created virtual environment with pinned requirements. `pip check` and `compileall -q src scripts dashboard` passed. All five domain builders completed from local raw snapshots; all six notebooks executed with the registered portfolio kernel; five reports, an executive summary, and an eight-slide deck were generated. `scripts/validate_artifacts.py --all --submission` reported **READY (0 missing paths)**, with valid metric and chart contracts.

Further recorded checks include 25 unique chart IDs with existing image files; five seven-page domain PDFs and a three-page executive summary with valid PDF signatures; successful Streamlit rendering of the overview and five domains; filter, reset, and no-match behavior; responsive widths of 390, 1024, and 1440 pixels; recovery messages for missing metrics and malformed JSON; and a local Markdown scan with zero broken links across 42 files. Findings and recommendation headlines were reconciled against metrics and report narratives.

No separate automated test suite was present. The validation record and acceptance checklist contain the detailed evidence. A Windows-specific Jupyter kernel-listing command raised WinError 623 in the clean environment, while the project's notebook runner successfully launched and ran all six notebooks. A direct screen-reader assessment was not performed.

## 11. API and deployment notes

There is no Django backend or REST API in scope. The application is a local Streamlit analytics dashboard with no user account, database, or network API. The dashboard can be run locally by following the setup instructions above. Cloud hosting and public deployment have not been completed or verified; this report does not claim production readiness.

## 12. Submission checklist mapping

| Submission criterion | Evidence in this project |
|---|---|
| Project overview and objectives | Project overview, objectives, and deliverables in this report |
| Setup instructions | Environment, data retrieval, build, and launch steps in this report |
| Organized code structure | Responsibility-based modules and domain analyses described in this report |
| Visual documentation | Seven embedded dashboard screenshots, 25 unique charts, five domain reports, and a presentation |
| Technical details and methods | Domain methods, assumptions, notebooks, and reusable Python components |
| Testing and validation evidence | Clean-environment reproduction, notebook execution, dashboard checks, and artifact validation |
| User guide | Dashboard navigation, filter behavior, and run/stop instructions |
| Architecture overview | Local data flow and separation between analysis, dashboard, and reporting |
| Deployment guide | Local run instructions included; no cloud deployment is claimed |
| API documentation | Not applicable: no Django or REST API is implemented |

## Related deliverables

The submission includes five analysis notebooks, five domain reports, five recommendation documents, a portfolio summary notebook, an executive summary, a slide presentation, the interactive dashboard, and supporting setup, methods, and validation guides.

**Conclusion:** The portfolio delivers five reproducible domain analyses, six executed notebooks, 25 unique visualizations, five PDF reports, an interactive local dashboard, documented setup and methods, and recorded validation evidence. Its conclusions are limited to the documented historical source snapshots.
