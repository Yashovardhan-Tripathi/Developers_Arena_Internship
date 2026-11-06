"""Dispatch reproducible domain analysis builders."""

from __future__ import annotations


from collections.abc import Callable
from typing import Any


BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {}


def build_domain_outputs(domain: str) -> dict[str, Any]:
    """Run a completed domain builder, failing clearly when it is not registered."""
    if domain not in BUILDERS:
        raise ValueError(f"Unsupported or unfinished domain: {domain}")
    return BUILDERS[domain]()


def register_builders() -> None:
    """Load builders lazily so the CLI imports only the selected domain stack."""
    from src.domains.ecommerce import build as ecommerce
    from src.domains.finance import build as finance
    from src.domains.healthcare import build as healthcare
    from src.domains.sales import build as sales
    from src.domains.sports import build as sports

    BUILDERS.update({
        "sales": sales, "healthcare": healthcare, "sports": sports,
        "finance": finance, "ecommerce": ecommerce,
    })
