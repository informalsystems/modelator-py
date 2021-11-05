import os
import tempfile

from recordclass import recordclass

from modelator.tlc.args import TlcArgs

from ..util import read_entire_dir_contents
from .raw import RawCmd, tlc_raw

# mypy: ignore-errors

pure_cmd_fields = (
    "jar",  # Location of tla2tools jar (full path with suffix like tla2tools.jar)
    "args",  # Tlc args
    "files",  # Current working directory for child shell process
)

PureCmd = recordclass(
    "PureCmd", pure_cmd_fields, defaults=(None,) * len(pure_cmd_fields)
)


def tlc_pure(*, cmd: PureCmd = None, json_obj=None):  # type: ignore
    """
    Execute a Tlc command using either a PureCmd object, or build the PureCmd from json

    Returns an ExecutionResult with .process and .files properties.
    Contains the subprocess result, and the list of filesystem files (and contents).
    """
    assert not (cmd is not None and json_obj is not None)

    if json_obj is not None:
        json_obj = {
            "files": None,
            "jar": None,
            "args": None,
        } | json_obj
        cmd = PureCmd()
        cmd.jar = json_obj["jar"]
        cmd.args = TlcArgs(**json_obj["args"])
        cmd.files = json_obj["files"]

    raw_cmd = RawCmd()
    raw_cmd.args = cmd.args
    # Always specify tlc '-cleanup'
    raw_cmd.args.cleanup = True
    raw_cmd.jar = cmd.jar

    ret = {}

    process_result = None

    with tempfile.TemporaryDirectory(prefix="mbt-python-tlc-temp-dir-") as dirname:
        raw_cmd.cwd = dirname
        for filename, file_content_str in cmd.files.items():
            full_path = os.path.join(dirname, filename)
            with open(full_path, "w") as fd:
                fd.write(file_content_str)

        process_result = tlc_raw(cmd=raw_cmd)

        all_files = read_entire_dir_contents(dirname)
        all_files = {os.path.basename(fn): content for fn, content in all_files.items()}
        # Throw out the files that the user gave as input
        ret["files"] = {
            fn: content for fn, content in all_files.items() if fn not in cmd.files
        }

    stdout_pretty = process_result.stdout.decode("unicode_escape")
    stderr_pretty = process_result.stderr.decode("unicode_escape")

    ret["shell_cmd"] = process_result.args
    ret["return_code"] = process_result.returncode
    ret["stdout"] = stdout_pretty
    ret["stderr"] = stderr_pretty

    return ret
