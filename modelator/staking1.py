import os

from modelator.tlc.pure import tlc_pure
from modelator.util.tlc.cli import tlc_itf
import json
from modelator.util.tlc.stdout_to_informal_trace_format import (
    split_into_states,
    extract_traces,
)
from modelator.util.tlc.state_to_informal_trace_format import (
    state_to_informal_trace_format_state,
)
from modelator.util.informal_trace_format import (
    ITFTrace,
    JsonSerializer,
    with_lists,
    with_records,
)
from .staking1_aux import select_subset


def fn(s):
    root = "/Users/danwt/Documents/work/cosmos-sdk-fork/x/staking/mbt"
    return os.path.join(root, s)


def main():

    txt = None
    print("Reading TLC stdout")
    with open(fn("tlc.8steps.action.outcome.out"), "r") as fd:
        txt = fd.read()
    print("Extracting trace strings")
    traces = extract_traces(txt)
    print(f"Processing {len(traces)} traces")
    traces = [split_into_states(t) for t in traces]

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
        projected, target_size=32
    )
    traces = [traces[i] for i in indexes_of_best]
    print(f"Subset selected")
    print(f"Final loss value: {loss_value}")
    print(f"Random loss value: {random_choice_loss_value}")
    print(f"Ratio of random: {loss_value/random_choice_loss_value}")

    def to_itf(t):
        states = [state_to_informal_trace_format_state(state) for state in t]
        vars = []
        if 0 < len(states):
            vars = list(states[0].var_value_map.keys())

        return ITFTrace(vars, states)

    print(f"Translating to ITF")
    traces = [to_itf(t) for t in traces]
    traces = [with_lists(t) for t in traces]
    traces = [with_records(t) for t in traces]
    print(f"Serializing")
    traces = [JsonSerializer().visit(t) for t in traces]
    with open(fn("model_based_testing_traces_8_steps_auto.json"), "w") as fd:
        fd.write(json.dumps(traces, indent=2))
    print("Done.")
