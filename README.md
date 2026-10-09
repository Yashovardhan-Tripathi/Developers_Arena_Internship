# Developers Arena Internship

This repository contains the **Complete Personal Productivity Suite**, based on the company's internship brief. The Python command-line application combines everyday tools while demonstrating modular programming, object-oriented design, file handling, input validation, and persistence.

## Project and launch

The application is in [`personal_productivity_suite_/`](personal_productivity_suite_/). The trailing underscore is part of the folder name.

```powershell
git clone https://github.com/Yashovardhan-Tripathi/Developers_Arena_Internship.git
cd Developers_Arena_Internship/personal_productivity_suite_
python main.py
```

For an existing checkout, enter `personal_productivity_suite_` from the repository root and run `python main.py`. Use Python 3.10+ as the documented baseline; substitute `python3` where required. The application uses only the standard library.

| Menu | Tool |
| --- | --- |
| 1 | Calculator: arithmetic, expressions, temporary history |
| 2 | Notes: JSON persistence, search, edit/delete, TXT/JSON/CSV exports |
| 3 | Countdown timer and stopwatch with laps |
| 4 | File organizer with previews and extension-based categories |
| 5 | Length, mass, temperature, time, and digital storage conversions |
| 6 | Local notes backup and restore |
| 7 | Exit |

The implementation covers the **Standard Version** tools, plus exports and local backup/restore. Advanced data analysis, customization settings, and cloud sync are not implemented.

For optional test setup, run these commands from the application folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

On macOS/Linux, activate with `source .venv/bin/activate`. The dependency file contains `pytest>=7.4.0` for testing only. See the [application README](personal_productivity_suite_/README.md) for usage and troubleshooting.

## Current folder structure

```text
Developers_Arena_Internship/
|-- README.md
|-- .gitattributes
`-- personal_productivity_suite_/
    |-- README.md
    |-- main.py
    |-- calculator.py
    |-- notes_manager.py
    |-- timer.py
    |-- file_organizer.py
    |-- unit_converter.py
    |-- backup_manager.py
    |-- utils.py
    |-- requirements.txt
    |-- .gitignore
    |-- data/
    |   |-- notes.json
    |   `-- backups/
    |-- docs/
    |   |-- text/          # Installation, user, architecture, module guides
    |   `-- screenshots/   # Nine PNGs and a README
    |-- tests/            # Seven test modules
    `-- examples/         # Sample notes, files, and organizer demo
```

`exports/` is created when needed. Python and pytest caches are generated files, excluded by the application's `.gitignore`.

## Structure assessment against the company brief

The layout is understandable for a small CLI, but does **not exactly match the final submission checklist**:

- The company places `main.py`, `requirements.txt`, `modules/`, `data/`, `docs/`, `tests/`, and `examples/` at the submission root. Here the application is one level below the internship repository root.
- Tools are individual modules beside `main.py`; there is no `modules/` package. This matches the brief's earlier flat example, but differs from its final GitHub checklist.
- The local application directory has its own `.git` repository inside the outer repository. Decide whether to submit one repository or configure an explicit submodule. Nested Git metadata alone does not ensure that the outer repository publishes the application files.
- `docs/text/` is a valid grouping; documentation links must include it. Screenshot filenames have spaces and inconsistent spelling/capitalization; the READMEs use the existing names.

No folders, Git configuration, code, or sample data were reorganized during this README update. Any restructuring requires the owner's instruction.

## Documentation and evidence

- [Application setup, usage, architecture, and requirement mapping](personal_productivity_suite_/README.md)
- [Screenshot gallery](personal_productivity_suite_/docs/screenshots/README.md)
- [User guide](personal_productivity_suite_/docs/text/user_guide.md)
- [Architecture](personal_productivity_suite_/docs/text/architecture.md)
- [Tests](personal_productivity_suite_/tests/)
- [Examples](personal_productivity_suite_/examples/)

The source contains 63 test functions. Tests were not executed during this README-only review, so no current pass count or runtime is claimed. Non-README guides were left unchanged and may retain older paths or test-result statements; use the README commands and an actual test run for current evidence.
