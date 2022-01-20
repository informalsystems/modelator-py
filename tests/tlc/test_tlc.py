import json
import logging
import os
import unittest.mock

import pytest

from modelator.tlc.cli import Tlc
from modelator.tlc.raw import RawCmd, TlcArgs, stringify_raw_cmd, tlc_raw

from ..helper import get_resource_dir, get_tlc_path

LOG = logging.getLogger(__name__)


def test_stringify_raw_cmd():
    cmd = RawCmd()
    cmd.jar = get_tlc_path()
    args = TlcArgs()
    args.cleanup = True
    args.workers = "auto"
    args.config = "2PossibleTracesTlc.cfg"
    args.file = "2PossibleTraces.tla"
    cmd.args = args
    cmd_str = stringify_raw_cmd(cmd)
    LOG.debug(cmd_str)


@pytest.mark.skip(
    reason="Tlc 2.16 cannot guarantee correct parallel execution in all cases"
)
def test_pure_from_stdin_smoke():

    example = "tlc_pure_example.json"
    example_fn = os.path.join(get_resource_dir(), example)

    def write_command_to_resource_dir():
        data = {
            "jar": get_tlc_path(),
            "args": {
                "cleanup": False,
                "workers": "auto",
                "config": "2PossibleTracesTlc.cfg",
                "file": "2PossibleTraces.tla",
                "userfile": "tlc-pure-test-userfile.txt",
            },
            "files": {},
        }

        fns = [
            "2PossibleTracesTlc.cfg",
            "2PossibleTraces.tla",
            "2PossibleTracesTests.tla",
        ]

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
    app = Tlc(stdin)
    app.pure()


@pytest.mark.skip(
    reason="The 'tlc raw' command has side effects like dirtying the filesystem"
)
def test_raw_from_stdin_smoke():

    example = "tlc_raw_example.json"
    example_fn = os.path.join(get_resource_dir(), example)

    def write_command_to_resource_dir():
        data = {
            "jar": get_tlc_path(),
            "cwd": get_resource_dir(),
            "args": {
                "cleanup": False,
                "workers": "auto",
                "config": "2PossibleTracesTlc.cfg",
                "file": "2PossibleTraces.tla",
                "userfile": "tlc-raw-test-userfile.txt",
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
    app = Tlc(stdin)
    app.raw(stdin=True)


@pytest.mark.skip(
    reason="The 'tlc raw' command has side effects like dirtying the filesystem"
)
def test_raw_directly():
    # java -jar tla2tools.jar tlc2.TLC -cleanup -workers 'auto' -config 2PossibleTracesTlc.cfg 2PossibleTraces.tla
    cmd = RawCmd()
    cmd.jar = get_tlc_path()
    cmd.cwd = get_resource_dir()
    args = TlcArgs()
    args.cleanup = False
    args.workers = "auto"
    args.config = "2PossibleTracesTlc.cfg"
    args.file = "2PossibleTraces.tla"
    args.userfile = "tlc-raw-test-userfile.txt"
    cmd.args = args
    LOG.debug(stringify_raw_cmd(cmd))
    result = tlc_raw(cmd=cmd)
    LOG.debug(result.process.stdout.decode("unicode_escape"))
    LOG.debug(result.process.stderr.decode("unicode_escape"))
