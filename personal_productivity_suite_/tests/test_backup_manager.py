"""
Unit tests for the Backup & Restore module.
File: tests/test_backup_manager.py
"""

import json
from pathlib import Path
import pytest
from backup_manager import (
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
    validate_backup_file,
)


@pytest.fixture
def backup_test_env(tmp_path: Path):
    """Set up temporary source data and backup directory."""
    src_file = tmp_path / "notes.json"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()

    initial_notes = [
        {"id": 1, "title": "Note Alpha", "content": "Body A", "created_at": "2026-10-08 10:00:00"},
        {"id": 2, "title": "Note Beta", "content": "Body B", "created_at": "2026-10-08 10:05:00"},
    ]
    with open(src_file, "w", encoding="utf-8") as f:
        json.dump(initial_notes, f)

    return src_file, backup_dir


class TestBackupManager:
    """Test backup creation, validation, listing, and restoration."""

    def test_create_backup(self, backup_test_env):
        src_file, backup_dir = backup_test_env
        backup_path = create_backup(source_path=src_file, backup_dir=backup_dir)

        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.name.startswith("notes_backup_")

        is_valid, msg, count = validate_backup_file(backup_path)
        assert is_valid is True
        assert count == 2

    def test_list_backups(self, backup_test_env):
        src_file, backup_dir = backup_test_env
        create_backup(source_path=src_file, backup_dir=backup_dir)

        backups = list_backups(backup_dir=backup_dir)
        assert len(backups) == 1
        assert backups[0].note_count == 2
        assert backups[0].is_valid is True

    def test_validate_corrupted_backup(self, tmp_path: Path):
        corrupt_file = tmp_path / "corrupted_backup.json"
        corrupt_file.write_text("NOT JSON CONTENT")

        is_valid, msg, count = validate_backup_file(corrupt_file)
        assert is_valid is False
        assert "Corrupted JSON" in msg

    def test_restore_backup(self, backup_test_env, tmp_path: Path):
        src_file, backup_dir = backup_test_env
        backup_path = create_backup(source_path=src_file, backup_dir=backup_dir)

        # Now simulate user modifying/deleting notes in active file
        with open(src_file, "w", encoding="utf-8") as f:
            json.dump([{"id": 99, "title": "Modified", "content": "New"}], f)

        # Restore from backup
        success = restore_backup(backup_path=backup_path, target_path=src_file)
        assert success is True

        # Verify active file has restored content
        with open(src_file, "r", encoding="utf-8") as f:
            restored_data = json.load(f)
        assert len(restored_data) == 2
        assert restored_data[0]["title"] == "Note Alpha"

        # Verify pre-restore safety snapshot was created
        snapshot_file = src_file.with_suffix(".pre_restore.bak")
        assert snapshot_file.exists()

    def test_delete_backup(self, backup_test_env):
        src_file, backup_dir = backup_test_env
        backup_path = create_backup(source_path=src_file, backup_dir=backup_dir)
        assert backup_path.exists()

        assert delete_backup(backup_path) is True
        assert not backup_path.exists()
