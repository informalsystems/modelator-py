import sys

import fire

from .apalache.cli import Apalache
from .tlc.cli import Tlc
from .util.cli import Util


class App:
    def __init__(self, stdin):
        self._stdin = stdin
        self.tlc = Tlc(stdin)
        self.apalache = Apalache(stdin)
        self.util = Util(stdin)

    def easter(self, fizz, *, foo=True, bar=None, wiz):
        """
        This is an easter egg function designed as an example.

        You can read this documentation with `<prefix> easter --help`.

        Arguments:
            fizz : Crackle, pop!
            foo : Is it a bird, is it a plane?
            bar : How much wood would a woodchuck chuck?
            wiz : If Peter Piper picked a peck of pickled peppers...
        """
        print(f"Warning: this is just an example command: {foo=} {bar=} {wiz=}")


def cli():
    """
    Entrypoint for the cli
    """
    if len(sys.argv) == 1:
        raise Exception(
            "Providing only stdin input is not yet supported (at least one argument must be given)"
        )
    else:
        app = App(sys.stdin)
        fire.Fire(app)


if __name__ == "__main__":
    cli()
