from recordclass import recordclass

apalache_args_fields = (
    "cmd",  # The Apalache <command> to run. (check | config | parse | test | transpile | typecheck | noop)
    "file",  # A file containing a TLA+ specification (.tla or .json)
    "config_file",  # configuration to read from (JSON and HOCON formats supported). Overrides any local .aplache.cfg files. (overrides envvar CONFIG_FILE)
    "debug",  # extensive logging in detailed.log and log.smt, default: false
    "out_dir",  # where all output files will be written, default: ./_apalache-out (overrides envvar OUT_DIR)
    "profiling",  # write general profiling data to profile-rules.txt in the run directory, default: false (overrides envvar PROFILING)
    "run_dir",  # additional directory wherein output files for this run will be written directly, default: none (overrides envvar RUN_DIR)
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
    "no_deadlock",  # do not check for deadlocks, default: true
    "nworkers",  # the number of workers for the parallel checker (soon), default: 1
    "smt_encoding",  # the SMT encoding: oopsla19, arrays (experimental), default: oopsla19 (overrides envvar SMT_ENCODING)
    "tuning",  # filename of the tuning options, see docs/tuning.md
    "tuning_options",  # tuning options as arguments in the format key1=val1:key2=val2:key3=val3 (priority over --tuning)
    "view",  # the state view to use with --max-error=n, default: transition index
    "enable_stats",  # Let Apalache submit usage statistics to tlapl.us (shared with TLC and TLA+ Toolbox) See: https://apalache.informal.systems/docs/apalache/statistics.html
    "before",  # the name of an operator to prepare the test, similar to Init
    "action",  # the name of an action to execute, similar to Next
    "assertion",  # the name of an operator that should evaluate to true after executing `action`
    "next",  # the name of a transition operator, default: Next <file> : a file containing a TLA+ specification (.tla or .json)
    "infer_poly",  # allow the type checker to infer polymorphic types, default: true
    "output",  # file to which the typechecked or parsed source is written (.tla or .json), default: None
)

ApalacheArgs = recordclass(
    "ApalacheArgs", apalache_args_fields, defaults=(None,) * len(apalache_args_fields)
)
