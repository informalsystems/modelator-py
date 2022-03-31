import json as stdjson
import os
import sys
from contextlib import redirect_stdout

from modelator_py.apalache import (
    ApalacheArgs,
    ApalachePureCmd,
    ApalacheRawCmd,
    apalache_pure,
    apalache_raw,
)
from modelator_py.tlc import TlcArgs, TlcPureCmd, TlcRawCmd, tlc_pure, tlc_raw
from modelator_py.util.tlc.itf import TlcITFCmd, tlc_itf

# mypy: ignore-errors

"""
This program demonstrates programatic use of the utilities.

You can try out this code with the following minimal environment. This has no
relationship to the Poetry developer environment that modelator-py itself uses.

```
cd samples;
python3 -m venv env;
source env/bin/activate;
which python3; # Should have suffix 'env/bin/python3'
python3 -m pip install -r requirements.txt
```

then call the examples with

```
python3 library_usage.py <args>
```
"""


def tlc_path():
    # For demo purposes, find the path to TLC in this repo, but you can use
    # a path to your own TLC jar.
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "large/tlc_2_18.jar")
    )


def apa_path():
    # For demo purposes, find the path to Apalache in this repo, but you can use
    # a path to your own Apalache jar.
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "large/apa_0_23_0.jar")
    )


def read_file(fn):
    # Utility used in these demos
    with open(os.path.join(os.path.dirname(__file__), fn), "r") as fd:
        return {fn: fd.read()}


def apalache_pure_json_demo():
    """
    Call Apalache, encapsulated to remove side effects.
    """

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

    result = apalache_pure(json=data)

    # That's it. Now print for demo purposes.

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


def apalache_pure_cmd_demo():
    """
    Call Apalache, encapsulated to remove side effects.
    """

    cmd = ApalachePureCmd
    cmd.jar = apa_path()
    cmd.files = read_file("Hello.tla") | read_file("Hello.cfg")
    cmd.args = ApalacheArgs()
    cmd.args.cmd = "check"
    cmd.args.nworkers = 4
    cmd.args.file = "Hello.tla"
    cmd.args.config = "Hello.cfg"

    result = apalache_pure(cmd=cmd)

    # That's it. Now print for demo purposes.

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


def apalache_raw_json_demo():
    """
    Call Apalache directly without encapsulation.
    """

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

    result = apalache_raw(json=data)

    # That's it. Now print for demo purposes.

    stdout_pretty = result.stdout.decode("unicode_escape")
    stderr_pretty = result.stderr.decode("unicode_escape")

    obj_to_print = {}
    obj_to_print["shell_cmd"] = result.args
    obj_to_print["return_code"] = result.returncode
    obj_to_print["stdout"] = stdout_pretty
    obj_to_print["stderr"] = stderr_pretty

    to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
    print(to_print)


def apalache_raw_cmd_demo():
    """
    Call Apalache directly without encapsulation.
    """

    cmd = ApalacheRawCmd
    cmd.jar = apa_path()
    cmd.cwd = os.getcwd()
    cmd.args = ApalacheArgs()
    cmd.args.cmd = "check"
    cmd.args.nworkers = 4
    cmd.args.file = "Hello.tla"
    cmd.args.config = "Hello.cfg"

    result = apalache_raw(cmd=cmd)

    # That's it. Now print for demo purposes.

    stdout_pretty = result.stdout.decode("unicode_escape")
    stderr_pretty = result.stderr.decode("unicode_escape")

    obj_to_print = {}
    obj_to_print["shell_cmd"] = result.args
    obj_to_print["return_code"] = result.returncode
    obj_to_print["stdout"] = stdout_pretty
    obj_to_print["stderr"] = stderr_pretty

    to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
    print(to_print)


