"""Shared utilities used by the domain analysis builders."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd

from src.contracts import build_metrics_document, write_chart_manifest, write_metrics_document
from src.data_io import load_raw
from src.paths import PROJECT_ROOT, domain_path
from src.visualization import save_figure


PALETTE = ("#1D4ED8", "#0F766E", "#B45309", "#7C3AED", "#BE123C", "#475569")


def read_source_catalog() -> dict[str, dict[str, str]]:
    with (PROJECT_ROOT / "datasets/catalog.csv").open(newline="", encoding="utf-8") as stream:
        return {row["dataset_id"]: row for row in csv.DictReader(stream)}


def source_hashes(dataset_ids: list[str]) -> dict[str, str]:
    catalog = read_source_catalog()
    return {dataset_id: catalog[dataset_id]["sha256"] for dataset_id in dataset_ids}


def chart(domain: str, chart_id: str, title: str, question: str, purpose: str,
          chart_type: str, source: str, filename: str, coverage: str, units: str,
          accessibility: str) -> dict[str, str]:
    return {
        "chart_id": chart_id, "domain": domain, "title": title, "question": question,
        "purpose": purpose, "chart_type": chart_type, "input_source": source,
        "output_path": f"visualizations/{domain}/{filename}", "coverage": coverage,
        "units": units, "accessibility_summary": accessibility,
    }


def save_chart(domain: str, fig: Any, filename: str) -> None:
    fig.tight_layout()
    save_figure(fig, domain, filename)
    plt.close(fig)


def add_metric(metric_id: str, value: Any, unit: str, definition: str,
               denominator: str | None = None) -> dict[str, Any]:
    return {
        "metric_id": metric_id, "value": value, "unit": unit,
        "definition": definition, "denominator": denominator,
        "available": True, "unavailable_reason": None,
    }


def finish_domain(domain: str, dataset_ids: list[str], coverage: dict[str, str | None],
                  metrics: list[dict[str, Any]], limitations: list[str],
                  chart_rows: list[dict[str, str]]) -> dict[str, Any]:
    document = build_metrics_document(domain, source_hashes(dataset_ids), coverage, metrics, limitations)
    metrics_path = write_metrics_document(domain, document)
    manifest_path = write_chart_manifest(domain, chart_rows)
    return {
        "domain": domain,
        "metrics_path": str(metrics_path.relative_to(PROJECT_ROOT)),
        "manifest_path": str(manifest_path.relative_to(PROJECT_ROOT)),
        "chart_count": len(chart_rows),
        "metrics": {item["metric_id"]: item["value"] for item in metrics},
    }


def ensure_output_dir(domain: str, section: str = "outputs") -> Path:
    path = domain_path(section, domain)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_table(frame: pd.DataFrame, domain: str, filename: str) -> Path:
    target = domain_path("outputs", domain, "tables", filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)
    return target


def write_processed_table(frame: pd.DataFrame, domain: str, filename: str) -> Path:
    target = domain_path("datasets/processed", domain, filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(target, index=False)
    return target


def apply_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.edgecolor": "#CBD5E1", "axes.labelcolor": "#0F172A",
        "text.color": "#0F172A", "xtick.color": "#475569", "ytick.color": "#475569",
        "font.size": 10, "axes.titleweight": "bold", "axes.titlepad": 12,
    })
