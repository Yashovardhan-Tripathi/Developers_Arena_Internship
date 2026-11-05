# Dataset handling

Raw source files belong in `datasets/raw/<domain>/`; processed files are generated separately in `datasets/processed/<domain>/`. Raw files are ignored by Git. Preserve downloaded originals and record the snapshot date, source version, file size, SHA-256, row count, and columns in the catalog/data dictionary before analysis.

## Selected sources and intended use

| Domain | Source | Intended question and unit | Important limits |
| --- | --- | --- | --- |
| Sales | [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) | Invoice line sales, product contribution, order/customer patterns | Historical UK gift retailer, Dec 2009–Dec 2011, GBP; cancellations, missing customer IDs, and wholesaler behavior require explicit treatment. Revenue is not profit. |
| Healthcare | [UCI Diabetes 130-US Hospitals](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) | De-identified encounter outcomes and utilization; one row per encounter | US hospitals, 1999–2008; repeated encounters per patient; no causal or clinical advice. Remove/avoid patient identifiers in outputs. |
| Sports | [FiveThirtyEight NBA Elo](https://github.com/fivethirtyeight/data/tree/master/nba-elo) plus [historical RAPTOR player ratings](https://github.com/fivethirtyeight/data/tree/master/nba-raptor) | Team-game outcomes/trends and player ratings by season | CC BY 4.0 per repository. Historical ratings change methodology by era; ratings are publisher-defined estimates, not direct measurements. Game and player ID source attribution includes Basketball-Reference. Source is no longer periodically updated. |
| Finance | [Kaggle NYSE historical prices](https://www.kaggle.com/dgawlik/nyse), retrieved from a [public file mirror](https://github.com/kyi3081/stock-analysis/blob/master/prices-split-adjusted.csv) | Daily split-adjusted prices, returns, volatility, drawdown and correlations for the 501-symbol source universe | Kaggle card states CC0; source spans mostly 2010–2016 and says prices are split-adjusted; dividend adjustment is not documented. The file mirror content is pinned by SHA-256. The source's constituent selection creates survivorship risk; disclose provider and historical-coverage limits. |
| E-commerce | [UCI Online Shoppers Purchasing Intention](https://archive.ics.uci.edu/dataset/468/online+shoppers+purchasing+intention+dataset) | Session engagement and conversion; one session per user in the supplied year | 12,330 sessions; cannot support customer lifetime value, repeat purchase, or basket analysis. Session-level variables such as PageValues may encode outcome-adjacent information and must be excluded from any prediction unless timing is proven. |

The sales and e-commerce projects intentionally answer different questions and use different datasets. Do not combine the sources or generalize these historical records to current businesses.

## Acquisition and reproducibility

Use each linked source page as the authoritative citation and download entry point. Record the retrieval date and exact file hash locally; do not commit raw data by default. UCI datasets are CC BY 4.0 and require attribution. FiveThirtyEight's repository states CC BY 4.0 unless otherwise noted. The Kaggle finance card states CC0; preserve that attribution/rights note alongside any snapshot. Check source terms again before redistributing raw files or derived artifacts.

The finance download uses the documented raw-file mirror of the Kaggle dataset and is about 50 MB. The dataset card is the rights/source citation; the mirror is only the retrieval route. This mirror relationship and its exact file hash must remain documented. The full source universe is small enough for local analysis; coverage and symbol eligibility are checked from the downloaded snapshot.

Dataset snapshot metadata is maintained in [`catalog.csv`](catalog.csv); field meanings, units, quality decisions, and analysis exclusions belong in `docs/data_dictionary.md`.
