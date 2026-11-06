"""Sales analysis for the UCI Online Retail II source."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.domains.common import (
    PALETTE, add_metric, apply_style, chart, finish_domain, save_chart,
    write_processed_table, write_table,
)
from src.paths import PROJECT_ROOT
from src.statistics import bootstrap_mean_interval


DOMAIN = "sales"
DATASET_IDS = ["sales_online_retail_ii"]
SOURCE = "datasets/raw/sales/online_retail_II.xlsx"
LIMITATIONS = [
    "Sales are gross positive line extensions in GBP, not profit; freight, operating costs, and taxes are unavailable.",
    "Cancelled invoices and non-positive quantity/price rows are excluded from the primary sales analysis.",
    "Customer IDs are missing for a substantial share of source rows; customer-level results use identified customers only.",
    "The source is a historical UK retailer sample ending in December 2011 and is not representative of current retail markets.",
]


def _load_all_sheets() -> pd.DataFrame:
    path = PROJECT_ROOT / SOURCE
    sheets = pd.read_excel(path, sheet_name=None)
    return pd.concat(sheets.values(), ignore_index=True)


def build() -> dict[str, object]:
    apply_style()
    raw = _load_all_sheets()
    raw.columns = [str(column).strip() for column in raw.columns]
    data = raw.rename(columns={"Customer ID": "customer_id"}).copy()
    data["Invoice"] = data["Invoice"].astype("string").str.strip()
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Quantity"] = pd.to_numeric(data["Quantity"], errors="coerce")
    data["Price"] = pd.to_numeric(data["Price"], errors="coerce")
    data["gross_line_sales_gbp"] = data["Quantity"] * data["Price"]
    cancelled = data["Invoice"].str.upper().str.startswith("C", na=False)
    valid_date = data["InvoiceDate"].notna()
    positive = data["Quantity"].gt(0) & data["Price"].gt(0)
    analysis = data.loc[valid_date & positive & ~cancelled].copy()
    analysis["month"] = analysis["InvoiceDate"].dt.to_period("M").dt.to_timestamp()
    analysis["year"] = analysis["InvoiceDate"].dt.year
    analysis["customer_id"] = pd.to_numeric(analysis["customer_id"], errors="coerce")
    analysis["line_sales_gbp"] = analysis["Quantity"] * analysis["Price"]
    order = analysis.groupby("Invoice", as_index=False).agg(
        order_value_gbp=("line_sales_gbp", "sum"),
        order_date=("InvoiceDate", "min"),
        customer_id=("customer_id", "first"),
        line_count=("StockCode", "size"),
    )
    monthly = analysis.groupby("month", as_index=False).agg(
        sales_gbp=("line_sales_gbp", "sum"), orders=("Invoice", "nunique"), lines=("Invoice", "size")
    )
    products = analysis.groupby(["StockCode", "Description"], dropna=False, as_index=False).agg(
        sales_gbp=("line_sales_gbp", "sum"), units=("Quantity", "sum"), orders=("Invoice", "nunique")
    ).sort_values("sales_gbp", ascending=False).head(12)
    countries = analysis.groupby("Country", as_index=False).agg(
        sales_gbp=("line_sales_gbp", "sum"), orders=("Invoice", "nunique")
    ).sort_values("sales_gbp", ascending=False).head(12)
    customer_sales = analysis.dropna(subset=["customer_id"]).groupby("customer_id", as_index=False).agg(
        sales_gbp=("line_sales_gbp", "sum"), orders=("Invoice", "nunique"),
        last_purchase=("InvoiceDate", "max"), units=("Quantity", "sum"),
    ).sort_values("sales_gbp", ascending=False)
    identified_share = float(analysis["customer_id"].notna().mean())
    total_sales = float(analysis["line_sales_gbp"].sum())
    avg_order = float(order["order_value_gbp"].mean())
    ci = bootstrap_mean_interval(order["order_value_gbp"], resamples=1000, seed=42)
    top_product = str(products.iloc[0]["Description"] or products.iloc[0]["StockCode"])
    top_product_share = float(products.iloc[0]["sales_gbp"] / total_sales)
    top_country = str(countries.iloc[0]["Country"])
    time_min, time_max = analysis["InvoiceDate"].min(), analysis["InvoiceDate"].max()

    write_processed_table(analysis.drop(columns=["customer_id"]), DOMAIN, "sales_lines.csv")
    write_table(monthly, DOMAIN, "monthly_sales.csv")
    write_table(order, DOMAIN, "orders.csv")
    write_table(products, DOMAIN, "top_products.csv")
    write_table(countries, DOMAIN, "top_countries.csv")
    write_table(customer_sales.head(100), DOMAIN, "top_customers.csv")

    rows = []
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.plot(monthly["month"], monthly["sales_gbp"], marker="o", ms=3, lw=1.8, color=PALETTE[0])
    ax.set(title="Monthly gross sales from completed positive lines", xlabel="Invoice month", ylabel="Gross sales (GBP)")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")); fig.autofmt_xdate()
    save_chart(DOMAIN, fig, "monthly_sales.png")
    rows.append(chart(DOMAIN,"sales_monthly_gross","Monthly gross sales","How did gross sales vary by invoice month?","Shows observed monthly seasonality and coverage gaps.","line","outputs/sales/tables/monthly_sales.csv","monthly_sales.png",f"{time_min:%Y-%m} to {time_max:%Y-%m}","GBP","Monthly gross sales line with labeled invoice-month axis."))

    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_products = products.sort_values("sales_gbp")
    ax.barh(plot_products["Description"].fillna(plot_products["StockCode"]).astype(str).str.slice(0, 45), plot_products["sales_gbp"], color=PALETTE[1])
    ax.set(title="Top products by gross sales", xlabel="Gross sales (GBP)", ylabel="Product description")
    save_chart(DOMAIN, fig, "top_products.png")
    rows.append(chart(DOMAIN,"sales_top_products","Top products by gross sales","Which listed products contribute most gross sales?","Ranks the twelve highest gross-sales product descriptions.","horizontal_bar","outputs/sales/tables/top_products.csv","top_products.png",f"{time_min:%Y-%m} to {time_max:%Y-%m}","GBP","Horizontal bars rank products; labels are shortened to 45 characters."))

    fig, ax = plt.subplots(figsize=(10, 5.5))
    plot_countries = countries.sort_values("sales_gbp")
    ax.barh(plot_countries["Country"], plot_countries["sales_gbp"], color=PALETTE[2])
    ax.set(title="Top countries by gross sales", xlabel="Gross sales (GBP)", ylabel="Country")
    save_chart(DOMAIN, fig, "country_sales.png")
    rows.append(chart(DOMAIN,"sales_country_contribution","Country contribution","Which countries account for the largest gross sales totals?","Compares the twelve highest-volume country aggregates.","horizontal_bar","outputs/sales/tables/top_countries.csv","country_sales.png",f"{time_min:%Y-%m} to {time_max:%Y-%m}","GBP","Horizontal bars compare country gross sales."))

    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.hist(order["order_value_gbp"].clip(upper=order["order_value_gbp"].quantile(.99)), bins=45, color=PALETTE[0], alpha=.9)
    ax.set(title="Order value distribution (display capped at the 99th percentile)", xlabel="Gross order value (GBP)", ylabel="Orders")
    save_chart(DOMAIN, fig, "order_value_distribution.png")
    rows.append(chart(DOMAIN,"sales_order_value_distribution","Order value distribution","How are gross invoice values distributed?","Displays the central 99% range to make the skew readable; summary statistics use all orders.","histogram","outputs/sales/tables/orders.csv","order_value_distribution.png",f"{time_min:%Y-%m} to {time_max:%Y-%m}","GBP per invoice","Histogram uses a visible 99th-percentile display cap; reported mean includes all orders."))

    fig, ax = plt.subplots(figsize=(9, 5.2))
    cust_plot = customer_sales.head(20).sort_values("sales_gbp")
    ax.barh(cust_plot["customer_id"].astype("int64").astype(str), cust_plot["sales_gbp"], color=PALETTE[3])
    ax.set(title="Top identified customers by gross sales", xlabel="Gross sales (GBP)", ylabel="Customer ID")
    save_chart(DOMAIN, fig, "top_customers.png")
    rows.append(chart(DOMAIN,"sales_top_customers","Top identified customers","Which identified customers contribute the most gross sales?","Ranks customers only among lines carrying a non-missing customer ID.","horizontal_bar","outputs/sales/tables/top_customers.csv","top_customers.png",f"{time_min:%Y-%m} to {time_max:%Y-%m}","GBP","Horizontal bars rank the top 20 identified customer IDs."))

    metrics = [
        add_metric("gross_line_sales_gbp", round(total_sales,2), "GBP", "Sum of positive quantity multiplied by positive unit price on non-cancelled invoice lines.", "Eligible invoice lines"),
        add_metric("completed_orders", int(order["Invoice"].nunique()), "invoices", "Unique invoices remaining after cancellation, quantity, price, and date exclusions."),
        add_metric("mean_gross_order_value_gbp", round(avg_order,2), "GBP per invoice", f"Arithmetic mean of {len(order):,} eligible invoice totals.", "Eligible invoices"),
        add_metric("mean_order_value_ci95_lower_gbp", round(ci[0],2), "GBP per invoice", "Lower percentile-bootstrap bound for mean gross invoice value; 1,000 resamples, seed 42.", "Eligible invoices"),
        add_metric("mean_order_value_ci95_upper_gbp", round(ci[1],2), "GBP per invoice", "Upper percentile-bootstrap bound for mean gross invoice value; 1,000 resamples, seed 42.", "Eligible invoices"),
        add_metric("identified_customer_line_share", round(identified_share,4), "proportion", "Share of eligible lines with an available customer ID.", "Eligible invoice lines"),
        add_metric("top_product_gross_sales_share", round(top_product_share,4), "proportion", f"Gross sales share of the leading product ({top_product}).", "Eligible gross line sales"),
    ]
    summary = {
        "question": "How do sales vary over time, and which products, countries, orders, and identified customers contribute most?",
        "headline": f"Eligible gross line sales total GBP {total_sales:,.0f} across {len(order):,} invoices; the leading product contributes {top_product_share:.1%} of this total.",
        "statistical_note": f"Mean gross order value is GBP {avg_order:,.2f} (95% percentile-bootstrap interval GBP {ci[0]:,.2f}–{ci[1]:,.2f}; invoice-level resampling assumes independent invoices).",
        "recommendation": f"Review availability and stock planning for the leading product and largest customer accounts; validate margin and cancellation data before making profitability decisions.",
        "limitations": LIMITATIONS,
    }
    (PROJECT_ROOT / "reports/source").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "reports/source/sales.md").write_text(_report(summary, time_min, time_max, len(raw), len(analysis)), encoding="utf-8")
    (PROJECT_ROOT / "recommendations").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "recommendations/sales.md").write_text(f"# Sales recommendations\n\n## Finding\n\n{summary['headline']}\n\n## Action\n\n{summary['recommendation']}\n\n## Limitation\n\nRevenue is not profit, and customer IDs are missing on many lines.\n\n## Monitor\n\nMonthly gross sales, order count, cancellation/return share, and gross margin once cost data is available.\n", encoding="utf-8")
    result = finish_domain(DOMAIN, DATASET_IDS, {"start": time_min.date().isoformat(), "end": time_max.date().isoformat(), "unit_of_analysis": "invoice line"}, metrics, LIMITATIONS, rows)
    result.update({"headline": summary["headline"], "statistical_note": summary["statistical_note"], "recommendation": summary["recommendation"]})
    return result


def _report(summary: dict[str, object], start: pd.Timestamp, end: pd.Timestamp, raw_n: int, clean_n: int) -> str:
    return f"""# Sales analysis — source narrative

## Executive summary

{summary['headline']}

## Question and source

{summary['question']} The source is UCI Online Retail II, one row per invoice line, from {start:%Y-%m-%d} to {end:%Y-%m-%d}. Currency is GBP.

## Method

The source contains {raw_n:,} rows across its workbook sheets. After excluding canceled invoices, invalid dates, and non-positive quantity/price rows, {clean_n:,} invoice lines remain. Gross line sales equal quantity × unit price. Totals are not profit. Identified-customer analyses exclude missing IDs.

## Statistical summary

{summary['statistical_note']} The interval resamples invoices, not individual lines. Its interpretation is descriptive for this retailer snapshot.

## Findings and action

{summary['recommendation']}

## Limitations

""" + "\n".join(f"- {item}" for item in summary["limitations"]) + "\n\n## Figures\n\nSee `visualizations/sales/` and `visualizations/sales/manifest.csv`.\n"
