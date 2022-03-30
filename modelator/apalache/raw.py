import os
import pathlib
import subprocess

from recordclass import asdict, recordclass

from ..parse.apalache import parse_apalache_output_dir_name_from_stdout_str
from ..util import delete_dir, read_entire_dir_contents
from .args import ApalacheArgs

# mypy: ignore-errors

raw_cmd_fields = (
    "mem",  # Read the contents of the output directory into memory (?)
    "cleanup",  # Delete the output directory after Apalache terminates (?)
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of Apalache jar (full path with suffix like apalache.jar)
    "args",  # Apalache args
)

RawCmd = recordclass("RawCmd", raw_cmd_fields, defaults=(None,) * len(raw_cmd_fields))


def stringify_raw_cmd(cmd: RawCmd):

    jar = cmd.jar
    args = cmd.args

    def stringify(value):
        # Apalache will not accept capitalized bools
        if isinstance(value, bool):
            return str(value).lower()
        return value

    args = ApalacheArgs(**{k: stringify(v) for k, v in asdict(args).items()})

    cmd_str = f"""java\
 -jar {jar}\
{f" --debug={args.debug}" if args.debug is not None else ""}\
{f" --out-dir={args.out_dir}" if args.out_dir is not None else ""}\
{f" --profiling={args.profiling}" if args.profiling is not None else ""}\
{f" --smtprof={args.smtprof}" if args.smtprof is not None else ""}\
{f" --write-intermediate={args.write_intermediate}" if args.write_intermediate is not None else ""}\
 {args.cmd}\
{f" --algo={args.algo}" if args.algo is not None else ""}\
{f" --cinit={args.cinit}" if args.cinit is not None else ""}\
{f" --config={args.config}" if args.config is not None else ""}\
{f" --discard-disabled={args.discard_disabled}" if args.discard_disabled is not None else ""}\
{f" --init={args.init}" if args.init is not None else ""}\
{f" --inv={args.inv}" if args.inv is not None else ""}\
{f" --length={args.length}" if args.length is not None else ""}\
{f" --max-error={args.max_error}" if args.max_error is not None else ""}\
{f" --next={args.next}" if args.next is not None else ""}\
{f" --no-deadlock={args.no_deadlock}" if args.no_deadlock is not None else ""}\
{f" --nworkers={args.nworkers}" if args.nworkers is not None else ""}\
{f" --smt_encoding={args.smt_encoding}" if args.smt_encoding is not None else ""}\
{f" --tuning={args.tuning}" if args.tuning is not None else ""}\
{f" --tuning-options={args.tuning_options}" if args.tuning_options is not None else ""}\
{f" --view={args.view}" if args.view is not None else ""}\
{f" --enable-stats={args.enable_stats}" if args.enable_stats is not None else ""}\
{f" --output={args.output}" if args.output is not None else ""}\
{f" --infer-poly={args.infer_poly}" if args.infer_poly is not None else ""}\
{f" {args.file}" if args.file is not None else ""}\
{f" {args.before}" if args.before is not None else ""}\
{f" {args.action}" if args.action is not None else ""}\
{f" {args.assertion}" if args.assertion is not None else ""}\
"""

    return cmd_str


ExecutionResult = recordclass(
    "ExecutionResult", ["process", "files"], defaults=(None, None)
)


def json_to_cmd(json) -> RawCmd:
    json_obj = {
        "mem": None,
        "cleanup": None,
        "cwd": None,
        "jar": None,
        "args": None,
    } | json_obj
    cmd = RawCmd()
    cmd.mem = json_obj["mem"]
    cmd.cleanup = json_obj["cleanup"]
    cmd.cwd = json_obj["cwd"]
    cmd.jar = json_obj["jar"]
    cmd.args = ApalacheArgs(**json_obj["args"])
    return cmd


def apalache_raw(*, cmd: RawCmd = None, json=None):
    """
    Execute an Apalache command using either a RawCmd object, or build the RawCmd from json

    Returns an ExecutionResult with .process and .files properties.
    Contains the subprocess result, and the list of filesystem files (and contents).
    """
    assert not (cmd is not None and json is not None)

    if json is not None:
        cmd = json_to_cmd(json)

    if cmd.args.out_dir is not None:
        cmd.args.out_dir = os.path.expanduser(cmd.args.out_dir)
    if cmd.cwd is not None:
        cmd.cwd = os.path.expanduser(cmd.cwd)
        if not os.path.isabs(cmd.cwd):
            raise Exception("cwd must be absolute (after expanding user)")
    if cmd.jar is not None:
        cmd.jar = os.path.expanduser(cmd.jar)
        if not os.path.isabs(cmd.jar):
            raise Exception("apalache jar path must be absolute (after expanding user)")

    cmd_str = stringify_raw_cmd(cmd)

    # Semantics a bit complex here - see https://stackoverflow.com/a/15109975/8346628
    process_result = subprocess.run(
        cmd_str, shell=True, capture_output=True, cwd=cmd.cwd
    )

    ret = ExecutionResult()
    ret.process = process_result

    output_dir = parse_apalache_output_dir_name_from_stdout_str(
        ret.process.stdout.decode("unicode_escape")
    )

    if cmd.mem:
        files = read_entire_dir_contents(output_dir)
        ret.files = {os.path.basename(fn): content for fn, content in files.items()}
    if cmd.cleanup:
        # Need to take parent as format is output_dir_name = prefix/<out-dir>/<randomized dir>/
        if not os.path.isabs(output_dir):
            raise Exception(
                "Output directory parsed from Apalache stdout is not an absolute path"
            )

        output_dir = pathlib.Path(output_dir).parent.absolute()
        delete_dir(output_dir)

    return ret
