"""Common domain-builder interface and explicit incomplete-phase errors."""

from __future__ import annotations


class DomainNotImplementedError(RuntimeError):
    """Raised when a domain phase has not yet implemented its output builder."""


def build_domain_outputs(domain: str) -> None:
    raise DomainNotImplementedError(
        f"The {domain} analysis is not implemented yet. Complete its phase-owned notebook, "
        "analysis module, metrics, chart manifest, report narrative, and recommendations first."
    )
