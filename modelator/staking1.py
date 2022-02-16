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
from .staking1_aux import select_subset


def fn(s):
    root = "/Users/danwt/Documents/work/cosmos-sdk-fork/x/staking/mbt"
    return os.path.join(root, s)


def main():

    IN_FN = "tlc.8steps.out"
    OUT_FN = "model_based_testing_traces_auto.json"
    # OUT_FN = "debug.json"

    txt = None
    print("Reading TLC stdout")
    with open(fn(IN_FN), "r") as fd:
        txt = fd.read()
    print("Extracting TLC traces")
    traces = extract_traces(txt)
    print(f"Processing {len(traces)} traces")

    def project(t):
        s = set()
        for i, state in enumerate(t):
            outcome = None
            nature = None
            for line in state.split("\n"):
                if "nature" in line:
                    nature = line[line.find(">") + 3 : -2]
                if "outcome" in line:
                    outcome = line[line.find("=") + 3 : -1]
            e = (i / 2, nature, outcome)
            s.add(e)
        return s

    print(f"Projecting")
    projected = [project(t) for t in traces]
    print(f"Selecting subset")
    indexes_of_best, loss_value, random_choice_loss_value = select_subset(
        projected, target_size=64, iterations=240000
    )
    traces = [traces[i] for i in indexes_of_best]
    print(f"Subset selected")
    print(f"Final loss value:         {loss_value}")
    print(f"Random loss value:        {random_choice_loss_value}")
    print(f"Ratio compared to random: {loss_value/random_choice_loss_value}")

    print(f"Translating to ITF")
    traces = [tlc_trace_to_informal_trace_format_trace(t) for t in traces]
    traces = [with_lists(t) for t in traces]
    traces = [with_records(t) for t in traces]
    print(f"Serializing")
    traces = [JsonSerializer().visit(t) for t in traces]
    with open(fn(OUT_FN), "w") as fd:
        fd.write(json.dumps(traces, indent=2))
    print("Done.")
