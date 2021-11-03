import json
import sys

import fire
from apalache import Apalache


class App:
    def __init__(self, stdin):
        self.stdin = stdin
        self.Apalache = Apalache(stdin)

    def example(*_ignore, foo=True, bar=None, wiz):
        print(f"{foo=}{bar=}{wiz=}")


if __name__ == "__main__":

    """
    # Checks "cmd" field for the actual command, uses the rest of the json as
    # input
    cli < cmd.json

    # Takes an Apalache jar and executes raw Apalache commands, does not move
    # things around the filesystem or anything like that
    cli apalache raw <apalache cli args> <--

    # Reads json from stdin which specifies the raw Apalache cmd
    cli apalache pure <--out-dir,--temp-dir,--(no)cleanup>

    """
    if len(sys.argv) == 1:
        """
        Optionally take the command structure entirely from a json at stdin
        """
        json.loads(sys.stdin.read())
        # TODO: impl
    else:
        app = App(sys.stdin)
        fire.Fire(app)
