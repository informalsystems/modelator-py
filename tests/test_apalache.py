import json
import logging
import os
import sys
import unittest.mock

import fire
import pytest

from modelator.apalache.cli import Apalache
from modelator.apalache.raw import ApalacheArgs, RawCmd, apalache_raw, stringify_raw_cmd

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
    reason="Apalache 0.17.1 cannot guarantee correct parallel execution in all cases"
)
def test_pure_from_stdin_smoke():

    example = "apalache_pure_example.json"
    example_fn = os.path.join(get_resource_dir(), example)

    def write_command_to_resource_dir():
        data = {
            "jar": get_apalache_path(),
            "args": {
                "cmd": "check",
                "max_error": 2,
                "view": "View",
                "inv": "IsThree",
                "config": "2PossibleTraces.cfg",
                "file": "2PossibleTracesTests.tla",
            },
            "files": {},
        }

        fns = ["2PossibleTraces.cfg", "2PossibleTraces.tla", "2PossibleTracesTests.tla"]

        for fn in fns:
            full_fn = os.path.join(get_resource_dir(), fn)
            with open(full_fn, "r") as fd:
                data["files"][fn] = fd.read()  # type: ignore

        with open(example_fn, "w") as fd:
            fd.write(json.dumps(data, indent=4))

    write_command_to_resource_dir()

    data = None
    with open(example_fn, "r") as fd:
        data = fd.read()
    stdin = unittest.mock.Mock()
    stdin.read = lambda: data
    app = Apalache(stdin)
    app.pure()


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_stdin_smoke():

    example = "apalache_raw_example.json"
    example_fn = os.path.join(get_resource_dir(), example)

    def write_command_to_resource_dir():
        data = {
            "jar": get_apalache_path(),
            "cwd": get_resource_dir(),
            "args": {
                "cmd": "check",
                "max_error": 2,
                "view": "View",
                "inv": "IsThree",
                "config": "2PossibleTraces.cfg",
                "file": "2PossibleTracesTests.tla",
            },
        }

        with open(example_fn, "w") as fd:
            fd.write(json.dumps(data, indent=4))

    write_command_to_resource_dir()

    data = None
    with open(example_fn, "r") as fd:
        data = fd.read()
    stdin = unittest.mock.Mock()
    stdin.read = lambda: data
    app = Apalache(stdin)
    app.raw(stdin=True)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_command_line_args_smoke():
    args = [
        "raw",
        "--cmd=check",
        "--max-error=2",
        "--view=View",
        "--inv=IsThree",
        f"--config={os.path.join(get_resource_dir(),'2PossibleTraces.cfg')}",
        f"--file={os.path.join(get_resource_dir(), '2PossibleTracesTests.tla')}",
        f"--jar={get_apalache_path()}",
        "--out-dir=apalache-out",
        f"--cwd={get_resource_dir()}",
    ]
    app = Apalache(sys.stdin)
    fire.Fire(app, args)


@pytest.mark.skip(
    reason="The 'apalache raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly_parse():
    # apalache-mc parse --out-dir=apalache-out --output=parsed.tla 2PossibleTracesTests.tla
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
    result = apalache_raw(cmd=cmd)
    LOG.debug(result.process.stderr.decode("unicode_escape"))
    LOG.debug(result.process.stdout.decode("unicode_escape"))


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
    result = apalache_raw(cmd=cmd)
    LOG.debug(result.process.stdout.decode("unicode_escape"))
    LOG.debug(result.process.stderr.decode("unicode_escape"))
    LOG.debug("\n".join(list(result.files.keys())))
