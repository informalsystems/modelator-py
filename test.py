import json

obj = {}
obj["files"] = {}
fns = ["HelloWorld.tla", "HelloWorld.cfg"]
for fn in fns:
    with open(fn, "r") as fd:
        obj["files"][fn] = fd.read()
obj["jar"] = "/Users/danwt/Documents/model-checkers/tla2tools.jar"
obj["args"] = {}
obj["args"]["workers"] = "auto"
obj["args"]["config"] = "HelloWorld.cfg"
obj["args"]["file"] = "HelloWorld.tla"
with open("HelloWorld_tlc_pure.json", "w") as fd:
    fd.write(json.dumps(obj, indent=4, sort_keys=True))
