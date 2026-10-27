# Personal Productivity Suite — Technical Module Documentation

This document provides in-depth technical documentation for every Python module in the **Personal Productivity Suite**. It details design choices, class structures, method signatures, inputs, outputs, operational logic, dependencies, and error-handling behavior.

---

## Architecture Overview

The system employs a strict single-responsibility layered architecture. Control flows top-down from `main.py` to specialized domain modules, supported by cross-cutting utility functions in `utils.py`:

```text
                           ┌─────────────┐
                           │   main.py   │  (Coordinator & Primary Menu)
                           └──────┬──────┘
                                  │
    ┌──────────────┬──────────────┼──────────────┬──────────────┬──────────────┐
    │              │              │              │              │              │
┌───▼────────┐ ┌───▼────────┐ ┌───▼────────┐ ┌───▼────────┐ ┌───▼────────┐ ┌───▼────────┐
│ calculator │ │   notes_   │ │   timer    │ │    file_   │ │   unit_    │ │   backup_  │
│    .py     │ │ manager.py │ │    .py     │ │organizer.py│ │converter.py│ │ manager.py │
└───┬────────┘ └───┬────────┘ └───┬────────┘ └───┬────────┘ └───┬────────┘ └───┬────────┘
    │              │              │              │              │              │
    └──────────────┴──────────────┼──────────────┴──────────────┴──────────────┘
                                  │
                           ┌──────▼──────┐
                           │  utils.py   │  (Shared Utilities & Validation)
                           └─────────────┘
```

---

## 1. `main.py` — Central Suite Coordinator

### Purpose
Serves as the main executable entry point. Coordinates CLI flow, renders the primary navigation menu, dispatches control to each specialized tool module, and catches top-level terminal exceptions.

### Key Functions
- `display_main_menu() -> None`: Clears the screen and prints the branded ASCII header and numbered menu options (1–7).
- `main() -> None`: Primary execution loop. Prompts the user with `get_valid_int("Enter your choice (1-7)", min_val=1, max_val=7)` and executes the selected module's entry function.

### Key Logic & Flow
1. Resolves `PROJECT_ROOT = Path(__file__).resolve().parent` and prepends it to `sys.path` so the application can be executed from any current working directory.
2. Runs inside an infinite `while True` loop until Option `7` is chosen or termination signals are caught.
3. Catches `KeyboardInterrupt` (`Ctrl+C`) and `EOFError` at the top level to cleanly exit with status code `0`, avoiding ugly tracebacks.
4. Wraps execution in a generic `except Exception as exc:` block to catch unexpected faults, display user-friendly error banners, and prompt before returning to the main menu.

### Dependencies
- Internal: `backup_manager`, `calculator`, `file_organizer`, `notes_manager`, `timer`, `unit_converter`, `utils`.
- Standard Library: `sys`, `pathlib.Path`.

---

## 2. `calculator.py` — Arithmetic & Safe Expression Evaluator

### Purpose
Provides basic arithmetic operations, session calculation history, and a secure mathematical expression evaluator based on Abstract Syntax Trees (AST), strictly eliminating vulnerabilities inherent to Python's built-in `eval()`.

### Key Functions & Classes

#### Elementary Arithmetic
- `add(a, b) -> Union[int, float]`: Returns $a + b$.
- `subtract(a, b) -> Union[int, float]`: Returns $a - b$.
- `multiply(a, b) -> Union[int, float]`: Returns $a \times b$.
- `divide(a, b) -> float`: Returns $a / b$. Raises `ZeroDivisionError` if $b = 0$.
- `modulus(a, b) -> Union[int, float]`: Returns $a \pmod b$. Raises `ZeroDivisionError` if $b = 0$.
- `power(a, b) -> Union[int, float]`: Returns $a^b$. Validates non-negative bases for fractional exponents to prevent complex numbers, limits exponents to $|b| \le 10,000$ to prevent CPU freeze, and catches `OverflowError`.

