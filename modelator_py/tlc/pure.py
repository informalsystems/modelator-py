import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from modelator_py.tlc.args import TlcArgs

from ..helper import read_entire_dir_contents
from .raw import RawCmd, tlc_raw

# mypy: ignore-errors


@dataclass
class PureCmd:
    files: Optional[str] = None  # dict : file name -> content
    jar: Optional[
        str
    ] = None  # Location of TLC jar (e.g. full path with suffix like tla2tools.jar)
    args: Optional[TlcArgs] = None  # TLC args


def json_to_cmd(json) -> PureCmd:
    json = {
        **{
            "files": None,
            "jar": None,
            "args": None,
        },
        **json,
    }
    cmd = PureCmd()
    cmd.jar = json["jar"]
    cmd.args = TlcArgs(**json["args"])
    cmd.files = json["files"]
    return cmd


def tlc_pure(*, cmd: PureCmd = None, json=None):  # type: ignore
    """
    Run a TLC command using either a PureCmd object, or build the PureCmd from json.

    Run TLC without side effects in a temporary directory.

    Returns an ExecutionResult with .process and .files properties. Contains the
    subprocess result, and the list of filesystem files (and contents).
    """
    assert not (cmd is not None and json is not None)
    assert (cmd is not None) or (json is not None)

    if json is not None:
        cmd = json_to_cmd(json)

    raw_cmd = RawCmd()
    raw_cmd.args = cmd.args
    # Always specify tlc '-cleanup'
    raw_cmd.args.cleanup = True
    raw_cmd.jar = cmd.jar

    ret = {}

    result = None

    with tempfile.TemporaryDirectory(prefix="modelator-py-tlc-temp-dir-") as dirname:
        raw_cmd.cwd = dirname
        for filename, file_content_str in cmd.files.items():
            full_path = os.path.join(dirname, filename)
            with open(full_path, "w") as fd:
                fd.write(file_content_str)

        result = tlc_raw(cmd=raw_cmd)

        # Read dir contents (not recursively)
        all_files = read_entire_dir_contents(dirname)
        all_files = {os.path.basename(fn): content for fn, content in all_files.items()}
        # Throw out the files that the user gave as input
        ret["files"] = {
            fn: content for fn, content in all_files.items() if fn not in cmd.files
        }

    stdout_pretty = result.stdout.decode()
    stderr_pretty = result.stderr.decode()

    ret["shell_cmd"] = result.args
    ret["return_code"] = result.returncode
    ret["stdout"] = stdout_pretty
    ret["stderr"] = stderr_pretty

    return ret
