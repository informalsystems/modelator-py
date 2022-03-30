import json
import logging
import os
import unittest.mock
from contextlib import redirect_stdout
from io import StringIO

import pytest

from modelator.apalache.cli import Apalache
from modelator.apalache.raw import RawCmd, ApalacheArgs, stringify_raw_cmd

from ..helper import get_resource_dir, get_apalache_path

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    """
    Use for debugging - ensure that the shell command generated is sensible.
    """
    cmd = RawCmd()
    cmd.jar = get_apalache_path()
    args = Apalache()
    args.cleanup = True
    args.workers = "auto"
    args.config = "HelloWorld.cfg"
    args.file = "HelloWorld.tla"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


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

    app = Tlc(stdin)
    s = StringIO()
    with redirect_stdout(s):
        app.pure()
    # Check that TLC finishes
    json_obj = json.loads(s.getvalue())
    assert "Finished in" in json_obj["stdout"]


@pytest.mark.skip(
    reason="The 'tlc raw' command has side effects. E.g. polluting the filesystem"
)
def test_raw_with_json():
    """
    Use for debugging - using the raw interface is not idempotent

    This is a convenient debugging test, and you could write your own assertions.
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
    app = Tlc(stdin)
    app.raw(json=True)
