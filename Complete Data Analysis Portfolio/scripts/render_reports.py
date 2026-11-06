"""Render consistent multi-page PDF reports from validated project outputs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from src.paths import PROJECT_ROOT


DOMAINS = {
    "sales": "Business sales analysis",
    "healthcare": "Healthcare encounter analysis",
    "sports": "Sports analytics",
    "finance": "Historical financial risk analysis",
    "ecommerce": "E-commerce session analysis",
}


def page_header(fig, title: str, subtitle: str = "Complete Data Analysis Portfolio") -> None:
    fig.text(.08, .955, subtitle, fontsize=9, color="#475569")
    fig.text(.08, .92, title, fontsize=21, weight="bold", color="#0F172A")
    fig.lines.append(plt.Line2D([.08,.92],[.9,.9],transform=fig.transFigure,color="#CBD5E1",lw=1))


def wrap(text: str, width: int = 98) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False))


def load_manifest(domain: str) -> list[dict[str, str]]:
    path = PROJECT_ROOT / "visualizations" / domain / "manifest.csv"
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def load_sources(domain: str) -> list[dict[str, str]]:
    with (PROJECT_ROOT / "datasets/catalog.csv").open(newline="", encoding="utf-8") as stream:
        return [row for row in csv.DictReader(stream) if row["domain"] == domain]


def source_report(domain: str) -> str:
    return (PROJECT_ROOT / "reports" / "source" / f"{domain}.md").read_text(encoding="utf-8")


def render(domain: str, title: str) -> Path:
    metric_doc = json.loads((PROJECT_ROOT / "outputs" / domain / "metrics.json").read_text(encoding="utf-8"))
    metrics = metric_doc["metrics"]
    rows = load_manifest(domain)
    narrative = source_report(domain)
    headline = next((line for line in narrative.splitlines() if line and not line.startswith("#") and not line.startswith("##")), "See the source narrative for findings.")
    path = PROJECT_ROOT / "reports" / f"project_{domain}_report.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(path) as pdf:
        fig = plt.figure(figsize=(8.27,11.69), facecolor="white")
        page_header(fig,title)
        fig.text(.08,.85,"EXECUTIVE SUMMARY",fontsize=10,weight="bold",color="#1D4ED8")
        fig.text(.08,.81,wrap(headline,94),fontsize=13,weight="bold",va="top",linespacing=1.4)
        q = next((line for line in narrative.splitlines() if line.endswith("?") or "? " in line), "")
        fig.text(.08,.68,"QUESTION",fontsize=10,weight="bold",color="#1D4ED8")
        fig.text(.08,.645,wrap(q,100),fontsize=11,va="top",linespacing=1.35)
        fig.text(.08,.55,"KEY METRICS",fontsize=10,weight="bold",color="#1D4ED8")
        y=.51
        for item in metrics[:6]:
            val=item["value"]
            unit=item["unit"]
            if isinstance(val,float) and unit in {"proportion", "proportion correct", "annualized proportion", "proportion from peak"}:
                val=f"{val:.2%}"
                unit=""
            elif isinstance(val,float):
                val=f"{val:,.4f}" if abs(val)<1 else f"{val:,.2f}"
            fig.text(.09,y,f"•  {item['metric_id'].replace('_',' ').title()}: {val} {unit}",fontsize=10.5,color="#0F172A")
            y-=.045
        fig.text(.08,.19,"SOURCE COVERAGE",fontsize=10,weight="bold",color="#1D4ED8")
        cov=" · ".join(f"{k.replace('_',' ').title()}: {v}" for k,v in metric_doc["coverage"].items() if v is not None)
        fig.text(.08,.155,wrap(cov,100),fontsize=9.5,color="#334155",va="top")
        fig.text(.08,.065,"Generated from the reproducible project outputs. All findings are historical and limited by the source coverage described in this report.",fontsize=8,color="#475569")
        pdf.savefig(fig,bbox_inches="tight");plt.close(fig)

        for index,row in enumerate(rows, start=1):
            fig=plt.figure(figsize=(8.27,11.69),facecolor="white");page_header(fig,row["title"])
            image_path=PROJECT_ROOT / row["output_path"]
            image=mpimg.imread(image_path)
            ax=fig.add_axes([.09,.37,.82,.48]);ax.imshow(image);ax.axis("off")
            fig.text(.09,.32,f"Question answered: {row['question']}",fontsize=10.5,weight="bold",color="#0F172A",wrap=True)
            fig.text(.09,.25,f"Purpose: {row['purpose']}",fontsize=9.5,color="#334155",wrap=True)
            fig.text(.09,.18,f"Coverage: {row['coverage']}    |    Units: {row['units']}",fontsize=9,color="#475569",wrap=True)
            fig.text(.09,.115,f"Source: {row['input_source']}",fontsize=8.5,color="#475569",wrap=True)
            fig.text(.09,.075,f"Accessibility note: {row['accessibility_summary']}",fontsize=8.2,color="#475569",wrap=True)
            pdf.savefig(fig,bbox_inches="tight");plt.close(fig)

        fig=plt.figure(figsize=(8.27,11.69),facecolor="white");page_header(fig,"Recommendations and limitations")
        recommendation=(PROJECT_ROOT/"recommendations"/f"{domain}.md").read_text(encoding="utf-8")
        body=[]
        for line in recommendation.splitlines():
            if line.startswith("#"):
                body.append(line.lstrip("# ").upper())
            elif line.startswith("## "):
                body.append("\n"+line[3:].upper())
            elif line.strip():
                body.append("•  "+line.strip() if line.startswith("- ") else line.strip())
        fig.text(.09,.85,wrap("\n".join(body),100),fontsize=10.2,va="top",linespacing=1.45,color="#0F172A")
        source_lines=[]
        for index,source in enumerate(load_sources(domain),start=1):
            ref=source["doi_or_version"] or source["source_url"]
            source_lines.append(f"[{index}] {source['title']} — {source['publisher']}; {ref}; {source['license']}. {source['source_url']}")
        fig.text(.09,.1,"SOURCES AND TERMS",fontsize=8.5,weight="bold",color="#1D4ED8")
        fig.text(.09,.075,wrap("\n".join(source_lines),115),fontsize=7,color="#475569",va="top")
        pdf.savefig(fig,bbox_inches="tight");plt.close(fig)
    return path


def main() -> None:
    for domain,title in DOMAINS.items():
        path=render(domain,title)
        print(f"RENDERED {path.relative_to(PROJECT_ROOT)}",flush=True)


if __name__=="__main__":
    main()
