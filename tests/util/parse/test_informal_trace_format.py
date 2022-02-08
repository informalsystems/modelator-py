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
    print(text)


class ITFBuilder:
    def __init__(self):
        pass


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
        name = node.name
        return self.nodes.Opaque(name)

    def visit_List(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        assert (
            type(node.op) == Nodes.And
        ), "the top level of TLC output is a conjunction"
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            assert (
                type(expr) == Nodes.Apply
            ), "the top level of TLC output is a conjunction of Eq Apply's"
            exprs.append(expr_)
        return self.nodes.List(op, exprs)

    def visit_SetEnum(self, node, *arg, **kw):
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        return self.nodes.SetEnum(exprs)

    def visit_Record(self, node, *arg, **kw):
        items = list()
        for name, expr in node.items:
            name_ = copy.copy(name)
            expr_ = self.visit(expr, *arg, **kw)
            pair = (name_, expr_)
            items.append(pair)
        return self.nodes.Record(items)

    def visit_String(self, node, *arg, **kw):
        return self.nodes.String(node.value)

    def visit_Eq(self, node, *arg, **kw):
        return self.nodes.Eq()

    def visit_Parens(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        pform = self.visit(node.pform, *arg, **kw)
        return self.nodes.Parens(expr, pform)

    def visit_Syntax(self, node, *arg, **kw):
        return self.nodes.Syntax()

    def visit_Tuple(self, node, *arg, **kw):
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        return self.nodes.Tuple(exprs)

    def visit_FALSE(self, node, *arg, **kw):
        return self.nodes.FALSE()

    def visit_TRUE(self, node, *arg, **kw):
        return self.nodes.TRUE()

    def visit_Apply(self, node, *arg, **kw):
        builder = kw["builder"]
        op = self.visit(node.op, *arg, **kw)

        print(
            type(op),
            op.to_str(width=80),
            [oper.to_str(width=80) for oper in node.operands],
        )
        operands = list()

        if type(op) == Nodes.Eq:
            variable_name = node.operands[0].name

        for operand in node.operands:
            res = self.visit(operand, *arg, **kw)
            operands.append(res)
        return self.nodes.Apply(op, operands)

    def visit_Number(self, node, *arg, **kw):
        return self.nodes.Number(node.integer, node.mantissa)

    def visit_And(self, node, *arg, **kw):
        return self.nodes.And()

    def visit_Opaque(self, node, *arg, **kw):
        return self.nodes.Opaque(node.name)


def test_debug():
    print()
    s = get_expr()
    tree = parser.parse_expr(s, nodes=Nodes)
    assert tree is not None
    text = tree.to_str(width=80)
    # print(text)
    visitor = Experiment()
    builder = ITFBuilder()
    visitor.visit(tree, builder=builder)
