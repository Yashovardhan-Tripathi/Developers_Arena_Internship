"""
Personal Productivity Suite
File: main.py

Central application coordinator and unified CLI entry point.
Provides the interactive main menu and coordinates navigation between:
1. Calculator Tool
2. Notes Manager
3. Timer & Stopwatch
4. File Organizer
5. Unit Converter
6. Backup & Restore
7. Exit
"""

import sys
from pathlib import Path

# Ensure the project directory is on sys.path for robust execution from any directory
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backup_manager import run_backup_tool
from calculator import run_calculator_tool
from file_organizer import run_file_organizer_tool
from notes_manager import run_notes_manager
from timer import run_timer_tool
from unit_converter import run_unit_converter_tool
from utils import (
    clear_screen,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_success,
)


def display_main_menu() -> None:
    """Print the primary interactive navigation menu."""
    clear_screen()
    print_header("PERSONAL PRODUCTIVITY SUITE", subtitle="Integrated Terminal Tools for Developers")
    print("MAIN MENU:")
    print("  1. Calculator Tool")
    print("  2. Notes Manager")
    print("  3. Timer & Stopwatch")
    print("  4. File Organizer")
    print("  5. Unit Converter")
    print("  6. Backup & Restore")
    print("  7. Exit")
    print()


def main() -> None:
    """Main program execution loop."""
    print_info("Initializing Personal Productivity Suite...")

    while True:
        try:
            display_main_menu()
            choice = get_valid_int("Enter your choice (1-7)", min_val=1, max_val=7)

            if choice == 1:
                run_calculator_tool()
            elif choice == 2:
                run_notes_manager()
            elif choice == 3:
                run_timer_tool()
            elif choice == 4:
                run_file_organizer_tool()
            elif choice == 5:
                run_unit_converter_tool()
            elif choice == 6:
                run_backup_tool()
            elif choice == 7:
                clear_screen()
                print_header("GOODBYE!", subtitle="Thank you for using Personal Productivity Suite")
                print_success("Session ended successfully. Have a productive day!\n")
                sys.exit(0)

        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C at the main menu
            print("\n")
            print_info("KeyboardInterrupt detected. Exiting gracefully.")
            print_success("Goodbye!\n")
            sys.exit(0)
        except EOFError:
            print("\n")
            print_info("End of input stream detected. Exiting suite.")
            sys.exit(0)
        except Exception as exc:
            print_error(f"An unexpected error occurred in the suite coordinator: {exc}")
            pause("Press Enter to return to the main menu...")


if __name__ == "__main__":
    main()
