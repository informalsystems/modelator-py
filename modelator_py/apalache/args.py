from recordclass import recordclass

apalache_args_fields = (
    # The Apalache <command> to run. (check | config | parse | test | transpile | typecheck | noop)
    "cmd",
    "file",  # A file containing a TLA+ specification (.tla or .json)
    # configuration to read from (JSON and HOCON formats supported). Overrides any local .aplache.cfg files. (overrides envvar CONFIG_FILE)
    "config_file",
    "debug",  # extensive logging in detailed.log and log.smt, default: false
    # where all output files will be written, default: ./_apalache-out (overrides envvar OUT_DIR)
    "out_dir",
    # write general profiling data to profile-rules.txt in the run directory, default: false (overrides envvar PROFILING)
    "profiling",
    # additional directory wherein output files for this run will be written directly, default: none (overrides envvar RUN_DIR)
    "run_dir",
    "smtprof",  # profile SMT constraints in log.smt, default: false
    # write intermediate output files to `out-dir`, default: false (overrides envvar WRITE_INTERMEDIATE)
    "write_intermediate",
    # the search algorithm: offline, incremental, parallel (soon), default: incremental
    "algo",
    "cinit",  # the name of an operator that initializes CONSTANTS, default: None
    "config",  # configuration file in TLC format, default: <file>.cfg, or none if <file>.cfg not present
    "discard_disabled",  # pre-check, whether a transition is disabled, and discard it, to make SMT queries smaller, default: true
    "init",  # the name of an operator that initializes VARIABLES, default: Init
    "inv",  # the name of an invariant operator, e.g., Inv
    "length",  # maximal number of Next steps, default: 10
    # do not stop on first error, but produce up to a given number of counterexamples (fine tune with --view), default: 1
    "max_error",
    # do not stop after a first simulation run, but produce up to a given number of runs (unless reached --max-error), default: 100
    "max_run",
    "no_deadlock",  # do not check for deadlocks, default: true
    "nworkers",  # the number of workers for the parallel checker (soon), default: 1
    # the SMT encoding: oopsla19, arrays (experimental), default: oopsla19 (overrides envvar SMT_ENCODING)
    "smt_encoding",
    "tuning",  # filename of the tuning options, see docs/tuning.md
    # tuning options as arguments in the format key1=val1:key2=val2:key3=val3 (priority over --tuning)
    "tuning_options",
    "view",  # the state view to use with --max-error=n, default: transition index
    # Let Apalache submit usage statistics to tlapl.us (shared with TLC and TLA+ Toolbox) See: https://apalache.informal.systems/docs/apalache/statistics.html
    "enable_stats",
    "before",  # the name of an operator to prepare the test, similar to Init
    "action",  # the name of an action to execute, similar to Next
    "assertion",  # the name of an operator that should evaluate to true after executing `action`
    # the name of a transition operator, default: Next <file> : a file containing a TLA+ specification (.tla or .json)
    "next",
    "infer_poly",  # allow the type checker to infer polymorphic types, default: true
    # file to which the typechecked or parsed source is written (.tla or .json), default: None
    "output",
    "features",  # a comma-separated list of experimental features, default: None
    "output_traces",  # save an example trace for each symbolic run, default: false
)

ApalacheArgs = recordclass(
    "ApalacheArgs", apalache_args_fields, defaults=(None,) * len(apalache_args_fields)
)
