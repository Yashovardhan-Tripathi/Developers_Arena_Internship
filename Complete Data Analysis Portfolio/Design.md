# UI/UX and Presentation Design

Status: Proposed experience specification; no UI has been implemented.
Last updated: 2026-10-31

## 1. Experience goals

Make five domain analyses easy to explore and evaluate. A reader should quickly understand the question, data coverage, main findings, supporting charts, recommendations, and limitations. Use a consistent visual identity while respecting domain-specific metrics and units.

The planned UI is a local Streamlit dashboard with Plotly charts. Final tool selection remains provisional. Reports, notebooks, slides, and README navigation share the same naming and formatting conventions.

## 2. Information architecture

Primary navigation:

1. Portfolio overview.
2. Business sales.
3. Healthcare.
4. Sports.
5. Finance.
6. E-commerce.

Each domain view includes an inline methodology/source area and links to its notebook, report, and recommendations when those artifacts exist. The README provides equivalent navigation for readers who do not run the dashboard.

## 3. Portfolio overview layout

```text
Portfolio title and concise purpose
Data coverage note and navigation
--------------------------------------------------
Project count | Dataset count | Chart count
--------------------------------------------------
Five project cards
  Domain, question, coverage, verified finding, Open
--------------------------------------------------
Methods and tools summary
Deliverable links and portfolio limitations
```

Counts must come from actual completed artifacts. Do not combine unrelated domain currencies or rates into a misleading overall KPI. Before results exist, show explanatory placeholders only in design drafts, never as measured results in a delivered UI.

## 4. Domain view layout

```text
Domain title
Question, source, coverage, and refresh/snapshot date
--------------------------------------------------
Filters and Reset filters
Active filter summary
--------------------------------------------------
Three or four relevant KPI cards
--------------------------------------------------
Primary trend or comparison chart
Secondary charts with short interpretations
--------------------------------------------------
Findings and recommended actions
Methods, definitions, limitations, and downloads
```

Show the central question and coverage before charts. Keep filter labels close to controls. Present technical details in expandable sections while keeping limitations that change interpretation visible.

## 5. Domain content specification

All metrics and filters below are candidates; display them only if supported by selected data and validated definitions.

| View | Candidate KPIs | Candidate filters | Chart emphasis |
| --- | --- | --- | --- |
| Sales | Revenue, orders, average order value, active customers | Date, category, product, region | Trends, contribution, customer distribution |
| Healthcare | Encounters, outcome rate, median stay, median cost | Period, department, age group | Distributions and group comparisons with sample sizes |
| Sports | Matches, win rate, player contribution, performance rate | Season, team, player, competition | Rankings, normalized comparisons, match trends |
| Finance | Period return, volatility, maximum drawdown, portfolio value | Period, asset, portfolio selection if supported | Indexed prices, returns, drawdowns, correlation |
| E-commerce | Customers, repeat purchase rate, order value, segment size | Period, customer segment, product category | Segments, purchase behavior, product relationships |

Display prediction or segmentation sections only where implemented and evaluated. Show the baseline, evaluation period, metric, and limitations alongside predictive results.

## 6. Visual system

| Element | Specification |
| --- | --- |
| Canvas | Light background `#F8FAFC`; white content surfaces |
| Main text | Dark slate `#0F172A` |
| Secondary text | Slate `#475569` |
| Primary action | Blue `#1D4ED8`, with white text where contrast is verified |
| Borders | `#CBD5E1`; use spacing and headings as the main grouping tools |
| Positive/status accent | Dark green `#166534`, accompanied by a label/icon |
| Caution accent | Dark amber `#92400E`, accompanied by explanatory text |
| Error accent | Dark red `#B91C1C`, accompanied by recovery guidance |
| Typography | System sans-serif; approximately 16 px body, 24 px section headings, 32 px page title |
| Spacing | Multiples of 8 px; approximately 16–24 px between related blocks and 32 px between sections |
| Cards | Simple border, 8 px radius, restrained or absent shadow |
| Content width | Comfortable reading width; full-width charts where labels require space |

