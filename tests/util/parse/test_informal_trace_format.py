import os
import copy

from modelator.util.parse.tla import parser, visit
from modelator.util.parse.tla.to_str import Nodes as Nodes
from ...helper import get_resource_dir

from collections import defaultdict


def get_expr():
    fn = "TlcStateExpressionExample0.txt"
    path = os.path.join(get_resource_dir(), fn)
    with open(path, "r") as fd:
        return fd.read()


def test_tla_state_expression_to_informal_trace_format_state():

    """
    json in the Informal Trace Format contains a state field mapping to a
    list of states.

    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format

    Test the translation of a single state.
    """

    # poetry run pytest tests/util/parse/test_informal_trace_format.py -s -k 'test_tla_state_expression_to_informal_trace_format_state'

    s = get_expr()
    tree = parser.parse_expr(s, nodes=Nodes)
    assert tree is not None
    text = tree.to_str(width=80)


class ITFSet:
    """{ "#set": [ <expr>, ..., <expr> ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False

    def __repr__(self):
        obj = {"#set": self.elements}
        return repr(obj)


class ITFMap:
    """{ "#map": [ [ <expr>, <expr> ], ..., [ <expr>, <expr> ] ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFMap):
            return self.elements == other.elements
        return False

    def __repr__(self):
        obj = {"#map": self.elements}
        return repr(obj)


def merge_itf_maps(f, g):
    """
    f @@ g == [
        x \in (DOMAIN f) \cup (DOMAIN g) |->
        IF x \in DOMAIN f THEN f[x] ELSE g[x]
    ]
    """
    f_keys = set(pair[0] for pair in f.elements)
    elements = f.elements
    for key, value in g.elements:
        if key not in f_keys:
            elements.append([key, value])
    return ITFMap(elements)


class Experiment(visit.NodeTransformer):
    """A visitor for experimentation."""

    def visit(self, node, *arg, **kw):
        """Call the implementation method for `node`.

        For each `node` of class named `ClsName`,
        there is a method named `visit_ClsName`.

        Override the `visit_*` methods to change
        the visitor's behavior, by subclassing it.
        """
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node, *arg, **kw)

    def visit_Opaque(self, node, *arg, **kw):
        # .name
        return node.name

    def visit_List(self, node, *arg, **kw):
        """
        For parsing TLC state the only List is at the top
        level (variable conjunction), therefore we do not
        need to return the op
        """
        # .op
        # .exprs
        self.visit(node.op, *arg, **kw)
        variable_pairs = []
        for expr in node.exprs:
            e = self.visit(expr, *arg, **kw)
            variable_pairs.append(e)
        return variable_pairs

    def visit_SetEnum(self, node, *arg, **kw):
        # .exprs
        elements = set()
        for expr in node.exprs:
            e = self.visit(expr, *arg, **kw)
            elements.add(e)
        return ITFSet(elements)

    def visit_Record(self, node, *arg, **kw):
        # .items
        pairs = []
        for name, expr in node.items:
            e = self.visit(expr, *arg, **kw)
            pair = [name, e]
            pairs.append(pair)
        return ITFMap(pairs)

    def visit_String(self, node, *arg, **kw):
        # .value
        return node.value

    def visit_Eq(self, node, *arg, **kw):
        pass

    def visit_Parens(self, node, *arg, **kw):
        # .expr
        # .pform
        expr = self.visit(node.expr, *arg, **kw)
        self.visit(node.pform, *arg, **kw)
        return expr

    def visit_Syntax(self, node, *arg, **kw):
        pass

    def visit_Tuple(self, node, *arg, **kw):
        # .exprs
        i = 1
        pairs = []
        for expr in node.exprs:
            e = self.visit(expr, *arg, **kw)
            pair = [i, e]
            pairs.append(pair)
            i += 1
        return ITFMap(pairs)

    def visit_FALSE(self, node, *arg, **kw):
        return False

    def visit_TRUE(self, node, *arg, **kw):
        return True

    def visit_Apply(self, node, *arg, **kw):
        # .op
        # .operands

        assert type(node.op) in {Nodes.Eq, Nodes.Opaque}

        self.visit(node.op, *arg, **kw)

        if type(node.op) == Nodes.Eq:
            assert len(node.operands) == 2
            variable_name = node.operands[0].name
            variable_value = self.visit(node.operands[1], *arg, **kw)
            return [variable_name, variable_value]
        if type(node.op) == Nodes.Opaque:
            assert node.op.name in {":>", "@@", "-."}
            if node.op.name == ":>":
                assert len(node.operands) == 2
                key = self.visit(node.operands[0], *arg, **kw)
                value = self.visit(node.operands[1], *arg, **kw)
                return ITFMap([[key, value]])
            if node.op.name == "@@":
                assert len(node.operands) == 2
                f = self.visit(node.operands[0], *arg, **kw)
                g = self.visit(node.operands[1], *arg, **kw)
                assert type(f) == ITFMap
                assert type(g) == ITFMap
                return merge_itf_maps(f, g)
            if node.op.name == "-.":
                assert len(node.operands) == 1
                return -self.visit(node.operands[0], *arg, **kw)

    def visit_Number(self, node, *arg, **kw):
        """WARNING: does not support floating point"""
        # .integer
        # .mantissa
        return int(node.integer)

    def visit_And(self, node, *arg, **kw):
        pass

    def visit_Opaque(self, node, *arg, **kw):
        # .name
        return node.name


def test_debug():
    print()
    s = get_expr()
    tree = parser.parse_expr(s, nodes=Nodes)
    assert tree is not None
    text = tree.to_str(width=80)
    # print(text)
    visitor = Experiment()
    variable_pairs = visitor.visit(tree)
    for key, value in variable_pairs:
        print(key)
        print(value)
