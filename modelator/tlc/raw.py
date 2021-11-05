import os
import pathlib
import subprocess

from recordclass import asdict, recordclass

from ..util import delete_dir, read_entire_dir_contents
from .args import TlcArgs

# mypy: ignore-errors

raw_cmd_fields = (
    "mem",  # Read the contents of the output directory into memory (?)
    "cleanup",  # Delete the output directory after Tlc terminates (?)
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of Tlc jar (full path with suffix like tla2tools.jar)
    "args",  # Tlc args
)

RawCmd = recordclass("RawCmd", raw_cmd_fields, defaults=(None,) * len(raw_cmd_fields))


def stringify_raw_cmd(cmd: RawCmd):

    jar = cmd.jar
    args = cmd.args

    def stringify(value):
        # Tlc will not accept capitals
        if isinstance(value, bool):
            return str(value).lower()
        return value

    args = TlcArgs(**{k: stringify(v) for k, v in asdict(args).items()})

    cmd_str = f"""java\
 -cp {jar}\
 tlc2.TLC\
{f" -aril {args.aril}" if args.aril is not None else ""}\
{f" -checkpoint {args.checkpoint}" if args.checkpoint is not None else ""}\
{f" -cleanup" if args.cleanup is not None else ""}\
{f" -config {args.config}" if args.config is not None else ""}\
{f" -continue" if args.cont is not None else ""}\
{f" -coverage {args.coverage}" if args.coverage is not None else ""}\
{f" -deadlock" if args.deadlock is not None else ""}\
{f" -debug" if args.debug is not None else ""}\
{f" -depth {args.depth}" if args.depth is not None else ""}\
{f" -dfid {args.dfid}" if args.dfid is not None else ""}\
{f" -difftrace" if args.difftrace is not None else ""}\
{f" -dump {args.dump}" if args.dump is not None else ""}\
{f" -fp {args.fp}" if args.fp is not None else ""}\
{f" -fpbits {args.fpbits}" if args.fpbits is not None else ""}\
{f" -fpmem {args.fpmem}" if args.fpmem is not None else ""}\
{f" -generateSpecTE" if args.generate_spec_te is not None else ""}\
{f" -gzip" if args.gzip is not None else ""}\
{f" -h" if args.h is not None else ""}\
{f" -maxSetSize {args.max_set_size}" if args.max_set_size is not None else ""}\
{f" -metadir {args.metadir}" if args.metadir is not None else ""}\
{f" -nowarning" if args.nowarning is not args.nowarning else ""}\
{f" -recover {args.recover}" if args.recover is not None else ""}\
{f" -seed {args.seed}" if args.seed is not None else ""}\
{f" -simulate" if args.simulate is not None else ""}\
{f" -terse" if args.terse is not None else ""}\
{f" -tool" if args.tool is not None else ""}\
{f" -userFile {args.userfile}" if args.userfile is not None else ""}\
{f" -view" if args.view is not None else ""}\
{f" -workers {args.workers}" if args.workers is not None else ""}\
{f" {args.file}" if args.file is not None else ""}\
"""

    return cmd_str


ExecutionResult = recordclass(
    "ExecutionResult", ["process", "files"], defaults=(None, None)
)


def tlc_raw(*, cmd: RawCmd = None, json_obj=None):
    """
    Execute a Tlc command using either a RawCmd object, or build the RawCmd from json

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
        cmd = RawCmd()
        cmd.files = json_obj["files"]
        cmd.jar = json_obj["jar"]
        cmd.args = TlcArgs(**json_obj["args"])

    if cmd.cwd is not None:
        cmd.cwd = os.path.expanduser(cmd.cwd)
        if not os.path.isabs(cmd.cwd):
            raise Exception("cwd must be absolute (after expanding user)")
    if cmd.jar is not None:
        cmd.jar = os.path.expanduser(cmd.jar)
        if not os.path.isabs(cmd.jar):
            raise Exception("tlc jar path must be absolute (after expanding user)")

    cmd_str = stringify_raw_cmd(cmd)

    # Semantics a bit complex here - see https://stackoverflow.com/a/15109975/8346628
    process_result = subprocess.run(
        cmd_str, shell=True, capture_output=True, cwd=cmd.cwd
    )

    ret = ExecutionResult()
    ret.process = process_result

    output_dir = None  # TODO:

    if cmd.mem:
        files = read_entire_dir_contents(output_dir)
        ret.files = {os.path.basename(fn): content for fn, content in files.items()}
    if cmd.cleanup:
        if not os.path.isabs(output_dir):
            raise Exception("Output directory TODO: better message")

        output_dir = pathlib.Path(output_dir).parent.absolute()
        delete_dir(output_dir)

    return ret
