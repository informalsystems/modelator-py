import os
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from typing import Optional

from .args import ApalacheArgs

# mypy: ignore-errors


@dataclass
class RawCmd:
    cwd: Optional[str] = None  # Current working directory for child shell process
    jar: Optional[
        str
    ] = None  # Location of Apalache jar (full path with suffix like apalache.jar)
    args: Optional[ApalacheArgs] = None  # Apalache args


def stringify_raw_cmd(cmd: RawCmd, java_temp_dir: str = None):

    jar = cmd.jar
    args = cmd.args

    if java_temp_dir is None:
        tmpdir_setup = ""
    else:
        tmpdir_setup = " -Djava.io.tmpdir={}".format(java_temp_dir)

    def stringify(value):
        # Apalache will not accept capitalized bools
        if isinstance(value, bool):
            return str(value).lower()
        return value

    args = ApalacheArgs(**{k: stringify(v) for k, v in asdict(args).items()})

    cmd_str = f"""java{tmpdir_setup}\
 -jar "{jar}"\
{f" --config-file={args.config_file}" if args.config_file is not None else ""}\
{f" --debug={args.debug}" if args.debug is not None else ""}\
{f" --out-dir={args.out_dir}" if args.out_dir is not None else ""}\
{f" --profiling={args.profiling}" if args.profiling is not None else ""}\
{f" --run-dir={args.run_dir}" if args.run_dir is not None else ""}\
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
{f" --max-run={args.max_run}" if args.max_run is not None else ""}\
{f" --no-deadlock={args.no_deadlock}" if args.no_deadlock is not None else ""}\
{f" --output-traces={args.output_traces}" if args.output_traces is not None else ""}\
{f" --nworkers={args.nworkers}" if args.nworkers is not None else ""}\
{f" --smt-encoding={args.smt_encoding}" if args.smt_encoding is not None else ""}\
{f" --tuning={args.tuning}" if args.tuning is not None else ""}\
{f" --tuning-options={args.tuning_options}" if args.tuning_options is not None else ""}\
{f" --view={args.view}" if args.view is not None else ""}\
{f" --enable-stats={args.enable_stats}" if args.enable_stats is not None else ""}\
{f" --before={args.before}" if args.before is not None else ""}\
{f" --action={args.action}" if args.action is not None else ""}\
{f" --assertion={args.assertion}" if args.assertion is not None else ""}\
{f" --next={args.next}" if args.next is not None else ""}\
{f" --infer-poly={args.infer_poly}" if args.infer_poly is not None else ""}\
{f" --output={args.output}" if args.output is not None else ""}\
{f" --features={args.features}" if args.features is not None else ""}\
{f" {args.file}" if args.file is not None else ""}\
{f" {args.before}" if args.before is not None else ""}\
{f" {args.action}" if args.action is not None else ""}\
{f" {args.assertion}" if args.assertion is not None else ""}\
"""

    return cmd_str


def json_to_cmd(json) -> RawCmd:
    json = {
        **{
            "cwd": None,
            "jar": None,
            "args": None,
        },
        **json,
    }
    cmd = RawCmd()
    cmd.cwd = json["cwd"]
    cmd.jar = json["jar"]
    cmd.args = ApalacheArgs(**json["args"])
    return cmd


def apalache_raw(*, cmd: RawCmd = None, json=None):
    """
    Run an Apalache command using either a RawCmd object, or build the RawCmd from json.

    Run Apalache with side effects without creating a temporary directory.

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
            raise Exception("Apalache jar path must be absolute (after expanding user)")
    if cmd.jar is None:
        raise Exception("Apalache jar path must be absolute (after expanding user)")

    with tempfile.TemporaryDirectory(
        prefix="modelator-py-apalache-java-temp-dir-"
    ) as java_temp:
        cmd_str = stringify_raw_cmd(cmd, java_temp_dir=java_temp)

        # Semantics a bit complex here - see https://stackoverflow.com/a/15109975/8346628
        return subprocess.run(cmd_str, shell=True, capture_output=True, cwd=cmd.cwd)
