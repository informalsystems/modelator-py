def extract_traces(stdout: str):
    """
    Extract zero, one or more traces from the stdout of TLC.
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
