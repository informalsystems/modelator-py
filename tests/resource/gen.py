import json

"""
This program generates an example
"""

data = {
    "jar": "~/Documents/work/mbt-python/apalache-pkg-0.17.1-full.jar",
    "args": {
        "cmd": "check",
        "max_error": 2,
        "view": "View",
        "inv": "IsThree",
        "config": "2PossibleTraces.cfg",
        "file": "2PossibleTracesTests.tla",
    },
    "files": {},
}

fns = ["2PossibleTraces.cfg", "2PossibleTraces.tla", "2PossibleTracesTests.tla"]

for fn in fns:
    with open(fn, "r") as fd:
        data["files"][fn] = fd.read()  # type: ignore

out = "apalache_pure_example.json"

with open(out, "w") as fd:
    fd.write(json.dumps(data, indent=4))

print("Done")
