"""TLA+ parser and syntax tree."""
from tla.parser import parse, parse_expr

try:
    from tla._version import version as __version__
except:
    __version__ = None
