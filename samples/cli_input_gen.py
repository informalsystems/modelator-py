import json
import os

from helper import apa_path, read_file, tlc_path

# mypy: ignore-errors

"""
Used to generate JSON input for CLI examples.
"""


def apalache_pure():
    data = {
        "jar": apa_path(),
        "args": {
            "cmd": "check",
            "nworkers": 4,
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
        "files": read_file("Hello.tla") | read_file("Hello.cfg"),
    }
    with open("cli_input_apalache_pure.json", "w") as fd:
        fd.write(json.dumps(data, indent=4))


def apalache_raw():
    data = {
        "jar": apa_path(),
        "cwd": os.getcwd(),
        "args": {
            "cmd": "check",
            "nworkers": 4,
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
    }
    with open("cli_input_apalache_raw.json", "w") as fd:
        fd.write(json.dumps(data, indent=4))


def tlc_pure():

    data = {
        "jar": tlc_path(),
        "args": {
            "workers": "auto",
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
        "files": read_file("Hello.tla") | read_file("Hello.cfg"),
    }
    with open("cli_input_tlc_pure.json", "w") as fd:
        fd.write(json.dumps(data, indent=4))


def tlc_raw():
    data = {
        "jar": tlc_path(),
        "cwd": os.getcwd(),
        "args": {
            "workers": "auto",
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
    }
    with open("cli_input_tlc_raw.json", "w") as fd:
        fd.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    apalache_pure()
    apalache_raw()
    tlc_pure()
    tlc_raw()
