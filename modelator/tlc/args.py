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

"""
TLC2 Version 2.16 of 31 December 2020 (rev: cdddf55)

NAME

	TLC - provides model checking and simulation of TLA+ specifications - Version 2.16 of 31 December 2020


SYNOPSIS

	TLC [-h] [-cleanup] [-continue] [-deadlock] [-debug] [-difftrace] [-generateSpecTE [nomonolith]] [-gzip] [-nowarning] [-terse] [-tool] [-view] [-checkpoint minutes] [-config file] [-coverage minutes] [-dfid num] [-dump [dot actionlabels,colorize,snapshot] file] [-fp N] [-fpbits num] [-fpmem num] [-maxSetSize num] [-metadir path] [-recover id] [-userFile file] [-workers num] SPEC
	TLC [-h] [-cleanup] [-continue] [-deadlock] [-debug] [-difftrace] [-generateSpecTE [nomonolith]] [-gzip] [-nowarning] [-terse] [-tool] [-aril num] [-checkpoint minutes] [-config file] [-coverage minutes] [-depth num] [-dump [dot actionlabels,colorize,snapshot] file] [-fp N] [-fpbits num] [-fpmem num] [-maxSetSize num] [-metadir path] [-recover id] [-seed num] [-userFile file] [-workers num] -simulate [file=X,num=Y] SPEC

DESCRIPTION

	The model checker (TLC) provides the functionalities of model checking
	or simulation of TLA+ specifications. It may be invoked from the command
	line, or via the model checking functionality of the Toolbox.

	By default, TLC starts in the model checking mode using breadth-first
	approach for the state space exploration.

OPTIONS

	-aril num
		adjust the seed for random simulation; defaults to 0
	-checkpoint minutes
		interval between check point; defaults to 30
	-cleanup
		clean up the states directory
	-config file
		provide the configuration file; defaults to SPEC.cfg
	-continue
		continue running even when an invariant is violated; default
		behavior is to halt on first violation
	-coverage minutes
		interval between the collection of coverage information;
		if not specified, no coverage will be collected
	-deadlock
		if specified DO NOT CHECK FOR DEADLOCK. Setting the flag is
		the same as setting CHECK_DEADLOCK to FALSE in config
		file. When -deadlock is specified, config entry is
		ignored; default behavior is to check for deadlocks
	-debug
		print various debugging information - not for production use

	-depth num
		specifies the depth of random simulation; defaults to 100
	-dfid num
		run the model check in depth-first iterative deepening
		starting with an initial depth of 'num'
	-difftrace
		show only the differences between successive states when
		printing trace information; defaults to printing
		full state descriptions
	-dump file
		dump all states into the specified file; this parameter takes
		optional parameters for dot graph generation. Specifying
		'dot' allows further options, comma delimited, of zero
		or more of 'actionlabels', 'colorize', 'snapshot' to be
		specified before the '.dot'-suffixed filename
	-fp N
		use the Nth irreducible polynomial from the list stored
		in the class FP64
	-fpbits num
		the number of MSB used by MultiFPSet to create nested
		FPSets; defaults to 1
	-fpmem num
		a value in (0.0,1.0) representing the ratio of total
		physical memory to devote to storing the fingerprints
		of found states; defaults to 0.25
	-generateSpecTE
		if errors are encountered during model checking, generate
		a SpecTE tla/cfg file pair which encapsulates Init-Next
		definitions to specify the state conditions of the error
		state; this enables 'tool' mode. The generated SpecTE
		will include tool output as well as all non-Standard-
		Modules dependencies embeded in the module. To prevent
		the embedding of dependencies, add the parameter
		'nomonolith' to this declaration
	-gzip
		control if gzip is applied to value input/output streams;
		defaults to 'off'
	-h
		display these help instructions
	-maxSetSize num
		the size of the largest set which TLC will enumerate; defaults
		to 1000000 (10^6)
	-metadir path
		specify the directory in which to store metadata; defaults to
		SPEC-directory/states if not specified
	-nowarning
		disable all warnings; defaults to reporting warnings
	-recover id
		recover from the checkpoint with the specified id
	-seed num
		provide the seed for random simulation; defaults to a
		random long pulled from a pseudo-RNG
	-simulate
		run in simulation mode; optional parameters may be specified
		comma delimited: 'num=X' where X is the maximum number of
		total traces to generate and/or 'file=Y' where Y is the
		absolute-pathed prefix for trace file modules to be written
		by the simulation workers; for example Y='/a/b/c/tr' would
		produce, e.g, '/a/b/c/tr_1_15'
	-terse
		do not expand values in Print statements; defaults to
		expanding values
	-tool
		run in 'tool' mode, surrounding output with message codes;
		if '-generateSpecTE' is specified, this is enabled
		automatically
	-userFile file
		an absolute path to a file in which to log user output (for
		example, that which is produced by Print)
	-view
		apply VIEW (if provided) when printing out states
	-workers num
		the number of TLC worker threads; defaults to 1. Use 'auto'
		to automatically select the number of threads based on the
		number of available cores.

TIPS

	When using the  '-generateSpecTE' you can version the generated specification by doing:
		./tla2tools.jar -generateSpecTE MySpec.tla && NAME="SpecTE-$(date +%s)" && sed -e "s/MODULE SpecTE/MODULE $NAME/g" SpecTE.tla > $NAME.tla

	If, while checking a SpecTE created via '-generateSpecTE', you get an error message concerning
	CONSTANT declaration and you've previous used 'integers' as model values, rename your
	model values to start with a non-numeral and rerun the model check to generate a new SpecTE.

	If, while checking a SpecTE created via '-generateSpecTE', you get a warning concerning
	duplicate operator definitions, this is likely due to the 'monolith' specification
	creation. Try re-running TLC adding the 'nomonolith' option to the '-generateSpecTE'
	parameter.

"""
