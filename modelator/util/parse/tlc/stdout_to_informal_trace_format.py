from .state_to_informal_trace_format import state_to_informal_trace_format_state
from modelator.util.parse.informal_trace_format import ITFTrace


def extract_traces(stdout: str):
    """
    Extract zero, one or more traces from the stdout of TLC.

    A trace returned by this function is a substring of stdout
    containing exactly one sequence of state expressions.

    WARNING: Does not support lasso traces
    """
    ret = []
    lines = stdout.split("\n")
    HEADER = "Error: Invariant"
    FOOTER = "Finished in "
    header_cnt = 0
    header_ix = -1
    footer_seen = False
    for i, line in enumerate(lines):
        if line.startswith(HEADER):
            if 0 < header_cnt:
                trace_lines = lines[header_ix:i]
                trace = "\n".join(trace_lines)
                ret.append(trace)
            header_cnt += 1
            header_ix = i
        if line.startswith(FOOTER):
            footer_seen = True

    # This block makes sure to include the last trace
    if footer_seen and 0 < header_cnt:
        trace_lines = lines[header_ix:i]
        trace = "\n".join(trace_lines)
        ret.append(trace)

    return ret


def split_into_states(trace) -> list[str]:
    """
    Returns a list of states.

    A trace from TLC is a sequence of [header, content] pairs.
    The headers are not valid TLA+.
    This function returns a list where each item is valid TLA+ content.
    """
    ret = []
    lines = trace.split("\n")
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

    ret = ["\n".join(lines) for lines in ret]
    for expr in ret:
        print(expr)
    return ret


def tlc_trace_to_informal_trace_format_trace(trace):
    """
    Convert a tla trace from TLC stdout to the Informal Trace Format
    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#adr-015-informal-trace-format-in-json
    """

    trace = split_into_states(trace)
    states = [state_to_informal_trace_format_state(state) for state in trace]
    vars = []
    if 0 < len(states):
        vars = list(states[0].var_value_map.keys())

    return ITFTrace(vars, states)
