from .tlc.cli import Tlc


class Util:
    def __init__(self, stdin, stdout):
        self._stdin = stdin
        self._stdout = stdout
        self.tlc = Tlc(stdin, stdout)
