# Sales analysis — source narrative

## Executive summary

Eligible gross line sales total GBP 20,972,595 across 40,077 invoices; the leading product contributes 1.6% of this total.

## Question and source

How do sales vary over time, and which products, countries, orders, and identified customers contribute most? The source is UCI Online Retail II, one row per invoice line, from 2009-12-01 to 2011-12-09. Currency is GBP.

## Method

The source contains 1,067,371 rows across its workbook sheets. After excluding canceled invoices, invalid dates, and non-positive quantity/price rows, 1,041,670 invoice lines remain. Gross line sales equal quantity × unit price. Totals are not profit. Identified-customer analyses exclude missing IDs.

## Statistical summary

Mean gross order value is GBP 523.31 (95% percentile-bootstrap interval GBP 508.96–538.25; invoice-level resampling assumes independent invoices). The interval resamples invoices, not individual lines. Its interpretation is descriptive for this retailer snapshot.

## Findings and action

Review availability and stock planning for the leading product and largest customer accounts; validate margin and cancellation data before making profitability decisions.

## Limitations

- Sales are gross positive line extensions in GBP, not profit; freight, operating costs, and taxes are unavailable.
- Cancelled invoices and non-positive quantity/price rows are excluded from the primary sales analysis.
- Customer IDs are missing for a substantial share of source rows; customer-level results use identified customers only.
- The source is a historical UK retailer sample ending in December 2011 and is not representative of current retail markets.

## Figures

See `visualizations/sales/` and `visualizations/sales/manifest.csv`.
