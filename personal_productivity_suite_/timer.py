"""
Personal Productivity Suite - Timer & Stopwatch Module
File: timer.py

Provides a countdown timer with animated progress bar and audio-visual completion,
plus an interactive stopwatch with lap tracking and interruptible pause/resume controls.
"""

import sys
import time
from typing import List, Optional, Tuple

from utils import (
    clear_screen,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_sub_header,
    print_success,
    print_warning,
)


def format_seconds(total_seconds: int) -> str:
    """Format total seconds into HH:MM:SS or MM:SS."""
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_stopwatch_time(elapsed_seconds: float) -> str:
    """Format floating-point elapsed seconds into HH:MM:SS.ss."""
    total_hundredths = int(round(elapsed_seconds * 100))
    total_sec = total_hundredths // 100
    hundredths = total_hundredths % 100
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    seconds = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{hundredths:02d}"
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"


def render_progress_bar(current: int, total: int, width: int = 30) -> str:
    """Create a visual text progress bar for the countdown."""
    if total <= 0:
        return "[" + "=" * width + "] 100%"
    progress = max(0.0, min(1.0, (total - current) / total))
    filled_len = int(width * progress)
    bar = "=" * filled_len + ("-" * (width - filled_len))
    percent = int(progress * 100)
    return f"[{bar}] {percent:3d}%"


def run_countdown(duration_seconds: int) -> bool:
    """
    Run an interactive countdown timer with progress display.
    Can be safely interrupted via Ctrl+C without terminating the suite.
    
    Args:
        duration_seconds: Total seconds to count down.
        
    Returns:
        bool: True if completed naturally, False if cancelled by user.
    """
    if duration_seconds <= 0:
        print_error("Duration must be greater than zero.")
        return False

    total = duration_seconds
    remaining = total

    print()
    print_info("Timer started! Press Ctrl+C at any time to pause or cancel.")
    print("-" * 50)

    try:
        while remaining > 0:
            time_str = format_seconds(remaining)
            bar = render_progress_bar(remaining, total)
            sys.stdout.write(f"\r  Remaining: {time_str}  {bar} ")
            sys.stdout.flush()
            time.sleep(1)
            remaining -= 1

        sys.stdout.write(f"\r  Remaining: {format_seconds(0)}  {render_progress_bar(0, total)} \n")
        sys.stdout.flush()

        # Alert the user visually and with bell ring
        print()
        sys.stdout.write("\a")  # ASCII Bell
        sys.stdout.flush()
        print("*" * 50)
        print_success(">>> TIME'S UP! The countdown has finished. <<<")
        print("*" * 50)
        return True

    except KeyboardInterrupt:
        print("\n")
        print_warning("Timer paused.")
        return False


def run_countdown_interactive() -> None:
    """CLI flow for configuring and launching a countdown timer."""
    print_sub_header("COUNTDOWN TIMER CONFIGURATION")
    print("Choose duration input method:")
    print("1. Enter Minutes and Seconds")
    print("2. Enter Total Seconds")
    print("0. Cancel")

    mode = get_valid_int("Select method", min_val=0, max_val=2)
    if mode == 0:
        return

    if mode == 1:
        minutes = get_valid_int("Enter minutes", min_val=0, max_val=1440, default=0)
        seconds = get_valid_int("Enter seconds", min_val=0, max_val=59, default=0)
        total_seconds = (minutes * 60) + seconds
    else:
        total_seconds = get_valid_int("Enter total seconds", min_val=1, max_val=86400)

    if total_seconds <= 0:
        print_error("Total timer duration must be at least 1 second.")
        pause()
        return

    run_countdown(total_seconds)
    pause()


class Stopwatch:
    """Encapsulates stopwatch timing state, laps, and elapsed time calculation."""

    def __init__(self) -> None:
        self.accumulated: float = 0.0
        self.start_time: Optional[float] = None
        self.is_running: bool = False
        self.laps: List[float] = []

    def start(self) -> None:
        """Start or resume the stopwatch."""
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def pause(self) -> float:
        """Pause the stopwatch and record elapsed duration."""
        if self.is_running and self.start_time is not None:
            self.accumulated += time.time() - self.start_time
            self.is_running = False
            self.start_time = None
        return self.accumulated

    def reset(self) -> None:
        """Reset stopwatch back to zero and clear laps."""
        self.accumulated = 0.0
        self.start_time = None
        self.is_running = False
        self.laps.clear()

    def get_elapsed(self) -> float:
        """Get the current total elapsed time."""
        if self.is_running and self.start_time is not None:
            return self.accumulated + (time.time() - self.start_time)
        return self.accumulated

    def record_lap(self) -> float:
        """Record a lap timestamp and return the lap duration."""
        current = self.get_elapsed()
        self.laps.append(current)
        return current


def run_stopwatch_interactive() -> None:
    """Interactive CLI runner for the stopwatch tool."""
    sw = Stopwatch()

    while True:
        clear_screen()
        print_header("STOPWATCH", subtitle="Precision Time Tracker")
        elapsed = sw.get_elapsed()
        print(f" Current Time:  {format_stopwatch_time(elapsed)}")
        print(f" Status:        {'Running' if sw.is_running else 'Stopped / Paused'}")
        print()

        if sw.laps:
            print("Recorded Laps:")
            for idx, lap in enumerate(sw.laps, 1):
                print(f"  Lap #{idx:02d}: {format_stopwatch_time(lap)}")
            print("-" * 40)
            print()

        print("Controls:")
        if not sw.is_running:
            print("1. Start / Resume")
        else:
            print("1. Pause")
        print("2. Record Lap")
        print("3. Reset Stopwatch")
        print("0. Back to Timer Menu")
        print()

        choice = get_valid_int("Select action", min_val=0, max_val=3)

        if choice == 0:
            sw.pause()
            break

        if choice == 1:
            if sw.is_running:
                sw.pause()
                print_info(f"Stopwatch paused at {format_stopwatch_time(sw.get_elapsed())}.")
            else:
                sw.start()
                print_info("Stopwatch running... (Press Enter or Ctrl+C to open controls)")
                try:
                    while sw.is_running:
                        time.sleep(0.1)
                        sys.stdout.write(
                            f"\r  Elapsed: {format_stopwatch_time(sw.get_elapsed())}  "
                            f"[Press Enter to pause] "
                        )
                        sys.stdout.flush()
                        # Check if non-blocking stdin is possible or wait for keyboard interrupt
                        # On standard CLI, a brief loop with KeyboardInterrupt provides reliable cross-platform pause
                except KeyboardInterrupt:
                    sw.pause()
                    print("\n")
                    print_info(f"Stopwatch paused at {format_stopwatch_time(sw.get_elapsed())}.")

        elif choice == 2:
            if sw.get_elapsed() == 0:
                print_warning("Start the stopwatch before recording a lap.")
            else:
                lap_val = sw.record_lap()
                print_success(f"Lap #{len(sw.laps)} recorded: {format_stopwatch_time(lap_val)}")
            pause()

        elif choice == 3:
            sw.reset()
            print_success("Stopwatch reset to 00:00.00.")
            pause()


def run_timer_tool() -> None:
    """Main menu entry point for Timer and Stopwatch features."""
    while True:
        clear_screen()
        print_header("TIMER & STOPWATCH", subtitle="Time Management Suite")
        print("1. Countdown Timer")
        print("2. Stopwatch")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select an option", min_val=0, max_val=2)

        if choice == 0:
            break
        elif choice == 1:
            run_countdown_interactive()
        elif choice == 2:
            run_stopwatch_interactive()
