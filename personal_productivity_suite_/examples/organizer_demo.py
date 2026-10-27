"""
Example script: Demonstrate programmatic use of the File Organizer
File: examples/organizer_demo.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from file_organizer import organize_directory, scan_target_directory


def run_demo():
    sample_dir = Path(__file__).resolve().parent / "sample_files"
    sample_dir.mkdir(parents=True, exist_ok=True)

    # Populate sample files if empty
    demo_files = {
        "report.pdf": "PDF document content",
        "chart.png": "PNG image data",
        "notes.txt": "Text file content",
        "script.py": "print('hello from demo')",
        "data.csv": "col1,col2\nval1,val2",
        "archive.zip": "binary zip data",
    }
    for filename, content in demo_files.items():
        fpath = sample_dir / filename
        if not fpath.exists():
            fpath.write_text(content)

    print(f"Sample directory: {sample_dir}")
    print(f"Files found: {[p.name for p in scan_target_directory(sample_dir)]}")

    print("\nRunning Dry Run Simulation...")
    dry_report = organize_directory(sample_dir, dry_run=True)
    print(f"Would move {dry_report.moved_count} files into categories:")
    for cat, count in dry_report.category_summary.items():
        print(f"  - {cat}/: {count} file(s)")


if __name__ == "__main__":
    run_demo()