def tlc_pure_json_demo():
    """
    Call TLC, encapsulated to remove side effects.
    """

    data = {
        "jar": tlc_path(),
        "args": {
            "workers": "auto",
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
        "files": read_file("Hello.tla") | read_file("Hello.cfg"),
    }

    result = tlc_pure(json=data)

    # That's it. Now print for demo purposes.

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


def tlc_pure_cmd_demo():
    """
    Call TLC, encapsulated to remove side effects.
    """

    cmd = TlcPureCmd()
    cmd.jar = tlc_path()
    cmd.files = read_file("Hello.tla") | read_file("Hello.cfg")
    cmd.args = TlcArgs()
    cmd.args.workers = "auto"
    cmd.args.file = "Hello.tla"
    cmd.args.config = "Hello.cfg"

    result = tlc_pure(cmd=cmd)

    # That's it. Now print for demo purposes.

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


def tlc_raw_json_demo():
    """
    Call TLC directly without encapsulation.
    """

    data = {
        "jar": tlc_path(),
        "cwd": os.getcwd(),
        "args": {
            "workers": "auto",
            "file": "Hello.tla",
            "config": "Hello.cfg",
        },
    }

    result = tlc_raw(json=data)

    # That's it. Now print for demo purposes.

    stdout_pretty = result.stdout.decode("unicode_escape")
    stderr_pretty = result.stderr.decode("unicode_escape")

    obj_to_print = {}
    obj_to_print["shell_cmd"] = result.args
    obj_to_print["return_code"] = result.returncode
    obj_to_print["stdout"] = stdout_pretty
    obj_to_print["stderr"] = stderr_pretty

    to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
    print(to_print)


def tlc_raw_cmd_demo():
    """
    Call TLC directly without encapsulation.
    """

    cmd = TlcRawCmd
    cmd.jar = tlc_path()
    cmd.cwd = os.getcwd()
    cmd.args = TlcArgs()
    cmd.args.workers = "auto"
    cmd.args.file = "Hello.tla"
    cmd.args.config = "Hello.cfg"

    result = tlc_raw(cmd=cmd)

    # That's it. Now print for demo purposes.

    stdout_pretty = result.stdout.decode("unicode_escape")
    stderr_pretty = result.stderr.decode("unicode_escape")

    obj_to_print = {}
    obj_to_print["shell_cmd"] = result.args
    obj_to_print["return_code"] = result.returncode
    obj_to_print["stdout"] = stdout_pretty
    obj_to_print["stderr"] = stderr_pretty

    to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
    print(to_print)


def tlc_itf_json_demo():
    """
    Extract traces in ITF format from the stdout of a TLC run
    """

    # See TlcTraces.out for example TLC output

    data = {
        "stdout": read_file("TlcTraces.out")["TlcTraces.out"],
    }

    result = tlc_itf(json=data)

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


def tlc_itf_cmd_demo():
    """
    Extract traces in ITF format from the stdout of a TLC run
    """

    # See TlcTraces.out for example TLC output

    cmd = TlcITFCmd()
    cmd.stdout = read_file("TlcTraces.out")["TlcTraces.out"]

    result = tlc_itf(cmd=cmd)

    to_print = stdjson.dumps(result, indent=4, sort_keys=True)
    print(to_print)


if __name__ == "__main__":
    if sys.argv[1] == "apalache_pure_json":
        apalache_pure_json_demo()
    if sys.argv[1] == "apalache_pure_cmd":
        apalache_pure_cmd_demo()
    if sys.argv[1] == "apalache_raw_json":
        apalache_raw_json_demo()
    if sys.argv[1] == "apalache_raw_cmd":
        apalache_raw_cmd_demo()
    if sys.argv[1] == "tlc_pure_json":
        tlc_pure_json_demo()
    if sys.argv[1] == "tlc_pure_cmd":
        tlc_pure_cmd_demo()
    if sys.argv[1] == "tlc_raw_json":
        tlc_raw_json_demo()
    if sys.argv[1] == "tlc_raw_cmd":
        tlc_raw_cmd_demo()
    if sys.argv[1] == "tlc_itf_json":
        tlc_itf_json_demo()
    if sys.argv[1] == "tlc_itf_cmd":
        tlc_itf_cmd_demo()
    if sys.argv[1] == "all":
        for fun in [
            apalache_pure_json_demo,
            apalache_pure_cmd_demo,
            apalache_raw_json_demo,
            apalache_raw_cmd_demo,
            tlc_pure_json_demo,
            tlc_pure_cmd_demo,
            tlc_raw_json_demo,
            tlc_raw_cmd_demo,
            tlc_itf_json_demo,
            tlc_itf_cmd_demo,
        ]:
            with open(f"{fun.__name__}.json", "w") as fd:
                with redirect_stdout(fd):
                    fun()
