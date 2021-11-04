import sys

import fire

from .apalache.cli import Apalache


class App:
    def __init__(self, stdin):
        self.stdin = stdin
        self.apalache = Apalache(stdin)

    def example(*_ignore, foo=True, bar=None, wiz):
        print(f"{foo=}{bar=}{wiz=}")


def cli():
    if len(sys.argv) == 1:
        """
        Optionally take the command structure entirely from a json at stdin
        """
        raise Exception("Purely stdin input is not yet supported")
    else:
        app = App(sys.stdin)
        fire.Fire(app)


if __name__ == "__main__":
    cli()
