"""TLA+ parser and syntax tree."""
from .parser import parse, parse_expr

__all__ = ["parse", "parse_expr"]
