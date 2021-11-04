import json
import logging
import os
import sys
import unittest.mock
from pathlib import Path

import fire
import pytest

from modelator.apalache.cli import Apalache
from modelator.apalache.raw import RawCmd, exec_apalache_raw_cmd, stringify_raw_cmd

LOG = logging.getLogger(__name__)


def get_tests_dir():
    this_file_path = Path(__file__)
    return this_file_path.parent


def get_project_dir():
    tests_dir = get_tests_dir()
    return tests_dir.parent


def get_resource_dir():
    tests_dir = get_tests_dir()
    return os.path.join(tests_dir, "resource")


def get_apalache_path():
    project_dir = get_project_dir()
    apalache_jar = "apalache-pkg-0.17.1-full.jar"
    apalache_path = os.path.join(project_dir, apalache_jar)
    return apalache_path


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.cmd = "check"
    cmd.profiling = True
    cmd.inv = "InvariantFoo"
    cmd.file = "spec.tla"
    cmd.out_dir = "apalache-out"
    cmd.jar = get_apalache_path()
    cmd.cinit = "CInit"
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_parse():
    cmd = RawCmd()
    # apalache-mc check --max-error=2 --view=View --inv=IsThree --config=2PossibleTraces.cfg 2PossibleTracesTests.tla
    cmd.cmd = "parse"
    cmd.file = "2PossibleTracesTests.tla"
    cmd.out_dir = "apalache-out"
    cmd.write_intermediate = True
    cmd.output = "parsed.tla"
    cmd.jar = get_apalache_path()
    cmd.cwd = get_resource_dir()
    LOG.debug(stringify_raw_cmd(cmd))
    result = exec_apalache_raw_cmd(cmd)
    LOG.debug(result.stdout.decode("unicode_escape"))
    LOG.debug(result.stderr.decode("unicode_escape"))
    assert 0


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_check():
    cmd = RawCmd()
    # apalache-mc check --max-error=2 --view=View --inv=IsThree --config=2PossibleTraces.cfg 2PossibleTracesTests.tla
    cmd.cmd = "check"
    cmd.max_error = 2
    cmd.view = "View"
    cmd.inv = "IsThree"
    cmd.config = "2PossibleTraces.cfg"
    cmd.file = "2PossibleTracesTests.tla"
    cmd.out_dir = "apalache-out"
    cmd.jar = get_apalache_path()
    cmd.cwd = get_resource_dir()
    cmd.mem = True
    cmd.cleanup = True
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
