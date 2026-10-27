"""
Personal Productivity Suite - Backup & Restore Module
File: backup_manager.py

Provides timestamped backups of application data into data/backups/,
backup integrity validation, backup listing, and safe rollback-protected restore.
"""

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from utils import (
    clear_screen,
    confirm,
    get_backups_dir,
    get_data_dir,
    get_filename_timestamp,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_sub_header,
    print_success,
    print_warning,
)


@dataclass
class BackupInfo:
    """Metadata describing a discovered backup file."""
    path: Path
    filename: str
    created_at: str
    size_bytes: int
    note_count: int
    is_valid: bool
    status_msg: str


def get_default_notes_path() -> Path:
    """Return the default path to notes.json."""
    return get_data_dir() / "notes.json"


def validate_backup_file(backup_path: Path) -> Tuple[bool, str, int]:
    """
    Validate that a backup file is well-formed JSON representing notes.
    
    Returns:
        (is_valid: bool, status_msg: str, note_count: int)
    """
    if not backup_path.exists():
        return False, "File does not exist.", 0

    try:
        with open(backup_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return True, "Empty backup file.", 0
            data = json.loads(content)

        if not isinstance(data, list):
            return False, "Malformed format: Root element is not a JSON list.", 0

        # Validate that items look like notes
        for idx, item in enumerate(data):
            if not isinstance(item, dict) or "id" not in item or "title" not in item:
                return False, f"Malformed item at index {idx}.", len(data)

        return True, "Valid backup file.", len(data)

    except json.JSONDecodeError as err:
        return False, f"Corrupted JSON: {err.msg}", 0
    except OSError as err:
        return False, f"Read error: {err}", 0


def create_backup(
    source_path: Optional[Path] = None,
    backup_dir: Optional[Path] = None,
) -> Optional[Path]:
    """
    Create a timestamped backup copy of the notes data file.
    
    Args:
        source_path: Source JSON file (defaults to data/notes.json).
        backup_dir: Destination folder (defaults to data/backups/).
        
    Returns:
        Path to the created backup file, or None on failure.
    """
    src = source_path if source_path else get_default_notes_path()
    dest_dir = backup_dir if backup_dir else get_backups_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        # If no notes file exists yet, create an empty one first
        src.parent.mkdir(parents=True, exist_ok=True)
        with open(src, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

    timestamp_str = get_filename_timestamp()
    backup_filename = f"notes_backup_{timestamp_str}.json"
    backup_path = dest_dir / backup_filename

    try:
        # Atomic copy
        shutil.copy2(src, backup_path)
        is_valid, msg, count = validate_backup_file(backup_path)
        if not is_valid:
            print_error(f"Backup verification failed: {msg}")
            backup_path.unlink(missing_ok=True)
            return None
        return backup_path
    except OSError as err:
        print_error(f"Failed to create backup: {err}")
        return None


def list_backups(backup_dir: Optional[Path] = None) -> List[BackupInfo]:
    """
    Scan the backup directory and return sorted metadata for all discovered backups.
    """
    target_dir = backup_dir if backup_dir else get_backups_dir()
    if not target_dir.exists():
        return []

    backups: List[BackupInfo] = []
    for file_path in target_dir.glob("notes_backup_*.json"):
        if file_path.is_file():
            stat = file_path.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            is_valid, msg, count = validate_backup_file(file_path)

            backups.append(
                BackupInfo(
                    path=file_path,
                    filename=file_path.name,
                    created_at=mod_time,
                    size_bytes=stat.st_size,
                    note_count=count,
                    is_valid=is_valid,
                    status_msg=msg,
                )
            )

    # Sort newest first
    return sorted(backups, key=lambda b: b.filename, reverse=True)


def restore_backup(
    backup_path: Path,
    target_path: Optional[Path] = None,
) -> bool:
    """
    Safely restore notes data from a verified backup file.
    Takes a pre-restore safety snapshot of the active data file before replacing.
    
    Args:
        backup_path: Path to the backup file to restore.
        target_path: Destination active notes file (defaults to data/notes.json).
        
    Returns:
        bool: True if restored successfully, False otherwise.
    """
    dest = target_path if target_path else get_default_notes_path()

    is_valid, msg, count = validate_backup_file(backup_path)
    if not is_valid:
        print_error(f"Cannot restore invalid backup: {msg}")
        return False

    # Safety: Create snapshot of current data before overwriting
    if dest.exists():
        safety_snapshot = dest.with_suffix(".pre_restore.bak")
        try:
            shutil.copy2(dest, safety_snapshot)
        except OSError as err:
            print_error(f"Could not create safety snapshot before restore: {err}")
            return False

    try:
        # Atomic restore via temporary file
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=dest.parent,
            delete=False,
        ) as tf:
            temp_name = tf.name
            with open(backup_path, "r", encoding="utf-8") as bf:
                tf.write(bf.read())

        os.replace(temp_name, dest)
        return True

    except Exception as err:
        print_error(f"Failed to restore backup: {err}")
        return False


def delete_backup(backup_path: Path) -> bool:
    """Safely delete an existing backup file."""
    if not backup_path.exists():
        return False
    try:
        backup_path.unlink()
        return True
    except OSError as err:
        print_error(f"Failed to delete backup file: {err}")
        return False


def _display_backups_table(backups: List[BackupInfo]) -> None:
    """Render a clean CLI table of available backups."""
    if not backups:
        print_info("No backup files found in data/backups/.")
        return

    print("-" * 75)
    print(f"{'#':<3} | {'Backup Filename':<32} | {'Notes':<5} | {'Size':<8} | {'Status'}")
    print("-" * 75)
    for idx, b in enumerate(backups, 1):
        status = "OK" if b.is_valid else f"ERR: {b.status_msg[:12]}"
        size_str = f"{b.size_bytes} B" if b.size_bytes < 1024 else f"{b.size_bytes / 1024:.1f} KB"
        print(f"{idx:<3} | {b.filename:<32} | {b.note_count:<5} | {size_str:<8} | {status}")
    print("-" * 75)


def run_backup_tool() -> None:
    """Interactive CLI runner for Backup & Restore operations."""
    while True:
        clear_screen()
        print_header("BACKUP & RESTORE", subtitle="Application Data Protection")
        print("1. Create New Backup")
        print("2. List Available Backups")
        print("3. Restore From Backup")
        print("4. Delete a Backup")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select an option", min_val=0, max_val=4)

        if choice == 0:
            break

        if choice == 1:
            print_sub_header("CREATE BACKUP")
            created = create_backup()
            if created:
                is_valid, msg, count = validate_backup_file(created)
                print_success(f"Backup created successfully:\n  {created.name}")
                print_info(f"Contains {count} note(s). Location: {created.parent}")
            else:
                print_error("Failed to create backup.")
            pause()

        elif choice == 2:
            clear_screen()
            print_header("AVAILABLE BACKUPS")
            backups = list_backups()
            _display_backups_table(backups)
            print_info(f"Total Backups: {len(backups)}")
            pause()

        elif choice == 3:
            clear_screen()
            print_header("RESTORE BACKUP")
            backups = list_backups()
            if not backups:
                print_info("No backups available to restore.")
                pause()
                continue

            _display_backups_table(backups)
            selected_idx = get_valid_int(
                "Enter backup # to restore (or 0 to cancel)",
                min_val=0,
                max_val=len(backups),
            )

            if selected_idx == 0:
                print_info("Restore cancelled.")
                pause()
                continue

            chosen_backup = backups[selected_idx - 1]
            if not chosen_backup.is_valid:
                print_error(f"Cannot restore: Backup is marked invalid ({chosen_backup.status_msg}).")
                pause()
                continue

            print()
            print_warning(
                f"Restoring '{chosen_backup.filename}' will replace the current active notes data."
            )
            print_info("(A temporary pre-restore snapshot will be saved automatically).")

            if confirm("Are you sure you want to proceed with restore?", default=False):
                if restore_backup(chosen_backup.path):
                    print_success(
                        f"Successfully restored data from '{chosen_backup.filename}' "
                        f"({chosen_backup.note_count} note(s))."
                    )
                else:
                    print_error("Restore operation failed.")
            else:
                print_info("Restore cancelled by user.")
            pause()

        elif choice == 4:
            clear_screen()
            print_header("DELETE BACKUP")
            backups = list_backups()
            if not backups:
                print_info("No backups available to delete.")
                pause()
                continue

            _display_backups_table(backups)
            selected_idx = get_valid_int(
                "Enter backup # to delete (or 0 to cancel)",
                min_val=0,
                max_val=len(backups),
            )

            if selected_idx == 0:
                print_info("Deletion cancelled.")
                pause()
                continue

            chosen_backup = backups[selected_idx - 1]
            if confirm(f"Permanently delete '{chosen_backup.filename}'?", default=False):
                if delete_backup(chosen_backup.path):
                    print_success(f"Deleted backup: {chosen_backup.filename}")
                else:
                    print_error("Failed to delete backup.")
            else:
                print_info("Deletion cancelled.")
            pause()
