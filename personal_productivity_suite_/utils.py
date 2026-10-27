"""
Personal Productivity Suite - Shared Utilities Module
File: utils.py

Provides reusable console formatting, safe user input validation,
timestamp helpers, and directory resolution routines across all suite tools.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# ANSI escape sequences for clean, readable terminal styling
USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

if USE_COLOR:
    COLOR_RESET = "\033[0m"
    COLOR_BOLD = "\033[1m"
    COLOR_DIM = "\033[2m"
    COLOR_CYAN = "\033[96m"
    COLOR_GREEN = "\033[92m"
    COLOR_YELLOW = "\033[93m"
    COLOR_RED = "\033[91m"
    COLOR_BLUE = "\033[94m"
    COLOR_MAGENTA = "\033[95m"
else:
    COLOR_RESET = ""
    COLOR_BOLD = ""
    COLOR_DIM = ""
    COLOR_CYAN = ""
    COLOR_GREEN = ""
    COLOR_YELLOW = ""
    COLOR_RED = ""
    COLOR_BLUE = ""
    COLOR_MAGENTA = ""


def get_project_root() -> Path:
    """Return the absolute path to the project root directory."""
    return Path(__file__).resolve().parent


def get_data_dir() -> Path:
    """Return the absolute path to the data directory, creating it if needed."""
    data_dir = get_project_root() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_backups_dir() -> Path:
    """Return the absolute path to data/backups directory, creating it if needed."""
    backups_dir = get_data_dir() / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def get_exports_dir() -> Path:
    """Return the absolute path to exports directory, creating it if needed."""
    exports_dir = get_project_root() / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir


def clear_screen() -> None:
    """Clear the terminal screen cleanly across Windows, macOS, and Linux."""
    # Only clear when running in a genuine interactive terminal
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def print_divider(char: str = "=", width: int = 50) -> None:
    """Print a horizontal divider line."""
    print(char * width)


def print_header(title: str, width: int = 50, subtitle: Optional[str] = None) -> None:
    """Display a formatted, centered header box for tool titles and menus."""
    print()
    print_divider("=", width)
    print(f"{COLOR_BOLD}{title.center(width)}{COLOR_RESET}")
    if subtitle:
        print(f"{COLOR_CYAN}{subtitle.center(width)}{COLOR_RESET}")
    print_divider("=", width)
    print()


def print_sub_header(title: str, width: int = 50) -> None:
    """Display a concise sub-section header."""
    print()
    print(f"{COLOR_BOLD}{title}{COLOR_RESET}")
    print("-" * min(len(title) + 4, width))


def print_success(message: str) -> None:
    """Display a success message highlighted in green."""
    print(f"{COLOR_GREEN}[SUCCESS] {message}{COLOR_RESET}")


def print_error(message: str) -> None:
    """Display an error message highlighted in red."""
    print(f"{COLOR_RED}[ERROR] {message}{COLOR_RESET}")


def print_warning(message: str) -> None:
    """Display a warning message highlighted in yellow."""
    print(f"{COLOR_YELLOW}[WARNING] {message}{COLOR_RESET}")


def print_info(message: str) -> None:
    """Display an informational note highlighted in cyan."""
    print(f"{COLOR_CYAN}[INFO] {message}{COLOR_RESET}")


def pause(message: str = "Press Enter to continue...") -> None:
    """Pause execution until the user presses Enter."""
    print()
    try:
        input(f"{COLOR_DIM}{message}{COLOR_RESET}")
    except (EOFError, KeyboardInterrupt):
        print()


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Prompt the user for a Yes/No confirmation.
    
    Args:
        prompt: Question to ask the user.
        default: Default answer if user enters blank. True for Yes, False for No.
        
    Returns:
        bool: True if confirmed, False otherwise.
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        try:
            choice = input(f"{prompt}{suffix}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return default

        if not choice:
            return default
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print_error("Invalid response. Please enter 'y' for yes or 'n' for no.")


def get_valid_int(
    prompt: str,
    min_val: Optional[int] = None,
    max_val: Optional[int] = None,
    default: Optional[int] = None,
) -> int:
    """
    Safely prompt for an integer within optional bounds.
    
    Args:
        prompt: Display prompt.
        min_val: Minimum acceptable value (inclusive).
        max_val: Maximum acceptable value (inclusive).
        default: Optional default value if input is empty.
        
    Returns:
        int: Validated integer.
    """
    default_text = f" [{default}]" if default is not None else ""
    full_prompt = f"{prompt}{default_text}: "

    while True:
        try:
            raw_input = input(full_prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            if default is not None:
                return default
            raise

        if not raw_input:
            if default is not None:
                return default
            print_error("Input cannot be empty. Please enter a whole number.")
            continue

        try:
            val = int(raw_input)
        except ValueError:
            print_error(f"'{raw_input}' is not a valid integer. Please try again.")
            continue

        if min_val is not None and val < min_val:
            print_error(f"Value must be at least {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print_error(f"Value cannot exceed {max_val}.")
            continue

        return val


def get_valid_float(
    prompt: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    default: Optional[float] = None,
) -> float:
    """
    Safely prompt for a floating-point number within optional bounds.
    
    Args:
        prompt: Display prompt.
        min_val: Minimum acceptable value (inclusive).
        max_val: Maximum acceptable value (inclusive).
        default: Optional default value if input is empty.
        
    Returns:
        float: Validated float value.
    """
    default_text = f" [{default}]" if default is not None else ""
    full_prompt = f"{prompt}{default_text}: "

    while True:
        try:
            raw_input = input(full_prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            if default is not None:
                return default
            raise

        if not raw_input:
            if default is not None:
                return default
            print_error("Input cannot be empty. Please enter a number.")
            continue

        try:
            val = float(raw_input)
        except ValueError:
            print_error(f"'{raw_input}' is not a valid number. Please try again.")
            continue

        if min_val is not None and val < min_val:
            print_error(f"Value must be at least {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print_error(f"Value cannot exceed {max_val}.")
            continue

        return val


def get_non_empty_string(
    prompt: str,
    allow_empty: bool = False,
    default: Optional[str] = None,
) -> str:
    """
    Prompt user for a text string, optionally disallowing empty inputs.
    
    Args:
        prompt: Display prompt.
        allow_empty: If True, returns empty string when user submits nothing.
        default: Optional default string if user submits nothing.
        
    Returns:
        str: Validated string.
    """
    default_text = f" [{default}]" if default is not None else ""
    full_prompt = f"{prompt}{default_text}: "

    while True:
        try:
            val = input(full_prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            if default is not None:
                return default
            raise

        if not val:
            if default is not None:
                return default
            if allow_empty:
                return ""
            print_error("Input cannot be blank. Please enter text.")
            continue
        return val


def get_current_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current system timestamp formatted as a readable string."""
    return datetime.now().strftime(format_str)


def get_filename_timestamp(format_str: str = "%Y-%m-%d_%H%M%S") -> str:
    """Return a sanitized timestamp suitable for inclusion in backup filenames."""
    return datetime.now().strftime(format_str)
