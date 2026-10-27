"""
Personal Productivity Suite - Unit Converter Module
File: unit_converter.py

Provides conversions across multiple measurement categories:
Length, Weight/Mass, Temperature, Time, and Digital Storage.
Enforces physical domain validation (e.g. non-negative lengths, absolute zero).
"""

from typing import Dict, List, Tuple, Union

from utils import (
    clear_screen,
    get_valid_float,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_sub_header,
    print_success,
)


# Length conversion factors to base unit: meters (m)
LENGTH_TO_BASE: Dict[str, float] = {
    "meters": 1.0,
    "kilometers": 1000.0,
    "centimeters": 0.01,
    "millimeters": 0.001,
    "miles": 1609.344,
    "yards": 0.9144,
    "feet": 0.3048,
    "inches": 0.0254,
}

# Weight / Mass conversion factors to base unit: kilograms (kg)
WEIGHT_TO_BASE: Dict[str, float] = {
    "kilograms": 1.0,
    "grams": 0.001,
    "milligrams": 0.000001,
    "metric tons": 1000.0,
    "pounds": 0.45359237,
    "ounces": 0.028349523125,
}

# Time conversion factors to base unit: seconds (s)
TIME_TO_BASE: Dict[str, float] = {
    "seconds": 1.0,
    "minutes": 60.0,
    "hours": 3600.0,
    "days": 86400.0,
    "weeks": 604800.0,
}

# Digital Storage factors to base unit: bytes (B) (1 KB = 1024 B)
DIGITAL_TO_BASE: Dict[str, float] = {
    "bytes": 1.0,
    "kilobytes": 1024.0,
    "megabytes": 1024.0 ** 2,
    "gigabytes": 1024.0 ** 3,
    "terabytes": 1024.0 ** 4,
}


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a length measurement between supported units.
    
    Raises:
        ValueError: For unknown units or negative lengths.
    """
    f_u = from_unit.strip().lower()
    t_u = to_unit.strip().lower()

    if f_u not in LENGTH_TO_BASE:
        raise ValueError(f"Unknown source length unit '{from_unit}'.")
    if t_u not in LENGTH_TO_BASE:
        raise ValueError(f"Unknown target length unit '{to_unit}'.")
    if value < 0:
        raise ValueError("Length value cannot be negative.")

    base_meters = value * LENGTH_TO_BASE[f_u]
    return base_meters / LENGTH_TO_BASE[t_u]


def convert_weight(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a weight/mass measurement between supported units.
    
    Raises:
        ValueError: For unknown units or negative weights.
    """
    f_u = from_unit.strip().lower()
    t_u = to_unit.strip().lower()

    if f_u not in WEIGHT_TO_BASE:
        raise ValueError(f"Unknown source weight unit '{from_unit}'.")
    if t_u not in WEIGHT_TO_BASE:
        raise ValueError(f"Unknown target weight unit '{to_unit}'.")
    if value < 0:
        raise ValueError("Weight value cannot be negative.")

    base_kg = value * WEIGHT_TO_BASE[f_u]
    return base_kg / WEIGHT_TO_BASE[t_u]


