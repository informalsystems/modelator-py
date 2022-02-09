# Usage examples

_This document is a work in progress and not all features are documented yet_

## Extract traces from TLC output in [Informal Trace Format](https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format) format

The TLC model checker will generate counterexamples written in TLA+ and embed them in stdout, interleaved with ASCII text. This output can contain 0, 1 or more traces. Run the `poetry run cli util tlc itf` tool to extract a list of traces in the Informal Trace Format.

There is more than one way to run the tool. The tool writes Json to `stdout`.

### Provide TLC's stdout data on stdin and flags as cli args

```bash
poetry run cli util tlc itf < <TLC_STDOUT_STRING> # Run without flags
poetry run cli util tlc itf --lists=<bool> --records=<bool> < <TLC_STDOUT_STRING> # Run with flags
```

### Provide TLC's stdout data and flags inside a json object

```bash
poetry run cli util tlc itf --json < <JSON_OBJECT>
```

### Flag explanation

```bash
# In TLA+ there is no distinction between some functions and sequences. This means
# that a sequence may be represented by function with domain 1..n for some n,
# and vice versa. It is likely convenient to handle such functions as lists. 
# Default: True
--lists
# In TLA+ there is no distinction between some functions and records. This means
# that a record may be represented by functions with domain all strings, and vice
# versa. It is likely convenient to handle such functions as records. 
# Default: True
--records 
```

### Examples

The `tests/resource` directory contains convenient example data.

```bash
cd tests/resource
```

```bash
# Provide TLC's stdout data on stdin and flags as cli args
poetry run cli util tlc itf --lists=False < TlcTraceParse.txt > traces.json
# Provide TLC's stdout data and flags inside a json object
poetry run cli util tlc itf --json < HelloWorld_util_tlc_itf.json > traces.json
```
