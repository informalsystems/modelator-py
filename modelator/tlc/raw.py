import os
import pathlib
import subprocess

from recordclass import asdict, recordclass

from ..util import delete_dir, read_entire_dir_contents

# mypy: ignore-errors

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

raw_cmd_fields = (
    "mem",  # Read the contents of the output directory into memory (?)
    "cleanup",  # Delete the output directory after Tlc terminates (?)
    "cwd",  # Current working directory for child shell process
    "jar",  # Location of Tlc jar (full path with suffix like tla2tools.jar)
    "args",  # Tlc args
)

RawCmd = recordclass("RawCmd", raw_cmd_fields, defaults=(None,) * len(raw_cmd_fields))

ExecutionResult = recordclass(
    "ExecutionResult", ["process", "files"], defaults=(None, None)
)


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
 -jar {jar}\
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


def exec_tlc_raw_cmd(cmd: RawCmd):
    """
    Execute an Tlc RawCmd

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
            raise Exception(
                "Output directory TODO: better message
            )

        output_dir = pathlib.Path(output_dir).parent.absolute()
        delete_dir(output_dir)

    return ret
