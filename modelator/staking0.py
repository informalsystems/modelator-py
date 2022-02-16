import os

from modelator.tlc.pure import tlc_pure
from modelator.util.tlc.cli import tlc_itf
import json


def fn(s):
    root = "/Users/danwt/Documents/work/cosmos-sdk-fork/x/staking/mbt"
    return os.path.join(root, s)


def read_tla():
    with open(fn("staking.tla"), "r") as fd:
        return fd.read()


def read_folds():
    with open(fn("tlcFolds.tla"), "r") as fd:
        return fd.read()


def read_cfg(inv):
    return f"""CONSTANTS
v0 = v0
v1 = v1
INIT Init
NEXT Next
VIEW View
INVARIANT {inv}
SYMMETRY ValidatorPermutationsSymmetry"""


def main():
    invs = [f"P{i}" for i in range(0, 14)]

    invs = [
        "P0",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
        "P7",
        "P8",
        # "P9",
        # "P10",
        # "P11",
        # "P12"
    ]

    tla = read_tla()
    folds = read_folds()

    def proc(inv):
        cfg = read_cfg(inv)
        obj = {}
        obj["args"] = {}
        obj["args"]["config"] = "staking.cfg"
        obj["args"]["file"] = "staking.tla"
        obj["args"]["workers"] = "auto"
        obj["files"] = {}
        obj["files"]["staking.tla"] = tla
        obj["files"]["staking.cfg"] = cfg
        obj["files"]["tlcFolds.tla"] = folds
        obj["jar"] = "/Users/danwt/Documents/model-checkers/tla2tools.jar"
        res = tlc_pure(json=obj)
        itf = tlc_itf(json={"stdout": res["stdout"]})
        with open(fn(f"model_based_testing_traces_{inv}.json"), "w") as fd:
            fd.write(json.dumps(itf, indent=2))

    for inv in invs:
        proc(inv)
        print(f"Done {inv}")

    def fun(inv):
        return f"""func TestTraces{inv}(t *testing.T) {{
    ExecuteTraces(t, loadTraces("mbt/model_based_testing_traces_{inv}.json"))
}}
"""

    s = """"""
    for inv in invs:
        s += fun(inv)
    with open(fn(f"stub"), "w") as fd:
        fd.write(s)
