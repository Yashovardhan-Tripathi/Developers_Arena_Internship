"""Build domain analysis artifacts through phase-owned builders."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.contracts import DOMAINS
from src.domains.base import DomainNotImplementedError, build_domain_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--domain", choices=DOMAINS)
    selection.add_argument("--all", action="store_true")
    args = parser.parse_args()
    domains = DOMAINS if args.all else (args.domain,)
    failures = 0
    for domain in domains:
        try:
            build_domain_outputs(domain)
            print(f"BUILT {domain}")
        except DomainNotImplementedError as exc:
            print(f"NOT READY {domain}: {exc}")
            failures += 1
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
