# Personal Productivity Suite — Installation & Setup Guide

This document provides a comprehensive, step-by-step setup and installation guide for the **Personal Productivity Suite** command-line application. It is designed for new users, reviewers, and evaluators across Windows, macOS, and Linux platforms.

---

## Table of Contents
1. [System Prerequisites](#1-system-prerequisites)
2. [Cloning the Repository](#2-cloning-the-repository)
3. [Navigating to the Project Directory](#3-navigating-to-the-project-directory)
4. [Setting Up a Virtual Environment](#4-setting-up-a-virtual-environment)
5. [Installing Dependencies](#5-installing-dependencies)
6. [Starting the Application](#6-starting-the-application)
7. [Running the Automated Test Suite](#7-running-the-automated-test-suite)
8. [Common Installation Troubleshooting](#8-common-installation-troubleshooting)

---

## 1. System Prerequisites

Before installing the suite, ensure your machine satisfies the following minimum requirements:

| Component | Minimum Requirement | Recommended | Verification Command |
| :--- | :--- | :--- | :--- |
| **Python** | Python 3.10 | Python 3.11 – 3.13 | `python3 --version` or `python --version` |
| **Git** | Git 2.20+ | Latest Git | `git --version` |
| **Terminal** | ANSI-capable Shell | Terminal / PowerShell / iTerm2 | Standard system shell |
| **Disk Space** | 25 MB | 50 MB (including virtualenv) | N/A |

> [!NOTE]
> The core runtime suite uses **only** the Python Standard Library (`ast`, `json`, `csv`, `shutil`, `tempfile`, `pathlib`, `time`, `datetime`, `dataclasses`). No third-party packages are required to run the main application. Third-party packages (`pytest`) are solely used for automated testing.

---

## 2. Cloning the Repository

Open your terminal or command prompt and clone the repository using Git:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

*(Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL provided in your submission).*

If you received the project as a `.zip` or `.tar.gz` archive, extract it to a directory of your choice:

```bash
unzip personal_productivity_suite.zip
```

---

## 3. Navigating to the Project Directory

Enter the project root folder:

```bash
cd personal_productivity_suite
```

Verify that you are in the correct root directory by listing files:

**On macOS / Linux:**
```bash
ls -la
```

**On Windows:**
```cmd
dir
```

You should see `main.py`, `requirements.txt`, `README.md`, `tests/`, and `docs/`.

---

## 4. Setting Up a Virtual Environment

Creating an isolated virtual environment guarantees that development dependencies (such as `pytest`) do not conflict with system-level packages.

### On macOS / Linux

```bash
# 1. Create a virtual environment named 'venv'
python3 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate
```

When activated, your terminal prompt will be prefixed with `(venv)`.

### On Windows (Command Prompt or PowerShell)

**Command Prompt (`cmd.exe`):**
```cmd
:: 1. Create a virtual environment
python -m venv venv

:: 2. Activate the virtual environment
venv\Scripts\activate
```

**PowerShell (`pwsh`):**
```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

> [!IMPORTANT]
> If Windows PowerShell throws an `Execution_Policies` restriction error when activating the script, run PowerShell as Administrator and execute:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then retry activating the virtual environment.

---

## 5. Installing Dependencies

With the virtual environment active, install the testing and development dependencies:

```bash
pip install -r requirements.txt
```

### Understanding `requirements.txt`
The file contains:
```text
# Personal Productivity Suite
# Requirements Specification

# Core Application:
# Pure Python 3 standard library is utilized for the entire suite.
# No external third-party dependencies are required to run the main application.

# Testing & Development:
pytest>=7.4.0
```

Verify that `pytest` is installed correctly:
```bash
pytest --version
```

---

## 6. Starting the Application

Launch the central coordinator using Python:

**On macOS / Linux:**
```bash
python3 main.py
```

**On Windows:**
```cmd
python main.py
```

### Expected Startup Output
Upon successful launch, the terminal screen will clear and display the unified interactive header and main menu:

```text
==================================================
           PERSONAL PRODUCTIVITY SUITE            
    Integrated Terminal Tools for Developers      
==================================================

MAIN MENU:
  1. Calculator Tool
  2. Notes Manager
  3. Timer & Stopwatch
  4. File Organizer
  5. Unit Converter
  6. Backup & Restore
  7. Exit

Enter your choice (1-7): 
```

To test navigation, enter `1` to open the Calculator, then enter `0` to return to the Main Menu. Enter `7` to exit cleanly.

---

## 7. Running the Automated Test Suite

The project includes **63 comprehensive automated unit tests** verifying all business logic, boundary constraints, and error recovery behaviors.

### Run All Tests
```bash
pytest
```
or with verbose output:
```bash
pytest -v
```

### Expected Test Output
```text
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.5.0
rootdir: /Users/.../personal_productivity_suite
plugins: anyio-4.15.1
collected 63 items

tests/test_backup_manager.py .....                                       [  7%]
tests/test_calculator.py ................                                [ 33%]
tests/test_file_organizer.py .....                                       [ 41%]
tests/test_notes_manager.py ..........                                   [ 57%]
tests/test_timer.py .......                                              [ 68%]
tests/test_unit_converter.py ..................                          [ 96%]
tests/test_utils.py ..                                                   [100%]

============================== 63 passed in 0.23s ==============================
```

### Run Tests for an Individual Module
```bash
pytest tests/test_calculator.py -v
pytest tests/test_notes_manager.py -v
pytest tests/test_file_organizer.py -v
pytest tests/test_backup_manager.py -v
pytest tests/test_timer.py -v
pytest tests/test_unit_converter.py -v
pytest tests/test_utils.py -v
```

---

## 8. Common Installation Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `python3: command not found` or `'python' is not recognized` | Python is not installed or not added to system `PATH`. | Download and install Python from [python.org](https://www.python.org/). On Windows, check **"Add Python to PATH"** during setup. |
| `No module named venv` (Debian/Ubuntu) | The `python3-venv` system package is missing. | Run `sudo apt update && sudo apt install python3-venv`. |
| `Script execution disabled` (Windows PowerShell) | PowerShell execution policy blocks unsigned script execution. | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` in PowerShell. |
| `pip: command not found` | `pip` is not installed with Python. | Run `python3 -m ensurepip --upgrade`. |
| Terminal displays ANSI garbage characters (e.g., `\033[96m`) | Terminal emulator does not support ANSI escape codes. | Set the environment variable `export NO_COLOR=1` (or `$env:NO_COLOR="1"` in PowerShell) to disable terminal color formatting automatically. |
