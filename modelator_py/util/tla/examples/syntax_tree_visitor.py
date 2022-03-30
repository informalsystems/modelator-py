"""How to use the visitor pattern when traversing the syntax tree."""
from modelator_py.util.tla import parser, to_str, visit

expr = r"x = 1 /\ y = 2"


class CollectIdentifiers(visit.NodeTransformer):
    """A visitor that collects identifiers."""

    def visit_Opaque(self, node, *arg, **kw):
        name = node.name
        kw["identifiers"].add(name)
        return self.nodes.Opaque(name)


def visit_tla_expr():
    """Traverse the syntax tree to collect identifiers."""
    tree = parser.parse_expr(expr, nodes=to_str.Nodes)
    identifiers = set()
    visitor = CollectIdentifiers()
    visitor.visit(tree, identifiers=identifiers)
    print(identifiers)


if __name__ == "__main__":
    visit_tla_expr()
