"""Download documented public snapshots into ignored raw-data folders."""

from __future__ import annotations

import argparse
import shutil
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "sales": (
        "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip",
        ROOT / "datasets/raw/sales",
        "online_retail_II.xlsx",
    ),
    "healthcare": (
        "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip",
        ROOT / "datasets/raw/healthcare",
        ("diabetic_data.csv", "IDS_mapping.csv"),
    ),
    "ecommerce": (
        "https://archive.ics.uci.edu/static/public/468/online+shoppers+purchasing+intention+dataset.zip",
        ROOT / "datasets/raw/ecommerce",
        "online_shoppers_intention.csv",
    ),
}
SPORTS_URL = "https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-elo/nbaallelo.csv"
SPORTS_PLAYER_URL = "https://raw.githubusercontent.com/fivethirtyeight/data/master/nba-raptor/historical_RAPTOR_by_player.csv"
FINANCE_URL = "https://raw.githubusercontent.com/kyi3081/stock-analysis/master/prices-split-adjusted.csv"


def safe_members(archive: zipfile.ZipFile) -> None:
    root = Path(".")
    for member in archive.infolist():
        if Path(member.filename).is_absolute() or ".." in Path(member.filename).parts:
            raise ValueError(f"Unsafe path in source archive: {member.filename}")


def download_archive(domain: str, overwrite: bool) -> None:
    url, destination, expected = SOURCES[domain]
    wanted = {expected} if isinstance(expected, str) else set(expected)
    destination.mkdir(parents=True, exist_ok=True)
    archive_path = destination / ".source-download.zip"
    urllib.request.urlretrieve(url, archive_path)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            safe_members(archive)
            names = {Path(name).name: name for name in archive.namelist() if not name.endswith("/")}
            missing = wanted - names.keys()
            if missing:
                raise FileNotFoundError(f"Expected source files missing from {domain} archive: {sorted(missing)}")
            for filename in sorted(wanted):
                target = destination / filename
                if target.exists() and not overwrite:
                    print(f"SKIP existing {target.relative_to(ROOT)}")
                    continue
                partial = target.with_suffix(target.suffix + ".part")
                with archive.open(names[filename]) as source, partial.open("wb") as output:
                    shutil.copyfileobj(source, output)
                partial.replace(target)
                print(f"SAVED {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")
    finally:
        archive_path.unlink(missing_ok=True)


def download_sports(overwrite: bool) -> None:
    folder = ROOT / "datasets/raw/sports"
    folder.mkdir(parents=True, exist_ok=True)
    for filename, url in (("nbaallelo.csv", SPORTS_URL), ("historical_RAPTOR_by_player.csv", SPORTS_PLAYER_URL)):
        target = folder / filename
        if target.exists() and not overwrite:
            print(f"SKIP existing {target.relative_to(ROOT)}")
            continue
        request = urllib.request.Request(url, headers={"User-Agent": "CompleteDataAnalysisPortfolio/1.0"})
        partial = target.with_suffix(target.suffix + ".part")
        with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as output:
            shutil.copyfileobj(response, output)
        partial.replace(target)
        print(f"SAVED {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")


def download_finance(overwrite: bool) -> None:
    target = ROOT / "datasets/raw/finance/prices-split-adjusted.csv"
    if target.exists() and not overwrite:
        print(f"SKIP existing {target.relative_to(ROOT)}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(FINANCE_URL, headers={"User-Agent": "CompleteDataAnalysisPortfolio/1.0"})
    partial = target.with_suffix(target.suffix + ".part")
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as output:
        shutil.copyfileobj(response, output)
    partial.replace(target)
    print(f"SAVED {target.relative_to(ROOT)} ({target.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", choices=[*sorted(SOURCES), "sports", "finance", "all"], required=True)
    parser.add_argument("--overwrite", action="store_true", help="Replace existing raw files")
    args = parser.parse_args()
    domains = [*SOURCES, "sports", "finance"] if args.domain == "all" else [args.domain]
    for domain in domains:
        if domain == "sports":
            download_sports(args.overwrite)
        elif domain == "finance":
            download_finance(args.overwrite)
        else:
            download_archive(domain, args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
