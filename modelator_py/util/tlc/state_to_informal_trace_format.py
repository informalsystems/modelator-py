from modelator_py.util.informal_trace_format import ITFMap, ITFSet, ITFState
from modelator_py.util.tla import parser, visit
from modelator_py.util.tla.to_str import Nodes


def merge_itf_maps(f, g):
    """

    Computes the result of the @@ operator.

    f @@ g == [
        x \\in (DOMAIN f) \\cup (DOMAIN g) |->
        IF x \\in DOMAIN f THEN f[x] ELSE g[x]
    ]

    The output of TLC should never contain functions
    with overlapping domains so we can skip the overlap
    check that is present in a model checker.
    """
    assert isinstance(f, ITFMap)
    assert isinstance(g, ITFMap)
    elements = f.elements
    elements.extend(g.elements)
    return ITFMap(elements)


class Visitor(visit.NodeTransformer):
    """
    Translates a state expression from the stdout of TLC to
    a list of [<variable name>, <value>] pairs.

    TLC states are given in a conjunction list. This visitor ONLY
    work on such input.
    """

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
        elements = []
        for expr in node.exprs:
            e = self.visit(expr, *arg, **kw)
            elements.append(e)
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

        """.value is a string with quote characters"""
        return node.value[1:-1]

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


def state_to_informal_trace_format_state(state_expr_str: str):
    """
    Converts a state expression string as found in the stdout of TLC
    into an in memory AST representation.

    Note: this is a slow operation.
    """
    tree = parser.parse_expr(state_expr_str, nodes=Nodes)
    visitor = Visitor()
    var_value_pairs = visitor.visit(tree)
    var_value_map = {key: value for key, value in var_value_pairs}
    return ITFState(var_value_map)