def convert_time(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert a time interval between supported units.
    
    Raises:
        ValueError: For unknown units or negative time.
    """
    f_u = from_unit.strip().lower()
    t_u = to_unit.strip().lower()

    if f_u not in TIME_TO_BASE:
        raise ValueError(f"Unknown source time unit '{from_unit}'.")
    if t_u not in TIME_TO_BASE:
        raise ValueError(f"Unknown target time unit '{to_unit}'.")
    if value < 0:
        raise ValueError("Time duration cannot be negative.")

    base_sec = value * TIME_TO_BASE[f_u]
    return base_sec / TIME_TO_BASE[t_u]


def convert_digital(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert digital storage measurement between binary units (1024-based).
    
    Raises:
        ValueError: For unknown units or negative capacity.
    """
    f_u = from_unit.strip().lower()
    t_u = to_unit.strip().lower()

    if f_u not in DIGITAL_TO_BASE:
        raise ValueError(f"Unknown source digital storage unit '{from_unit}'.")
    if t_u not in DIGITAL_TO_BASE:
        raise ValueError(f"Unknown target digital storage unit '{to_unit}'.")
    if value < 0:
        raise ValueError("Digital storage cannot be negative.")

    base_bytes = value * DIGITAL_TO_BASE[f_u]
    return base_bytes / DIGITAL_TO_BASE[t_u]


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.
    Validates physical limits (cannot drop below Absolute Zero).
    
    Raises:
        ValueError: For unknown units or temperatures below absolute zero.
    """
    f_u = from_unit.strip().lower()
    t_u = to_unit.strip().lower()

    valid_units = {"celsius", "fahrenheit", "kelvin"}
    if f_u not in valid_units:
        raise ValueError(f"Unknown source temperature unit '{from_unit}'.")
    if t_u not in valid_units:
        raise ValueError(f"Unknown target temperature unit '{to_unit}'.")

    # Verify physical lower boundary: Absolute Zero
    if f_u == "celsius" and value < -273.15:
        raise ValueError("Temperature cannot be below Absolute Zero (-273.15°C).")
    if f_u == "kelvin" and value < 0:
        raise ValueError("Temperature in Kelvin cannot be below 0 K.")
    if f_u == "fahrenheit" and value < -459.67:
        raise ValueError("Temperature cannot be below Absolute Zero (-459.67°F).")

    # Step 1: Normalize to Celsius
    if f_u == "celsius":
        celsius = value
    elif f_u == "fahrenheit":
        celsius = (value - 32.0) * (5.0 / 9.0)
    else:  # kelvin
        celsius = value - 273.15

    # Step 2: Convert from Celsius to target
    if t_u == "celsius":
        return celsius
    elif t_u == "fahrenheit":
        return (celsius * (9.0 / 5.0)) + 32.0
    else:  # kelvin
        return celsius + 273.15


def _run_category_converter(
    category_name: str,
    units_list: List[str],
    convert_func,
    allow_negative: bool = False,
) -> None:
    """Helper runner for interactive conversion within a specific category."""
    while True:
        clear_screen()
        print_header(f"{category_name.upper()} CONVERTER")
        print("Available units:")
        for idx, u in enumerate(units_list, 1):
            print(f" {idx:2d}. {u.capitalize()}")
        print("  0. Back to Unit Categories")
        print()

        from_idx = get_valid_int("Select 'FROM' unit", min_val=0, max_val=len(units_list))
        if from_idx == 0:
            break

        to_idx = get_valid_int("Select 'TO' unit", min_val=0, max_val=len(units_list))
        if to_idx == 0:
            break

        from_unit = units_list[from_idx - 1]
        to_unit = units_list[to_idx - 1]

        val = get_valid_float(
            f"Enter value in {from_unit}",
            min_val=None if allow_negative else 0.0,
        )

        try:
            converted = convert_func(val, from_unit, to_unit)
            print()
            print_success(f"{val:g} {from_unit} = {converted:g} {to_unit}")
        except ValueError as err:
            print_error(f"Conversion error: {err}")

        pause()


def run_unit_converter_tool() -> None:
    """Interactive CLI runner for the Unit Converter tool."""
    while True:
        clear_screen()
        print_header("UNIT CONVERTER", subtitle="Length, Weight, Temp, Time & Digital")
        print("1. Length (Meters, Kilometers, Miles, Feet, Inches, etc.)")
        print("2. Weight & Mass (Kilograms, Grams, Pounds, Ounces, etc.)")
        print("3. Temperature (Celsius, Fahrenheit, Kelvin)")
        print("4. Time (Seconds, Minutes, Hours, Days, Weeks)")
        print("5. Digital Storage (Bytes, KB, MB, GB, TB)")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select category", min_val=0, max_val=5)

        if choice == 0:
            break
        elif choice == 1:
            _run_category_converter("Length", list(LENGTH_TO_BASE.keys()), convert_length)
        elif choice == 2:
            _run_category_converter("Weight & Mass", list(WEIGHT_TO_BASE.keys()), convert_weight)
        elif choice == 3:
            _run_category_converter("Temperature", ["celsius", "fahrenheit", "kelvin"], convert_temperature, allow_negative=True)
        elif choice == 4:
            _run_category_converter("Time", list(TIME_TO_BASE.keys()), convert_time)
        elif choice == 5:
            _run_category_converter("Digital Storage", list(DIGITAL_TO_BASE.keys()), convert_digital)
