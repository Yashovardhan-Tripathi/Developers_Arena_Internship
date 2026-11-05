"""Versioned output metadata and visualization manifest contracts."""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.paths import domain_path


DOMAINS = ("sales", "healthcare", "sports", "finance", "ecommerce")
METRIC_FIELDS = {
    "metric_id", "value", "unit", "definition", "denominator", "available", "unavailable_reason"
}
CHART_FIELDS = (
    "chart_id", "domain", "title", "question", "purpose", "chart_type",
    "input_source", "output_path", "coverage", "units", "accessibility_summary",
)


def validate_metric(metric: dict[str, Any]) -> None:
    if not isinstance(metric, dict):
        raise ValueError("Each metric record must be an object.")
    missing = METRIC_FIELDS - metric.keys()
    if missing:
        raise ValueError(f"Metric record is missing fields: {sorted(missing)}")
    if any(not isinstance(metric[field], str) or not metric[field].strip() for field in ("metric_id", "unit", "definition")):
        raise ValueError("Metric ID, unit, and definition must be explicit.")
    if metric["denominator"] is not None and (
        not isinstance(metric["denominator"], str) or not metric["denominator"].strip()
    ):
        raise ValueError("Metric denominator must be a description or null when not applicable.")
    if metric["unavailable_reason"] is not None and not isinstance(metric["unavailable_reason"], str):
        raise ValueError("Metric unavailable_reason must be text or null.")
    if metric["available"] and metric["value"] is None:
        raise ValueError("An available metric needs a value.")
    if not metric["available"] and (
        not isinstance(metric["unavailable_reason"], str) or not metric["unavailable_reason"].strip()
    ):
        raise ValueError("An unavailable metric needs a reason; do not substitute zero.")
    if not isinstance(metric["available"], bool):
        raise ValueError("Metric availability must be a boolean.")
    value = metric["value"]
    if value is not None and not isinstance(value, (str, int, float, bool)):
        raise ValueError("Metric values must be JSON scalar values or null.")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Metric values must be finite; represent unavailable values explicitly.")


def validate_metrics_document(document: dict[str, Any], domain: str | None = None) -> None:
    """Validate the shared metrics schema before writing or consuming it."""
    if not isinstance(document, dict):
        raise ValueError("Metrics document must be a JSON object.")
    required = {
        "schema_version", "domain", "dataset_snapshots", "generated_at_utc",
        "coverage", "metrics", "limitations",
    }
    missing = required - document.keys()
    if missing:
        raise ValueError(f"Metrics document is missing fields: {sorted(missing)}")
    if document["schema_version"] != "1.0" or document["domain"] not in DOMAINS:
        raise ValueError("Metrics document has an unsupported schema version or domain.")
    if domain is not None and document["domain"] != domain:
        raise ValueError("Metrics document domain does not match the requested contract.")
    snapshots = document["dataset_snapshots"]
    if not isinstance(snapshots, dict) or not snapshots or any(
        not isinstance(key, str) or not key or not isinstance(value, str) or not value
        for key, value in snapshots.items()
    ):
        raise ValueError("Dataset snapshots must map non-empty source IDs to version or hash strings.")
    coverage = document["coverage"]
    if not isinstance(coverage, dict) or not coverage or any(
        not isinstance(key, str) or not key or (value is not None and not isinstance(value, str))
        for key, value in coverage.items()
    ):
        raise ValueError("Coverage must map labels to strings or null when unavailable.")
    try:
        generated = datetime.fromisoformat(document["generated_at_utc"].replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("generated_at_utc must be an ISO-8601 timestamp.") from exc
    if generated.tzinfo is None or generated.utcoffset() is None or generated.utcoffset().total_seconds() != 0:
        raise ValueError("generated_at_utc must include a UTC timezone.")
    metrics = document["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise ValueError("Metrics must be a non-empty list of metric records.")
    metric_ids: set[str] = set()
    for metric in metrics:
        if not isinstance(metric, dict):
            raise ValueError("Each metric must be an object.")
        validate_metric(metric)
        if metric["metric_id"] in metric_ids:
            raise ValueError(f"Duplicate metric ID: {metric['metric_id']}")
        metric_ids.add(metric["metric_id"])
    if not isinstance(document["limitations"], list) or any(
        not isinstance(item, str) or not item.strip() for item in document["limitations"]
    ):
        raise ValueError("Limitations must be a list of non-empty strings.")


def validate_chart_rows(domain: str, rows: list[dict[str, str]]) -> None:
    """Validate chart inventory fields, IDs, and project-relative output paths."""
    if domain not in DOMAINS:
        raise ValueError(f"Unsupported domain: {domain}")
    if len(rows) < 5:
        raise ValueError("A completed domain chart manifest must contain at least five charts.")
    seen: set[str] = set()
    required_text = set(CHART_FIELDS) - {"coverage"}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each chart entry must be an object.")
        missing = set(CHART_FIELDS) - row.keys()
        if missing:
            raise ValueError(f"Chart entry is missing fields: {sorted(missing)}")
        if any(not isinstance(row[field], str) for field in CHART_FIELDS):
            raise ValueError("Chart manifest fields must be strings.")
        if any(not row[field].strip() for field in required_text):
            raise ValueError("Chart ID, labels, sources, units, and output path must be non-empty.")
        if row["domain"] != domain or row["chart_id"] in seen:
            raise ValueError("Chart domain must match and chart IDs must be unique.")
        output_path = Path(row["output_path"])
        if output_path.is_absolute() or ".." in output_path.parts:
            raise ValueError("Chart output paths must stay project-relative.")
        seen.add(row["chart_id"])


def build_metrics_document(
    domain: str,
    dataset_snapshots: dict[str, str],
    coverage: dict[str, str | None],
    metrics: list[dict[str, Any]],
    limitations: list[str],
) -> dict[str, Any]:
    if domain not in DOMAINS:
        raise ValueError(f"Unsupported domain: {domain}")
    for metric in metrics:
        validate_metric(metric)
    return {
        "schema_version": "1.0",
        "domain": domain,
        "dataset_snapshots": dataset_snapshots,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "coverage": coverage,
        "metrics": metrics,
        "limitations": limitations,
    }


def write_metrics_document(domain: str, document: dict[str, Any]) -> Path:
    validate_metrics_document(document, domain)
    path = domain_path("outputs", domain, "metrics.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_chart_manifest(domain: str, rows: list[dict[str, str]]) -> Path:
    validate_chart_rows(domain, rows)
    path = domain_path("visualizations", domain, "manifest.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=CHART_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path
