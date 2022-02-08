from abc import ABCMeta, abstractmethod


class ITFNode(object):
    __metaclass__ = ABCMeta

    def __repr__(self):
        return repr(self.to_obj())

    @abstractmethod
    def to_obj():
        pass


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
        lam = lambda e: e.to_obj() if isinstance(e, ITFNode) else e
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
        lam = lambda e: e.to_obj() if isinstance(e, ITFNode) else e
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
        if meta is None:
            meta = {
                "source": "https://github.com/informalsystems/modelator",
                "bug-report": "https://github.com/informalsystems/modelator/issues",
            }
        self.meta = meta
        self.var_value_map = var_value_map

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, ITFState):
            return self.meta == other.meta and self.var_value_map == other.var_value_map
        return False

    def to_obj(self):
        lam = lambda e: e.to_obj() if isinstance(e, ITFNode) else e
        var_value_map = {k: lam(v) for k, v in self.var_value_map.items()}
        return {"#meta": self.meta} | var_value_map


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
