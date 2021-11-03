import json
from collections import namedtuple

fields = [
    "jar",  # Location of Apalache jar (named like apalache-pkg-0.xx.0-full.jar)                                                                                                  (# noqa: E501)
    "cmd",  # The Apalache <command> to run. (check | config | parse | test | typecheck)                                                                                          (# noqa: E501)
    "file",  # A file containing a TLA+ specification (.tla or .json)                                                                                                             (# noqa: E501)
    "debug",  # extensive logging in detailed.log and log.smt, default: false                                                                                                     (# noqa: E501)
    "out_dir",  # where output files will be written, default: ./_apalache-out (overrides envvar OUT_DIR)                                                                         (# noqa: E501)
    "profiling",  # write general profiling data to profile-rules.txt in the run directory, default: false (overrides envvar PROFILING)                                           (# noqa: E501)
    "smtprof",  # profile SMT constraints in log.smt, default: false                                                                                                              (# noqa: E501)
    "write_intermediate",  # write intermediate output files to `out-dir`, default: false (overrides envvar WRITE_INTERMEDIATE)                                                   (# noqa: E501)
    "algo",  # the search algorithm: offline, incremental, parallel (soon), default: incremental                                                                                  (# noqa: E501)
    "cinit",  # the name of an operator that initializes CONSTANTS, default: None                                                                                                 (# noqa: E501)
    "config",  # configuration file in TLC format, default: <file>.cfg, or none if <file>.cfg not present                                                                         (# noqa: E501)
    "discard_disabled",  # pre-check, whether a transition is disabled, and discard it, to make SMT queries smaller, default: true                                                (# noqa: E501)
    "init",  # the name of an operator that initializes VARIABLES, default: Init                                                                                                  (# noqa: E501)
    "inv",  # the name of an invariant operator, e.g., Inv                                                                                                                        (# noqa: E501)
    "length",  # maximal number of Next steps, default: 10                                                                                                                        (# noqa: E501)
    "max_error",  # do not stop on first error, but produce up to a given number of counterexamples (fine tune with --view), default: 1                                           (# noqa: E501)
    "next",  # the name of a transition operator, default: Next                                                                                                                   (# noqa: E501)
    "no_deadlock",  # do not check for deadlocks, default: true                                                                                                                   (# noqa: E501)
    "nworkers",  # the number of workers for the parallel checker (soon), default: 1                                                                                              (# noqa: E501)
    "smt_encoding",  # the SMT encoding: oopsla19, arrays (experimental), default: oopsla19 (overrides envvar SMT_ENCODING)                                                       (# noqa: E501)
    "tuning",  # filename of the tuning options, see docs/tuning.md                                                                                                               (# noqa: E501)
    "tuning_options",  # tuning options as arguments in the format key1=val1:key2=val2:key3=val3 (priority over --tuning)                                                         (# noqa: E501)
    "view",  # the state view to use with --max-error=n, default: transition index                                                                                                (# noqa: E501)
    "enable_stats",  # Let Apalache submit usage statistics to tlapl.us (shared with TLC and TLA+ Toolbox). See: https://apalache.informal.systems/docs/apalache/statistics.html  (# noqa: E501)
    "output",  # filename where to output the parsed source (.tla or .json), default: None                                                                                        (# noqa: E501)
    "before",  # the name of an operator to prepare the test, similar to Init                                                                                                     (# noqa: E501)
    "action",  # the name of an action to execute, similar to Next                                                                                                                (# noqa: E501)
    "assertion",  # the name of an operator that should evaluate to true after executing `action`                                                                                 (# noqa: E501)
    "infer_poly",  # allow the type checker to infer polymorphic types, default: true                                                                                             (# noqa: E501)
]

RawCmd = namedtuple("RawCmd", fields)  # type: ignore


def exec_apalache_raw_cmd(cmd: RawCmd):
    print(f"{cmd=}")


class Apalache:
    def __init__(self, stdin):
        self.stdin = stdin

    def raw(
        self,
        *_ignore,
        stdin=None,  # Read command from stdin or not
        jar=None,
        cmd=None,
        file=None,
        debug=None,
        out_dir=None,
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
            # Fill what's missing
            for field in fields:
                if field not in data.keys():
                    data[field] = None
            cmd = RawCmd(**data)
        else:
            cmd = RawCmd(
                jar,
                cmd,
                file,
                debug,
                out_dir,
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
        exec_apalache_raw_cmd(cmd)
