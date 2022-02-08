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
