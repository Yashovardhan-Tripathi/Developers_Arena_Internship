# Finance analysis — source narrative

## Executive summary

The source has 851,264 security-date records across 501 symbols; 467 symbols span all 1,762 dates. The illustrative equal-weight price-return index annualized at 14.4% with 16.8% annualized volatility and -21.9% maximum drawdown.

## Question and source

The unit is one security-date close. Data covers 2010-01-04 to 2016-12-30. Prices are split-adjusted; dividend adjustment is not documented. The complete-coverage cohort includes 467 symbols over 1,762 common source dates.

## Methods and assumptions

Daily close-to-close price returns are calculated per symbol after sorting by date. Annualized volatility uses sample daily standard deviation × sqrt(252); geometric annualized return uses the number of observed daily intervals. Drawdown is computed from cumulative price-return growth. The illustrative cohort is daily rebalanced and equally weighted among complete-coverage symbols, with no transaction costs, taxes, or cash drag. A bootstrap interval across symbols describes cross-sectional dispersion and is not a future-return forecast.

## Recommendation

Treat the portfolio curve as a historical risk illustration, not an investable backtest. Before any portfolio decision, rebuild with point-in-time constituents, dividend-adjusted total returns, explicit rebalancing/transaction-cost rules, and out-of-sample periods.

## Limitations

- Prices are split-adjusted; dividend adjustment is not documented, so results are price-return based rather than total returns.
- The source constituents create survivorship/selection risk; the complete 467-symbol cohort is not a point-in-time investable universe.
- The source is a public mirror snapshot and its original version/commit is unavailable; the downloaded file is pinned by SHA-256.
- The equal-weight portfolio is an analytical illustration, not an investment recommendation; daily rebalancing, transaction costs, taxes, liquidity, and delistings are not modeled.
- Annualization uses 252 trading days and historical observations do not establish future return or risk.

## Figures

See `visualizations/finance/` and `visualizations/finance/manifest.csv`.
