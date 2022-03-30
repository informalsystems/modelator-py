"""How to parse a TLA+ expression."""
from modelator_py.util.tla import parser
from modelator_py.util.tla.to_str import Nodes

expr = r"""
    \/ /\ x = 1
       /\ x' = 2

    \/ /\ x = 2
       /\ x' = 1
"""


def parse_expr():
    """Parse a TLA+ expression."""
    tree = parser.parse_expr(expr)
    print(tree)


def parse_expr_and_pretty_print():
    """Parse and print a TLA+ expression."""
    tree = parser.parse_expr(expr, nodes=Nodes)
    s = tree.to_str(width=80)
    print(s)


if __name__ == "__main__":
    parse_expr()
    parse_expr_and_pretty_print()
