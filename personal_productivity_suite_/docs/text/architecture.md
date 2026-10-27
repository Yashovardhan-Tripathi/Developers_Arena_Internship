# Personal Productivity Suite - Architectural Design

This document details the architectural principles and design patterns applied in the project.

---

## 1. High-Level Architecture

The Personal Productivity Suite follows a modular, single-responsibility layered design:

```
[ main.py (Coordinator & Primary Menu) ]
    │
    ├── [ calculator.py ]      (Math Logic & AST Evaluator)
    ├── [ notes_manager.py ]   (Note CRUD & JSON Persistence)
    ├── [ timer.py ]           (Timer & Stopwatch State Machine)
    ├── [ file_organizer.py ]  (Extension Categorizer & Safe Mover)
    ├── [ unit_converter.py ]  (Physics Base-Unit Conversions)
    ├── [ backup_manager.py ]  (Timestamped Backups & Safe Restore)
    │
    └── [ utils.py ]           (Cross-Cutting Concerns: Input, ANSI, Paths)
```

---

## 2. Design Principles

### Single Responsibility Principle (SRP)
- `main.py` is strictly a coordinator: it displays menus and dispatches control. It contains zero business logic.
- Each core tool resides in its own isolated module (`calculator.py`, `notes_manager.py`, `timer.py`, etc.).
- `utils.py` contains shared utilities (screen clearing, safe input validation, path resolution) used by all tools.

### Safe File Persistence & Atomic Writes
When updating persistent data (`data/notes.json`), the application avoids writing directly to the target file. Instead:
1. Data is written to a temporary file in the same directory (`tempfile.NamedTemporaryFile`).
2. The operating system performs an atomic replace (`os.replace`) to swap the temporary file into place.
3. If a write fails or is interrupted midway, the original data file remains completely uncorrupted.

### Safe Mathematical Expression Parsing
Arbitrary user-provided math strings are **never** passed to Python's built-in `eval()`.
Instead, `calculator.py` uses `ast.parse(expr, mode='eval')` to construct an Abstract Syntax Tree:
- Only white-listed node types (`ast.Expression`, `ast.Constant`, `ast.BinOp`, `ast.UnaryOp`) are evaluated.
- Any attempt to call functions, reference variables, access attributes, or perform system calls raises an immediate `ValueError`.

### Defensive File Operations
`file_organizer.py` implements multiple safeguards:
- **Scope limitation**: Files outside the selected folder are never modified.
- **Top-level only**: Nested subdirectories are excluded to avoid breaking existing folder trees.
- **Dry run simulation**: Users can simulate and preview file moves prior to executing them.
- **Collision resolution**: Existing destination files are never overwritten; incrementing suffixes (`_1`, `_2`) are appended automatically.

### Cross-Platform Path Handling
All filesystem interactions utilize Python's `pathlib.Path`, guaranteeing smooth execution on Windows, macOS, and Linux without hardcoded slashes or OS-specific separators.
