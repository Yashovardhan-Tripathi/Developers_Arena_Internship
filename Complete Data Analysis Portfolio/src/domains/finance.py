"""Historical return and risk analysis for the split-adjusted NYSE snapshot."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.data_io import load_raw
from src.domains.common import PALETTE, add_metric, apply_style, chart, finish_domain, save_chart, write_processed_table, write_table
from src.statistics import bootstrap_mean_interval


DOMAIN="finance"
DATASET_IDS=["finance_us_equities"]
LIMITATIONS=[
    "Prices are split-adjusted; dividend adjustment is not documented, so results are price-return based rather than total returns.",
    "The source constituents create survivorship/selection risk; the complete 467-symbol cohort is not a point-in-time investable universe.",
    "The source is a public mirror snapshot and its original version/commit is unavailable; the downloaded file is pinned by SHA-256.",
    "The equal-weight portfolio is an analytical illustration, not an investment recommendation; daily rebalancing, transaction costs, taxes, liquidity, and delistings are not modeled.",
    "Annualization uses 252 trading days and historical observations do not establish future return or risk.",
]


def build()->dict[str,object]:
    apply_style()
    data=load_raw(DOMAIN,"prices-split-adjusted.csv",parse_dates=["date"])
    for col in ["open","close","low","high","volume"]: data[col]=pd.to_numeric(data[col],errors="coerce")
    data=data.dropna(subset=["date","symbol","close"]).sort_values(["symbol","date"])
    duplicate_count=int(data.duplicated(["symbol","date"]).sum())
    data=data.drop_duplicates(["symbol","date"],keep="last")
    data["daily_return"]=data.groupby("symbol",sort=False)["close"].pct_change()
    coverage=data.groupby("symbol")["date"].nunique()
    all_dates=pd.Index(sorted(data["date"].unique()))
    complete_symbols=coverage.loc[coverage.eq(len(all_dates))].index.tolist()
    matrix=data.loc[data["symbol"].isin(complete_symbols)].pivot(index="date",columns="symbol",values="daily_return").sort_index().dropna(how="any")
    prices=data.loc[data["symbol"].isin(complete_symbols)].pivot(index="date",columns="symbol",values="close").sort_index()
    returns=matrix.dropna(how="any")
    periods=len(returns)
    ann_return=(prices.iloc[-1]/prices.iloc[0])**(252/(len(prices)-1))-1
    ann_vol=returns.std(ddof=1)*np.sqrt(252)
    max_drawdown=(prices/prices.cummax()-1).min()
    summary=pd.DataFrame({"symbol":ann_return.index,"annualized_price_return":ann_return.values,"annualized_volatility":ann_vol.reindex(ann_return.index).values,"maximum_drawdown":max_drawdown.reindex(ann_return.index).values,"observations":len(prices)})
    summary=summary.replace([np.inf,-np.inf],np.nan).dropna().sort_values("annualized_price_return",ascending=False)
    portfolio_daily=returns.mean(axis=1)
    portfolio_value=(1+portfolio_daily).cumprod()
    portfolio_dd=portfolio_value/portfolio_value.cummax()-1
    portfolio_ann_return=float(portfolio_value.iloc[-1]**(252/len(portfolio_daily))-1)
    portfolio_ann_vol=float(portfolio_daily.std(ddof=1)*np.sqrt(252))
    portfolio_maxdd=float(portfolio_dd.min())
    avg_ci=bootstrap_mean_interval(summary["annualized_price_return"],resamples=1000,seed=42)
    representative=complete_symbols[::max(1,len(complete_symbols)//12)][:12]
    price_index=prices[representative]/prices[representative].iloc[0]*100
    corr=returns[representative].corr()
    selected_summary=summary.loc[summary["symbol"].isin(representative)]
    start=prices.index.min();end=prices.index.max()

    write_processed_table(data[["date","symbol","open","close","low","high","volume","daily_return"]],DOMAIN,"daily_prices_and_returns.csv")
    write_table(summary,DOMAIN,"security_risk_summary.csv")
    write_table(portfolio_value.rename("growth_of_1").rename_axis("date").reset_index(),DOMAIN,"equal_weight_growth.csv")
    write_table(selected_summary,DOMAIN,"representative_security_summary.csv")
    write_table(corr.rename_axis("symbol").reset_index(),DOMAIN,"representative_return_correlations.csv")
    rows=[]
    fig,ax=plt.subplots(figsize=(9.5,5));ax.plot(portfolio_value.index,portfolio_value,color=PALETTE[0],lw=1.8);ax.set(title="Illustrative equal-weight growth of 1",xlabel="Trading date",ylabel="Growth of 1 (price returns)")
    save_chart(DOMAIN,fig,"equal_weight_growth.png");rows.append(chart(DOMAIN,"finance_equal_weight_growth","Equal-weight historical growth","How did an illustrative equal-weight portfolio of complete-coverage symbols evolve?","A daily rebalanced equal-weight illustration over the shared complete-coverage window.","line","outputs/finance/tables/equal_weight_growth.csv","equal_weight_growth.png",f"{start:%Y-%m-%d} to {end:%Y-%m-%d}","growth of 1, split-adjusted price returns","Line shows the illustrative index; it excludes dividends, transaction costs, taxes, and survivorship corrections."))

    fig,ax=plt.subplots(figsize=(9,5.2));ax.scatter(summary["annualized_volatility"]*100,summary["annualized_price_return"]*100,s=20,alpha=.55,color=PALETTE[1],edgecolors="none");ax.axhline(0,color="#94A3B8",lw=1);ax.set(title="Historical annualized return and volatility by symbol",xlabel="Annualized daily volatility (%)",ylabel="Annualized price return (%)")
    save_chart(DOMAIN,fig,"risk_return_scatter.png");rows.append(chart(DOMAIN,"finance_risk_return_scatter","Risk and return dispersion","How did historical annualized price returns vary with volatility across symbols?","Displays the 467-symbol complete-coverage cohort; no risk-adjusted ranking is implied.","scatter","outputs/finance/tables/security_risk_summary.csv","risk_return_scatter.png",f"{start:%Y-%m-%d} to {end:%Y-%m-%d}","annualized percent","Each point is one complete-coverage symbol; axes are annualized using 252 trading days."))

    fig,ax=plt.subplots(figsize=(9.5,5.3));ax.plot(portfolio_dd.index,portfolio_dd*100,color=PALETTE[4]);ax.axhline(0,color="#64748B",lw=1);ax.set(title="Illustrative equal-weight drawdown",xlabel="Trading date",ylabel="Drawdown from prior peak (%)")
    save_chart(DOMAIN,fig,"equal_weight_drawdown.png");rows.append(chart(DOMAIN,"finance_equal_weight_drawdown","Historical drawdown","What was the decline from prior peaks in the illustrative price-return index?","Tracks peak-to-trough drawdown in the equal-weight illustration.","area","outputs/finance/tables/equal_weight_growth.csv","equal_weight_drawdown.png",f"{start:%Y-%m-%d} to {end:%Y-%m-%d}","percent from prior peak","Drawdown remains at or below zero and excludes dividends and costs."))

    fig,ax=plt.subplots(figsize=(10,5.5));price_index.plot(ax=ax,lw=1.35);ax.set(title="Indexed prices for a systematic sample of symbols",xlabel="Trading date",ylabel="Split-adjusted close index (first date = 100)");ax.legend(title="Symbol",ncol=2,fontsize=8)
    save_chart(DOMAIN,fig,"sample_price_indices.png");rows.append(chart(DOMAIN,"finance_sample_price_indices","Selected indexed prices","How did indexed prices evolve for systematically sampled symbols?","Shows twelve symbols sampled at regular positions in alphabetical order, not selected by performance.","multi_line","datasets/raw/finance/prices-split-adjusted.csv","sample_price_indices.png",f"{start:%Y-%m-%d} to {end:%Y-%m-%d}","indexed close, base 100","Each line starts at 100; symbols are sampled systematically from the full alphabetized cohort."))

    fig,ax=plt.subplots(figsize=(8.5,7));sns.heatmap(corr,ax=ax,cmap="vlag",center=0,vmin=-1,vmax=1,square=True,cbar_kws={"label":"Daily return correlation"});ax.set(title="Daily return correlation for representative symbols",xlabel="Symbol",ylabel="Symbol")
    save_chart(DOMAIN,fig,"sample_correlation.png");rows.append(chart(DOMAIN,"finance_sample_correlation","Selected-symbol return correlation","How strongly did daily returns co-move for the representative symbol sample?","Displays pairwise daily return correlation for the same systematic twelve-symbol sample.","heatmap","outputs/finance/tables/representative_return_correlations.csv","sample_correlation.png",f"{start:%Y-%m-%d} to {end:%Y-%m-%d}","correlation coefficient","Heatmap uses a fixed -1 to 1 scale and a diverging color map."))

    metrics=[
        add_metric("complete_coverage_symbols",len(complete_symbols),"symbols","Symbols with one record on every date in the source-wide date set."),
        add_metric("source_dates",len(all_dates),"trading dates","Distinct dates in the source snapshot."),
        add_metric("equal_weight_annualized_price_return",round(portfolio_ann_return,4),"annualized proportion","Geometric annualized return of the daily rebalanced equal-weight complete-coverage cohort; price returns only.","467 complete-coverage symbols"),
        add_metric("equal_weight_annualized_volatility",round(portfolio_ann_vol,4),"annualized proportion","Sample standard deviation of daily equal-weight returns multiplied by sqrt(252).","Daily equal-weight price returns"),
        add_metric("equal_weight_max_drawdown",round(portfolio_maxdd,4),"proportion from peak","Minimum value of cumulative growth divided by its running maximum minus one.","Daily equal-weight price-return series"),
        add_metric("cross_symbol_mean_annualized_return",round(float(summary["annualized_price_return"].mean()),4),"annualized proportion","Arithmetic mean of symbol-level annualized split-adjusted price returns across complete coverage symbols.","467 complete-coverage symbols"),
        add_metric("cross_symbol_mean_return_ci95_lower",round(avg_ci[0],4),"annualized proportion","Lower bootstrap bound for the cross-symbol mean annualized price return; 1,000 symbol resamples, seed 42.","Complete-coverage symbol cohort"),
        add_metric("cross_symbol_mean_return_ci95_upper",round(avg_ci[1],4),"annualized proportion","Upper bootstrap bound for the cross-symbol mean annualized price return; 1,000 symbol resamples, seed 42.","Complete-coverage symbol cohort"),
        add_metric("duplicate_symbol_date_rows_removed",duplicate_count,"rows","Duplicate symbol-date records dropped, retaining the last occurrence."),
    ]
    headline=f"The source has {len(data):,} security-date records across {len(coverage):,} symbols; {len(complete_symbols)} symbols span all {len(all_dates):,} dates. The illustrative equal-weight price-return index annualized at {portfolio_ann_return:.1%} with {portfolio_ann_vol:.1%} annualized volatility and {portfolio_maxdd:.1%} maximum drawdown."
    recommendation="Treat the portfolio curve as a historical risk illustration, not an investable backtest. Before any portfolio decision, rebuild with point-in-time constituents, dividend-adjusted total returns, explicit rebalancing/transaction-cost rules, and out-of-sample periods."
    report=f"""# Finance analysis — source narrative

