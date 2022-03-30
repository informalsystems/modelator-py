import os
import subprocess

from recordclass import asdict, recordclass

from .args import TlcArgs

# mypy: ignore-errors

raw_cmd_fields = (
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of TLC jar (full path with suffix like tla2tools.jar)
    "args",  # TLC args
)

RawCmd = recordclass("RawCmd", raw_cmd_fields, defaults=(None,) * len(raw_cmd_fields))


def stringify_raw_cmd(cmd: RawCmd) -> str:
    """
    Returns a string which can be passed to a shell to run TLC.
    """

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


def json_to_cmd(json) -> RawCmd:
    json = {
        "cwd": None,
        "jar": None,
        "args": None,
    } | json
    cmd = RawCmd()
    cmd.cwd = json["cwd"]
    cmd.jar = json["jar"]
    cmd.args = TlcArgs(**json["args"])
    return cmd


def tlc_raw(*, cmd: RawCmd = None, json=None):
    """
    Run a TLC command using either a RawCmd object, or build the RawCmd from json.

    Run TLC with side effects without creating a temporary directory.

    Returns a subprocess call result object.
    """
    assert cmd is not None or json is not None
    assert not (cmd is not None and json is not None)

    if json is not None:
        cmd = json_to_cmd(json)

    if cmd.cwd is not None:
        cmd.cwd = os.path.expanduser(cmd.cwd)
        if not os.path.isabs(cmd.cwd):
            raise Exception("cwd must be absolute (after expanding user)")
    if cmd.cwd is None:
        raise Exception("cwd must be absolute (after expanding user)")
    if cmd.jar is not None:
        cmd.jar = os.path.expanduser(cmd.jar)
        if not os.path.isabs(cmd.jar):
            raise Exception("TLC jar path must be absolute (after expanding user)")
    if cmd.jar is None:
        raise Exception("TLC jar path must be absolute (after expanding user)")

    cmd_str = stringify_raw_cmd(cmd)

    # Semantics a bit complex here - see https://stackoverflow.com/a/15109975/8346628
    return subprocess.run(cmd_str, shell=True, capture_output=True, cwd=cmd.cwd)
