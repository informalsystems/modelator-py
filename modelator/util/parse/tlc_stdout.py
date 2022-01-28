def extract_traces(stdout: str):
    """
    Extract zero, one or more traces from the stdout of TLC.

    Note: Does not support lasso traces
    """

    def extract_trace_strings():
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

    def split_into_states(trace_str):
        """
        Returns a list of states.

        A trace string from TLC is a sequence of [header, content] pairs.
        The headers are not valid TLA+.
        This function returns a list where each item is a TLA+ expression.
        """
        ret = []
        lines = trace_str.split("\n")
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

    trace_strings = extract_trace_strings()
    traces = [split_into_states(s) for s in trace_strings]
    return traces
