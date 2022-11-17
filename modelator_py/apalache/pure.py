import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from ..helper import get_dirnames_in_dir, read_entire_dir_contents
from .args import ApalacheArgs
from .raw import RawCmd, apalache_raw

LOG = logging.getLogger(__name__)

# mypy: ignore-errors


@dataclass
class PureCmd:
    jar: Optional[
        str
    ] = None  # Location of Apalache jar (full path with suffix like apalache.jar)
    args: Optional[ApalacheArgs] = None  # Apalache args
    files: Optional[str] = None  # Current working directory for child shell process


# Used to overwrite Apalache's "--out-dir" flag
APALACHE_OUT_DIR_NAME = "out"


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
    cmd.args = ApalacheArgs(**json["args"])
    cmd.files = json["files"]
    return cmd


def read_apalache_output_into_memory(full_dirname):
    """
    Read files output by Apalache into a dictionary

    Apalache writes output of a command with argument --out-dir=<dir> to a
    directory inside <dir>/<identifier>/<identifier>, (3 levels deep).
    """

    subdirs = get_dirnames_in_dir(full_dirname)

    assert (
        APALACHE_OUT_DIR_NAME in os.path.dirname(sd) for sd in subdirs
    ), f"[Apalache output directory has unexpected structure, contains subdirs] [{subdirs=}]: "

    full_dirname = os.path.join(full_dirname, APALACHE_OUT_DIR_NAME)

    # Traverse two directories deep

    subdirs = get_dirnames_in_dir(full_dirname)
    assert (
        len(subdirs) == 1
    ), f"[Apalache output directory has unexpected structure, contains subdirs] [{subdirs=}]: "
    full_dirname = subdirs[0]

    subdirs = get_dirnames_in_dir(full_dirname)
    assert (
        len(subdirs) == 1
    ), f"[Apalache output subdirectory has unexpected structure, contains subdirs] [{subdirs=}]"
    full_dirname = subdirs[0]

    LOG.debug(f"{full_dirname=}")

    all_files = read_entire_dir_contents(full_dirname)
    all_files = {os.path.basename(fn): content for fn, content in all_files.items()}

    subdirs = get_dirnames_in_dir(full_dirname)

    INTERMEDIATE_DIR = "intermediate"
    if os.path.join(full_dirname, INTERMEDIATE_DIR) in subdirs:
        intermediate_files = read_entire_dir_contents(
            os.path.join(full_dirname, INTERMEDIATE_DIR)
        )

        def filename(full_filename):
            base = os.path.basename(full_filename)
            return os.path.join(INTERMEDIATE_DIR, base)

        all_files = {
            **all_files,
            **{filename(fn): content for fn, content in intermediate_files.items()},
        }

    return all_files


def apalache_pure(*, cmd: PureCmd = None, json=None):  # type: ignore
    """
    Run a Apalache command using either a PureCmd object, or build the PureCmd from json.

    Run Apalache without side effects in a temporary directory.

    Returns an ExecutionResult with .process and .files properties. Contains the
    subprocess result, and the list of filesystem files (and contents).
    """

    assert not (cmd is not None and json is not None)
    assert (cmd is not None) or (json is not None)
    if json is not None:
        cmd = json_to_cmd(json)

    raw_cmd = RawCmd()
    raw_cmd.args = cmd.args
    raw_cmd.jar = cmd.jar

    if raw_cmd.args.out_dir is not None:
        raise Exception(
            "--out-dir flag value is not None but Apalache pure command overwrites\
this flag. Do not include a value for this flag."
        )
    raw_cmd.args.out_dir = "out"

    ret = {}

    result = None

    with tempfile.TemporaryDirectory(
        prefix="modelator-py-apalache-temp-dir-"
    ) as dirname:
        raw_cmd.cwd = dirname
        for filename, file_content_str in cmd.files.items():
            full_path = os.path.join(dirname, filename)
            with open(full_path, "w") as fd:
                fd.write(file_content_str)

        result = apalache_raw(cmd=raw_cmd)

        try:
            ret["files"] = read_apalache_output_into_memory(dirname)
        except FileNotFoundError:
            ret["files"] = dict()

        # Throw out the files that the user originally gave as input
        ret["files"] = {
            fn: content for fn, content in ret["files"].items() if fn not in cmd.files
        }

    stdout_pretty = result.stdout.decode()
    stderr_pretty = result.stderr.decode()

    ret["shell_cmd"] = result.args
    ret["return_code"] = result.returncode
    ret["stdout"] = stdout_pretty
    ret["stderr"] = stderr_pretty

    return ret
