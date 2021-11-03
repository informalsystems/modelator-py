import sys

import fire
from apalache import ApalachePure, ApalacheRaw

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
        # TODO: use stdin
        pass
    else:
        cli = {"apalache": {"raw": ApalacheRaw, "pure": ApalachePure}}
        fire.Fire(cli)
