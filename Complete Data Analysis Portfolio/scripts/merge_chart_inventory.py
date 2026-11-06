"""Merge domain chart manifests into the portfolio inventory."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from src.contracts import CHART_FIELDS,DOMAINS,validate_chart_rows


def merge()->Path:
    rows=[];seen=set()
    for domain in DOMAINS:
        manifest=ROOT/"visualizations"/domain/"manifest.csv"
        if not manifest.is_file(): raise FileNotFoundError(f"Missing domain chart manifest: {manifest.relative_to(ROOT)}")
        with manifest.open(newline="",encoding="utf-8") as stream:
            reader=csv.DictReader(stream)
            if tuple(reader.fieldnames or ())!=CHART_FIELDS: raise ValueError(f"Unexpected chart manifest schema: {manifest.relative_to(ROOT)}")
            current=list(reader)
        validate_chart_rows(domain,current)
        for row in current:
            if row["chart_id"] in seen: raise ValueError(f"Duplicate portfolio chart ID: {row['chart_id']}")
            artifact=(ROOT/row["output_path"]).resolve()
            if not artifact.is_relative_to(ROOT) or not artifact.is_file(): raise FileNotFoundError(f"Chart artifact missing or outside project: {row['output_path']}")
            seen.add(row["chart_id"]);rows.append(row)
    if len(rows)<25: raise ValueError(f"At least 25 distinct charts are required; found {len(rows)}.")
    target=ROOT/"visualizations"/"inventory.csv";target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_suffix(".csv.part")
    with temp.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,fieldnames=CHART_FIELDS);writer.writeheader();writer.writerows(sorted(rows,key=lambda row:(row["domain"],row["chart_id"])))
    temp.replace(target)
    return target


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__);parser.parse_args()
    try:
        path=merge();print(f"MERGED {len(list(csv.DictReader(path.open(newline='',encoding='utf-8'))))} charts into {path.relative_to(ROOT)}");return 0
    except (OSError,csv.Error,ValueError) as exc:
        print(f"FAILED inventory merge: {exc}");return 2


if __name__=="__main__":raise SystemExit(main())
