"""Simple safe calculator CLI and evaluator.

Usage:
  - Run interactively: `python -m calculator.calc`
  - Evaluate one expression: `python -m calculator.calc "2+3*4"`

This module evaluates arithmetic expressions safely using the AST module.
"""

from __future__ import annotations

import ast
import operator as op
import sys
from typing import Any

# supported binary operators
_BINARY_OPERATORS: dict[type[ast.operator], Any] = {
	ast.Add: op.add,
	ast.Sub: op.sub,
	ast.Mult: op.mul,
	ast.Div: op.truediv,
	ast.FloorDiv: op.floordiv,
	ast.Mod: op.mod,
	ast.Pow: op.pow,
}

# supported unary operators
_UNARY_OPERATORS: dict[type[ast.unaryop], Any] = {
	ast.UAdd: op.pos,
	ast.USub: op.neg,
}


def _eval_node(node: ast.AST) -> float:
	if isinstance(node, ast.Expression):
		return _eval_node(node.body)

	if isinstance(node, ast.Constant):  # Python 3.8+
		if isinstance(node.value, (int, float)):
			return float(node.value)
		raise ValueError(f"Unsupported constant: {node.value!r}")

	if isinstance(node, ast.Num):  # older AST
		return float(node.n)

	if isinstance(node, ast.BinOp):
		left = _eval_node(node.left)
		right = _eval_node(node.right)
		op_type = type(node.op)
		if op_type in _BINARY_OPERATORS:
			func = _BINARY_OPERATORS[op_type]
			return func(left, right)
		raise ValueError(f"Unsupported binary operator: {op_type.__name__}")

	if isinstance(node, ast.UnaryOp):
		operand = _eval_node(node.operand)
		op_type = type(node.op)
		if op_type in _UNARY_OPERATORS:
			func = _UNARY_OPERATORS[op_type]
			return func(operand)
		raise ValueError(f"Unsupported unary operator: {op_type.__name__}")

	# disallow names, calls, attributes, subscripts, etc.
	raise ValueError(f"Unsupported expression element: {type(node).__name__}")


def evaluate(expr: str) -> float:
	"""Evaluate an arithmetic expression and return a float result.

	The function is deliberately strict and only allows numeric literals,
	unary +/-, and binary operators + - * / // % **. Use '^' as power
	(it will be converted to '**').
	"""
	if not isinstance(expr, str):
		raise TypeError("Expression must be a string")

	# allow users to write ^ for power (common in some calculators)
	expr = expr.replace("^", "**")

	try:
		node = ast.parse(expr, mode="eval")
	except SyntaxError as e:
		raise ValueError(f"Invalid expression: {e}")

	# walk AST to ensure only allowed nodes are present
	for n in ast.walk(node):
		if isinstance(n, (ast.Call, ast.Name, ast.Attribute, ast.Subscript)):
			raise ValueError("Names, calls, attributes and indexing are not allowed")

	return _eval_node(node)


def main(argv: list[str] | None = None) -> int:
	argv = list(argv or sys.argv[1:])
	if argv:
		expr = " ".join(argv)
		try:
			result = evaluate(expr)
		except Exception as e:
			print(f"Error: {e}")
			return 2
		print(result)
		return 0

	# interactive loop
	try:
		while True:
			try:
				s = input("calc> ").strip()
			except (EOFError, KeyboardInterrupt):
				print()
				break
			if not s:
				continue
			if s.lower() in {"quit", "exit", "q"}:
				break
			try:
				print(evaluate(s))
			except Exception as e:
				print("Error:", e)
	except KeyboardInterrupt:
		print()

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

