import os
import json


from modelator.util.tlc.stdout_to_informal_trace_format import (
    extract_traces,
    tlc_trace_to_informal_trace_format_trace,
)

from modelator.util.informal_trace_format import (
    JsonSerializer,
    with_lists,
    with_records,
)


def main():
    d = "/Users/danwt/Documents/work/cosmos-sdk-fork/x/staking/mbt"
    fn = "long.txt"
    fp = os.path.join(d, fn)
    out_fn = os.path.join(d, "long.json")
    content = None
    with open(fp, "r") as fd:
        content = fd.read()
    traces = extract_traces(content)
    traces = [tlc_trace_to_informal_trace_format_trace(t) for t in traces]

    traces = [with_lists(t) for t in traces]
    traces = [with_records(t) for t in traces]
    print(f"Serializing")
    traces = [JsonSerializer().visit(t) for t in traces]
    with open(out_fn, "w") as fd:
        fd.write(json.dumps(traces, indent=2))
    print("Done.")