## Executive summary

{headline}

## Question and source

The unit is one security-date close. Data covers {start:%Y-%m-%d} to {end:%Y-%m-%d}. Prices are split-adjusted; dividend adjustment is not documented. The complete-coverage cohort includes 467 symbols over {len(all_dates):,} common source dates.

## Methods and assumptions

Daily close-to-close price returns are calculated per symbol after sorting by date. Annualized volatility uses sample daily standard deviation × sqrt(252); geometric annualized return uses the number of observed daily intervals. Drawdown is computed from cumulative price-return growth. The illustrative cohort is daily rebalanced and equally weighted among complete-coverage symbols, with no transaction costs, taxes, or cash drag. A bootstrap interval across symbols describes cross-sectional dispersion and is not a future-return forecast.

## Recommendation

{recommendation}

## Limitations

"""+"\n".join(f"- {x}" for x in LIMITATIONS)+"\n\n## Figures\n\nSee `visualizations/finance/` and `visualizations/finance/manifest.csv`.\n"
    Path("reports/source").mkdir(parents=True,exist_ok=True);Path("reports/source/finance.md").write_text(report,encoding="utf-8")
    Path("recommendations").mkdir(exist_ok=True);Path("recommendations/finance.md").write_text(f"# Finance recommendations\n\n## Finding\n\n{headline}\n\n## Action\n\n{recommendation}\n\n## Limitation\n\nThe complete-coverage cohort has selection/survivorship bias and price-only returns.\n\n## Monitor\n\nTotal-return volatility, drawdown, turnover, costs, and point-in-time constituent coverage in any future backtest.\n",encoding="utf-8")
    result=finish_domain(DOMAIN,DATASET_IDS,{"start":start.strftime("%Y-%m-%d"),"end":end.strftime("%Y-%m-%d"),"unit_of_analysis":"security-date","return_type":"split-adjusted price return; dividend policy undocumented"},metrics,LIMITATIONS,rows)
    result.update({"headline":headline,"recommendation":recommendation})
    return result
