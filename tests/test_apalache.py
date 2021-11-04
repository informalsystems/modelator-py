import json
import logging
import os
import sys
import unittest.mock

import fire
import pytest

from modelator.apalache.cli import Apalache
from modelator.apalache.raw import (
    ApalacheArgs,
    RawCmd,
    exec_apalache_raw_cmd,
    stringify_raw_cmd,
)

from .util import get_apalache_path, get_resource_dir

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.jar = get_apalache_path()
    args = ApalacheArgs()
    args.cmd = "check"
    args.profiling = True
    args.inv = "InvariantFoo"
    args.file = "spec.tla"
    args.out_dir = "apalache-out"
    args.cinit = "CInit"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_parse():
    # apalache-mc check --max-error=2 --view=View --inv=IsThree --config=2PossibleTraces.cfg 2PossibleTracesTests.tla
    cmd = RawCmd()
    cmd.jar = get_apalache_path()
    cmd.cwd = get_resource_dir()
    args = ApalacheArgs()
    args.cmd = "parse"
    args.file = "2PossibleTracesTests.tla"
    args.out_dir = "apalache-out"
    args.write_intermediate = True
    args.output = "parsed.tla"
    cmd.args = args
    LOG.debug(stringify_raw_cmd(cmd))
    result = exec_apalache_raw_cmd(cmd)
    LOG.debug(result.stdout.decode("unicode_escape"))
    LOG.debug(result.stderr.decode("unicode_escape"))
    assert 0


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_check():
    # apalache-mc check --max-error=2 --view=View --inv=IsThree --config=2PossibleTraces.cfg 2PossibleTracesTests.tla
    cmd = RawCmd()
    cmd.mem = True
    cmd.cleanup = True
    cmd.jar = get_apalache_path()
    cmd.cwd = get_resource_dir()
    args = ApalacheArgs()
    args.cmd = "check"
    args.max_error = 2
    args.view = "View"
    args.inv = "IsThree"
    args.config = "2PossibleTraces.cfg"
    args.file = "2PossibleTracesTests.tla"
    args.out_dir = "apalache-out"
    cmd.args = args
    LOG.debug(stringify_raw_cmd(cmd))
    result = exec_apalache_raw_cmd(cmd)
    LOG.debug(result.process.stdout.decode("unicode_escape"))
    LOG.debug(result.process.stderr.decode("unicode_escape"))
    LOG.debug("\n".join(list(result.files.keys())))


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_stdin_smoke():

    stdin_json = {
        "mem": True,
        "cleanup": True,
        "cwd": "~/Documents/work/mbt-python/tests/resource",
        "jar": "~/Documents/work/mbt-python/apalache-pkg-0.17.1-full.jar",
        "args": {
            "cmd": "check",
            "max_error": 2,
            "view": "View",
            "inv": "IsThree",
            "config": "2PossibleTraces.cfg",
            "file": "2PossibleTracesTests.tla",
            "out_dir": "apalache-out",
        },
    }
    data = json.dumps(stdin_json)
    stdin = unittest.mock.Mock()
    stdin.read = lambda: data
    app = Apalache(stdin)
    app.raw(stdin=True)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_command_line_args_smoke():
    args = ["raw", "--cmd=" "noop"]
    app = Apalache(sys.stdin)
    fire.Fire(app, args)


def test_pure_from_stdin_smoke():
    data = None
    path = os.path.join(get_resource_dir(), "apalache_pure_example.json")
    with open(path, "r") as fd:
        data = fd.read()
    stdin = unittest.mock.Mock()
    stdin.read = lambda: data
    app = Apalache(stdin)
    app.pure()