Use domain accents consistently: sales blue, healthcare teal, sports purple, finance orange, and e-commerce magenta. Final chart colors must be checked for contrast and color-vision accessibility. Do not use color alone to communicate categories, trends, or status.

## 7. Chart and table standards

- Titles state the analytical question or measured result; subtitles state scope and units.
- Label axes, currencies, percentages, date intervals, and denominators where relevant.
- Bar charts normally begin at zero; disclose and justify truncated axes on other charts.
- Sort categories meaningfully, keep time chronological, and avoid 3D decoration.
- Use line charts for trends, bars for comparisons, histograms/box plots for distributions, scatter plots for relationships, and heatmaps for appropriate matrices.
- Do not force 25 different chart types. Count distinct, useful analytical views; re-exporting a chart does not add to the inventory.
- Include sample sizes and uncertainty where needed for interpretation.
- Format currency with its actual code or symbol; use consistent separators and meaningful precision.
- Tooltips show readable labels, exact values, units, and relevant context.
- Give every important chart a short textual takeaway and an accessible table or equivalent summary.
- Large tables use sorting, readable columns, sensible row limits, and downloadable filtered data when redistribution permits.

## 8. Interaction behavior

- Apply supported filters consistently to related charts and KPIs; visibly identify fixed reference metrics.
- Initialize date ranges from actual data coverage and show selected scope.
- Reset restores the page defaults. Avoid hidden filters persisting between unrelated domains.
- Offer downloads only for generated files or permitted data; label format and content clearly.
- Cache appropriate loading and derived work. Do not fit models during filter changes.
- Preserve useful page context while rendering updated results.

## 9. Required states

| State | User experience |
| --- | --- |
| Loading | A short progress indicator and description of the operation |
| No matching records | Explain that current filters return no data; offer reset |
| Missing generated input | Explain which preparation step is needed and link to setup guidance |
| Invalid input or schema | Show a concise recoverable message; keep diagnostics in development logs |
| Metric unavailable | Display “Not available” and reason; do not substitute zero |
| Limited coverage | Show a visible note near affected charts and findings |
| Model not applicable | Explain the suitability decision in the methods area |

## 10. Responsive behavior and accessibility

- Wide screens: sidebar navigation, up to four KPI cards, and two-column charts when readable.
- Tablet widths: reduce card and chart columns according to available space.
- Narrow screens: stack cards/charts and allow framework-supported collapsed navigation; avoid clipped labels and unnecessary horizontal scrolling.
- Validate representative widths near 1440 px, 1024 px, and 390 px during implementation.
- Support keyboard navigation, visible focus, descriptive control labels, and meaningful link text.
- Target WCAG AA contrast, including 4.5:1 for normal text; verify actual rendered colors.
- Do not rely exclusively on hover, animation, or color to convey findings.

## 11. Reports, notebooks, and slides

Reports: consistent title page, executive summary, question and source, methodology, findings, charts, recommendations, limitations, and references. Use readable print sizing and inspect page breaks, clipped charts, legends, and tables in the rendered PDF.

Notebooks: use a predictable narrative and concise markdown explanations before major analysis sections. Keep outputs relevant and figures readable without running the dashboard.

Slides: open with the portfolio purpose, cover each domain's question and strongest supported finding, show selected readable charts, and close with methods, recommendations, and limitations. Include source notes and avoid dense code screenshots.

Screenshots: capture actual completed views with descriptive filenames; do not use mockups as proof of implemented functionality.

## 12. Design acceptance




Verify navigation, filter consistency, reset behavior, keyboard access, chart readability, empty/error states, data context, valid downloads, responsive layouts, and agreement with reports. Record tested behavior and any framework limitations in `docs/validation.md`.
