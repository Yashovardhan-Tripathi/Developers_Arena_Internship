# Personal Productivity Suite — Troubleshooting Guide

This guide provides troubleshooting solutions for common configuration, runtime, and data recovery issues encountered when installing and operating the **Personal Productivity Suite**.

---

## Quick Diagnostic Checklist

If you encounter any unexpected behavior, run through this 4-step diagnostic checklist:
1. **Verify Python Version**: `python3 --version` (Must be $\ge$ 3.10).
2. **Verify Environment**: Ensure `(venv)` is displayed in your terminal prompt.
3. **Verify Integrity with Tests**: Run `pytest` from the root directory. All 63 tests should pass.
4. **Check File Structure**: Verify that `data/` and `data/backups/` directories exist in the project root.

---

## 1. Installation & Environment Issues

### Issue 1.1: `python3: command not found` or `'python' is not recognized`
- **Symptom**: Attempting to run `python3 main.py` results in a command-not-found error.
- **Cause**: Python is not installed or its executable is not added to your system's `PATH` environment variable.
- **Resolution**:
  - **macOS**: Install Python via Homebrew (`brew install python`) or download from [python.org](https://www.python.org/).
  - **Linux**: Install via package manager: `sudo apt update && sudo apt install python3 python3-pip python3-venv`.
  - **Windows**: Download the official Windows installer from python.org. **Crucial:** Ensure the checkbox **"Add Python to PATH"** is selected on the first installer screen.

### Issue 1.2: Wrong Python Version (< 3.10)
- **Symptom**: Syntax errors or `ImportError: cannot import name 'dataclass'` or type union syntax errors.
- **Cause**: Running on an outdated Python version (such as Python 3.8 or 2.7).
- **Resolution**: Upgrade to Python 3.10 or newer. Check which version is active with `python3 -V`.

### Issue 1.3: Virtual Environment Not Activated
- **Symptom**: `pytest: command not found` when attempting to run automated tests.
- **Cause**: Packages were installed into the virtual environment, but the environment is not active in the current shell session.
- **Resolution**:
  - macOS/Linux: `source venv/bin/activate`
  - Windows Command Prompt: `venv\Scripts\activate`
  - Windows PowerShell: `.\venv\Scripts\Activate.ps1`

### Issue 1.4: PowerShell Blocks Script Execution
- **Symptom**: `File ... Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
- **Cause**: Default Windows PowerShell ExecutionPolicy blocks script execution.
- **Resolution**: Open PowerShell and run:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
  Then reactivate: `.\venv\Scripts\Activate.ps1`.

### Issue 1.5: Dependency Installation Failure (`pip install -r requirements.txt`)
- **Symptom**: `pip install` fails with network timeouts or wheel compile errors.
- **Cause**: Outdated `pip` version or network proxy restriction.
- **Resolution**:
  1. Upgrade pip: `python3 -m pip install --upgrade pip`
  2. Note that the core suite requires **no** external dependencies to run. `requirements.txt` only specifies `pytest>=7.4.0` for running automated tests.

---

## 2. Application Startup & Runtime Issues

### Issue 2.1: Application Fails to Start (`ModuleNotFoundError`)
- **Symptom**: `ModuleNotFoundError: No module named 'utils'` when launching `main.py`.
- **Cause**: Launching from an unconventional path where Python does not recognize the root directory.
- **Resolution**: Ensure you are in the project root directory where `main.py` is located (`cd personal_productivity_suite`). `main.py` automatically sets `sys.path` to the script's directory, ensuring reliable module imports.

### Issue 2.2: Terminal Shows Garbled ANSI Color Codes
- **Symptom**: Text includes literal escape codes such as `\033[96m[INFO]\033[0m`.
- **Cause**: Running in a legacy terminal emulator that does not interpret ANSI escape sequences.
- **Resolution**:
  - The application automatically disables ANSI color codes if `NO_COLOR` is defined in the environment.
  - Run the application with:
    ```bash
    NO_COLOR=1 python3 main.py
    ```

### Issue 2.3: `KeyboardInterrupt` Unhandled Crash
- **Symptom**: Hitting `Ctrl+C` exits the program with a messy stack trace.
- **Resolution**: In the Personal Productivity Suite, `KeyboardInterrupt` is trapped at both module and coordinator levels. At the main menu, `Ctrl+C` triggers an orderly, clean exit. In tools like the Timer, `Ctrl+C` pauses the timer without closing the suite.

---

## 3. Notes Storage & Data Recovery

### Issue 3.1: Active Notes Disappeared (`data/notes.json` Missing or Empty)
- **Symptom**: Opening Notes Manager displays `0` notes.
- **Cause**: File was accidentally deleted or replaced.
- **Resolution**:
  1. The application automatically recreates a clean `data/notes.json` if missing.
  2. If you had saved backups, navigate to **Main Menu -> 6. Backup & Restore -> 3. Restore From Backup**. Select your latest backup to restore all notes.
  3. Pre-populated sample data is also available in `examples/sample_notes.json`. You can restore it with:
     ```bash
     cp examples/sample_notes.json data/notes.json
     ```

### Issue 3.2: Corrupted JSON Error Banner
- **Symptom**: On startup or opening Notes Manager, you see:
  `[ERROR] Corrupted notes file detected. Saved backup to 'notes.json.corrupt.bak'.`
- **Cause**: Manual edits to `data/notes.json` introduced invalid JSON syntax (e.g., missing commas, unclosed brackets).
- **Resolution**:
  - The suite safeguards corrupted files by copying them to `data/notes.json.corrupt.bak` before re-initializing.
  - Open `data/notes.json.corrupt.bak` in any code editor, fix syntax errors, and rename it back to `notes.json`.

---

## 4. File Organizer Issues

### Issue 4.1: "Path does not exist" or "Path is not a directory"
- **Symptom**: File organizer displays error when entering a folder path.
- **Cause**: Misspelled directory name or invalid relative path.
- **Resolution**:
  - Use absolute paths (e.g., `/Users/name/Downloads` or `C:\Users\name\Downloads`).
  - Home directory tilde expansion (`~/Downloads`) is automatically resolved.

### Issue 4.2: Files Inside Subfolders Were Not Moved
- **Symptom**: Organization completed, but files inside subfolders were not categorized.
- **Cause**: By intentional design, the File Organizer only organizes **top-level files** in the selected directory.
- **Rationale**: Recursively organizing existing subdirectories could destroy project folder structures (e.g., source code trees). To organize a specific subdirectory, provide that directory's path directly.

### Issue 4.3: Permission Denied (`PermissionError`)
- **Symptom**: `[WARNING] 1 issue(s) encountered: ! filename: [Errno 13] Permission denied`.
- **Cause**: The current operating system user does not have write or move permissions for the target file or folder.
- **Resolution**: Check folder permissions (`ls -ld <folder>` on Unix) or run the terminal with appropriate read/write privileges.

---

## 5. Automated Tests Failing

### Issue 5.1: `pytest` Fails When Executed
- **Symptom**: One or more of the 63 tests reports `FAILED`.
- **Diagnosis**: Run `pytest -v` to identify the failing test name and failure assertion.
- **Common Causes**:
  - Modifying base constants (e.g., altering `LENGTH_TO_BASE` factors).
  - Outdated cached bytecode: clear Python bytecode by running:
    ```bash
    find . -type d -name "__pycache__" -exec rm -rf {} +
    pytest -v
    ```
