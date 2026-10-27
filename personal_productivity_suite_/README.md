# Complete Personal Productivity Suite

A menu-driven Python application combining a calculator, persistent notes manager, timer and stopwatch, file organizer, unit converter, and local notes backup/restore. Built for the Developers Arena internship brief to demonstrate reusable modules, object-oriented design, file operations, and input validation.

The implementation covers the company's **Standard Version** tools, plus exports and local backup/restore. Data analysis, cloud synchronization, and user-configurable settings remain future work.

## Setup and installation

Use Python 3.10+ as the documented baseline and a terminal with write access to the application directory. The runtime uses only Python's standard library. Cross-platform terminal handling exists in the source; this documentation review does not establish testing on every operating system or Python version.

From the outer internship repository:

```powershell
cd personal_productivity_suite_
python main.py
```

To obtain that repository first:

```powershell
git clone https://github.com/Yashovardhan-Tripathi/Developers_Arena_Internship.git
cd Developers_Arena_Internship/personal_productivity_suite_
python main.py
```

The current directory name ends in `_`. The application files are tracked directly in the outer internship repository and are included in a normal clone. See the [outer README's structure assessment](../README.md#structure-assessment-against-the-company-brief) for the submission layout. In an application-only checkout, launch from the directory containing `main.py`.

Optional virtual environment and test dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS/Linux, use `python3` where needed and `source .venv/bin/activate`. In Windows Command Prompt, activate with `.venv\Scripts\activate.bat`. If PowerShell blocks activation, use `.venv\Scripts\python.exe` directly. `requirements.txt` contains `pytest>=7.4.0`, needed for testing only.

## Tools and user guide

```text
MAIN MENU:
  1. Calculator Tool
  2. Notes Manager
  3. Timer & Stopwatch
  4. File Organizer
  5. Unit Converter
  6. Backup & Restore
  7. Exit
```

Enter the displayed option number and follow the prompts. Tool menus use `0` to go back; this applies to menu prompts, not every text or numeric input. At the main menu, `7`, Ctrl+C, or end-of-input exits.

| Tool | Implemented behavior | Example workflow |
| --- | --- | --- |
| Calculator | Arithmetic, power, AST expressions, view/clear history | Main `1`, calculator `7`, enter `(15 + 5) * 3 / 2`; its mathematical result is `30`. Expressions use `**` for power; `^` is only the dedicated power option's display symbol. |
| Notes | View, add, search title/content, details, edit/delete, export | Main `2`, notes `2`, enter title and one line of content. Notes `7` exports TXT/JSON/CSV. Blank edit fields retain existing values. |
| Timer and stopwatch | Countdown progress and terminal bell; stopwatch start/pause/resume/reset and cumulative lap timestamps | Main `3`, then `1` for countdown or `2` for stopwatch. Ctrl+C interrupts countdown or pauses a running stopwatch. |
| File organizer | Extension categories, dry run, move report, numbered suffixes for collisions | Main `4`, organizer `2`, enter `./examples/sample_files` for a dry run. Option `1` previews then asks to move files. |
| Unit converter | Length, mass, temperature, time, digital storage | Main `5`, category `1`, select kilometers then miles and enter `5`. Storage uses 1024-based factors. |
| Backup and restore | Create, list, validate, restore, delete notes backups | Main `6`, `1` creates a backup, `2` lists, `3` restores after confirmation. |

The organizer processes immediate files, skips dot-prefixed names and subdirectories, and puts unknown extensions in `others/`. Real organization moves files. At the move confirmation, blank input accepts the default **Yes**; use the dry-run option first.

A running stopwatch responds to **Ctrl+C** to pause. Its Enter-to-pause message is not backed by an input check in that loop. A cancelled countdown returns without a resume operation. Bell sound depends on terminal settings.

## Data, exports, and recovery

Storage paths are relative to the application's source directory, rather than the shell's current directory:

| Location | Purpose |
| --- | --- |
| `data/notes.json` | Active notes persisted as a JSON list |
| `data/backups/notes_backup_YYYY-MM-DD_HHMMSS.json` | Manually created notes backups |
| `exports/notes_export_YYYYMMDD_HHMMSS.txt`, `.json`, `.csv` | Notes exports; directory created when needed |
| `data/notes.corrupt.bak` | Copy attempted for certain malformed-note errors |
| `data/notes.pre_restore.bak` | Snapshot of existing notes before restore |

Each note has `id`, `title`, `content`, `created_at`, and `updated_at`. Notes use a list of `Note` dataclasses; search uses case-insensitive substring matching. On load, the next ID is one greater than the highest stored ID. Calculator history lasts until leaving the calculator session, and stopwatch state remains in memory.

Notes saves and restores write a temporary file in the destination directory, then replace the target with `os.replace`. Backups copy the notes file and check basic JSON list structure and `id`/`title` keys; they do not enforce a complete field-type schema. Backup creation is manual and covers notes only, not organized files or the entire project.

Data is local plain text without encryption or cloud sync. Backup and export timestamps have second resolution, so repeated operations within a second can reuse a name. A failed save can print an error while the CRUD caller still reports an in-memory success; check error messages and storage permissions before relying on persistence. Recovery from every malformed input or filesystem failure is not guaranteed.

## Architecture and actual layout

`main.py` dispatches to tool CLI runners. Tool modules expose reusable functions and state classes; `utils.py` shares prompts, display helpers, paths, and timestamps. The calculator recursively interprets allowed numeric AST nodes without `eval()`. Conversions use base-unit factors and temperature formulas, with lower-bound checks. The organizer uses an extension dictionary and `shutil.move`.

```text
personal_productivity_suite_/
|-- main.py                  # Menu and tool dispatch
|-- calculator.py            # Arithmetic, AST evaluator, CalculatorSession
|-- notes_manager.py         # Note, NotesManager, exports
|-- timer.py                 # Countdown and Stopwatch
|-- file_organizer.py        # Classification and OrganizationReport
|-- unit_converter.py        # Conversion tables and functions
|-- backup_manager.py        # BackupInfo, backup/restore and validation
|-- utils.py                 # Prompts, display, paths
|-- requirements.txt         # pytest, testing only
|-- README.md
|-- .gitignore
|-- data/
|   |-- notes.json
|   `-- backups/
|-- docs/
|   |-- text/
|   |   |-- installation_guide.md
|   |   |-- user_guide.md
|   |   |-- architecture.md
|   |   |-- module_documentation.md
|   |   |-- module_reference.md
|   |   |-- technical_requirements.md
|   |   `-- troubleshooting.md
|   `-- screenshots/         # Nine PNGs and README.md
|-- tests/
|   |-- __init__.py
|   |-- test_calculator.py
|   |-- test_notes_manager.py
|   |-- test_timer.py
|   |-- test_file_organizer.py
|   |-- test_unit_converter.py
|   |-- test_backup_manager.py
|   `-- test_utils.py
`-- examples/
    |-- sample_notes.json
    |-- organizer_demo.py
    `-- sample_files/
```

`exports/` appears at runtime. Caches and local Git metadata are omitted above. The flat modules suit this small CLI and match the brief's initial example, but its final checklist requests `modules/`. The application is also nested inside the internship repository with its own Git repository. See the [outer README](../README.md) for the assessment. No restructuring was performed.

## Company requirements mapping

| Requirement / deliverable | Implementation / evidence | Qualification |
| --- | --- | --- |
| Calculator, notes, timer | Corresponding modules and `main.py` menu | Core tools present in source |
| File organizer, unit conversion | `file_organizer.py`, `unit_converter.py` | Standard Version tools present |
| Reusable modules and OOP | Tool files, `NotesManager`, `CalculatorSession`, `Stopwatch`, dataclasses | Individual modules, no `modules/` package |
| JSON, CSV, TXT operations | JSON persistence and three-format exports | No CSV/TXT import feature |
| Menu and input/error handling | Shared validators and tool-specific checks | Common cases handled; exhaustive resilience is not established |
| Persistence and backup/restore | Notes JSON, local backups, pre-restore snapshot | Notes persist; history/timers do not |
| Documentation and screenshots | READMEs, `docs/text/`, nine existing PNG files | No dedicated invalid-input screenshot |
| Sample data and examples | Sample notes, sample files, organizer demo | Media/archive sample files are text placeholders for categorization, not usable PDF/PNG/ZIP assets |
| Unit tests | Seven test modules, 63 test functions | Source inventory, not a current pass claim |
| Advanced analysis, customization, cloud sync | Not implemented | Exports alone do not complete the Advanced Version |
| GitHub submission structure | Entry point, dependencies, data, docs, tests, examples | Root placement, `modules/`, nested Git need a submission decision |

The company's six-week guide describes a suggested workflow; it does not establish completed weekly milestones or dates.

## Screenshots

Nine PNG files are present. The [screenshot gallery](docs/screenshots/README.md) includes calculator, notes, countdown, stopwatch, organizer, converter, backup manager, and exit views.

![Main application menu](docs/screenshots/main%20menu.png)

These are existing assets, not a newly executed acceptance test. A dedicated error-handling image remains a submission improvement.

## Tests and examples

From the folder containing `main.py`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -v
python -m pytest tests/test_calculator.py -v
```

Source inspection found **63 test functions** across seven test files. Tests were not run during this README-only review, so no pass count, execution time, coverage percentage, or Python-version verification is asserted.

Tests cover arithmetic and expression rejection, notes CRUD/search/persistence/exports, timer formatting and stopwatch state, organizer dry runs and collisions, conversion boundaries, backup validation/restore, and utility paths. File-operation tests mostly use temporary directories; `test_utils.py` calls real path helpers and can create runtime directories such as `exports/`.

The existing example runs with:

```powershell
python examples/organizer_demo.py
```

It demonstrates dry-run categorization but creates missing sample files before previewing. `examples/sample_notes.json` is reference data, not an automatic import; the CLI has no notes-import command.

## Troubleshooting

| Issue | Action |
| --- | --- |
| `main.py` or `requirements.txt` not found | Enter `personal_productivity_suite_` from the outer repository. |
| Python command unavailable | Check installation and PATH; try `python3` or Windows `py`. |
| `No module named pytest` | Install requirements with the interpreter used for `python -m pytest`. |
| Notes fail to save | Check errors, permissions, and disk space. An in-memory success does not prove the write succeeded. |
| Malformed notes detected | Preserve the original and any `notes.corrupt.bak`; restore a known-good backup through main `6`. |
| Stopwatch ignores Enter | Use Ctrl+C while running. |
| Organizer skips nested files | Only immediate files are processed; dot-prefixed names are skipped. |
| Unreadable colors | PowerShell: `$env:NO_COLOR = '1'`; macOS/Linux: `NO_COLOR=1 python3 main.py`. |

## Additional documentation

- [Installation guide](docs/text/installation_guide.md)
- [User guide](docs/text/user_guide.md)
- [Architecture](docs/text/architecture.md)
- [Detailed module documentation](docs/text/module_documentation.md)
- [Module reference](docs/text/module_reference.md)
- [Technical requirements](docs/text/technical_requirements.md)
- [Troubleshooting guide](docs/text/troubleshooting.md)
- [Screenshot gallery](docs/screenshots/README.md)

Non-README guides were left unchanged as requested. Some retain older paths, control descriptions, or test-result statements; this README records the current source inspection and does not certify those historical claims.

## Remaining submission considerations

- Decide how to align root placement and `modules/` with the final checklist, including nested Git metadata.
- Capture invalid-input evidence and collect an actual test-run result.
- Add data analysis, configurable settings, or cloud sync only if pursuing the Advanced Version.
- No license file is present in this workspace; this README does not assert an MIT license grant.
