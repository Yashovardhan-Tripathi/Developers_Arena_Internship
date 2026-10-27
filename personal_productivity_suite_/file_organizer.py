"""
Personal Productivity Suite - File Organizer Module
File: file_organizer.py

Safely categorizes and organizes files in a target directory by their file extensions.
Includes path validation, dry-run simulation, collision-free renaming,
and confirmation safeguards to prevent unintended file operations.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from utils import (
    clear_screen,
    confirm,
    get_non_empty_string,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_sub_header,
    print_success,
    print_warning,
)


# Standard extension-to-category mapping
EXTENSION_CATEGORIES: Dict[str, str] = {
    # Images
    ".jpg": "images",
    ".jpeg": "images",
    ".png": "images",
    ".gif": "images",
    ".bmp": "images",
    ".svg": "images",
    ".webp": "images",
    ".ico": "images",
    # Documents
    ".pdf": "documents",
    ".doc": "documents",
    ".docx": "documents",
    ".odt": "documents",
    ".rtf": "documents",
    ".epub": "documents",
    # Text
    ".txt": "text",
    ".md": "text",
    ".log": "text",
    # Spreadsheets
    ".csv": "spreadsheets",
    ".xlsx": "spreadsheets",
    ".xls": "spreadsheets",
    ".ods": "spreadsheets",
    # Python
    ".py": "python",
    ".pyw": "python",
    ".ipynb": "python",
    # Code & Web
    ".html": "code",
    ".css": "code",
    ".js": "code",
    ".ts": "code",
    ".json": "code",
    ".xml": "code",
    ".c": "code",
    ".cpp": "code",
    ".java": "code",
    ".rs": "code",
    ".go": "code",
    ".sql": "code",
    ".sh": "code",
    # Audio
    ".mp3": "audio",
    ".wav": "audio",
    ".aac": "audio",
    ".flac": "audio",
    ".ogg": "audio",
    # Video
    ".mp4": "video",
    ".mkv": "video",
    ".avi": "video",
    ".mov": "video",
    ".wmv": "video",
    # Archives
    ".zip": "archives",
    ".tar": "archives",
    ".gz": "archives",
    ".bz2": "archives",
    ".rar": "archives",
    ".7z": "archives",
}


@dataclass
class OrganizationReport:
    """Summary of operations performed during directory organization."""
    total_found: int = 0
    moved_count: int = 0
    category_summary: Dict[str, int] = field(default_factory=dict)
    actions: List[Tuple[str, str, str]] = field(default_factory=list)  # (filename, category, new_path)
    errors: List[Tuple[str, str]] = field(default_factory=list)  # (filename, reason)


def get_category_for_file(filepath: Path) -> str:
    """Determine the destination category folder name for a given file."""
    ext = filepath.suffix.lower()
    return EXTENSION_CATEGORIES.get(ext, "others")


def get_unique_destination_path(dest_dir: Path, original_filename: str) -> Path:
    """
    Ensure no file is overwritten. If a file exists with the same name,
    appends an incrementing counter: name_1.ext, name_2.ext, etc.
    """
    dest_path = dest_dir / original_filename
    if not dest_path.exists():
        return dest_path

    stem = Path(original_filename).stem
    suffix = Path(original_filename).suffix
    counter = 1

    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def scan_target_directory(directory_path: Path) -> List[Path]:
    """
    Scan a directory for regular files to organize.
    Ignores subdirectories and hidden files (starting with '.') for safety.
    """
    if not directory_path.exists() or not directory_path.is_dir():
        return []

    files = [
        p for p in directory_path.iterdir()
        if p.is_file() and not p.name.startswith(".")
    ]
    return sorted(files, key=lambda p: p.name.lower())


def organize_directory(
    target_path: Path,
    dry_run: bool = False,
) -> OrganizationReport:
    """
    Organize files in target_path by extension categories.
    
    Args:
        target_path: Path to the directory to organize.
        dry_run: If True, simulates the moves without touching the filesystem.
        
    Returns:
        OrganizationReport containing details of planned or executed moves.
    """
    report = OrganizationReport()

    if not target_path.exists():
        report.errors.append((str(target_path), "Directory does not exist."))
        return report

    if not target_path.is_dir():
        report.errors.append((str(target_path), "Specified path is not a directory."))
        return report

    files_to_organize = scan_target_directory(target_path)
    report.total_found = len(files_to_organize)

    if not files_to_organize:
        return report

    for file_path in files_to_organize:
        try:
            category = get_category_for_file(file_path)
            dest_dir = target_path / category

            dest_file = get_unique_destination_path(dest_dir, file_path.name)

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_file))

            report.moved_count += 1
            report.category_summary[category] = report.category_summary.get(category, 0) + 1
            report.actions.append((file_path.name, category, str(dest_file.name)))

        except (PermissionError, OSError) as err:
            report.errors.append((file_path.name, str(err)))

    return report


def display_report(report: OrganizationReport, is_dry_run: bool = False) -> None:
    """Format and display organization results."""
    action_label = "Simulated Organization Preview" if is_dry_run else "Organization Summary"
    print_sub_header(action_label)

    print(f" Total files detected:    {report.total_found}")
    print(f" Files {'to be moved' if is_dry_run else 'moved'}:      {report.moved_count}")
    print()

    if report.category_summary:
        print("Categorization Breakdown:")
        for cat, count in sorted(report.category_summary.items()):
            print(f"  • {cat}/: {count} file(s)")
        print()

    if report.actions:
        print(f"Sample Operations ({'Preview' if is_dry_run else 'Completed'}):")
        for orig, cat, new_name in report.actions[:10]:
            print(f"  {orig}  -->  {cat}/{new_name}")
        if len(report.actions) > 10:
            print(f"  ... and {len(report.actions) - 10} more files.")
        print()

    if report.errors:
        print_warning(f"{len(report.errors)} issue(s) encountered:")
        for fname, err in report.errors:
            print(f"  ! {fname}: {err}")
        print()


def run_file_organizer_tool() -> None:
    """Interactive CLI runner for the File Organizer tool."""
    while True:
        clear_screen()
        print_header("FILE ORGANIZER", subtitle="Categorize Files by Extension")
        print("1. Organize a Directory (Move files into category folders)")
        print("2. Preview Organization (Dry Run / Simulation)")
        print("3. View Supported Categories & Extensions")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select an option", min_val=0, max_val=3)

        if choice == 0:
            break

        if choice == 3:
            clear_screen()
            print_header("SUPPORTED EXTENSIONS")
            cats: Dict[str, List[str]] = {}
            for ext, cat in EXTENSION_CATEGORIES.items():
                cats.setdefault(cat, []).append(ext)

            for cat, exts in sorted(cats.items()):
                print(f"  {cat.capitalize():<14} : {', '.join(sorted(exts))}")
            print(f"  {'Others':<14} : Unrecognized or extensionless files")
            pause()
            continue

        is_dry_run = (choice == 2)
        print_sub_header("SELECT DIRECTORY")
        raw_path = get_non_empty_string("Enter directory path to organize (e.g., ./downloads)")
        target_path = Path(raw_path).expanduser().resolve()

        if not target_path.exists():
            print_error(f"Path does not exist: {target_path}")
            pause()
            continue

        if not target_path.is_dir():
            print_error(f"Path is not a directory: {target_path}")
            pause()
            continue

        # Prevent accidental organization of system roots
        root_paths = [Path("/"), Path.home(), Path("/etc"), Path("/bin"), Path("/usr")]
        if target_path in root_paths:
            print_warning(f"Warning: '{target_path}' is a sensitive root/home directory.")
            if not confirm("Are you sure you want to organize this directory?", default=False):
                print_info("Operation aborted.")
                pause()
                continue

        files_found = scan_target_directory(target_path)
        if not files_found:
            print_info(f"No regular files found directly inside '{target_path}'. Nothing to organize.")
            pause()
            continue

        print_info(f"Found {len(files_found)} file(s) in '{target_path}'.")

        if is_dry_run:
            report = organize_directory(target_path, dry_run=True)
            display_report(report, is_dry_run=True)
            print_info("Dry run completed. No files were moved or changed.")
        else:
            # Preview dry run first
            preview_report = organize_directory(target_path, dry_run=True)
            display_report(preview_report, is_dry_run=True)

            if confirm(f"Proceed with moving {preview_report.moved_count} file(s)?", default=True):
                exec_report = organize_directory(target_path, dry_run=False)
                display_report(exec_report, is_dry_run=False)
                print_success(f"Directory successfully organized: {target_path}")
            else:
                print_info("Organization cancelled by user.")

        pause()
