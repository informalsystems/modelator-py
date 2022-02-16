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


def project_action_outcome(t):
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


def project_q_lens(t):
    def validator(lines):
        found = None
        for i, line in enumerate(lines):
            if line.startswith("/\ validatorQ"):
                found = i
        return len(lines) - found

    def undelegation(lines):
        found = None
        for i, line in enumerate(lines):
            if line.startswith("/\ undelegationQ"):
                found = i
            if line.startswith("/\ unbondingHeight"):
                assert found is not None
                return i - found
        assert False

    def redelegation(lines):
        found = None
        for i, line in enumerate(lines):
            if line.startswith("/\ redelegationQ"):
                found = i
            if line.startswith("/\ tokens"):
                assert found is not None
                return i - found
        assert False

    s = set()
    lens = []
    for i, state in enumerate(t):
        lines = state.split("\n")
        e = (validator(lines), undelegation(lines), redelegation(lines))
        lens.append(e)
    for i in range(len(lens) - 1):
        a = lens[i]
        b = lens[i + 1]
        diff = [None] * 3
        for k in range(3):
            x = b[k] - a[k]
            if x == 0:
                diff[k] = 0
            else:
                diff[k] = x / abs(x)
        s.add(tuple(diff))
    return s


def main():

    IN_FN = "tlc.8steps.out"
    OUT_FN = "model_based_testing_traces_auto_queue_differential.json"
    # OUT_FN = "model_based_testing_traces_auto_action_outcome.json"
    # OUT_FN = "debug.json"

    txt = None
    print("Reading TLC stdout")
    with open(fn(IN_FN), "r") as fd:
        txt = fd.read()
    print("Extracting TLC traces")
    traces = extract_traces(txt)
    print(f"Processing {len(traces)} traces")

    print(f"Projecting")
    # projected = [project_action_outcome(t) for t in traces]
    projected = [project_q_lens(t) for t in traces]
    print(f"Selecting subset")
    indexes_of_best, loss_value, random_choice_loss_value = select_subset(
        projected, target_size=64, iterations=160000
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
