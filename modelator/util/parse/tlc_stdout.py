from .tla.parser import parse_expr


def extract_traces(stdout: str):
    """
    Extract zero, one or more traces from the stdout of TLC.

    NOTE: Does not support lasso traces
    """
    ret = []
    lines = stdout.split("\n")
    HEADER = "State 1"
    FOOTER = "Model checking completed."
    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if line.startswith(HEADER) or line.startswith(FOOTER):
            if 0 < header_cnt:
                trace_lines = lines[header_ix:i]
                trace = "\n".join(trace_lines)
                ret.append(trace)
            header_cnt += 1
            header_ix = i
    return ret


def tla_trace_to_informal_trace_format_trace(trace):
    """
    Convert a tla trace from TLC stdout to the Informal Trace Format
    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#adr-015-informal-trace-format-in-json
    """

    def split_into_states(trace):
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
            ret.append(lines[header_ix + 1 : i])

        ret = ["\n".join(lines) for lines in ret]
        return ret

    trace = split_into_states(trace)
    # Use tla parser to get the AST for the expression
    # TODO: write tree visitor
    trace = [parse_expr(state) for state in trace]
    return trace
