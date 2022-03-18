from modelator.tlc.pure import tlc_pure, PureCmd, TlcArgs
from modelator.util.tlc.itf import tlc_itf, TLCITFCmd
import os
import json


def cfg(inv):
    return f"""CONSTANTS
    v0 = v0
    v1 = v1
INIT Init
NEXT Next
VIEW View
SYMMETRY ValidatorPermutationsSymmetry
INVARIANT P{inv}"""


DIR = "/Users/danwt/Documents/work/cosmos-sdk-fork/mbt/x/staking"

invs = list(range(0, 9))


def main():
    print("Running scratch2")
    tlc_cmd = PureCmd()
    tlc_cmd.jar = "/Users/danwt/Documents/model-checkers/tla2tools.jar"
    tlc_cmd.files = {}
    tlc_cmd.args = TlcArgs(file="spec.tla")
    itf_cmd = TLCITFCmd()
    itf_cmd.lists = True
    itf_cmd.records = True
    with open(os.path.join(DIR, "spec.tla"), "r") as fd:
        tlc_cmd.files["spec.tla"] = fd.read()
    with open(os.path.join(DIR, "tlcFolds.tla"), "r") as fd:
        tlc_cmd.files["tlcFolds.tla"] = fd.read()
    for inv in invs:
        tlc_cmd.files["spec.cfg"] = cfg(inv)
        result = tlc_pure(cmd=tlc_cmd)
        stdout = result["stdout"]
        # print(result["shell_cmd"])
        print(inv, result["return_code"])
        # print(result["stderr"])
        # print(result["stdout"])
        itf_cmd.stdout = stdout
        traces = tlc_itf(cmd=itf_cmd)
        with open(os.path.join(DIR, f"traces/P{inv}.json"), "w") as fd:
            fd.write(json.dumps(traces))
