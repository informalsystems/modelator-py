import typing

from modelator.util.informal_trace_format import ITFTrace

from .state_to_informal_trace_format import state_to_informal_trace_format_state


def trace_lines_model_checking_mode(stdout) -> typing.List[typing.List[str]]:
    """Returns list of lists. Each sublist is a list of lines
    that make a trace.

    stdout : stdout of TLC execution run in model checking mode
    """
    ret = []
    lines = stdout.split("\n")

    def is_header(line):
        """Begins a trace and may also end a previous trace"""
        HEADER = "Error: Invariant"
        return line.startswith(HEADER)

    def is_footer(line):
        return (
            ("states generated" in line)
            and ("distinct states found" in line)
            and ("states left on queue" in line)
            and (not line.startswith("Progress"))
        ) or ("Model checking completed" in line)

    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if is_header(line):
            if 0 < header_cnt:
                """
                Traces are prefixed:
                '
                    Error: Invariant Inv is violated.
                    Error: The behavior up to this point is:
                    State 1: <Initial predicate>
                '
                so we add 2 to the catchment index.
                """
                trace = lines[header_ix + 2 : i]
                ret.append(trace)
            header_cnt += 1
            header_ix = i
        if is_footer(line):
            if 0 < header_cnt:
                trace = lines[header_ix + 2 : i]  # see comment above
                ret.append(trace)
            break

    return ret


def trace_lines_simulation_mode(stdout) -> typing.List[typing.List[str]]:
    """Returns list of lists. Each sublist is a list of lines
    that make a trace.

    stdout : stdout of TLC execution run in simulation mode
    """
    ret = []
    lines = stdout.split("\n")

    def is_header(line):
        """Begins a trace and may also end a previous trace"""
        HEADER = "State 1:"
        return line.startswith(HEADER)

    def is_footer(line):
        """Ends the list of traces"""
        return line.startswith("Finished in")

    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if is_header(line):
            if 0 < header_cnt:
                trace = lines[header_ix : i - 4]
                ret.append(trace)
            header_cnt += 1
            header_ix = i
        if is_footer(line) and 0 < header_cnt:
            ret.append(lines[header_ix : i - 4])

    return ret


def split_into_states(lines) -> typing.List[str]:
    """
    Returns a list of states.

    A trace from TLC is a sequence of [header, content] pairs.
    The headers are not valid TLA+.
    This function returns a list where each item is valid TLA+ content.
    """
    ret = []
    HEADER = "State "
    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if line.startswith(HEADER):
            if 0 < header_cnt:
                ret.append(lines[header_ix + 1 : i])
            header_ix = i
            header_cnt += 1
    if 0 < header_cnt:
        ret.append(lines[header_ix + 1 :])

    return ret


def extract_traces(stdout: str):
    """
    Extract zero, one or more traces from the stdout of TLC.

    A trace returned by this function is a list of lists of substrings of stdout.
    Each sublist of substrings is a trace and each substring is a state.

    WARNING: Does not support lasso traces
    """
    traces = None
    if "Running Random Simulation" in stdout:
        traces = trace_lines_simulation_mode(stdout)
    else:
        traces = trace_lines_model_checking_mode(stdout)
    traces = [split_into_states(t) for t in traces]
    traces = [["\n".join(lines) for lines in t] for t in traces]
    return traces


def tlc_trace_to_informal_trace_format_trace(trace: typing.List[str]):
    """
    Convert a tla trace from TLC stdout to the Informal Trace Format
    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#adr-015-informal-trace-format-in-json

    Trace input is a list of states. Each state is a string.
    """

    states = [state_to_informal_trace_format_state(state) for state in trace]
    vars = []
    if 0 < len(states):
        vars = list(states[0].var_value_map.keys())

    return ITFTrace(vars, states)
