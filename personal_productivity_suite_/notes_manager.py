"""
Personal Productivity Suite - Notes Manager Module
File: notes_manager.py

Handles persistent notes storage, retrieval, search, editing, deletion,
and multi-format export (TXT, JSON, CSV) using safe JSON file persistence.
"""

import csv
import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils import (
    clear_screen,
    confirm,
    get_current_timestamp,
    get_data_dir,
    get_exports_dir,
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


@dataclass
class Note:
    """Represents an individual user note."""
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert Note instance to serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Note":
        """Reconstruct Note instance from a dictionary."""
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            content=str(data.get("content", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", data.get("created_at", ""))),
        )


class NotesManager:
    """
    Manages CRUD operations and persistent JSON storage for Notes.
    Implements atomic file writing to prevent data corruption.
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        if storage_path is None:
            self.storage_path = get_data_dir() / "notes.json"
        else:
            self.storage_path = Path(storage_path)

        self.notes: List[Note] = []
        self._next_id: int = 1
        self.load_notes()

    def load_notes(self) -> bool:
        """
        Load notes from JSON file. Handles missing and malformed files safely.
        
        Returns:
            bool: True if loaded successfully, False if corrupted or empty.
        """
        if not self.storage_path.exists():
            self.notes = []
            self._next_id = 1
            return True

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    self.notes = []
                    self._next_id = 1
                    return True
                raw_data = json.loads(content)

            loaded_notes: List[Note] = []
            for item in raw_data:
                loaded_notes.append(Note.from_dict(item))

            self.notes = loaded_notes
            self._next_id = max((n.id for n in self.notes), default=0) + 1
            return True

        except (json.JSONDecodeError, KeyError, ValueError) as err:
            # Create a backup of the corrupted file before resetting
            backup_corrupt = self.storage_path.with_suffix(".corrupt.bak")
            try:
                shutil.copyfile(self.storage_path, backup_corrupt)
                print_error(
                    f"Corrupted notes file detected ({err}). "
                    f"Saved backup to '{backup_corrupt.name}'."
                )
            except OSError:
                pass
            self.notes = []
            self._next_id = 1
            return False

        except OSError as err:
            print_error(f"Failed to access notes file: {err}")
            self.notes = []
            self._next_id = 1
            return False

    def save_notes(self) -> bool:
        """
        Persist notes to disk atomically using a temporary file.
        
        Returns:
            bool: True on success, False on failure.
        """
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = [n.to_dict() for n in self.notes]

            # Write to a temporary file in the same directory, then rename
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.storage_path.parent,
                delete=False,
            ) as tf:
                temp_name = tf.name
                json.dump(data, tf, indent=2, ensure_ascii=False)

            # Atomic replace
            os.replace(temp_name, self.storage_path)
            return True

        except Exception as err:
            print_error(f"Failed to save notes: {err}")
            return False

    def add_note(self, title: str, content: str) -> Note:
        """Create and persist a new note."""
        now = get_current_timestamp()
        note = Note(
            id=self._next_id,
            title=title.strip(),
            content=content.strip(),
            created_at=now,
            updated_at=now,
        )
        self._next_id += 1
        self.notes.append(note)
        self.save_notes()
        return note

    def get_all_notes(self) -> List[Note]:
        """Return all notes sorted by ID."""
        return sorted(self.notes, key=lambda n: n.id)

    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Find a note by its unique numeric ID."""
        for note in self.notes:
            if note.id == note_id:
                return note
        return None

    def search_notes(self, query: str) -> List[Note]:
        """Search notes by title or content (case-insensitive)."""
        q = query.strip().lower()
        if not q:
            return []
        return [
            n for n in self.notes
            if q in n.title.lower() or q in n.content.lower()
        ]

    def edit_note(
        self,
        note_id: int,
        new_title: Optional[str] = None,
        new_content: Optional[str] = None,
    ) -> bool:
        """Update an existing note's title and/or content."""
        note = self.get_note_by_id(note_id)
        if not note:
            return False

        updated = False
        if new_title is not None and new_title.strip():
            note.title = new_title.strip()
            updated = True
        if new_content is not None and new_content.strip():
            note.content = new_content.strip()
            updated = True

        if updated:
            note.updated_at = get_current_timestamp()
            self.save_notes()
            return True
        return False

    def delete_note(self, note_id: int) -> bool:
        """Remove a note by ID."""
        note = self.get_note_by_id(note_id)
        if not note:
            return False

        self.notes = [n for n in self.notes if n.id != note_id]
        self.save_notes()
        return True

    def export_notes(
        self,
        format_type: str,
        export_dir: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Export notes to a chosen format: 'txt', 'json', or 'csv'.
        
        Args:
            format_type: One of 'txt', 'json', 'csv'.
            export_dir: Destination directory.
            
        Returns:
            Path of exported file or None if export failed.
        """
        fmt = format_type.lower().strip()
        if fmt not in ("txt", "json", "csv"):
            raise ValueError(f"Unsupported export format '{format_type}'. Must be txt, json, or csv.")

        target_dir = export_dir if export_dir else get_exports_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        now_str = get_current_timestamp("%Y%m%d_%H%M%S")
        file_path = target_dir / f"notes_export_{now_str}.{fmt}"

        try:
            if fmt == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([n.to_dict() for n in self.notes], f, indent=2, ensure_ascii=False)

            elif fmt == "csv":
                with open(file_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Title", "Content", "Created At", "Updated At"])
                    for n in self.notes:
                        writer.writerow([n.id, n.title, n.content, n.created_at, n.updated_at])

            elif fmt == "txt":
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("=" * 60 + "\n")
                    f.write("PERSONAL PRODUCTIVITY SUITE - NOTES EXPORT\n")
                    f.write(f"Generated: {get_current_timestamp()}\n")
                    f.write(f"Total Notes: {len(self.notes)}\n")
                    f.write("=" * 60 + "\n\n")

                    for n in self.notes:
                        f.write(f"ID: {n.id}\n")
                        f.write(f"Title: {n.title}\n")
                        f.write(f"Created: {n.created_at} | Updated: {n.updated_at}\n")
                        f.write("-" * 40 + "\n")
                        f.write(f"{n.content}\n")
                        f.write("\n" + "=" * 60 + "\n\n")

            return file_path

        except OSError as err:
            print_error(f"Export failed: {err}")
            return None


def _display_notes_list(notes: List[Note]) -> None:
    """Format and print a table/list of notes."""
    if not notes:
        print_info("No notes found.")
        return

    print("-" * 75)
    print(f"{'ID':<4} | {'Title':<28} | {'Created':<19} | {'Preview'}")
    print("-" * 75)
    for n in notes:
        preview = (n.content[:20] + "...") if len(n.content) > 20 else n.content
        preview = preview.replace("\n", " ")
        title = (n.title[:25] + "...") if len(n.title) > 25 else n.title
        print(f"{n.id:<4} | {title:<28} | {n.created_at:<19} | {preview}")
    print("-" * 75)


def run_notes_manager() -> None:
    """Interactive CLI runner for Notes Manager."""
    manager = NotesManager()

    while True:
        clear_screen()
        print_header("NOTES MANAGER", subtitle="Persistent Note Organization")
        print("1. View All Notes")
        print("2. Add New Note")
        print("3. Search Notes")
        print("4. View Note Details")
        print("5. Edit Note")
        print("6. Delete Note")
        print("7. Export Notes")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select an option", min_val=0, max_val=7)

        if choice == 0:
            break

        if choice == 1:
            clear_screen()
            print_header("ALL NOTES")
            all_notes = manager.get_all_notes()
            _display_notes_list(all_notes)
            print_info(f"Total Notes: {len(all_notes)}")
            pause()

        elif choice == 2:
            print_sub_header("ADD NEW NOTE")
            title = get_non_empty_string("Enter note title")
            content = get_non_empty_string("Enter note content")
            created_note = manager.add_note(title, content)
            print()
            print_success("Note added successfully!")
            print(f" Note ID: {created_note.id}")
            print(f" Created: {created_note.created_at}")
            pause()

        elif choice == 3:
            print_sub_header("SEARCH NOTES")
            query = get_non_empty_string("Enter search term (title or content)")
            results = manager.search_notes(query)
            print()
            print_info(f"Found {len(results)} note(s) matching '{query}':")
            _display_notes_list(results)
            pause()

        elif choice == 4:
            print_sub_header("VIEW NOTE DETAILS")
            all_notes = manager.get_all_notes()
            if not all_notes:
                print_info("No notes available to view.")
                pause()
                continue
            _display_notes_list(all_notes)
            note_id = get_valid_int("Enter Note ID to view")
            note = manager.get_note_by_id(note_id)
            if not note:
                print_error(f"Note with ID {note_id} not found.")
            else:
                clear_screen()
                print_header(f"NOTE #{note.id}: {note.title}")
                print(f"Created: {note.created_at}")
                print(f"Updated: {note.updated_at}")
                print("-" * 50)
                print(note.content)
                print("-" * 50)
            pause()

        elif choice == 5:
            print_sub_header("EDIT NOTE")
            all_notes = manager.get_all_notes()
            if not all_notes:
                print_info("No notes available to edit.")
                pause()
                continue
            _display_notes_list(all_notes)
            note_id = get_valid_int("Enter Note ID to edit")
            note = manager.get_note_by_id(note_id)
            if not note:
                print_error(f"Note with ID {note_id} not found.")
                pause()
                continue

            print()
            print_info(f"Editing Note #{note.id}: '{note.title}'")
            print_info("Leave blank and press Enter to keep current value.")
            new_title = get_non_empty_string(f"New title [{note.title}]", allow_empty=True)
            new_content = get_non_empty_string(f"New content [{note.content}]", allow_empty=True)

            title_to_set = new_title if new_title else note.title
            content_to_set = new_content if new_content else note.content

            if manager.edit_note(note_id, title_to_set, content_to_set):
                print_success(f"Note #{note_id} updated successfully!")
            else:
                print_warning("No changes were made to the note.")
            pause()

        elif choice == 6:
            print_sub_header("DELETE NOTE")
            all_notes = manager.get_all_notes()
            if not all_notes:
                print_info("No notes available to delete.")
                pause()
                continue
            _display_notes_list(all_notes)
            note_id = get_valid_int("Enter Note ID to delete")
            note = manager.get_note_by_id(note_id)
            if not note:
                print_error(f"Note with ID {note_id} not found.")
                pause()
                continue

            if confirm(f"Are you sure you want to delete Note #{note.id} ('{note.title}')?"):
                if manager.delete_note(note_id):
                    print_success(f"Note #{note_id} permanently deleted.")
                else:
                    print_error("Failed to delete note.")
            else:
                print_info("Deletion cancelled.")
            pause()

        elif choice == 7:
            print_sub_header("EXPORT NOTES")
            all_notes = manager.get_all_notes()
            if not all_notes:
                print_info("No notes available to export.")
                pause()
                continue

            print("Available Export Formats:")
            print("1. Text File (.txt)")
            print("2. JSON File (.json)")
            print("3. CSV Spreadsheet (.csv)")
            print("0. Cancel")
            fmt_choice = get_valid_int("Select format", min_val=0, max_val=3)

            fmt_map = {1: "txt", 2: "json", 3: "csv"}
            if fmt_choice in fmt_map:
                fmt = fmt_map[fmt_choice]
                out_path = manager.export_notes(fmt)
                if out_path:
                    print_success(f"Notes successfully exported to:\n  {out_path}")
                else:
                    print_error("Failed to export notes.")
            else:
                print_info("Export cancelled.")
            pause()
