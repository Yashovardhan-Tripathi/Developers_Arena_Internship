"""
Unit tests for the File Organizer module.
File: tests/test_file_organizer.py
"""

from pathlib import Path
import pytest
from file_organizer import (
    get_category_for_file,
    get_unique_destination_path,
    organize_directory,
    scan_target_directory,
)


class TestFileOrganizerLogic:
    """Test classification and path generation logic."""

    def test_extension_categorization(self):
        assert get_category_for_file(Path("photo.jpg")) == "images"
        assert get_category_for_file(Path("document.pdf")) == "documents"
        assert get_category_for_file(Path("script.py")) == "python"
        assert get_category_for_file(Path("notes.txt")) == "text"
        assert get_category_for_file(Path("data.csv")) == "spreadsheets"
        assert get_category_for_file(Path("archive.zip")) == "archives"
        assert get_category_for_file(Path("unknown_file.xyz123")) == "others"
        assert get_category_for_file(Path("no_extension_file")) == "others"

    def test_unique_destination_collision_handling(self, tmp_path: Path):
        dest_dir = tmp_path / "documents"
        dest_dir.mkdir()

        # Target does not exist yet
        target1 = get_unique_destination_path(dest_dir, "report.pdf")
        assert target1.name == "report.pdf"

        # Create the file
        (dest_dir / "report.pdf").touch()

        # Should generate collision-free name with _1
        target2 = get_unique_destination_path(dest_dir, "report.pdf")
        assert target2.name == "report_1.pdf"

        # Create report_1.pdf too
        (dest_dir / "report_1.pdf").touch()

        # Should generate _2
        target3 = get_unique_destination_path(dest_dir, "report.pdf")
        assert target3.name == "report_2.pdf"


class TestDirectoryOrganizationExecution:
    """Test scanning, dry runs, and actual file movements in temporary directory."""

    @pytest.fixture
    def populated_dir(self, tmp_path: Path) -> Path:
        """Create a directory with diverse sample files for organization."""
        work_dir = tmp_path / "sandbox"
        work_dir.mkdir()

        (work_dir / "invoice.pdf").write_text("dummy pdf")
        (work_dir / "avatar.png").write_text("dummy png")
        (work_dir / "notes.txt").write_text("dummy txt")
        (work_dir / "script.py").write_text("print('hi')")
        (work_dir / "metrics.csv").write_text("a,b,c")
        (work_dir / "random.xyz").write_text("unknown")
        # Hidden file (should be ignored)
        (work_dir / ".hidden_config").write_text("secret")
        # Existing directory (should be ignored)
        (work_dir / "subfolder").mkdir()

        return work_dir

    def test_scan_ignores_hidden_and_subdirectories(self, populated_dir: Path):
        scanned = scan_target_directory(populated_dir)
        names = [p.name for p in scanned]
        assert "invoice.pdf" in names
        assert "avatar.png" in names
        assert ".hidden_config" not in names
        assert "subfolder" not in names
        assert len(scanned) == 6

    def test_dry_run_does_not_modify_disk(self, populated_dir: Path):
        report = organize_directory(populated_dir, dry_run=True)
        assert report.total_found == 6
        assert report.moved_count == 6

        # Check that files are still in original root and no category folders created
        assert (populated_dir / "invoice.pdf").exists()
        assert not (populated_dir / "documents").exists()

    def test_actual_organization_moves_files(self, populated_dir: Path):
        report = organize_directory(populated_dir, dry_run=False)
        assert report.moved_count == 6

        # Check category folders exist and files were moved
        assert (populated_dir / "documents" / "invoice.pdf").exists()
        assert (populated_dir / "images" / "avatar.png").exists()
        assert (populated_dir / "text" / "notes.txt").exists()
        assert (populated_dir / "python" / "script.py").exists()
        assert (populated_dir / "spreadsheets" / "metrics.csv").exists()
        assert (populated_dir / "others" / "random.xyz").exists()

        # Original top-level files should have been moved
        assert not (populated_dir / "invoice.pdf").exists()
        # Hidden file remains intact
        assert (populated_dir / ".hidden_config").exists()
