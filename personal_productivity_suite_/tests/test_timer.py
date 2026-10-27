"""
Unit tests for the Timer & Stopwatch module.
File: tests/test_timer.py
"""

import time
from timer import (
    Stopwatch,
    format_seconds,
    format_stopwatch_time,
    render_progress_bar,
)


class TestTimerFormatting:
    """Test timer string formatting and progress rendering."""

    def test_format_seconds_minutes_only(self):
        assert format_seconds(0) == "00:00"
        assert format_seconds(5) == "00:05"
        assert format_seconds(65) == "01:05"
        assert format_seconds(599) == "09:59"

    def test_format_seconds_hours(self):
        assert format_seconds(3600) == "01:00:00"
        assert format_seconds(3665) == "01:01:05"

    def test_format_stopwatch_time(self):
        assert format_stopwatch_time(0.0) == "00:00.00"
        assert format_stopwatch_time(12.34) == "00:12.34"
        assert format_stopwatch_time(3601.50) == "01:00:01.50"

    def test_render_progress_bar(self):
        bar_start = render_progress_bar(100, 100, width=10)
        assert "[----------]   0%" in bar_start

        bar_mid = render_progress_bar(50, 100, width=10)
        assert "[=====-----]  50%" in bar_mid

        bar_done = render_progress_bar(0, 100, width=10)
        assert "[==========] 100%" in bar_done


class TestStopwatchLogic:
    """Test stopwatch state transitions without waiting for long real-time intervals."""

    def test_stopwatch_initial_state(self):
        sw = Stopwatch()
        assert sw.get_elapsed() == 0.0
        assert sw.is_running is False
        assert len(sw.laps) == 0

    def test_stopwatch_start_pause_reset(self):
        sw = Stopwatch()
        sw.start()
        assert sw.is_running is True
        time.sleep(0.05)  # brief sleep to test accumulation
        elapsed = sw.pause()
        assert sw.is_running is False
        assert elapsed > 0.0

        # Reset
        sw.reset()
        assert sw.get_elapsed() == 0.0
        assert sw.is_running is False

    def test_stopwatch_laps(self):
        sw = Stopwatch()
        sw.start()
        time.sleep(0.02)
        lap1 = sw.record_lap()
        assert len(sw.laps) == 1
        assert lap1 > 0.0

        time.sleep(0.02)
        lap2 = sw.record_lap()
        assert len(sw.laps) == 2
        assert lap2 > lap1
        sw.pause()
