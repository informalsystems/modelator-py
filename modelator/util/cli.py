from .tlc.cli import Tlc


class Util:
    def __init__(self, stdin):
        self._stdin = stdin
        self.tlc = Tlc(stdin)
