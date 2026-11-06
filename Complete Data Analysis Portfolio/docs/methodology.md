# Portfolio methodology

This note summarizes analytical units, decisions, and limitations across the five projects. Detailed calculations, source coverage, and chart descriptions are recorded in each notebook, the `reports/source/` narratives, metric JSON files, and chart manifests.

| Domain | Analysis unit and outcome | Statistical or predictive method | Boundary of interpretation |
| --- | --- | --- | --- |
| Business sales | Invoice line; gross positive quantity × price, aggregated to invoice, product, country, and identified customer | Descriptive aggregation; invoice-level percentile bootstrap for mean gross order value | GBP sales are not profit. Invoice resampling interval assumes invoices are independent. Customer results omit unidentified IDs. |
| Healthcare | Eligible hospital encounter, with repeated encounters grouped by patient; source `<30` readmission label | Patient-cluster percentile bootstrap for the overall 30-day rate; descriptive comparisons by encounter groups | Observational 1999–2008 hospital data; associations are not causal or clinical guidance. Encounters with disposition 11 are excluded. |
| Sports | One non-copy NBA team perspective per game; separate player-season RAPTOR records | Evaluate the source Elo pregame probabilities on a chronological final-three-season holdout using accuracy and Brier score; descriptive RAPTOR summaries | Published historical forecast is assessed, not a new model. Elo ends 2015; RAPTOR ends 2022 and methods vary across eras. |
| Finance | Security-date observations and daily returns for the complete-coverage cohort | Descriptive return, annualized volatility, drawdown, and equally weighted daily rebalanced cohort summary | Split-adjusted prices; dividend policy is undocumented. Annualization uses 252 trading days. Survivorship and source-mirror limitations apply; results are illustrative historical calculations, not advice. |
| E-commerce | One session; `Revenue` is the purchase-session outcome | Wilson interval for overall conversion; chi-square association test for visitor type; descriptive group rates | One-year historical session sample, not repeat purchasers or baskets. Association does not imply causation. `PageValues` is excluded from prediction because temporal availability is uncertain. |

## Shared controls

- Preserve source files and transform into derived tables; retain source lineage and snapshot metadata in the catalog.
- State denominators, grain, date coverage, currency, and exclusions alongside reported metrics.
- Use chronological evaluation for the sports holdout. No additional predictive model is claimed where the available question, coverage, or temporal fields do not justify one.
- Export chart manifests with purpose, source table, coverage, units, and accessibility description. The five domain manifests feed `visualizations/inventory.csv`.
- Do not interpret observational group differences as intervention effects. Recommendations are validation or operational review steps bounded by the source data.

For exact metric IDs, values, uncertainty intervals, and chart mappings, use `outputs/<domain>/metrics.json`, the corresponding `visualizations/<domain>/manifest.csv`, and `reports/source/<domain>.md`.
