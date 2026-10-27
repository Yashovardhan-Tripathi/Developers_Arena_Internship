"""
Unit tests for the Unit Converter module.
File: tests/test_unit_converter.py
"""

import pytest
from unit_converter import (
    convert_length,
    convert_weight,
    convert_time,
    convert_digital,
    convert_temperature,
)


class TestLengthConversion:
    """Test length units and bounds."""

    def test_meters_to_kilometers(self):
        assert convert_length(1000, "meters", "kilometers") == 1.0
        assert convert_length(5.5, "kilometers", "meters") == 5500.0

    def test_meters_to_centimeters(self):
        assert convert_length(2, "meters", "centimeters") == 200.0

    def test_miles_and_feet(self):
        # 1 mile = 5280 feet
        res = convert_length(1, "miles", "feet")
        assert pytest.approx(res, rel=1e-4) == 5280.0

    def test_negative_length_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            convert_length(-10, "meters", "feet")

    def test_unknown_unit_raises(self):
        with pytest.raises(ValueError, match="Unknown"):
            convert_length(10, "lightyears", "meters")


class TestWeightConversion:
    """Test mass / weight conversions."""

    def test_kilograms_to_grams(self):
        assert convert_weight(2.5, "kilograms", "grams") == 2500.0

    def test_pounds_to_kilograms(self):
        res = convert_weight(10, "pounds", "kilograms")
        assert pytest.approx(res, rel=1e-4) == 4.53592

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            convert_weight(-5, "grams", "kilograms")


class TestTimeConversion:
    """Test time interval conversions."""

    def test_hours_to_seconds(self):
        assert convert_time(1, "hours", "seconds") == 3600.0
        assert convert_time(24, "hours", "days") == 1.0

    def test_minutes_to_hours(self):
        assert convert_time(90, "minutes", "hours") == 1.5

    def test_negative_time_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            convert_time(-60, "seconds", "minutes")


class TestDigitalConversion:
    """Test binary digital storage conversions."""

    def test_megabytes_to_kilobytes(self):
        assert convert_digital(1, "megabytes", "kilobytes") == 1024.0

    def test_gigabytes_to_megabytes(self):
        assert convert_digital(4, "gigabytes", "megabytes") == 4096.0

    def test_negative_digital_raises(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            convert_digital(-100, "bytes", "kilobytes")


class TestTemperatureConversion:
    """Test temperature formulas and absolute zero boundaries."""

    def test_celsius_to_fahrenheit(self):
        assert convert_temperature(0, "celsius", "fahrenheit") == 32.0
        assert convert_temperature(100, "celsius", "fahrenheit") == 212.0
        assert convert_temperature(-40, "celsius", "fahrenheit") == -40.0

    def test_celsius_to_kelvin(self):
        assert convert_temperature(0, "celsius", "kelvin") == 273.15
        assert convert_temperature(25, "celsius", "kelvin") == 298.15

    def test_fahrenheit_to_celsius(self):
        assert convert_temperature(32, "fahrenheit", "celsius") == 0.0
        assert convert_temperature(212, "fahrenheit", "celsius") == 100.0

    def test_absolute_zero_validation(self):
        with pytest.raises(ValueError, match="Absolute Zero"):
            convert_temperature(-300, "celsius", "fahrenheit")

        with pytest.raises(ValueError, match="cannot be below 0 K"):
            convert_temperature(-1, "kelvin", "celsius")

        with pytest.raises(ValueError, match="Absolute Zero"):
            convert_temperature(-500, "fahrenheit", "celsius")
