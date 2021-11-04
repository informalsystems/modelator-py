import os
import pathlib
import subprocess

from recordclass import asdict, recordclass

from ..parse.apalache import parse_apalache_output_dir_name_from_stdout_str
from ..util import delete_dir, read_entire_dir_contents

# mypy: ignore-errors

apalache_args_fields = (
    "cmd",  # The Apalache <command> to run. (check | config | parse | test | typecheck | noop)
    "file",  # A file containing a TLA+ specification (.tla or .json)
    "debug",  # extensive logging in detailed.log and log.smt, default: false
    "out_dir",  # where output files will be written, default: ./_apalache-out (overrides envvar OUT_DIR) (relative to cwd)
    "profiling",  # write general profiling data to profile-rules.txt in the run directory, default: false (overrides envvar PROFILING)
    "smtprof",  # profile SMT constraints in log.smt, default: false
    "write_intermediate",  # write intermediate output files to `out-dir`, default: false (overrides envvar WRITE_INTERMEDIATE)
    "algo",  # the search algorithm: offline, incremental, parallel (soon), default: incremental
    "cinit",  # the name of an operator that initializes CONSTANTS, default: None
    "config",  # configuration file in TLC format, default: <file>.cfg, or none if <file>.cfg not present
    "discard_disabled",  # pre-check, whether a transition is disabled, and discard it, to make SMT queries smaller, default: true
    "init",  # the name of an operator that initializes VARIABLES, default: Init
    "inv",  # the name of an invariant operator, e.g., Inv
    "length",  # maximal number of Next steps, default: 10
    "max_error",  # do not stop on first error, but produce up to a given number of counterexamples (fine tune with --view), default: 1
    "next",  # the name of a transition operator, default: Next
    "no_deadlock",  # do not check for deadlocks, default: true
    "nworkers",  # the number of workers for the parallel checker (soon), default: 1
    "smt_encoding",  # the SMT encoding: oopsla19, arrays (experimental), default: oopsla19 (overrides envvar SMT_ENCODING)
    "tuning",  # filename of the tuning options, see docs/tuning.md
    "tuning_options",  # tuning options as arguments in the format key1=val1:key2=val2:key3=val3 (priority over --tuning)
    "view",  # the state view to use with --max-error=n, default: transition index
    "enable_stats",  # Let Apalache submit usage statistics to tlapl.us (shared with TLC and TLA+ Toolbox). See: https://apalache.informal.systems/docs/apalache/statistics.html
    "output",  # filename where to output the parsed source (.tla or .json), default: None
    "before",  # the name of an operator to prepare the test, similar to Init
    "action",  # the name of an action to execute, similar to Next
    "assertion",  # the name of an operator that should evaluate to true after executing `action`
    "infer_poly",  # allow the type checker to infer polymorphic types, default: true
)

ApalacheArgs = recordclass(
    "ApalacheArgs", apalache_args_fields, defaults=(None,) * len(apalache_args_fields)
)

raw_cmd_fields = (
    "mem",  # Read the contents of the output directory into memory (?)
    "cleanup",  # Delete the output directory after Apalache terminates (?)
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of Apalache jar (full path with suffix like apalache-pkg-0.xx.0-full.jar)
    "args",  # Apalache args
)

RawCmd = recordclass("RawCmd", raw_cmd_fields, defaults=(None,) * len(raw_cmd_fields))

ExecutionResult = recordclass(
    "ExecutionResult", ["process", "files"], defaults=(None, None)
)


def stringify_raw_cmd(cmd: RawCmd):

    jar = cmd.jar
    args = cmd.args

    def stringify(value):
        # Apalache will not accept capitals
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


def exec_apalache_raw_cmd(cmd: RawCmd):
    """
    Execute an Apalache RawCmd

    Returns an ExecutionResult with .process and .files raw_cmd_fields, which
    contain the subprocess result, and the list of filesystem files and their contents.
    """
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
