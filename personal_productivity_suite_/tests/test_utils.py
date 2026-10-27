"""
Unit tests for shared utility functions.
File: tests/test_utils.py
"""

from pathlib import Path
from utils import (
    get_backups_dir,
    get_current_timestamp,
    get_data_dir,
    get_exports_dir,
    get_filename_timestamp,
    get_project_root,
)


def test_directory_helpers():
    root = get_project_root()
    assert root.exists()
    assert (root / "main.py").exists()

    data_dir = get_data_dir()
    assert data_dir.exists()
    assert data_dir.name == "data"

    backups_dir = get_backups_dir()
    assert backups_dir.exists()
    assert backups_dir.name == "backups"

    exports_dir = get_exports_dir()
    assert exports_dir.exists()
    assert exports_dir.name == "exports"


def test_timestamp_helpers():
    ts = get_current_timestamp()
    assert len(ts) == 19  # YYYY-MM-DD HH:MM:SS
    assert ts[4] == "-" and ts[7] == "-" and ts[10] == " "

    file_ts = get_filename_timestamp()
    assert "_" in file_ts
    assert ":" not in file_ts  # Must be valid for filesystem names on all OSes
