"""Shared static-chart saving behavior and accessibility metadata helpers."""

from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure

from src.paths import domain_path


def save_figure(figure: Figure, domain: str, filename: str, *, dpi: int = 160) -> Path:
    """Save a figure under visualizations/<domain>/ with a stable artifact path."""
    if Path(filename).name != filename or Path(filename).suffix.lower() not in {".png", ".svg"}:
        raise ValueError("filename must be a single .png or .svg file name")
    target = domain_path("visualizations", domain, filename)
    target.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(target, dpi=dpi, bbox_inches="tight")
    return target
