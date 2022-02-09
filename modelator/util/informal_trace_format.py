from abc import ABCMeta, abstractmethod


class ITFNode(object):
    __metaclass__ = ABCMeta

    def __repr__(self):
        return repr(self.to_obj())

    @abstractmethod
    def to_obj(self):
        pass


class ITFList(ITFNode):
    """{ "#list": [ <expr>, ..., <expr> ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False

    def to_obj(self):
        def lam(e):
            return e.to_obj() if isinstance(e, ITFNode) else e

        elements = [lam(e) for e in self.elements]
        return {"#list": elements}


class ITFSet(ITFNode):
    """{ "#set": [ <expr>, ..., <expr> ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFSet):
            return self.elements == other.elements
        return False

    def to_obj(self):
        def lam(e):
            return e.to_obj() if isinstance(e, ITFNode) else e

        elements = [lam(e) for e in self.elements]
        return {"#set": elements}


class ITFMap(ITFNode):
    """{ "#map": [ [ <expr>, <expr> ], ..., [ <expr>, <expr> ] ] }"""

    def __init__(self, elements):
        self.elements = elements

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFMap):
            return self.elements == other.elements
        return False

    def to_obj(self):
        def lam(e):
            return e.to_obj() if isinstance(e, ITFNode) else e

        elements = [[lam(e) for e in p] for p in self.elements]
        return {"#map": elements}


class ITFState(ITFNode):
    """
    {
        "#meta": <optional object>,
        "<var1>": <expr>,
        ...
        "<varN>": <expr>
    }
    """

    def __init__(self, var_value_map, meta=None):
        self.meta = meta
        self.var_value_map = var_value_map

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFState):
            return self.meta == other.meta and self.var_value_map == other.var_value_map
        return False

    def to_obj(self):
        def lam(e):
            return e.to_obj() if isinstance(e, ITFNode) else e

        var_value_map = {k: lam(v) for k, v in self.var_value_map.items()}
        return {"#meta": self.meta} | var_value_map


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

    def __init__(self, vars, states, meta=None):
        self.meta = meta
        self.vars = vars
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

    def to_obj(self):
        return {
            "#meta": self.meta,
            "vars": self.vars,
            "states": [e.to_obj() for e in self.states],
        }


class Visitor:
    def __init__(self):
        pass

    def visit(self, node, *arg, **kw):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node, *arg, **kw)

    def visit_ITFSet(self, node, *arg, **kw):
        pass

    def visit_ITFMap(self, node, *arg, **kw):
        pass

    def visit_ITFState(self, node, *arg, **kw):
        pass

    def visit_ITFTrace(self, node, *arg, **kw):
        pass


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
