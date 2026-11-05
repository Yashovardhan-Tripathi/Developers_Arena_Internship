"""Project-root discovery and canonical artifact paths."""

from __future__ import annotations

from pathlib import Path


def find_project_root(start: str | Path | None = None) -> Path:
    """Find the nearest ancestor containing this project's PRD and source tree."""
    location = Path(start or __file__).expanduser().resolve()
    if location.is_file():
        location = location.parent
    for candidate in (location, *location.parents):
        if (candidate / "PRD.md").is_file() and (candidate / "src").is_dir():
            return candidate
    raise FileNotFoundError("Could not locate project root (expected PRD.md and src/ in an ancestor).")


PROJECT_ROOT = find_project_root()


def domain_path(section: str, domain: str, *parts: str) -> Path:
    """Build a safe path within a domain-owned project folder."""
    if domain not in {"sales", "healthcare", "sports", "finance", "ecommerce"}:
        raise ValueError(f"Unsupported domain: {domain}")
    base = (PROJECT_ROOT / section / domain).resolve()
    target = (base.joinpath(*parts)).resolve()
    if not target.is_relative_to(base):
        raise ValueError("Path escapes the requested domain folder.")
    return target
