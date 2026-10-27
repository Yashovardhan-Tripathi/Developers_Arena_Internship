# Personal Productivity Suite — Complete User Manual

Welcome to the **Personal Productivity Suite** user manual. This guide covers how to operate the application from start to finish, explaining every screen, required inputs, operational behavior, expected outputs, and common mistakes to avoid.

---

## Table of Contents
1. [Starting the Application](#1-starting-the-application)
2. [Navigating the Main Menu](#2-navigating-the-main-menu)
3. [Tool 1: Calculator Tool](#3-tool-1-calculator-tool)
4. [Tool 2: Notes Manager](#4-tool-2-notes-manager)
5. [Tool 3: Timer & Stopwatch](#5-tool-3-timer--stopwatch)
6. [Tool 4: File Organizer](#6-tool-4-file-organizer)
7. [Tool 5: Unit Converter](#7-tool-5-unit-converter)
8. [Tool 6: Backup & Restore](#8-tool-6-backup--restore)
9. [Exiting the Application](#9-exiting-the-application)

---

## 1. Starting the Application

### How to Launch
Open your terminal, navigate to the project directory, and run:

```bash
python3 main.py
```
*(On Windows: `python main.py`)*

### What Happens on Startup
1. The suite verifies and prepends the project directory to Python's system path.
2. Initializes underlying directories (`data/`, `data/backups/`, `exports/`).
3. Clears the terminal screen and displays the main menu header banner.

---

## 2. Navigating the Main Menu

### Menu Display
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

### General Navigation Rules
- **Selecting a Tool**: Enter a single digit between `1` and `7` and press **Enter**.
- **Returning to Main Menu**: Inside any tool or sub-menu, enter `0` to return to the parent menu.
- **Input Validation**: Entering letters, symbols, or out-of-range numbers will display an error message (e.g., `[ERROR] Value must be at least 1.`) and safely re-prompt you without crashing.
- **Keyboard Interrupt**: Pressing `Ctrl+C` at the main menu exits cleanly with a goodbye message.

---

## 3. Tool 1: Calculator Tool

### How to Access
Enter `1` at the Main Menu.

### Calculator Sub-Menu
```text
==================================================
                 CALCULATOR TOOL                  
      Basic Math & Safe Expression Evaluator      
==================================================

1. Addition (+)
2. Subtraction (-)
3. Multiplication (*)
4. Division (/)
5. Modulus (%)
6. Power / Exponentiation (^)
7. Evaluate Full Expression (e.g., (10 + 5) * 2)
8. View Calculation History
9. Clear History
0. Back to Main Menu

Select an option: 
```

### Operational Modes

#### A. Standard Arithmetic (Options 1–6)
1. **How to Access**: Select option `1` (Add), `2` (Subtract), `3` (Multiply), `4` (Divide), `5` (Modulus), or `6` (Power).
2. **Input Required**:
   - `Enter first number`: Any valid whole or decimal number (e.g., `25` or `3.14`).
   - `Enter second number`: Any valid whole or decimal number.
3. **What Happens**: The module executes the corresponding operation and records the transaction into the session history log.
4. **Output Received**:
   ```text
   [SUCCESS] Result: 25 + 15 = 40
   ```
5. **Common Mistakes**:
   - Entering `0` as the second number for Division or Modulus triggers `[ERROR] Math Error: Cannot divide by zero.`
   - Entering extreme exponents (over 10,000) for Power triggers `[ERROR] Exponent is too large.`

#### B. Safe Expression Evaluator (Option 7)
1. **How to Access**: Select option `7`.
2. **Input Required**: A mathematical expression string, such as `(12 + 8) * 3 / 2` or `100 - 25 * 2`.
3. **What Happens**: Uses Python's Abstract Syntax Tree (`ast`) to safely evaluate the math string without using dangerous `eval()`.
4. **Output Received**:
   ```text
   [SUCCESS] Result: 30
   ```
5. **Common Mistakes**:
   - Typing variable names or function names like `sin(30)` or `x + 5` triggers `[ERROR] Calculation failed: Unsafe or unsupported expression syntax`.
   - Unbalanced parentheses trigger a syntax error message with prompt to retry.

#### C. Session Calculation History (Options 8 & 9)
1. **Option 8 (View History)**: Displays all calculations performed during the current session with chronological index numbers.
2. **Option 9 (Clear History)**: Clears the in-memory history list and confirms with `[SUCCESS] Calculation history cleared.`

---

## 4. Tool 2: Notes Manager

### How to Access
Enter `2` at the Main Menu.

### Notes Manager Sub-Menu
```text
==================================================
                  NOTES MANAGER                   
           Persistent Note Organization           
==================================================

1. View All Notes
2. Add New Note
3. Search Notes
4. View Note Details
5. Edit Note
6. Delete Note
7. Export Notes
0. Back to Main Menu

Select an option: 
```

### Features

#### 1. View All Notes
- **Input**: None.
- **Output**: Formatted summary table displaying Note ID, Title, Creation Timestamp, and Content Preview.
- **Common Mistakes**: Viewing when no notes exist displays `[INFO] No notes found.`

#### 2. Add New Note
- **Input Required**:
  - `Enter note title`: Note headline (cannot be empty).
  - `Enter note content`: Body text (cannot be empty).
- **What Happens**: Assigns the next sequential integer ID, stamps creation and update times, and atomically writes to `data/notes.json`.
- **Output Received**:
  ```text
  [SUCCESS] Note added successfully!
   Note ID: 1
   Created: 2026-10-08 12:15:30
  ```

#### 3. Search Notes
- **Input Required**: Search keyword (case-insensitive).
- **What Happens**: Filters all notes where the keyword appears in either the title or body.
- **Output Received**: Shows matching notes table and count: `[INFO] Found 2 note(s) matching 'meeting':`.

#### 4. View Note Details
- **Input Required**: Note ID (e.g., `1`).
- **Output Received**: Displays the complete full-text note with creation time and last modified time.

#### 5. Edit Note
- **Input Required**:
  - Note ID to edit.
  - `New title`: Press Enter to keep existing title or type new text.
  - `New content`: Press Enter to keep existing body or type new text.
- **Output**: `[SUCCESS] Note #1 updated successfully!`

#### 6. Delete Note
- **Input Required**: Note ID to delete, followed by `[y/N]` confirmation.
- **Output**: If confirmed with `y`, permanently deletes the note from `data/notes.json`.

#### 7. Export Notes
- **Input Required**: Choose format: `1` (.txt), `2` (.json), or `3` (.csv).
- **Output Received**: Creates a file inside `exports/` and displays the saved path:
  ```text
  [SUCCESS] Notes successfully exported to:
    /path/to/exports/notes_export_20261008_121530.csv
  ```

---

## 5. Tool 3: Timer & Stopwatch

### How to Access
Enter `3` at the Main Menu.

### Timer & Stopwatch Sub-Menu
```text
==================================================
                TIMER & STOPWATCH                 
              Time Management Suite               
==================================================

1. Countdown Timer
2. Stopwatch
0. Back to Main Menu
```

### Features

#### 1. Countdown Timer
- **Access**: Select `1`.
- **Input Required**: Choose duration entry mode (`1` for Minutes & Seconds, `2` for Total Seconds).
- **What Happens**: Begins a real-time countdown updating every second in-place.
- **Live Output**:
  ```text
    Remaining: 00:45  [==========--------------------]  33%
  ```
- **Completion Output**: Emits a terminal bell sound (`\a`) and prints:
  ```text
  [SUCCESS] >>> TIME'S UP! The countdown has finished. <<<
  ```
- **User Control**: Press `Ctrl+C` at any time to pause or cancel the timer without closing the application.

#### 2. Stopwatch
- **Access**: Select `2`.
- **Controls Available**:
  - `1. Start / Resume`: Starts timer ticking at 100ms intervals.
  - `1. Pause`: Stops the timer and retains elapsed time.
  - `2. Record Lap`: Records the current timestamp as a discrete lap.
  - `3. Reset Stopwatch`: Resets time to `00:00.00` and clears recorded laps.
  - `0. Back to Timer Menu`: Pauses and exits back to menu.

---

## 6. Tool 4: File Organizer

### How to Access
Enter `4` at the Main Menu.

### File Organizer Sub-Menu
```text
==================================================
                  FILE ORGANIZER                  
          Categorize Files by Extension           
==================================================

1. Organize a Directory (Move files into category folders)
2. Preview Organization (Dry Run / Simulation)
3. View Supported Categories & Extensions
0. Back to Main Menu
```

### Features

#### 1. Organize a Directory
- **Input Required**: Path to the target directory (e.g., `./downloads` or `/Users/username/Desktop/test_folder`).
- **What Happens**:
  1. Validates that the path exists and is a directory.
  2. Runs an automatic simulation preview first.
  3. Asks for confirmation: `Proceed with moving N file(s)? [Y/n]:`.
  4. Upon confirmation, creates category folders (`images/`, `documents/`, etc.) and moves files into them.
- **Collision Protection**: If `notes.txt` already exists in `text/`, the new file is automatically renamed to `notes_1.txt`. No files are overwritten.

#### 2. Preview Organization (Dry Run / Simulation)
- **Input Required**: Target directory path.
- **What Happens**: Scans the folder and displays a full simulation breakdown without moving or modifying any files on disk.

#### 3. View Supported Categories & Extensions
- Displays the complete mapping of 45+ extensions mapped to category folders (`images`, `documents`, `text`, `spreadsheets`, `python`, `code`, `audio`, `video`, `archives`, `others`).

---

## 7. Tool 5: Unit Converter

### How to Access
Enter `5` at the Main Menu.

### Unit Converter Sub-Menu
```text
==================================================
                  UNIT CONVERTER                  
      Length, Weight, Temp, Time & Digital        
==================================================

1. Length (Meters, Kilometers, Miles, Feet, Inches, etc.)
2. Weight & Mass (Kilograms, Grams, Pounds, Ounces, etc.)
3. Temperature (Celsius, Fahrenheit, Kelvin)
4. Time (Seconds, Minutes, Hours, Days, Weeks)
5. Digital Storage (Bytes, KB, MB, GB, TB)
0. Back to Main Menu
```

### Conversion Procedure
1. Select measurement domain (Options 1–5).
2. Select source (`FROM`) unit number.
3. Select destination (`TO`) unit number.
4. Enter numeric value to convert.
5. **Output**: Displays exact formatted result, e.g., `[SUCCESS] 5 kilometers = 3.10686 miles`.

### Domain Restrictions
- Length, Weight, Time, and Digital Storage reject negative values (`[ERROR] Value must be at least 0.0`).
- Temperature permits negative values but rejects any value below **Absolute Zero** (`-273.15°C`, `0 K`, or `-459.67°F`).

---

## 8. Tool 6: Backup & Restore

### How to Access
Enter `6` at the Main Menu.

### Backup & Restore Sub-Menu
```text
==================================================
                 BACKUP & RESTORE                 
           Application Data Protection            
==================================================

1. Create New Backup
2. List Available Backups
3. Restore From Backup
4. Delete a Backup
0. Back to Main Menu
```

### Features

#### 1. Create New Backup
- **What Happens**: Copies `data/notes.json` into `data/backups/notes_backup_YYYY-MM-DD_HHMMSS.json` and verifies that the copied file is valid JSON.
- **Output**: `[SUCCESS] Backup created successfully: notes_backup_2026-10-08_121530.json`.

#### 2. List Available Backups
- **Output**: Displays an indexed table showing Backup Filename, Notes Count, File Size in bytes/KB, and Integrity Status (`OK` or `ERR`).

#### 3. Restore From Backup
- **Input Required**: Backup index number to restore.
- **What Happens**:
  1. Verifies that the selected backup is valid.
  2. Automatically takes a pre-restore safety snapshot of the active data (`notes.json.pre_restore.bak`).
  3. Prompts for explicit confirmation.
  4. Atomically replaces active data with the backup contents.
- **Output**: `[SUCCESS] Successfully restored data from 'notes_backup_...json' (N note(s)).`

#### 4. Delete a Backup
- Select backup index number and confirm with `y` to permanently delete an unwanted backup.

---

## 9. Exiting the Application

To terminate the application:
1. Select **Option 7 (Exit)** from the Main Menu.
2. Alternatively, press **Ctrl+C** at the main menu prompt.

The application displays a clean goodbye banner and terminates with exit code `0`:
```text
==================================================
                     GOODBYE!                     
   Thank you for using Personal Productivity Suite
==================================================

[SUCCESS] Session ended successfully. Have a productive day!
```