#### Safe Expression Evaluator
- `evaluate_expression(expr: str) -> Union[int, float]`:
  - **Input**: A math expression string, e.g., `"(12 + 4) * 5 / 2"`.
  - **Output**: The numeric result.
  - **Logic**: Parses the string into an AST using `ast.parse(expr, mode="eval")`. Recursively passes the AST to `_eval_ast_node()`.
  - **Security Whitelist**: Only allows `ast.Expression`, `ast.Constant`, `ast.BinOp`, and `ast.UnaryOp` nodes with safe operator mappings (`+`, `-`, `*`, `/`, `//`, `%`, `**`). Any node representing variable identifiers, function calls, attributes, or control loops raises an immediate `ValueError("Unsafe or unsupported expression syntax")`.
- `_format_result(val: Union[int, float]) -> str`: Trims trailing `.0` for whole numbers and formats floating-point values to clean precision.

#### `CalculatorSession` Class
- **Attributes**: `history: List[str]`
- **Methods**:
  - `record(entry: str) -> None`: Appends calculation string (e.g., `"5 * 4 = 20"`) to history.
  - `display_history() -> None`: Prints indexed calculation entries.
- `run_calculator_tool() -> None`: Primary interactive CLI loop offering operations 1–9 and back navigation.

### Error Handling
- Checks division and modulo by zero, raising explicit user-facing `ZeroDivisionError`.
- Validates syntax in AST parser, intercepting `SyntaxError` and wrapping it in `ValueError`.
- Handles numeric overflow safely.

---

## 3. `notes_manager.py` — Persistent Notes Management & Multi-Format Export

### Purpose
Implements full Create, Read, Update, Delete (CRUD) operations for notes with persistent JSON disk storage, atomic file-writing guarantees, and export capability to TXT, JSON, and CSV formats.

### Key Classes & Methods

#### `Note` Dataclass
Represents a structured user note.
- **Fields**:
  - `id: int`: Unique auto-incrementing integer identifier.
  - `title: str`: Header title of the note.
  - `content: str`: Body text.
  - `created_at: str`: ISO-formatted creation timestamp (`YYYY-MM-DD HH:MM:SS`).
  - `updated_at: str`: ISO-formatted last update timestamp.
- **Methods**:
  - `to_dict() -> Dict[str, Any]`: Serializes the instance to a dictionary.
  - `from_dict(data: Dict[str, Any]) -> Note`: Deserializes dictionary data back into a `Note` object.

#### `NotesManager` Class
- **Attributes**:
  - `storage_path: Path`: Absolute path to active storage (`data/notes.json`).
  - `notes: List[Note]`: In-memory list of active notes.
  - `_next_id: int`: Next sequential ID counter.
- **Methods**:
  - `load_notes() -> bool`: Reads and parses JSON data. If `data/notes.json` is missing, initializes cleanly. If the file is corrupted, automatically saves a copy to `data/notes.json.corrupt.bak` and re-initializes an empty list without crashing.
  - `save_notes() -> bool`: **Atomic Disk Write Pattern**. Serializes notes to JSON, writes into a temporary file (`tempfile.NamedTemporaryFile`) within `data/`, flushes, and invokes `os.replace` to atomically overwrite `notes.json`. This guarantees zero data corruption if an unexpected power loss or process kill occurs during write operations.
  - `add_note(title: str, content: str) -> Note`: Instantiates new note with incremented ID, appends to list, saves to disk, and returns the note.
  - `get_all_notes() -> List[Note]`: Returns all notes sorted by ID.
  - `get_note_by_id(note_id: int) -> Optional[Note]`: Performs $O(N)$ lookup by ID.
  - `search_notes(query: str) -> List[Note]`: Case-insensitive search across both `title` and `content`.
  - `edit_note(note_id: int, new_title: Optional[str], new_content: Optional[str]) -> bool`: Updates modified fields, updates `updated_at`, and triggers `save_notes()`.
  - `delete_note(note_id: int) -> bool`: Filters out the target note and persists changes.
  - `export_notes(format_type: str, export_dir: Optional[Path]) -> Optional[Path]`: Exports all active notes into `exports/notes_export_YYYYMMDD_HHMMSS.{ext}`. Supports `txt` (human-readable dossier), `json` (indented payload), and `csv` (spreadsheet format via `csv.writer`).

