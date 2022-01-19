from recordclass import recordclass

# mypy: ignore-errors
# flake8: noqa

tlc_args_fields = (
    "aril",  # num adjust the seed for random simulation; defaults to 0
    "checkpoint",  # minutes interval between check point; defaults to 30
    "cleanup",  # clean up the states directory
    "config",  # file provide the configuration file; defaults to SPEC.cfg
    "cont",  # continue running even when an invariant is violated; default behavior is to halt on first violation
    "coverage",  # minutes interval between the collection of coverage information; if not specified, no coverage will be collected
    "deadlock",  # if specified DO NOT CHECK FOR DEADLOCK. Setting the flag is the same as setting CHECK_DEADLOCK to FALSE in config file. When -deadlock is specified, config entry is ignored; default behavior is to check for deadlocks
    "debug",  # print various debugging information - not for production use
    "depth",  # num specifies the depth of random simulation; defaults to 100
    "dfid",  # num run the model check in depth-first iterative deepening starting with an initial depth of 'num'
    "difftrace",  # show only the differences between successive states when printing trace information; defaults to printing full state descriptions
    "dump",  # file dump all states into the specified file; this parameter takes optional parameters for dot graph generation. Specifying 'dot' allows further options, comma delimited, of zero or more of 'actionlabels', 'colorize', 'snapshot' to be specified before the '.dot'-suffixed filename
    "fp",  # N use the Nth irreducible polynomial from the list stored in the class FP64
    "fpbits",  # num the number of MSB used by MultiFPSet to create nested FPSets; defaults to 1
    "fpmem",  # num a value in (0.0,1.0) representing the ratio of total physical memory to devote to storing the fingerprints of found states; defaults to 0.25
    "generate_spec_te",  # if errors are encountered during model checking, generate a SpecTE tla/cfg file pair which encapsulates Init-Next definitions to specify the state conditions of the error state; this enables 'tool' mode. The generated SpecTE will include tool output as well as all non-Standard- Modules dependencies embeded in the module. To prevent the embedding of dependencies, add the parameter 'nomonolith' to this declaration
    "gzip",  # control if gzip is applied to value input/output streams; defaults to 'off'
    "h",  # display these help instructions
    "max_set_size",  # num the size of the largest set which TLC will enumerate; defaults to 1000000 (10^6)
    "metadir",  # path specify the directory in which to store metadata; defaults to SPEC-directory/states if not specified
    "nowarning",  # disable all warnings; defaults to reporting warnings
    "recover",  # id recover from the checkpoint with the specified id
    "seed",  # num provide the seed for random simulation; defaults to a random long pulled from a pseudo-RNG
    "simulate",  # run in simulation mode; optional parameters may be specified comma delimited: 'num=X' where X is the maximum number of total traces to generate and/or 'file=Y' where Y is the absolute-pathed prefix for trace file modules to be written by the simulation workers; for example Y='/a/b/c/tr' would produce, e.g, '/a/b/c/tr_1_15'
    "terse",  # do not expand values in Print statements; defaults to expanding values
    "tool",  # run in 'tool' mode, surrounding output with message codes; if '-generateSpecTE' is specified, this is enabled automatically
    "userfile",  # file an absolute path to a file in which to log user output (for example, that which is produced by Print)
    "view",  # apply VIEW (if provided) when printing out states
    "workers",  # the number of TLC worker threads; defaults to 1. Use 'auto' to automatically select the number of threads based on the number of available cores.
    "file",  # the target .tla spec file
)

TlcArgs = recordclass(
    "TlcArgs", tlc_args_fields, defaults=(None,) * len(tlc_args_fields)
)
