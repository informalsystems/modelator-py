import json
import os
import subprocess

from recordclass import asdict, recordclass

# mypy: ignore-errors

fields = (
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of Apalache jar (named like apalache-pkg-0.xx.0-full.jar)
    "cmd",  # The Apalache <command> to run. (check | config | parse | test | typecheck | noop)
    "file",  # A file containing a TLA+ specification (.tla or .json)
    "debug",  # extensive logging in detailed.log and log.smt, default: false
    "out_dir_relative_to_cwd",  # where output files will be written, default: ./_apalache-out (overrides envvar OUT_DIR)
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

RawCmd = recordclass("RawCmd", fields, defaults=(None,) * len(fields))


def stringify_raw_cmd(cmd: RawCmd):
    def stringify(value):
        # Apalache will not accept capitals
        if isinstance(value, bool):
            return str(value).lower()
        return value

    cmd = RawCmd(**{k: stringify(v) for k, v in asdict(cmd).items()})

    cmd_str = f"""java\
 -jar {cmd.jar}\
{f" --debug={cmd.debug}" if cmd.debug is not None else ""}\
{f" --out-dir={cmd.out_dir_relative_to_cwd}" if cmd.out_dir_relative_to_cwd is not None else ""}\
{f" --profiling={cmd.profiling}" if cmd.profiling is not None else ""}\
{f" --smtprof={cmd.smtprof}" if cmd.smtprof is not None else ""}\
{f" --write-intermediate={cmd.write_intermediate}" if cmd.write_intermediate is not None else ""}\
 {cmd.cmd}\
{f" --algo={cmd.algo}" if cmd.algo is not None else ""}\
{f" --cinit={cmd.cinit}" if cmd.cinit is not None else ""}\
{f" --config={cmd.config}" if cmd.config is not None else ""}\
{f" --discard-disabled={cmd.discard_disabled}" if cmd.discard_disabled is not None else ""}\
{f" --init={cmd.init}" if cmd.init is not None else ""}\
{f" --inv={cmd.inv}" if cmd.inv is not None else ""}\
{f" --length={cmd.length}" if cmd.length is not None else ""}\
{f" --max-error={cmd.max_error}" if cmd.max_error is not None else ""}\
{f" --next={cmd.next}" if cmd.next is not None else ""}\
{f" --no-deadlock={cmd.no_deadlock}" if cmd.no_deadlock is not None else ""}\
{f" --nworkers={cmd.nworkers}" if cmd.nworkers is not None else ""}\
{f" --smt_encoding={cmd.smt_encoding}" if cmd.smt_encoding is not None else ""}\
{f" --tuning={cmd.tuning}" if cmd.tuning is not None else ""}\
{f" --tuning-options={cmd.tuning_options}" if cmd.tuning_options is not None else ""}\
{f" --view={cmd.view}" if cmd.view is not None else ""}\
{f" --enable-stats={cmd.enable_stats}" if cmd.enable_stats is not None else ""}\
{f" --output={cmd.output}" if cmd.output is not None else ""}\
{f" --infer-poly={cmd.infer_poly}" if cmd.infer_poly is not None else ""}\
{f" {cmd.file}" if cmd.file is not None else ""}\
{f" {cmd.before}" if cmd.before is not None else ""}\
{f" {cmd.action}" if cmd.action is not None else ""}\
{f" {cmd.assertion}" if cmd.assertion is not None else ""}\
"""

    return cmd_str


def exec_apalache_raw_cmd(cmd: RawCmd):
    if cmd.out_dir_relative_to_cwd is not None:
        cmd.out_dir_relative_to_cwd = os.path.expanduser(cmd.out_dir_relative_to_cwd)
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
    result = subprocess.run(cmd_str, shell=True, capture_output=True, cwd=cmd.cwd)
    return result


class Apalache:
    def __init__(self, stdin):
        self.stdin = stdin

    def raw(
        self,
        *,
        cwd=None,
        stdin=None,  # Read command from stdin or not
        jar=None,
        cmd=None,
        file=None,
        debug=None,
        out_dir_relative_to_cwd=None,
        profiling=None,
        smtprof=None,
        write_intermediate=None,
        algo=None,
        cinit=None,
        config=None,
        discard_disabled=None,
        init=None,
        inv=None,
        length=None,
        max_error=None,
        next=None,
        no_deadlock=None,
        nworkers=None,
        smt_encoding=None,
        tuning=None,
        tuning_options=None,
        view=None,
        enable_stats=None,
        output=None,
        before=None,
        action=None,
        assertion=None,
        infer_poly=None,
    ):
        cmd = None
        if stdin:
            data = json.loads(self.stdin.read())
            cmd = RawCmd(**data)
        else:
            cmd = RawCmd(
                cwd,
                jar,
                cmd,
                file,
                debug,
                out_dir_relative_to_cwd,
                profiling,
                smtprof,
                write_intermediate,
                algo,
                cinit,
                config,
                discard_disabled,
                init,
                inv,
                length,
                max_error,
                next,
                no_deadlock,
                nworkers,
                smt_encoding,
                tuning,
                tuning_options,
                view,
                enable_stats,
                output,
                before,
                action,
                assertion,
                infer_poly,
            )
        result = exec_apalache_raw_cmd(cmd)
        stdout_pretty = result.stdout.decode("unicode_escape")
        stderr_pretty = result.stderr.decode("unicode_escape")

        print(
            f"""Ran 'apalache raw'.
shell cmd: {result.args}
return code: {result.returncode}
stdout: {stdout_pretty}
stderr: {stderr_pretty}"""
        )
