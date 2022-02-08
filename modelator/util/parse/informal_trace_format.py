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
        return repr(self.to_obj())

    def to_obj(self):
        return {"#set": self.elements}


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
        return repr(self.to_obj())

    def to_obj(self):
        return {"#map": self.elements}


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
