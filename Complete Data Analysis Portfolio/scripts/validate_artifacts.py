"""Validate only artifacts owned by the selected readiness stage."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.contracts import DOMAINS, validate_chart_rows, validate_metrics_document


DOMAIN_REQUIRED = {
    "sales": (
        "project1_sales_analysis/analysis.ipynb", "outputs/sales/metrics.json",
        "visualizations/sales/manifest.csv", "reports/source/sales.md", "reports/project_sales_report.pdf", "recommendations/sales.md",
    ),
    "healthcare": (
        "project2_healthcare_analysis/analysis.ipynb", "outputs/healthcare/metrics.json",
        "visualizations/healthcare/manifest.csv", "reports/source/healthcare.md", "reports/project_healthcare_report.pdf", "recommendations/healthcare.md",
    ),
    "sports": (
        "project3_sports_analytics/analysis.ipynb", "outputs/sports/metrics.json",
        "visualizations/sports/manifest.csv", "reports/source/sports.md", "reports/project_sports_report.pdf", "recommendations/sports.md",
    ),
    "finance": (
        "project4_financial_analysis/analysis.ipynb", "outputs/finance/metrics.json",
        "visualizations/finance/manifest.csv", "reports/source/finance.md", "reports/project_finance_report.pdf", "recommendations/finance.md",
    ),
    "ecommerce": (
        "project5_ecommerce_analytics/analysis.ipynb", "outputs/ecommerce/metrics.json",
        "visualizations/ecommerce/manifest.csv", "reports/source/ecommerce.md", "reports/project_ecommerce_report.pdf", "recommendations/ecommerce.md",
    ),
}
SUBMISSION_REQUIRED = (
    "portfolio_summary.ipynb", "executive_summary.pdf", "presentation/portfolio_presentation.pptx",
    "presentation/outline.md", "visualizations/inventory.csv", "docs/acceptance_matrix.md",
    "docs/methodology.md", "docs/setup.md", "docs/data_dictionary.md", "docs/validation.md",
    "README.md", "dashboard/app.py", "docs/screenshots/README.md",
    "docs/screenshots/dashboard-overview.png", "docs/screenshots/dashboard-sales.png",
    "docs/screenshots/dashboard-healthcare.png", "docs/screenshots/dashboard-sports.png",
    "docs/screenshots/dashboard-finance.png", "docs/screenshots/dashboard-ecommerce.png",
    "docs/screenshots/dashboard-sports-mobile.png",
)


def check_paths(paths: tuple[str, ...], label: str) -> int:
    failures = 0
    for relative in paths:
        path = PROJECT_ROOT / Path(relative)
        if path.is_file():
            print(f"OK {relative}")
        else:
            print(f"MISSING {label}: {relative}")
            failures += 1
    return failures


def check_domain_contracts(domain: str) -> int:
    """Validate metrics and chart schemas when their artifacts are present."""
    failures = 0
    metrics_path = PROJECT_ROOT / "outputs" / domain / "metrics.json"
    if metrics_path.is_file():
        try:
            document = json.loads(metrics_path.read_text(encoding="utf-8"))
            validate_metrics_document(document, domain)
            print(f"VALID metrics contract: {metrics_path.relative_to(PROJECT_ROOT)}")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"INVALID metrics contract: {metrics_path.relative_to(PROJECT_ROOT)}: {exc}")
            failures += 1
    manifest_path = PROJECT_ROOT / "visualizations" / domain / "manifest.csv"
    if manifest_path.is_file():
        try:
            with manifest_path.open(newline="", encoding="utf-8") as stream:
                reader = csv.DictReader(stream)
                if reader.fieldnames is None:
                    raise ValueError("Chart manifest has no header row.")
                validate_chart_rows(domain, list(reader))
            print(f"VALID chart contract: {manifest_path.relative_to(PROJECT_ROOT)}")
        except (OSError, csv.Error, TypeError, ValueError) as exc:
            print(f"INVALID chart contract: {manifest_path.relative_to(PROJECT_ROOT)}: {exc}")
            failures += 1
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--domain", choices=DOMAINS)
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--submission", action="store_true", help="Also check final submission deliverable paths")
    args = parser.parse_args()
    if args.submission and not args.all:
        parser.error("--submission requires --all")
    domains = DOMAINS if args.all else (args.domain,)
    failures = 0
    for domain in domains:
        failures += check_paths(DOMAIN_REQUIRED[domain], f"{domain} domain artifact")
        failures += check_domain_contracts(domain)
    if args.all:
        failures += check_paths(("visualizations/inventory.csv",), "integrated artifact")
    if args.submission:
        failures += check_paths(SUBMISSION_REQUIRED, "submission artifact")
    print(f"Validation result: {'INCOMPLETE' if failures else 'READY'} ({failures} missing paths)")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
