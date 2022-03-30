import json
import logging
import os
import unittest.mock
import sys

import pytest

from modelator.tlc.cli import Tlc
from modelator.tlc.raw import RawCmd, TlcArgs, stringify_raw_cmd

from ..helper import get_resource_dir, get_tlc_path

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    """
    Use for debugging - ensure that the shell command generated is sensible.
    """
    cmd = RawCmd()
    cmd.jar = get_tlc_path()
    args = TlcArgs()
    args.cleanup = True
    args.workers = "auto"
    args.config = "HelloWorld.cfg"
    args.file = "HelloWorld.tla"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    assert cmd_str.endswith(
        "tlc2.TLC -cleanup -config HelloWorld.cfg -workers auto HelloWorld.tla"
    )


def test_pure_with_json():
    def get_files():

        fns = [
            "HelloWorld.cfg",
            "HelloWorld.tla",
        ]

        ret = {}

        for fn in fns:
            full_fn = os.path.join(get_resource_dir(), fn)
            with open(full_fn, "r") as fd:
                ret[fn] = fd.read()  # type: ignore

        return ret

    data = {
        "jar": get_tlc_path(),
        "args": {
            "workers": "auto",
            "config": "HelloWorld.cfg",
            "file": "HelloWorld.tla",
        },
        "files": get_files(),
    }

    stdin = unittest.mock.Mock()
    stdin.read = lambda: json.dumps(data)
    out_obj = None
    calls = 0
    stdout = unittest.mock.Mock()

    def write_out(s):
        nonlocal out_obj
        nonlocal calls
        calls += 1
        # LOG.debug(s)
        # with open("debug.txt", "w") as fd:
        # fd.write(s)
        print("WRITEOUT", type(s), len(s), calls)
        # out_obj = json.loads(s)

    stdout.write = write_out
    app = Tlc(stdin, stdout)
    app.pure()
    # Check that TLC finishes
    # assert "Finished in" in out_obj["stdout"]


@pytest.mark.skip(
    reason="The 'tlc raw' command has side effects. E.g. polluting the filesystem"
)
def test_raw_with_json():
    """
    Use for debugging - using the raw interface is not idempotent
    """

    data = {
        "jar": get_tlc_path(),
        "cwd": get_resource_dir(),
        "args": {
            "cleanup": False,
            "workers": "auto",
            "config": "HelloWorld.cfg",
            "file": "HelloWorld.tla",
        },
    }

    stdin = unittest.mock.Mock()
    stdin.read = lambda: json.dumps(data)
    stdout = unittest.mock.Mock()
    stdout.write = lambda s: None
    app = Tlc(stdin)
    app.raw(json=True)
