"""Render the cross-domain executive summary PDF."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import textwrap

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

HEADLINES={"sales":("gross_line_sales_gbp","GBP gross line sales"),"healthcare":("readmission_within_30d_rate","30-day readmission rate"),"sports":("elo_holdout_accuracy","Historical Elo holdout accuracy"),"finance":("equal_weight_annualized_price_return","Illustrative annualized price return"),"ecommerce":("session_conversion_rate","Session conversion rate")}


def wrap(s:str,width:int=98)->str:return "\n".join(textwrap.wrap(s,width=width,break_long_words=False,break_on_hyphens=False))


def main()->None:
    domains=list(HEADLINES);docs={d:json.loads((ROOT/"outputs"/d/"metrics.json").read_text(encoding="utf-8")) for d in domains}
    rows=[]
    for domain in domains:
        key,label=HEADLINES[domain];metric=next(m for m in docs[domain]["metrics"] if m["metric_id"]==key)
        rows.append((domain,label,metric["value"],metric["unit"],docs[domain]["coverage"],docs[domain]["limitations"]))
    out=ROOT/"executive_summary.pdf"
    with PdfPages(out) as pdf:
        fig=plt.figure(figsize=(11.69,8.27),facecolor="white")
        fig.text(.07,.94,"COMPLETE DATA ANALYSIS PORTFOLIO",fontsize=10,color="#475569")
        fig.text(.07,.88,"Five domains. Five evidence-based analyses.",fontsize=24,weight="bold",color="#0F172A")
        fig.text(.07,.81,wrap("A reproducible portfolio exploring historical retail transactions, hospital encounters, NBA outcomes, equity prices, and online shopping sessions.",130),fontsize=12,color="#334155")
        for i,(domain,label,value,unit,coverage,limits) in enumerate(rows):
            y=.70-i*.10
            if isinstance(value,float):
                if unit in {"proportion", "proportion correct", "annualized proportion", "proportion from peak"}:
                    shown=f"{value:.1%}"
                    unit=""
                else:
                    shown=f"{value:,.2f}"
            else:shown=f"{value:,}"
            cov="; ".join(str(x) for x in coverage.values() if x is not None)
            fig.text(.08,y,TITLE(domain),fontsize=12,weight="bold",color="#1D4ED8")
            fig.text(.31,y,f"{label}: {shown} {unit}",fontsize=11,weight="bold",color="#0F172A")
            fig.text(.31,y-.03,wrap(cov,115),fontsize=8.5,color="#475569")
        fig.text(.07,.19,"Interpretation",fontsize=9.5,weight="bold",color="#1D4ED8")
        fig.text(.07,.14,wrap("Results are source-specific and historical. Denominators, units, source coverage, uncertainty, and limitations differ by domain. No combined cross-domain score is meaningful. Revenue is not profit; hospital associations are not clinical guidance; historical returns are not investment advice; e-commerce sessions do not measure repeat buying.",180),fontsize=7.7,color="#334155")
        pdf.savefig(fig,bbox_inches="tight");plt.close(fig)

        inventory=list(csv.DictReader((ROOT/"visualizations/inventory.csv").open(newline="",encoding="utf-8")))
        first_by_domain={d:next(row for row in inventory if row["domain"]==d) for d in domains}
        fig=plt.figure(figsize=(11.69,8.27),facecolor="white");fig.text(.07,.95,"SELECTED EVIDENCE",fontsize=11,weight="bold",color="#1D4ED8")
        positions=[(.07,.65),(.53,.65),(.07,.37),(.53,.37),(.30,.09)]
        for domain,(x,y) in zip(domains,positions):
            row=first_by_domain[domain];image=mpimg.imread(ROOT/row["output_path"])
            ax=fig.add_axes([x,y,.4,.23]);ax.imshow(image);ax.axis("off")
            fig.text(x,y-.025,TITLE(domain),fontsize=8.5,weight="bold",color="#0F172A")
        pdf.savefig(fig,bbox_inches="tight");plt.close(fig)

        fig=plt.figure(figsize=(11.69,8.27),facecolor="white");fig.text(.07,.94,"METHODS, SOURCES, AND REPRODUCTION",fontsize=11,weight="bold",color="#1D4ED8")
        notes=[
            "Sales: eligible positive invoice lines, with cancelled invoices excluded; gross sales are quantity × price in GBP.",
            "Healthcare: encounter-level readmission within 30 days; expired discharge disposition excluded; patient-cluster bootstrap interval.",
            "Sports: non-copy team-game records; Elo forecast assessed on the final three archive seasons; RAPTOR ratings are source estimates.",
            "Finance: split-adjusted close price returns; 252-day annualization; complete-coverage cohort has selection/survivorship risk.",
            "E-commerce: session conversion with a Wilson interval and visitor-type association test; no repeat-purchase or basket inference.",
        ]
        y=.86
        for note in notes:fig.text(.08,y,"•  "+wrap(note,130),fontsize=10,color="#0F172A");y-=.09
        sources=list(csv.DictReader((ROOT/"datasets/catalog.csv").open(newline="",encoding="utf-8")))
        y=.37;fig.text(.08,y,"Selected sources and terms",fontsize=10,weight="bold",color="#1D4ED8");y-=.04
        for source in sources:
            short=f"{source['title']} — {source['publisher']}; {source['doi_or_version']}; {source['license']}"
            fig.text(.09,y,wrap(short,130),fontsize=8.4,color="#334155");y-=.033
        fig.text(.08,.07,"Reproduce with docs/setup.md and the documented domain builders. Full provenance and caveats: datasets/catalog.csv and docs/data_dictionary.md.",fontsize=8.5,color="#475569")
        pdf.savefig(fig,bbox_inches="tight");plt.close(fig)
    print(f"RENDERED {out.relative_to(ROOT)}")


def TITLE(domain:str)->str:return {"sales":"BUSINESS SALES","healthcare":"HEALTHCARE","sports":"SPORTS","finance":"FINANCE","ecommerce":"E-COMMERCE"}[domain]

if __name__=="__main__":main()
