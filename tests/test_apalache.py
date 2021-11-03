import logging
import os
import sys
import unittest.mock
from pathlib import Path

import fire
import pytest

from modelator.apalache import (
    Apalache,
    RawCmd,
    exec_apalache_raw_cmd,
    stringify_raw_cmd,
)

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
    apalache_jar = "apalache-pkg-0.17.0-full.jar"
    apalache_path = os.path.join(project_dir, apalache_jar)
    return apalache_path


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.cmd = "check"
    cmd.profiling = True
    cmd.inv = "InvariantFoo"
    cmd.file = "spec.tla"
    cmd.out_dir_relative_to_cwd = "apalache-out"
    cmd.jar = get_apalache_path()
    cmd.cinit = "CInit"
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_smoke():
    cmd = RawCmd()
    # apalache-mc check --max-error=2 --view=View --inv=IsThree --config=2PossibleTraces.cfg 2PossibleTracesTests.tla
    cmd.cmd = "check"
    cmd.max_error = 2
    cmd.view = "View"
    cmd.inv = "IsThree"
    cmd.config = "2PossibleTraces.cfg"
    cmd.file = "2PossibleTracesTests.tla"
    cmd.out_dir_relative_to_cwd = "apalache-out"
    cmd.jar = get_apalache_path()
    cmd.cwd = get_resource_dir()
    LOG.debug(stringify_raw_cmd(cmd))
    result = exec_apalache_raw_cmd(cmd)
    LOG.debug(result.stdout)
    LOG.debug(result.stderr)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_direct_smoke():
    data = {"cmd": "noop"}
    cmd = RawCmd(**data)
    exec_apalache_raw_cmd(cmd)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_stdin_smoke():
    data = '{"cmd":"noop"}'
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