#### CLI Interface
- `run_notes_manager() -> None`: Interactive navigation displaying all CRUD actions and export options.

---

## 4. `timer.py` — Countdown Timer & Precision Stopwatch

### Purpose
Provides time management utilities: an animated countdown timer with terminal progress indicators and audio bell alerts, alongside an interruptible stopwatch supporting lap tracking.

### Key Functions & Classes

#### Helper Functions
- `format_seconds(total_seconds: int) -> str`: Converts integer seconds to `HH:MM:SS` or `MM:SS`.
- `format_stopwatch_time(elapsed_seconds: float) -> str`: Converts float seconds into hundredths-of-a-second representation (`MM:SS.ss` or `HH:MM:SS.ss`).
- `render_progress_bar(current: int, total: int, width: int = 30) -> str`: Generates a dynamic visual ASCII progress bar: `[==========--------------------]  33%`.
- `run_countdown(duration_seconds: int) -> bool`: Runs an iterative 1-second countdown loop. Emits `\r` carriage returns to dynamically redraw progress in-place on the current line. Upon completion, prints a success banner and emits an ASCII bell character (`\a`). Traps `KeyboardInterrupt` to cleanly pause without closing the application.

#### `Stopwatch` Class
- **Attributes**:
  - `accumulated: float`: Total elapsed time from previous paused intervals.
  - `start_time: Optional[float]`: Timestamp (`time.time()`) of current active run.
  - `is_running: bool`: Boolean execution status flag.
  - `laps: List[float]`: Sequential list of recorded elapsed timestamps.
- **Methods**:
  - `start() -> None`: Records start timestamp if not currently running.
  - `pause() -> float`: Accumulates delta between current time and start timestamp; sets `is_running = False`.
  - `reset() -> None`: Resets accumulated time to `0.0` and clears `laps`.
  - `get_elapsed() -> float`: Returns real-time accumulated + current delta duration.
  - `record_lap() -> float`: Appends current elapsed time to `self.laps`.

#### CLI Runners
- `run_countdown_interactive() -> None`: Prompts user for minutes/seconds or total seconds.
- `run_stopwatch_interactive() -> None`: Interactive loop with live hundredths-of-a-second counter, lap recording, pause/resume, and reset.
- `run_timer_tool() -> None`: Top-level sub-menu selector.

---

## 5. `file_organizer.py` — Extension-Based Directory Categorization

### Purpose
Scans any user-specified directory, categorizes regular top-level files by their file extensions, and sorts them into organized subdirectories. Includes dry-run simulation, sensitive root protections, and non-destructive collision renaming.

### Key Components

