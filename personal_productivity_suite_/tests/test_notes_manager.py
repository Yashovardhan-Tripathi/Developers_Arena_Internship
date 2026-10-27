"""
Unit tests for the Notes Manager module.
File: tests/test_notes_manager.py
"""

import json
from pathlib import Path
import pytest
from notes_manager import NotesManager, Note


@pytest.fixture
def temp_notes_file(tmp_path: Path) -> Path:
    """Fixture providing a temporary notes JSON file path."""
    return tmp_path / "test_notes.json"


@pytest.fixture
def notes_manager(temp_notes_file: Path) -> NotesManager:
    """Fixture providing a clean NotesManager instance backed by temporary storage."""
    return NotesManager(storage_path=temp_notes_file)


class TestNotesManagerCRUD:
    """Test Create, Read, Update, Delete logic."""

    def test_add_note(self, notes_manager: NotesManager):
        note = notes_manager.add_note("Meeting Notes", "Discussed Q4 roadmap")
        assert note.id == 1
        assert note.title == "Meeting Notes"
        assert note.content == "Discussed Q4 roadmap"
        assert note.created_at != ""
        assert note.updated_at != ""

    def test_auto_increment_ids(self, notes_manager: NotesManager):
        n1 = notes_manager.add_note("First", "Body 1")
        n2 = notes_manager.add_note("Second", "Body 2")
        assert n1.id == 1
        assert n2.id == 2

    def test_get_all_notes(self, notes_manager: NotesManager):
        assert len(notes_manager.get_all_notes()) == 0
        notes_manager.add_note("A", "Alpha")
        notes_manager.add_note("B", "Beta")
        all_notes = notes_manager.get_all_notes()
        assert len(all_notes) == 2
        assert all_notes[0].title == "A"
        assert all_notes[1].title == "B"

    def test_get_note_by_id(self, notes_manager: NotesManager):
        created = notes_manager.add_note("Find Me", "Important text")
        found = notes_manager.get_note_by_id(created.id)
        assert found is not None
        assert found.title == "Find Me"
        assert notes_manager.get_note_by_id(999) is None

    def test_search_notes(self, notes_manager: NotesManager):
        notes_manager.add_note("Shopping List", "Buy milk, eggs, bread")
        notes_manager.add_note("Project Plan", "Architecture and database design")
        notes_manager.add_note("Books to Read", "Python CookBook and Clean Code")

        # Search matching title
        results_title = notes_manager.search_notes("Shopping")
        assert len(results_title) == 1
        assert results_title[0].id == 1

        # Search matching content (case insensitive)
        results_content = notes_manager.search_notes("CLEAN")
        assert len(results_content) == 1
        assert results_content[0].title == "Books to Read"

        # Search matching multiple
        results_multi = notes_manager.search_notes("and")
        assert len(results_multi) == 2

        # Empty search
        assert notes_manager.search_notes("") == []

    def test_edit_note(self, notes_manager: NotesManager):
        note = notes_manager.add_note("Original Title", "Original Content")
        assert notes_manager.edit_note(note.id, new_title="Updated Title")
        updated = notes_manager.get_note_by_id(note.id)
        assert updated.title == "Updated Title"
        assert updated.content == "Original Content"

        assert notes_manager.edit_note(note.id, new_content="New Body")
        updated2 = notes_manager.get_note_by_id(note.id)
        assert updated2.content == "New Body"

        # Non-existent note edit returns False
        assert not notes_manager.edit_note(999, new_title="Ghost")

    def test_delete_note(self, notes_manager: NotesManager):
        n1 = notes_manager.add_note("Keep", "Content")
        n2 = notes_manager.add_note("Delete Me", "Content")
        assert len(notes_manager.get_all_notes()) == 2

        assert notes_manager.delete_note(n2.id)
        assert len(notes_manager.get_all_notes()) == 1
        assert notes_manager.get_note_by_id(n2.id) is None
        assert not notes_manager.delete_note(999)


class TestNotesPersistence:
    """Test disk serialization, reload, and error recovery."""

    def test_persistence_between_instances(self, temp_notes_file: Path):
        mgr1 = NotesManager(storage_path=temp_notes_file)
        mgr1.add_note("Persistent", "Data survives restart")

        mgr2 = NotesManager(storage_path=temp_notes_file)
        assert len(mgr2.get_all_notes()) == 1
        assert mgr2.get_all_notes()[0].title == "Persistent"

        # Auto-increment continues properly
        n2 = mgr2.add_note("Second Note", "Another entry")
        assert n2.id == 2

    def test_corrupted_json_handling(self, temp_notes_file: Path):
        # Write corrupted JSON to file
        temp_notes_file.write_text("{invalid json: [", encoding="utf-8")

        mgr = NotesManager(storage_path=temp_notes_file)
        # Should gracefully initialize with 0 notes instead of crashing
        assert len(mgr.get_all_notes()) == 0

        # Can now save new notes normally
        new_note = mgr.add_note("Fresh Note", "System recovered safely")
        assert new_note.id == 1


class TestNotesExport:
    """Test exporting notes to JSON, CSV, and TXT."""

    def test_export_formats(self, notes_manager: NotesManager, tmp_path: Path):
        notes_manager.add_note("Note 1", "Body 1")
        notes_manager.add_note("Note 2", "Body 2")
        export_dir = tmp_path / "exports"

        # Export JSON
        json_path = notes_manager.export_notes("json", export_dir=export_dir)
        assert json_path is not None and json_path.exists()
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert len(data) == 2

        # Export CSV
        csv_path = notes_manager.export_notes("csv", export_dir=export_dir)
        assert csv_path is not None and csv_path.exists()
        csv_content = csv_path.read_text(encoding="utf-8")
        assert "Title" in csv_content
        assert "Note 1" in csv_content

        # Export TXT
        txt_path = notes_manager.export_notes("txt", export_dir=export_dir)
        assert txt_path is not None and txt_path.exists()
        txt_content = txt_path.read_text(encoding="utf-8")
        assert "PERSONAL PRODUCTIVITY SUITE - NOTES EXPORT" in txt_content
        assert "Note 1" in txt_content
