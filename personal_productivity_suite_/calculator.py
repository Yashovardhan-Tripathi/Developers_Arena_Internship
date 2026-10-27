"""
Personal Productivity Suite - Calculator Module
File: calculator.py

Provides robust arithmetic operations, session calculation history,
and a secure AST-based mathematical expression evaluator without unsafe eval().
"""

import ast
import operator
from typing import List, Union

from utils import (
    clear_screen,
    get_non_empty_string,
    get_valid_float,
    get_valid_int,
    pause,
    print_error,
    print_header,
    print_info,
    print_sub_header,
    print_success,
)


# Allowed operators for the safe AST expression parser
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the sum of a and b."""
    return a + b


def subtract(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the difference of a and b."""
    return a - b


def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Return the product of a and b."""
    return a * b


def divide(a: Union[int, float], b: Union[int, float]) -> float:
    """
    Return the quotient of a divided by b.
    
    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def modulus(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Return the remainder of a divided by b.
    
    Raises:
        ZeroDivisionError: If b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot calculate modulus with divisor of zero.")
    return a % b


def power(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """
    Return a raised to the power of b.
    
    Raises:
        ValueError: If operation results in a complex number or excessive computation.
    """
    if a < 0 and isinstance(b, float) and not b.is_integer():
        raise ValueError("Negative base with fractional exponent produces a complex number.")
    if abs(b) > 10000:
        raise ValueError("Exponent is too large (maximum allowed exponent is 10,000).")
    try:
        result = a ** b
        if isinstance(result, complex):
            raise ValueError("Operation resulted in a complex number.")
        return result
    except OverflowError:
        raise ValueError("Calculation overflowed the numeric limits.")


def _eval_ast_node(node: ast.AST) -> Union[int, float]:
    """Recursively evaluate an AST node strictly restricted to numeric math."""
    if isinstance(node, ast.Expression):
        return _eval_ast_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.BinOp):
        left_val = _eval_ast_node(node.left)
        right_val = _eval_ast_node(node.right)
        op_type = type(node.op)

        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")

        if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right_val == 0:
            raise ZeroDivisionError("Division or modulo by zero in expression.")

        if op_type == ast.Pow:
            return power(left_val, right_val)

        return _SAFE_OPERATORS[op_type](left_val, right_val)

    if isinstance(node, ast.UnaryOp):
        operand_val = _eval_ast_node(node.operand)
        op_type = type(node.op)

        if op_type not in _SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

        return _SAFE_OPERATORS[op_type](operand_val)

    raise ValueError(f"Unsafe or unsupported expression syntax: '{type(node).__name__}'")


def evaluate_expression(expr: str) -> Union[int, float]:
    """
    Safely evaluate a mathematical expression string using Python's AST parser.
    Strictly forbids variables, function calls, attributes, loops, or unsafe eval().
    
    Args:
        expr: Mathematical expression string, e.g., '(12 + 4) * 5 / 2'.
        
    Returns:
        Evaluated numeric result.
        
    Raises:
        ValueError: For invalid syntax or disallowed expressions.
        ZeroDivisionError: For division/modulo by zero.
    """
    clean_expr = expr.strip()
    if not clean_expr:
        raise ValueError("Expression cannot be empty.")

    try:
        parsed = ast.parse(clean_expr, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid mathematical syntax: {exc.msg}") from exc

    return _eval_ast_node(parsed)


class CalculatorSession:
    """Manages calculator state, interactive operations, and calculation history."""

    def __init__(self) -> None:
        self.history: List[str] = []

    def record(self, entry: str) -> None:
        """Add an entry to the session history."""
        self.history.append(entry)

    def display_history(self) -> None:
        """Print recent session calculations."""
        print_sub_header("Calculation History")
        if not self.history:
            print_info("No calculations performed yet in this session.")
        else:
            for idx, item in enumerate(self.history, 1):
                print(f" {idx:2d}. {item}")
        print()


def _format_result(val: Union[int, float]) -> str:
    """Format numeric result cleanly, stripping trailing .0 when integer."""
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    if isinstance(val, float):
        # Round to 8 decimal places for clean float representation
        return f"{round(val, 8):g}"
    return str(val)


def run_calculator_tool() -> None:
    """Entry point for the interactive Calculator CLI tool."""
    session = CalculatorSession()

    while True:
        clear_screen()
        print_header("CALCULATOR TOOL", subtitle="Basic Math & Safe Expression Evaluator")
        print("1. Addition (+)")
        print("2. Subtraction (-)")
        print("3. Multiplication (*)")
        print("4. Division (/)")
        print("5. Modulus (%)")
        print("6. Power / Exponentiation (^)")
        print("7. Evaluate Full Expression (e.g., (10 + 5) * 2)")
        print("8. View Calculation History")
        print("9. Clear History")
        print("0. Back to Main Menu")
        print()

        choice = get_valid_int("Select an option", min_val=0, max_val=9)

        if choice == 0:
            break

        if choice == 8:
            session.display_history()
            pause()
            continue

        if choice == 9:
            session.history.clear()
            print_success("Calculation history cleared.")
            pause()
            continue

        if choice == 7:
            print_sub_header("Evaluate Expression")
            print_info("Supported: +, -, *, /, //, %, **, parentheses. Example: (15 + 5) * 3 / 2")
            expr = get_non_empty_string("Enter expression")
            try:
                res = evaluate_expression(expr)
                formatted = _format_result(res)
                log_line = f"{expr} = {formatted}"
                session.record(log_line)
                print_success(f"Result: {formatted}")
            except (ValueError, ZeroDivisionError) as err:
                print_error(f"Calculation failed: {err}")
            pause()
            continue

        # Standard two-operand operations (1-6)
        op_names = {
            1: ("Addition", "+", add),
            2: ("Subtraction", "-", subtract),
            3: ("Multiplication", "*", multiply),
            4: ("Division", "/", divide),
            5: ("Modulus", "%", modulus),
            6: ("Power", "^", power),
        }

        name, symbol, func = op_names[choice]
        print_sub_header(f"{name} ({symbol})")

        num1 = get_valid_float("Enter first number")
        num2 = get_valid_float("Enter second number")

        try:
            res = func(num1, num2)
            formatted = _format_result(res)
            log_line = f"{_format_result(num1)} {symbol} {_format_result(num2)} = {formatted}"
            session.record(log_line)
            print_success(f"Result: {log_line}")
        except ZeroDivisionError as err:
            print_error(f"Math Error: {err}")
        except ValueError as err:
            print_error(f"Value Error: {err}")
        except Exception as err:
            print_error(f"Unexpected error: {err}")

        pause()