#### Category Mapping (`EXTENSION_CATEGORIES`)
A dictionary mapping over 45 standard file extensions to 9 logical category folders:
- `images`: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.ico`
- `documents`: `.pdf`, `.doc`, `.docx`, `.odt`, `.rtf`, `.epub`
- `text`: `.txt`, `.md`, `.log`
- `spreadsheets`: `.csv`, `.xlsx`, `.xls`, `.ods`
- `python`: `.py`, `.pyw`, `.ipynb`
- `code`: `.html`, `.css`, `.js`, `.ts`, `.json`, `.xml`, `.c`, `.cpp`, `.java`, `.rs`, `.go`, `.sql`, `.sh`
- `audio`: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`
- `video`: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`
- `archives`: `.zip`, `.tar`, `.gz`, `.bz2`, `.rar`, `.7z`
- `others`: Unrecognized or extensionless files.

#### `OrganizationReport` Dataclass
Encapsulates operation results:
- `total_found: int`: Number of candidate files detected.
- `moved_count: int`: Number of files moved (or simulated).
- `category_summary: Dict[str, int]`: Distribution of files per category folder.
- `actions: List[Tuple[str, str, str]]`: Records `(filename, category, new_path)`.
- `errors: List[Tuple[str, str]]`: Records file exceptions `(filename, reason)`.

#### Core Functions
- `get_category_for_file(filepath: Path) -> str`: Extracts `.suffix.lower()` and resolves against dictionary.
- `get_unique_destination_path(dest_dir: Path, original_filename: str) -> Path`: **Collision Resolution Guarantee**. If `report.pdf` exists in `documents/`, generates candidate `report_1.pdf`, `report_2.pdf`, etc. Guarantees no existing files are ever overwritten.
- `scan_target_directory(directory_path: Path) -> List[Path]`: Collects regular files (`p.is_file()`). **Excludes subdirectories and hidden files** (`p.name.startswith(".")`) to preserve directory trees and system configs.
- `organize_directory(target_path: Path, dry_run: bool = False) -> OrganizationReport`: Executes or simulates file moves using `shutil.move()`.
- `run_file_organizer_tool() -> None`: Interactive CLI providing directory path entry, sensitive path detection (`/`, `~`, `/bin`), dry-run preview, and explicit confirmation before execution.

---

## 6. `unit_converter.py` — Multi-Domain Unit Conversion Engine

### Purpose
Implements conversion across five physical and computational measurement domains with mathematical precision and boundary validation.

### Supported Domains & Logic
All conversions use an intermediate **Base Unit Normalization** architecture:
$$\text{Target Value} = \frac{\text{Input Value} \times \text{Source To Base Factor}}{\text{Target To Base Factor}}$$

1. **Length**: Base unit = Meters (`m`)
   - Units: meters, kilometers, centimeters, millimeters, miles, yards, feet, inches.
2. **Weight & Mass**: Base unit = Kilograms (`kg`)
   - Units: kilograms, grams, milligrams, metric tons, pounds, ounces.
3. **Time**: Base unit = Seconds (`s`)
   - Units: seconds, minutes, hours, days, weeks.
4. **Digital Storage**: Base unit = Bytes (`B`) (Binary $1024$ multiplier)
   - Units: bytes, kilobytes ($1024$), megabytes ($1024^2$), gigabytes ($1024^3$), terabytes ($1024^4$).
5. **Temperature**: Specialized two-step affine transformation
   - Units: Celsius, Fahrenheit, Kelvin.
   - Enforces physical domain lower boundary: **Absolute Zero** ($-273.15^\circ\text{C}$, $0\text{ K}$, $-459.67^\circ\text{F}$). Values below these raise `ValueError`.

### Functions
- `convert_length(value, from_unit, to_unit) -> float`
- `convert_weight(value, from_unit, to_unit) -> float`
- `convert_time(value, from_unit, to_unit) -> float`
- `convert_digital(value, from_unit, to_unit) -> float`
- `convert_temperature(value, from_unit, to_unit) -> float`
- `run_unit_converter_tool() -> None`: Interactive menu dispatching category sub-menus.

---

## 7. `backup_manager.py` — Backup, Integrity Verification & Safe Restore

### Purpose
Provides timestamped backups of `data/notes.json` into `data/backups/`, inspects backup integrity, and offers safe restoration protected by automatic pre-restore snapshots.

### Key Classes & Methods

#### `BackupInfo` Dataclass
- Fields: `path: Path`, `filename: str`, `created_at: str`, `size_bytes: int`, `note_count: int`, `is_valid: bool`, `status_msg: str`.

#### Core Functions
- `validate_backup_file(backup_path: Path) -> Tuple[bool, str, int]`: Validates that the backup is a readable, syntactically valid JSON list containing dictionaries with `"id"` and `"title"` keys.
- `create_backup(source_path, backup_dir) -> Optional[Path]`: Generates a timestamped filename `notes_backup_YYYY-MM-DD_HHMMSS.json`, copies using `shutil.copy2` (preserving metadata), and validates integrity immediately.
- `list_backups(backup_dir) -> List[BackupInfo]`: Scans `data/backups/*.json` and returns sorted metadata (newest first).
- `restore_backup(backup_path: Path, target_path: Optional[Path]) -> bool`:
  - Validates source backup schema.
  - Takes a safety snapshot of the active data file (`data/notes.json.pre_restore.bak`).
  - Writes to a temporary file and atomically replaces `data/notes.json`.
- `delete_backup(backup_path: Path) -> bool`: Permanently unlinks a selected backup file after confirmation.
- `run_backup_tool() -> None`: Interactive CLI for backup operations.

---

## 8. `utils.py` — Shared Utilities & Validation Foundation

### Purpose
Centralizes cross-cutting concerns: terminal ANSI formatting, screen clearing, directory resolution, and crash-proof input validation.

### Key Utilities
- `get_project_root()`, `get_data_dir()`, `get_backups_dir()`, `get_exports_dir() -> Path`: Resolves absolute filesystem paths and creates directories on demand (`mkdir(parents=True, exist_ok=True)`).
- `clear_screen() -> None`: Executes `cls` on Windows or `clear` on POSIX systems when running in an interactive TTY.
- `print_header(title, width, subtitle)`, `print_sub_header(title)`: Renders formatted banners.
- `print_success(msg)`, `print_error(msg)`, `print_warning(msg)`, `print_info(msg)`: ANSI color-coded console messages (auto-disabled if `NO_COLOR` is detected).
- `get_valid_int(prompt, min_val, max_val, default) -> int`: Safe integer reader that prevents program crashes from non-integer strings and enforces boundary ranges.
- `get_valid_float(prompt, min_val, max_val, default) -> float`: Safe float reader with range validation.
- `get_non_empty_string(prompt, allow_empty, default) -> str`: Validates non-blank user input.
- `confirm(prompt, default) -> bool`: Safe yes/no confirmation prompt.
- `pause(message) -> None`: Halts execution until the user presses Enter.
- `get_current_timestamp()`, `get_filename_timestamp() -> str`: Standardized string timestamp generators.

---

## 9. Test Suite Structure (`tests/`)

All 63 automated tests use standard `pytest` fixtures, specifically utilizing `tmp_path` to create isolated mock environments, ensuring zero modification to real project data during testing:

| Test File | Focus & Verifications | Count |
| :--- | :--- | :--- |
| `tests/test_calculator.py` | Basic math, divide-by-zero, exponent caps, AST expression evaluation, syntax errors, history session. | 16 |
| `tests/test_notes_manager.py` | Note dataclass, CRUD operations, atomic saving, corrupt JSON recovery, search, export to TXT/JSON/CSV. | 10 |
| `tests/test_timer.py` | Time formatting (`HH:MM:SS`, `MM:SS.ss`), progress bar rendering, Stopwatch start/pause/lap/reset state machine. | 7 |
| `tests/test_file_organizer.py` | File category detection, unique collision renaming (`file_1.txt`), scanning, dry-run simulation, execution. | 5 |
| `tests/test_unit_converter.py` | Length, weight, time, digital conversions, temperature conversions, Absolute Zero boundary assertions. | 18 |
| `tests/test_backup_manager.py` | Backup creation, validation of valid/malformed files, backup listing, restore with safety snapshot, deletion. | 5 |
| `tests/test_utils.py` | Project path resolution, timestamp formatting. | 2 |
| **Total Tests** | **All passing (`63 passed in 0.23s`)** | **63** |
