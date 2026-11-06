"""Create and execute the five domain notebooks in the project interpreter."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = {
    "sales": ("project1_sales_analysis", "src.domains.sales", "Business sales", "How did sales vary over time, and which products, countries, and identified customers contributed most?"),
    "healthcare": ("project2_healthcare_analysis", "src.domains.healthcare", "Healthcare encounters", "How did encounter characteristics and 30-day readmission labels vary in the historical hospital sample?"),
    "sports": ("project3_sports_analytics", "src.domains.sports", "Sports analytics", "How did historical NBA team outcomes and player-season ratings vary in the selected archives?"),
    "finance": ("project4_financial_analysis", "src.domains.finance", "Financial risk", "How did split-adjusted prices, returns, volatility, and drawdowns evolve in the historical NYSE snapshot?"),
    "ecommerce": ("project5_ecommerce_analytics", "src.domains.ecommerce", "E-commerce sessions", "Which session characteristics were associated with purchase outcomes in the one-year sample?"),
}


def notebook_for(domain: str, module: str, title: str, question: str) -> nbformat.NotebookNode:
    notebook = nbformat.v4.new_notebook()
    notebook.metadata.update({
        "kernelspec": {"display_name": "Python (Complete Data Analysis Portfolio)", "language": "python", "name": "portfolio"},
        "language_info": {"name": "python"},
    })
    notebook.cells = [
        nbformat.v4.new_markdown_cell(
            f"# {title}\n\n## Decision question\n\n{question}\n\n"
            "This notebook calls the same deterministic builder used by `scripts/build_outputs.py`. "
            "It preserves raw source files and writes derived results to the documented project folders."
        ),
        nbformat.v4.new_markdown_cell(
            "## Workflow\n\n"
            "1. Resolve the project root from this notebook's location.\n"
            "2. Load and clean the documented raw source.\n"
            "3. Compute descriptive summaries and uncertainty or forecast diagnostics suited to the data.\n"
            "4. Save processed tables, metrics, chart data, figures, report narrative, and recommendations.\n"
            "5. Record source coverage and limitations with every result."
        ),
        nbformat.v4.new_code_cell(
            "from pathlib import Path\n"
            "import sys\n\n"
            "def find_project_root(start=Path.cwd()):\n"
            "    for candidate in (start.resolve(), *start.resolve().parents):\n"
            "        if (candidate / 'PRD.md').is_file() and (candidate / 'src').is_dir():\n"
            "            return candidate\n"
            "    raise FileNotFoundError('Run this notebook from inside the portfolio project.')\n\n"
            "PROJECT_ROOT = find_project_root()\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n"
            f"from {module} import build\n"
            "result = build()\n"
            "print(result['headline'])\n"
            "print('Charts:', result['chart_count'])\n"
            "print('Metrics:', result['metrics'])\n"
            "print('Recommendation:', result['recommendation'])"
        ),
        nbformat.v4.new_markdown_cell(
            "## Reproducibility and interpretation\n\n"
            "Run this notebook from a fresh project kernel after following [`docs/setup.md`](../docs/setup.md). "
            "All reported values are computed from the pinned local dataset snapshots. "
            "See `reports/source/` for the full methodology and `recommendations/` for finding-linked actions. "
            "The generated chart manifest and versioned metrics are checked by `scripts/validate_artifacts.py`."
        ),
    ]
    notebook.metadata["portfolio_domain"] = domain
    return notebook


def execute_in_process(notebook: nbformat.NotebookNode, cwd: Path) -> None:
    """Execute code cells in the selected interpreter when OS kernel spawning is unavailable."""
    namespace = {"__name__": "__main__"}
    for count, cell in enumerate(notebook.cells, start=1):
        if cell.cell_type != "code":
            continue
        output = io.StringIO()
        cell.execution_count = count
        try:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                exec(compile(cell.source, f"{notebook.metadata['portfolio_domain']}_notebook_cell_{count}", "exec"), namespace)
        except Exception as exc:
            cell.outputs = [nbformat.v4.new_output("stream", name="stderr", text=output.getvalue() + f"{type(exc).__name__}: {exc}\n")]
            raise
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text=output.getvalue())]


def main() -> None:
    import os

    os.chdir(ROOT)
    for domain, (folder, module, title, question) in NOTEBOOKS.items():
        notebook = notebook_for(domain, module, title, question)
        execute_in_process(notebook, ROOT)
        target = ROOT / folder / "analysis.ipynb"
        target.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(notebook, target)
        readme = target.parent / "README.md"
        readme.write_text(
            f"# {title}\n\n{question}\n\n"
            f"Analysis notebook: [analysis.ipynb](analysis.ipynb)\n\n"
            f"Editable report: [reports/source/{domain}.md](../reports/source/{domain}.md)\n\n"
            f"Recommendations: [recommendations/{domain}.md](../recommendations/{domain}.md)\n\n"
            f"Run `python scripts/build_outputs.py --domain {domain}` from the project root to regenerate the results.\n",
            encoding="utf-8",
        )
        print(f"WROTE {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
