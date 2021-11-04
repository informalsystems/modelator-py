import os
import tempfile

from recordclass import recordclass

from .raw import RawCmd, exec_apalache_raw_cmd

# mypy: ignore-errors

pure_cmd_fields = (
    "jar",  # Location of Apalache jar (full path with suffix like apalache-pkg-0.xx.0-full.jar)
    "args",  # Apalache args
    "files",  # Current working directory for child shell process
)

PureCmd = recordclass(
    "PureCmd", pure_cmd_fields, defaults=(None,) * len(pure_cmd_fields)
)


def exec_apalache_pure_cmd(cmd: PureCmd):  # type: ignore

    raw_cmd = RawCmd()
    raw_cmd.args = cmd.args
    raw_cmd.jar = cmd.jar
    raw_cmd.mem = True
    raw_cmd.cleanup = True

    result = None
    with tempfile.TemporaryDirectory(prefix="mbt-python-apalache-temp-dir-") as dirname:
        raw_cmd.cwd = dirname
        for filename, file_content_str in cmd.files.items():
            full_path = os.path.join(dirname, filename)
            with open(full_path, "w") as fd:
                fd.write(file_content_str)

        result = exec_apalache_raw_cmd(raw_cmd)

    stdout_pretty = result.process.stdout.decode("unicode_escape")
    stderr_pretty = result.process.stderr.decode("unicode_escape")

    ret = {}

    ret["shell_cmd"] = result.process.args
    ret["return_code"] = result.process.returncode
    ret["stdout"] = stdout_pretty
    ret["stderr"] = stderr_pretty
    ret["files"] = result.files

    return ret
