from abc import ABCMeta, abstractmethod


class ITFNode(object):
    __metaclass__ = ABCMeta

    def __repr__(self):
        assert False, """Not implement as uses visitor pattern
        and I don't want to think about circular reference right now."""


class ITFRecord(ITFNode):
    """{ "field1": <expr>, ..., "fieldN": <expr> }"""

    def __init__(self, elements):
        self.elements = elements  # dict

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False


class ITFList(ITFNode):
    """[ <expr>, ..., <expr> ]"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False


class ITFSet(ITFNode):
    """{ "#set": [ <expr>, ..., <expr> ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False


class ITFMap(ITFNode):
    """{ "#map": [ [ <expr>, <expr> ], ..., [ <expr>, <expr> ] ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFMap):
            return self.elements == other.elements
        return False


class ITFState(ITFNode):
    """
    {
        "#meta": <optional object>,
        "<var1>": <expr>,
        ...
        "<varN>": <expr>
    }
    """

    def __init__(self, var_value_map):
        self.var_value_map = var_value_map

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFState):
            return self.var_value_map == other.var_value_map
        return False


class ITFTrace(ITFNode):
    """
    {
        "#meta": <optional object>,
        "params": <optional array of strings>,
        "vars":  <array of strings>,
        "states": <array of states>,
        "loop": <optional int>
    }
    """

    def __init__(self, vars_, states, meta=None):
        self.meta = meta
        self.vars = vars_
        self.states = states

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFState):
            return (
                self.meta == other.meta
                and self.vars == other.vars
                and self.states == other.states
            )
        return False


class Visitor:
    def visit(self, node, *arg, **kw):
        # Only visit ITFNode objects.
        # It is sufficient to take face-value for python built-ins.
        if not isinstance(node, ITFNode):
            return node
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node, *arg, **kw)

    def visit_ITFRecord(self, node, *arg, **kw):
        elements = {k: self.visit(v) for k, v in node.elements}
        return ITFRecord(elements)

    def visit_ITFList(self, node, *arg, **kw):
        elements = [self.visit(e) for e in node.elements]
        return ITFList(elements)

    def visit_ITFSet(self, node, *arg, **kw):
        elements = [self.visit(e) for e in node.elements]
        return ITFSet(elements)

    def visit_ITFMap(self, node, *arg, **kw):
        elements = [[self.visit(e) for e in p] for p in node.elements]
        return ITFMap(elements)

    def visit_ITFState(self, node, *arg, **kw):
        var_value_map = {k: self.visit(v) for k, v in node.var_value_map.items()}
        return ITFState(var_value_map)

    def visit_ITFTrace(self, node, *arg, **kw):
        states = [self.visit(e) for e in node.states]
        return ITFTrace(node.vars, states, node.meta)


class JsonSerializer(Visitor):
    def visit_ITFRecord(self, node, *arg, **kw):
        elements = {k: self.visit(v) for k, v in node.elements}
        return elements

    def visit_ITFList(self, node, *arg, **kw):
        elements = [self.visit(e) for e in node.elements]
        return elements

    def visit_ITFSet(self, node, *arg, **kw):
        elements = [self.visit(e) for e in node.elements]
        return {"#set": elements}

    def visit_ITFMap(self, node, *arg, **kw):
        elements = [[self.visit(e) for e in p] for p in node.elements]
        return {"#map": elements}

    def visit_ITFState(self, node, *arg, **kw):
        var_value_map = {k: self.visit(v) for k, v in node.var_value_map.items()}
        return var_value_map

    def visit_ITFTrace(self, node, *arg, **kw):
        states = [self.visit(e) for e in node.states]
        return {"#meta": node.meta, "vars": node.vars, "states": states}


def with_lists(trace: ITFTrace):
    """
    Create a copy of the trace where lists take the place
    of 1-indexed maps.

    In TLA+ sequences (lists) are precisely functions with domain
    1..n for some n. This function transforms maps with domain
    1..n into ITF lists.
    """
    visitor = Visitor()
    visitor.visit(trace)
    return trace


def with_records(trace: ITFTrace):
    """
    Create a copy of the trace where sequences take the place
    of string-indexed maps.

    In TLA+ records are precisely functions with domain entirely
    of strings. This function transforms maps with domain of
    strings into ITF records.
    """
