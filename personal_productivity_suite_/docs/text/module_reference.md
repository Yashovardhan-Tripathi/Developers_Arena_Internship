# Personal Productivity Suite - Module Reference

Technical documentation of core modules, functions, classes, and architectural design.

---

## 1. `main.py`
The top-level application coordinator.

- `display_main_menu()`: Renders the primary numbered menu with branding header.
- `main()`: Contains the execution loop, input dispatching, and top-level exception handling (`KeyboardInterrupt`, `EOFError`).

---

## 2. `calculator.py`
Provides safe mathematical computation without arbitrary `eval()`.

### Functions
- `add(a, b)`, `subtract(a, b)`, `multiply(a, b)`: Elementary operations.
- `divide(a, b)`: Division with `ZeroDivisionError` prevention.
- `modulus(a, b)`: Modulo with `ZeroDivisionError` prevention.
- `power(a, b)`: Exponentiation with overflow limits and complex number guards.
- `evaluate_expression(expr: str)`: Safely parses mathematical expressions via `ast.parse(expr, mode='eval')` and validates against an allowed AST node whitelist.
- `run_calculator_tool()`: Interactive CLI session loop.

### Classes
- `CalculatorSession`: Tracks in-memory calculation history for the active session.

---

## 3. `notes_manager.py`
Provides persistent storage, CRUD, and multi-format exports for notes.

### Classes
- `Note`: Dataclass encapsulating `id`, `title`, `content`, `created_at`, `updated_at`.
- `NotesManager`:
  - `load_notes()`: Reads `data/notes.json` with recovery logic for missing or corrupted files.
  - `save_notes()`: Performs atomic disk writes using temporary files and `os.replace`.
  - `add_note(title, content) -> Note`: Creates and persists note with auto-increment ID.
  - `get_all_notes() -> List[Note]`: Retrieves all notes sorted by ID.
  - `get_note_by_id(note_id: int) -> Optional[Note]`: Finds note by ID.
  - `search_notes(query: str) -> List[Note]`: Case-insensitive search on title/content.
  - `edit_note(note_id, new_title, new_content) -> bool`: Updates note attributes and `updated_at`.
  - `delete_note(note_id: int) -> bool`: Deletes note by ID.
  - `export_notes(format_type: str, export_dir: Path) -> Path`: Exports to TXT, JSON, or CSV.

---

## 4. `timer.py`
Implements non-blocking, interruptible countdown timer and stopwatch.

### Functions
- `format_seconds(total_seconds: int) -> str`: Formats seconds into `MM:SS` or `HH:MM:SS`.
- `format_stopwatch_time(elapsed_seconds: float) -> str`: Formats seconds into `MM:SS.ss` with rounded hundredths.
- `render_progress_bar(current, total, width=30) -> str`: Generates text progress bar with percentage.
- `run_countdown(duration_seconds: int) -> bool`: Countdown loop with `\r` carriage return updates and `KeyboardInterrupt` trap.
- `run_timer_tool()`: CLI runner.

### Classes
- `Stopwatch`: State machine tracking `accumulated`, `start_time`, `is_running`, and `laps`.

---

## 5. `file_organizer.py`
Provides safe categorization of files in arbitrary folders.

### Functions
- `get_category_for_file(filepath: Path) -> str`: Looks up extension in `EXTENSION_CATEGORIES`.
- `get_unique_destination_path(dest_dir: Path, filename: str) -> Path`: Resolves name collisions using `_1`, `_2` suffixing.
- `scan_target_directory(directory_path: Path) -> List[Path]`: Discovers top-level non-hidden files.
- `organize_directory(target_path: Path, dry_run=False) -> OrganizationReport`: Moves files or simulates operations.
- `run_file_organizer_tool()`: Interactive CLI flow with previews and confirmations.

### Classes
- `OrganizationReport`: Dataclass summarizing `total_found`, `moved_count`, `category_summary`, `actions`, and `errors`.

---

## 6. `unit_converter.py`
Mathematical unit conversions across physical and digital domains.

### Functions
- `convert_length(value, from_unit, to_unit) -> float`: Length conversion via meters base.
- `convert_weight(value, from_unit, to_unit) -> float`: Mass conversion via kilograms base.
- `convert_time(value, from_unit, to_unit) -> float`: Time conversion via seconds base.
- `convert_digital(value, from_unit, to_unit) -> float`: Storage conversion via bytes base.
- `convert_temperature(value, from_unit, to_unit) -> float`: Converts Celsius, Fahrenheit, and Kelvin with absolute zero lower bound validation.
- `run_unit_converter_tool()`: Interactive CLI runner.

---

## 7. `backup_manager.py`
Application data protection and restore system.

### Functions
- `create_backup(source_path, backup_dir) -> Optional[Path]`: Timestamped backup copy.
- `list_backups(backup_dir) -> List[BackupInfo]`: Discovers and validates existing backups.
- `validate_backup_file(backup_path: Path) -> Tuple[bool, str, int]`: Validates JSON schema.
- `restore_backup(backup_path, target_path) -> bool`: Restores data with automated pre-restore backup.
- `delete_backup(backup_path: Path) -> bool`: Deletes selected backup.
- `run_backup_tool()`: CLI runner.

---

## 8. `utils.py`
Shared formatting, input validation, and platform abstractions.

- `clear_screen()`: Cross-platform terminal clear (`cls` on Windows, `clear` on POSIX).
- `print_header(title, subtitle)`: Styled banner output.
- `print_success(msg)`, `print_error(msg)`, `print_warning(msg)`, `print_info(msg)`: ANSI-styled messages.
- `get_valid_int(prompt, min_val, max_val, default)`: Validated integer reader.
- `get_valid_float(prompt, min_val, max_val, default)`: Validated float reader.
- `get_non_empty_string(prompt, allow_empty, default)`: Validated text reader.
- `confirm(prompt, default)`: Yes/no confirmation dialog.
- `pause(message)`: Halts execution until Enter is pressed.
- `get_project_root()`, `get_data_dir()`, `get_backups_dir()`, `get_exports_dir()`: Canonical directory getters.
