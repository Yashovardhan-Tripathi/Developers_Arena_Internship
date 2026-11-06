"""Build the portfolio presentation from validated metrics and figures."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR,PP_ALIGN
from pptx.util import Inches,Pt


DOMAINS=[("sales","Business sales","gross_line_sales_gbp","Gross line sales"),("healthcare","Healthcare","readmission_within_30d_rate","30-day readmission"),("sports","Sports","elo_holdout_accuracy","Elo holdout accuracy"),("finance","Finance","equal_weight_annualized_price_return","Illustrative annualized price return"),("ecommerce","E-commerce","session_conversion_rate","Session conversion")]
NAVY=RGBColor(15,23,42);BLUE=RGBColor(29,78,216);SLATE=RGBColor(71,85,105);PALE=RGBColor(248,250,252);BORDER=RGBColor(203,213,225);WHITE=RGBColor(255,255,255)


def textbox(slide,x,y,w,h,text,size=16,bold=False,color=NAVY,font="Aptos",align=PP_ALIGN.LEFT)->None:
    shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=shape.text_frame;tf.clear();tf.word_wrap=True
    tf.margin_left=Inches(.03);tf.margin_right=Inches(.03);tf.margin_top=Inches(.02);tf.margin_bottom=Inches(.02)
    p=tf.paragraphs[0];p.alignment=align;r=p.add_run();r.text=text;r.font.name=font;r.font.size=Pt(size);r.font.bold=bold;r.font.color.rgb=color
    return shape


def rounded_card(slide,x,y,w,h)->None:
    shape=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));shape.fill.solid();shape.fill.fore_color.rgb=PALE;shape.line.color.rgb=BORDER


def metric_value(metric:dict)->str:
    val=metric["value"]
    if isinstance(val,float):
        if "rate" in metric["metric_id"] or "accuracy" in metric["metric_id"]:return f"{val:.1%}"
        return f"{val:,.2f}"
    return f"{val:,}" if isinstance(val,int) else str(val)


def main()->None:
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    blank=prs.slide_layouts[6]
    # Title slide
    slide=prs.slides.add_slide(blank);slide.background.fill.solid();slide.background.fill.fore_color.rgb=NAVY
    textbox(slide,.8,1.1,11.7,.45,"DATA ANALYSIS PORTFOLIO",14,True,RGBColor(147,197,253))
    textbox(slide,.8,1.8,11.8,1.4,"Five domains.\nEvidence in context.",34,True,WHITE)
    textbox(slide,.82,3.55,10.7,.9,"Business sales · Healthcare · Sports · Finance · E-commerce",18,False,RGBColor(226,232,240))
    textbox(slide,.82,6.65,11.5,.35,"Historical public datasets · Reproducible Python workflow · Local interactive dashboard",10,False,RGBColor(203,213,225))

    # Portfolio overview
    slide=prs.slides.add_slide(blank);textbox(slide,.55,.35,12.2,.55,"A portfolio built around five distinct questions",25,True)
    textbox(slide,.58,1.02,11.9,.5,"Each project keeps its unit, denominator, coverage, and limitations visible. Metrics are not combined across unrelated domains.",12,False,SLATE)
    chart_count=sum(len(list(csv.DictReader((ROOT/"visualizations"/d/"manifest.csv").open(newline="",encoding="utf-8")))) for d,_,_,_ in DOMAINS)
    overview=[("5","Domain analyses"),("6","Dataset snapshots"),(str(chart_count),"Distinct charts")]
    for i,(value,label) in enumerate(overview):
        x=.65+i*4.1;rounded_card(slide,x,1.9,3.55,1.15);textbox(slide,x+.2,2.02,3.1,.5,value,24,True,BLUE,align=PP_ALIGN.CENTER);textbox(slide,x+.2,2.55,3.1,.35,label,11,False,SLATE,align=PP_ALIGN.CENTER)
    headlines={
      "sales":"Gross positive line sales; revenue is not profit.",
      "healthcare":"Historical encounter readmission; not clinical guidance.",
      "sports":"Historical Elo forecast evaluation; source ends in 2015.",
      "finance":"Split-adjusted price returns; survivorship limits remain.",
      "ecommerce":"One-year session conversion; not repeat buying.",
    }
    y=3.45
    for domain,title,_,_ in DOMAINS:
        textbox(slide,.75,y,2.15,.35,title,13,True,BLUE);textbox(slide,3.0,y,9.1,.4,headlines[domain],12,False,NAVY);y+=.56
    textbox(slide,.6,6.88,12,.25,"Source details and project navigation: README.md · datasets/catalog.csv · docs/data_dictionary.md",9,False,SLATE)

    # Domain evidence slides
    inventory=list(csv.DictReader((ROOT/"visualizations/inventory.csv").open(newline="",encoding="utf-8")))
    for domain,title,key,label in DOMAINS:
        doc=json.loads((ROOT/"outputs"/domain/"metrics.json").read_text(encoding="utf-8"));metric=next(x for x in doc["metrics"] if x["metric_id"]==key)
        report=(ROOT/"reports/source"/f"{domain}.md").read_text(encoding="utf-8")
        finding=next((line for line in report.splitlines() if line.strip() and not line.startswith("#")),"").strip()
        row=next(x for x in inventory if x["domain"]==domain)
        slide=prs.slides.add_slide(blank);textbox(slide,.55,.28,12.2,.5,title,25,True)
        textbox(slide,.6,.9,6.0,.35,label,11,True,SLATE)
        rounded_card(slide,.58,1.33,3.0,1.02);textbox(slide,.8,1.48,2.55,.42,metric_value(metric),24,True,BLUE);textbox(slide,.8,1.94,2.55,.25,metric["unit"],10,False,SLATE)
        textbox(slide,3.9,1.38,8.7,.78,finding,12,False,NAVY)
        image=ROOT/row["output_path"];slide.shapes.add_picture(str(image),Inches(.62),Inches(2.55),width=Inches(8.0),height=Inches(4.35))
        limitations=doc.get("limitations",[]);textbox(slide,8.9,2.7,3.75,.35,"READ WITH THESE LIMITS",10,True,BLUE)
        textbox(slide,8.9,3.1,3.8,2.2,"\n".join("• "+text for text in limitations[:4]),10,False,SLATE)
        textbox(slide,8.9,5.65,3.8,.75,f"Coverage: {'; '.join(str(v) for v in doc['coverage'].values() if v is not None)}",9,False,SLATE)
        textbox(slide,.65,7.12,12,.2,f"Chart question: {row['question']} · Source: {row['input_source']}",8.5,False,SLATE)

    # Closing slide
    slide=prs.slides.add_slide(blank);textbox(slide,.65,.45,12,.55,"What the evidence supports",25,True)
    textbox(slide,.7,1.25,11.7,1.0,"Use these results as reproducible historical analyses. Validate current data and operating context before making business, clinical, sports, or financial decisions.",17,False,NAVY)
    sections=[("Methods","Pandas preparation, descriptive statistics, uncertainty where suitable, chronological forecast review, and source-level limitations."),("Recommendations","Each action is tied to a measured result and includes a limit and a monitoring measure."),("Reproduce","Follow docs/setup.md; build domain outputs; open the five analysis notebooks and local dashboard.")]
    y=3.0
    for heading,body in sections:
        rounded_card(slide,.72,y,11.7,.9);textbox(slide,.95,y+.13,2.0,.3,heading,13,True,BLUE);textbox(slide,3.0,y+.13,9.1,.62,body,11,False,NAVY);y+=1.12
    textbox(slide,.72,6.85,11.5,.25,"This deck does not provide medical or investment advice, claim causation, or imply current conditions.",9,False,SLATE)

    target=ROOT/"presentation/portfolio_presentation.pptx";target.parent.mkdir(parents=True,exist_ok=True);prs.save(target)
    outline=ROOT/"presentation/outline.md";outline.write_text("# Portfolio presentation outline\n\n"+"\n".join(f"{i}. {label}" for i,label in enumerate(["Title and purpose","Portfolio overview",*[title for _,title,_,_ in DOMAINS],"Interpretation and reproduction"],start=1))+"\n",encoding="utf-8")
    print(f"RENDERED {target.relative_to(ROOT)} ({len(prs.slides)} slides)")


if __name__=="__main__":main()
