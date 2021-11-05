import os
import tempfile

from recordclass import recordclass

from modelator.tlc.args import TlcArgs

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

    # TODO: doesn't work yet, have to figure out best way to clear up

    raw_cmd = RawCmd()
    raw_cmd.args = cmd.args
    raw_cmd.jar = cmd.jar
    raw_cmd.mem = True
    raw_cmd.cleanup = True

    result = None
    with tempfile.TemporaryDirectory(prefix="mbt-python-tlc-temp-dir-") as dirname:
        raw_cmd.cwd = dirname
        for filename, file_content_str in cmd.files.items():
            full_path = os.path.join(dirname, filename)
            with open(full_path, "w") as fd:
                fd.write(file_content_str)

        result = tlc_raw(cmd=raw_cmd)

    stdout_pretty = result.process.stdout.decode("unicode_escape")
    stderr_pretty = result.process.stderr.decode("unicode_escape")

    ret = {}

    ret["shell_cmd"] = result.process.args
    ret["return_code"] = result.process.returncode
    ret["stdout"] = stdout_pretty
    ret["stderr"] = stderr_pretty
    ret["files"] = result.files

    return ret
