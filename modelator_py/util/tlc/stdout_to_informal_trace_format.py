import typing

from modelator_py.util.informal_trace_format import ITFTrace

from .state_to_informal_trace_format import state_to_informal_trace_format_state


def trace_lines_model_checking_mode(stdout) -> typing.List[typing.List[str]]:
    """
    Returns list of lists. Each sublist is a list of lines
    that make a trace.

    Args:
        stdout : stdout of TLC execution run in model checking mode
    """
    ret = []
    lines = stdout.split("\n")
    header_open = False

    def is_header(line):
        """One line before the beginning of the trace."""
        single_state_trace_header = "is violated by the initial state" in line
        mult_state_trace_header = line == "Error: The behavior up to this point is:"
        return single_state_trace_header or mult_state_trace_header

    def is_start_of_new_trace(line):
        """When there are multiple traces, closes the previous trace"""

        # when there are multiple violations, a new trace report starts with:
        continue_case = line.startswith("Error: Invariant")

        # when the first violation was in the init state, the second one starts with:
        init_state_continue_case = line.startswith("Finished computing initial states")
        return continue_case or init_state_continue_case

    def is_footer(line):
        multi_state_footer = (
            ("states generated" in line)
            and ("distinct states found" in line)
            and ("states left on queue" in line)
            and (not line.startswith("Progress"))
        ) or ("Model checking completed" in line)

        single_state_footer = "Finished in" in line

        return single_state_footer or multi_state_footer

    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if is_start_of_new_trace(line):
            header_open = True
            if 0 < header_cnt:
                trace = lines[header_ix + 1 : i]
                ret.append(trace)

        if is_header(line):
            header_cnt += 1
            header_ix = i

        # we need boolean header_open because the footer the conditions for the footer
        # of a single state trace will be met also in the line after the footer of a multi-state trace
        if header_open and is_footer(line):
            header_open = False
            if 0 < header_cnt:
                trace = lines[header_ix + 1 : i]
                ret.append(trace)
            break

    return ret


def trace_lines_simulation_mode(stdout) -> typing.List[typing.List[str]]:
    """
    Returns list of lists. Each sublist is a list of lines
    that make a trace.

    Args:
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


def split_into_states(lines: typing.List[str]) -> typing.List[typing.List[str]]:
    """
    Converts a TLA+/ASCII trace string expression into a list of TLA+ state
    string expressions. Requires removing non-TLA+ ascii from the trace string
    expression.

    A trace from TLC is a sequence of [header, content] pairs.
    The headers are not valid TLA+.
    This function returns a list where each item is valid TLA+ content.
    """
    ret = []
    HEADER = "State "
    header_cnt = 0
    header_ix = -1

    # this is for the case when the invariant is violated in the initial state
    # then, the counterexample is not prefixed with "State "
    if len(lines) > 0 and not lines[0].startswith(HEADER):
        lines = [HEADER] + lines
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
    traces = [split_into_states(t) for t in traces]  # type:ignore
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
