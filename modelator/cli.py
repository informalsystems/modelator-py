import sys

import fire

from .tlc.cli import Tlc
from .util.cli import Util


class App:
    def __init__(self, stdin):
        self._stdin = stdin
        self.tlc = Tlc(stdin)
        self.util = Util(stdin)

    def example(*_ignore, foo=True, bar=None, wiz):
        print(f"{foo=} {bar=} {wiz=}")


def cli():
    if len(sys.argv) == 1:
        raise Exception(
            "Solely stdin input is not yet supported (arguments must be passed)"
        )
    else:
        app = App(sys.stdin)
        fire.Fire(app)


if __name__ == "__main__":
    cli()
