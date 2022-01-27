def extract_traces(stdout: str) -> list[str]:
    """
    Extract zero, one or more traces from the stdout of TLC.

    Note: Does not support lasso traces
    """
    ret = []
    lines = stdout.split("\n")
    HEADER = "Error: Invariant"
    FOOTER = "Model checking completed."
    header_cnt = 0
    header_ix = -1
    for i, line in enumerate(lines):
        if line.startswith(HEADER) or line.startswith(FOOTER):
            if 0 < header_cnt:
                trace_lines = lines[header_ix + 2 : i]
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
        return ret

    trace = split_into_states(trace)
    """
    TODO: this is incomplete and is dependent on functionality to convert
    TLA+ expressions to Informal Trace Format
    """
