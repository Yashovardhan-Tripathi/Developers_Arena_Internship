"""Session-conversion analysis for UCI Online Shoppers Purchasing Intention."""

from __future__ import annotations

import calendar
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import chi2_contingency

from src.data_io import load_raw
from src.domains.common import PALETTE, add_metric, apply_style, chart, finish_domain, save_chart, write_processed_table, write_table


DOMAIN="ecommerce"
DATASET_IDS=["ecommerce_online_shoppers"]
LIMITATIONS=[
    "Each row is a session in a one-year sample; the source does not support repeat-purchase or basket-level analysis.",
    "PageValues is derived from pages visited before purchase and may encode post-engagement information; it is excluded from predictive features.",
    "Sessions are observational; group differences do not show that a browsing behavior causes conversion.",
    "The source is a historical sample and includes grouped traffic/device fields whose coding may not reflect current systems.",
]


def _wilson(successes:int,n:int)->tuple[float,float]:
    if n<=0: return (0.0,0.0)
    z=1.959963984540054; p=successes/n; den=1+z*z/n
    center=(p+z*z/(2*n))/den; half=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/den
    return center-half,center+half


def build()->dict[str,object]:
    apply_style()
    data=load_raw(DOMAIN,"online_shoppers_intention.csv")
    data["Revenue"]=data["Revenue"].astype(bool)
    duration_cols=["Administrative_Duration","Informational_Duration","ProductRelated_Duration"]
    data["total_page_duration"]=data[duration_cols].sum(axis=1)
    data["total_page_views"]=data[["Administrative","Informational","ProductRelated"]].sum(axis=1)
    month_numbers={calendar.month_abbr[i]:i for i in range(1,13)}
    month_numbers["June"]=6  # The source spells this month differently from the other abbreviations.
    data["month_order"]=data["Month"].map(month_numbers)
    data["conversion"]=data["Revenue"].astype(int)
    total=len(data); converted=int(data["conversion"].sum()); rate=converted/total; ci=_wilson(converted,total)
    month=data.groupby(["month_order","Month"],as_index=False).agg(sessions=("conversion","size"),conversions=("conversion","sum"),conversion_rate=("conversion","mean")).sort_values("month_order")
    visitor=data.groupby("VisitorType",as_index=False).agg(sessions=("conversion","size"),conversions=("conversion","sum"),conversion_rate=("conversion","mean"))
    weekend=data.groupby("Weekend",as_index=False).agg(sessions=("conversion","size"),conversions=("conversion","sum"),conversion_rate=("conversion","mean"))
    outcome=data.groupby("Revenue",as_index=False).agg(sessions=("conversion","size"),median_views=("total_page_views","median"),median_duration_seconds=("total_page_duration","median"),median_bounce_rate=("BounceRates","median"),median_exit_rate=("ExitRates","median"),median_page_value=("PageValues","median"))
    visitor_table=pd.crosstab(data["VisitorType"],data["Revenue"])
    chi2,pvalue,dof,_=chi2_contingency(visitor_table)
    uplift=float(visitor.loc[visitor["VisitorType"].eq("Returning_Visitor"),"conversion_rate"].iloc[0]-visitor.loc[visitor["VisitorType"].eq("New_Visitor"),"conversion_rate"].iloc[0])
    data_export=data.drop(columns=["month_order"])
    write_processed_table(data_export,DOMAIN,"sessions.csv")
    write_table(month,DOMAIN,"conversion_by_month.csv");write_table(visitor,DOMAIN,"conversion_by_visitor_type.csv");write_table(weekend,DOMAIN,"conversion_by_weekend.csv");write_table(outcome,DOMAIN,"engagement_by_conversion.csv")
    rows=[]
    fig,ax=plt.subplots(figsize=(9,4.8));ax.plot(month["Month"],month["conversion_rate"]*100,marker="o",color=PALETTE[0]);ax.set(title="Session conversion rate by month",xlabel="Sample month",ylabel="Sessions resulting in purchase (%)");ax.tick_params(axis="x",rotation=30)
    save_chart(DOMAIN,fig,"conversion_by_month.png");rows.append(chart(DOMAIN,"ecommerce_month_conversion","Monthly conversion","How does session conversion vary across the sample months?","Compares purchase-session share by month while exposing the one-year sample's seasonal pattern.","line","outputs/ecommerce/tables/conversion_by_month.csv","conversion_by_month.png","one-year session sample","percent of sessions","Line shows session conversion percent by month; all months are named."))

    fig,ax=plt.subplots(figsize=(8.5,4.8));v=visitor.sort_values("conversion_rate");ax.bar(v["VisitorType"],v["conversion_rate"]*100,color=PALETTE[1]);ax.set(title="Conversion by visitor type",xlabel="Source visitor type",ylabel="Sessions resulting in purchase (%)")
    save_chart(DOMAIN,fig,"conversion_by_visitor.png");rows.append(chart(DOMAIN,"ecommerce_visitor_conversion","Conversion by visitor type","How do conversion rates differ across source visitor groups?","Shows descriptive purchase-session rates for visitor categories.","bar","outputs/ecommerce/tables/conversion_by_visitor_type.csv","conversion_by_visitor.png","one-year session sample","percent of sessions","Bars show conversion percent by visitor type; sample counts are in the companion table."))

    fig,ax=plt.subplots(figsize=(8,4.8));w=weekend.copy();w["label"]=w["Weekend"].map({True:"Weekend",False:"Weekday"});ax.bar(w["label"],w["conversion_rate"]*100,color=PALETTE[2]);ax.set(title="Conversion by weekend status",xlabel="Session timing",ylabel="Sessions resulting in purchase (%)")
    save_chart(DOMAIN,fig,"conversion_by_weekend.png");rows.append(chart(DOMAIN,"ecommerce_weekend_conversion","Weekend and weekday conversion","Are observed purchase-session rates different on weekend and weekday sessions?","Contrasts session conversion by the source weekend flag.","bar","outputs/ecommerce/tables/conversion_by_weekend.csv","conversion_by_weekend.png","one-year session sample","percent of sessions","Bars compare weekend and weekday conversion rates."))

    fig,ax=plt.subplots(figsize=(8.5,4.8));ax.boxplot([data.loc[~data["Revenue"],"total_page_views"],data.loc[data["Revenue"],"total_page_views"]],tick_labels=["No purchase","Purchase"],showfliers=False);ax.set(title="Page views per session by purchase outcome",xlabel="Session outcome",ylabel="Administrative + informational + product page views")
    save_chart(DOMAIN,fig,"page_views_by_outcome.png");rows.append(chart(DOMAIN,"ecommerce_page_views_outcome","Page views and session outcome","How does page-view volume differ by purchase outcome?","Compares engagement counts by session outcome without implying causation.","boxplot","outputs/ecommerce/tables/engagement_by_conversion.csv","page_views_by_outcome.png","one-year session sample","page views per session","Box plots compare session page-view counts; whiskers exclude plotted fliers but all records remain in summaries."))

    fig,ax=plt.subplots(figsize=(8.5,4.8));groups=[data.loc[~data["Revenue"],"BounceRates"],data.loc[data["Revenue"],"BounceRates"]];ax.boxplot(groups,tick_labels=["No purchase","Purchase"],showfliers=False);ax.set(title="Bounce rate by session outcome",xlabel="Session outcome",ylabel="Source bounce-rate measure")
    save_chart(DOMAIN,fig,"bounce_rate_by_outcome.png");rows.append(chart(DOMAIN,"ecommerce_bounce_outcome","Bounce rate and conversion","How does the source bounce-rate measure differ by purchase outcome?","Describes an engagement measure associated with the session outcome.","boxplot","outputs/ecommerce/tables/engagement_by_conversion.csv","bounce_rate_by_outcome.png","one-year session sample","source bounce-rate measure","Box plots compare bounce-rate distributions by purchase outcome."))

    metrics=[
        add_metric("sessions",total,"sessions","Count of source rows; one row represents one session."),
        add_metric("purchase_sessions",converted,"sessions","Count of sessions with Revenue=true."),
        add_metric("session_conversion_rate",round(rate,4),"proportion","Purchase sessions divided by all source sessions.","12,330 sessions"),
        add_metric("conversion_rate_ci95_lower",round(ci[0],4),"proportion","Lower 95% Wilson score interval for the session conversion proportion.","All source sessions"),
        add_metric("conversion_rate_ci95_upper",round(ci[1],4),"proportion","Upper 95% Wilson score interval for the session conversion proportion.","All source sessions"),
        add_metric("visitor_type_chi_square_p",float(pvalue),"p-value","Pearson chi-square test of independence between visitor type and Revenue; expected counts assessed by scipy output."),
        add_metric("returning_minus_new_conversion",round(uplift,4),"proportion difference","Descriptive conversion-rate difference: returning visitors minus new visitors."),
    ]
    headline=f"{converted:,} of {total:,} sampled sessions resulted in a purchase ({rate:.1%}; 95% Wilson interval {ci[0]:.1%}–{ci[1]:.1%})."
    recommendation="Prioritize a controlled review of the observed visitor-type and engagement differences, and validate them on current session data before changing acquisition or checkout flows. Do not use PageValues in a pre-session purchase prediction because it may include information available only after navigation."
    report=f"""# E-commerce session analysis — source narrative

## Executive summary

{headline}

## Question and source

Which session groups and browsing behaviors are associated with purchase sessions? The UCI Online Shoppers dataset contains {total:,} sessions in a one-year sample; each user appears once in that sample. This is session conversion analysis, not repeat-purchase or basket analysis.

## Methods and statistics

The conversion proportion uses purchase sessions divided by all sessions. Its 95% Wilson interval is {ci[0]:.1%}–{ci[1]:.1%}. Visitor type and purchase outcome show a Pearson chi-square association test (p={pvalue:.3g}, df={dof}); the test is associational and the sample may not represent present-day traffic. PageValues is excluded from prediction because it can encode post-engagement information.

## Recommendation

{recommendation}

## Limitations

"""+"\n".join(f"- {x}" for x in LIMITATIONS)+"\n\n## Figures\n\nSee `visualizations/ecommerce/` and `visualizations/ecommerce/manifest.csv`.\n"
    Path("reports/source").mkdir(parents=True,exist_ok=True);Path("reports/source/ecommerce.md").write_text(report,encoding="utf-8")
    Path("recommendations").mkdir(exist_ok=True);Path("recommendations/ecommerce.md").write_text(f"# E-commerce recommendations\n\n## Finding\n\n{headline}\n\n## Action\n\n{recommendation}\n\n## Limitation\n\nThe data contains one-year session records and cannot establish repeat purchasing or causal changes.\n\n## Monitor\n\nSession conversion by visitor group, page-view distribution, bounce rate, and device/traffic composition in current first-party analytics.\n",encoding="utf-8")
    result=finish_domain(DOMAIN,DATASET_IDS,{"unit_of_analysis":"session","coverage":"one-year source sample"},metrics,LIMITATIONS,rows)
    result.update({"headline":headline,"recommendation":recommendation})
    return result
