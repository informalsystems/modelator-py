import logging
import os
import sys
import unittest.mock
from pathlib import Path

import fire

from modelator.apalache import (
    Apalache,
    RawCmd,
    exec_apalache_raw_cmd,
    stringify_raw_cmd,
)

# import pytest


LOG = logging.getLogger(__name__)


def get_apalache_path():
    this_file_path = Path(__file__)
    project_dir = this_file_path.parent.parent
    apalache_jar = "apalache-pkg-0.17.0-full.jar"
    apalache_path = os.path.join(project_dir, apalache_jar)
    return apalache_path


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.cmd = "check"
    cmd.profiling = True
    cmd.inv = "InvariantFoo"
    cmd.file = "spec.tla"
    cmd.out_dir = "out/"
    cmd.jar = get_apalache_path()
    cmd.cinit = "CInit"
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)
    assert 0


# @pytest.mark.skip(
# reason="The 'apalache raw' command has side effects like dirtying the filesystem"
# )
def test_raw_direct():
    cmd = RawCmd()
    cmd.cmd = "noop"
    exec_apalache_raw_cmd(cmd)


# @pytest.mark.skip(
# reason="The 'apalache raw' command has side effects like dirtying the filesystem"
# )
def test_raw_direct_smoke():
    data = {"cmd": "noop"}
    cmd = RawCmd(**data)
    exec_apalache_raw_cmd(cmd)


# @pytest.mark.skip(
# reason="The 'apalache raw' command has side effects like dirtying the filesystem"
# )
def test_raw_from_stdin_smoke():
    data = '{"cmd":"noop"}'
    stdin = unittest.mock.Mock()
    stdin.read = lambda: data
    app = Apalache(stdin)
    app.raw(stdin=True)


# @pytest.mark.skip(
# reason="The 'apalache raw' command has side effects like dirtying the filesystem"
# )
def test_raw_from_command_line_args_smoke():
    args = ["raw", "--cmd=" "noop"]
    app = Apalache(sys.stdin)
    fire.Fire(app, args)
