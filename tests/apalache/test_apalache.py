import json
import logging
import os
import unittest.mock
from contextlib import redirect_stdout
from io import StringIO

import pytest

from modelator_py.apalache.cli import Apalache
from modelator_py.apalache.raw import ApalacheArgs, RawCmd, stringify_raw_cmd

from ..helper import get_apalache_path, get_resource_dir

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    """
    Use for debugging - ensure that the shell command generated is sensible.
    """
    cmd = RawCmd()
    cmd.jar = get_apalache_path()
    args = ApalacheArgs()
    args.cmd = "check"
    args.out_dir = "foo"
    args.nworkers = 8
    args.config = "HelloWorldTyped.cfg"
    args.file = "HelloWorldTyped.tla"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    assert cmd_str.endswith(
        "--out-dir=foo check --config=HelloWorldTyped.cfg --nworkers=8 HelloWorldTyped.tla"
    )


def test_pure_with_json_write_intermediate_false():
    def get_files():

        fns = [
            "HelloWorldTyped.cfg",
            "HelloWorldTyped.tla",
        ]

        ret = {}

        for fn in fns:
            full_fn = os.path.join(get_resource_dir(), fn)
            with open(full_fn, "r") as fd:
                ret[fn] = fd.read()  # type: ignore

        return ret

    data = {
        "jar": get_apalache_path(),
        "args": {
            "cmd": "check",
            "nworkers": 8,
            "config": "HelloWorldTyped.cfg",
            "file": "HelloWorldTyped.tla",
            "write_intermediate": False,
        },
        "files": get_files(),
    }

    stdin = unittest.mock.Mock()
    stdin.read = lambda: json.dumps(data)

    app = Apalache(stdin)
    s = StringIO()
    with redirect_stdout(s):
        app.pure()
    # Check that Apalache finishes
    json_obj = json.loads(s.getvalue())
    LOG.debug(json.dumps(json_obj, indent=4))

    # HelloWorldTyped.tla should contain an error
    assert "Checker has found an error" in json_obj["stdout"]
    # There should be a counterexample
    assert any(fn.startswith("counterexample") for fn in json_obj["files"])


def test_pure_with_json_write_intermediate_true():
    def get_files():

        fns = [
            "HelloWorldTyped.cfg",
            "HelloWorldTyped.tla",
        ]

        ret = {}

        for fn in fns:
            full_fn = os.path.join(get_resource_dir(), fn)
            with open(full_fn, "r") as fd:
                ret[fn] = fd.read()  # type: ignore

        return ret

    data = {
        "jar": get_apalache_path(),
        "args": {
            "cmd": "check",
            "nworkers": 8,
            "config": "HelloWorldTyped.cfg",
            "file": "HelloWorldTyped.tla",
            "write_intermediate": True,
        },
        "files": get_files(),
    }

    stdin = unittest.mock.Mock()
    stdin.read = lambda: json.dumps(data)

    app = Apalache(stdin)
    s = StringIO()
    with redirect_stdout(s):
        app.pure()
    # Check that Apalache finishes
    json_obj = json.loads(s.getvalue())
    LOG.debug(json.dumps(json_obj, indent=4))

    # HelloWorldTyped.tla should contain an error
    assert "Checker has found an error" in json_obj["stdout"]
    # There should be a counterexample
    assert any(fn.startswith("counterexample") for fn in json_obj["files"])
    # There should be some intermediate files
    assert any(fn.startswith("intermediate") for fn in json_obj["files"])


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects. E.g. polluting the filesystem"
)
def test_raw_with_json():
    """
    Use for debugging - using the raw interface is not idempotent

    This is a convenient debugging test, and you could write your own assertions.
    """

    data = {
        "jar": get_apalache_path(),
        "cwd": get_resource_dir(),
        "args": {
            "cmd": "check",
            "out_dir": "foo",
            "nworkers": 8,
            "config": "HelloWorldTyped.cfg",
            "file": "HelloWorldTyped.tla",
        },
    }

    stdin = unittest.mock.Mock()
    stdin.read = lambda: json.dumps(data)
    app = Apalache(stdin)
    app.raw(json=True)
