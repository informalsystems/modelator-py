import json as stdjson

from recordclass import recordclass

from ..informal_trace_format import JsonSerializer, with_lists, with_records
from .stdout_to_informal_trace_format import (
    extract_traces,
    tlc_trace_to_informal_trace_format_trace,
)

# mypy: ignore-errors

cmd_fields = (
    "stdout",  # Captured stdout from TLC execution
    "lists",  # Transform 1-indexed TLA+ functions into lists
    "records",  # Transform string indexed functions into records
)

Cmd = recordclass("Cmd", cmd_fields, defaults=(None,) * len(cmd_fields))


def json_to_cmd(json) -> Cmd:
    json = {"stdout": None, "lists": True, "records": True} | json
    cmd = Cmd()
    cmd.stdout = json["stdout"]
    cmd.lists = json["lists"]
    cmd.records = json["records"]
    return cmd


def tlc_itf(*, cmd=None, json=None):  # types: ignore
    """
    Extract a list of execution traces in the Informal Trace Format
    from the stdout of a TLC execution.
    """

    if json is not None:
        cmd = json_to_cmd(json)

    assert cmd.stdout is not None, "tlc_itf requires TLC's stdout as input data"
    tlc_traces = extract_traces(cmd.stdout)
    itf_traces = [
        tlc_trace_to_informal_trace_format_trace(trace) for trace in tlc_traces
    ]
    if cmd.lists:
        itf_traces = [with_lists(e) for e in itf_traces]
    if cmd.records:
        itf_traces = [with_records(e) for e in itf_traces]
    itf_traces_objects = [JsonSerializer().visit(e) for e in itf_traces]
    return itf_traces_objects


class Tlc:
    def __init__(self, stdin):
        self._stdin = stdin

    def itf(
        self,
        *,
        lists=True,
        records=True,
        json=False,  # Read parameters from Json?
    ):
        result = None
        if json:
            json_dict = stdjson.loads(self._stdin.read())
            result = tlc_itf(json=json_dict)
        else:
            assert (
                self._stdin is not None
            ), "TLC's stdout string should be passed on stdin if not passing json"
            cmd = Cmd()
            cmd.stdout = self._stdin.read()
            cmd.lists = lists
            cmd.records = records
            assert (
                cmd.stdout is not None
            ), "TLC's stdout string should be passed on stdin if not passing json"
            result = tlc_itf(cmd=cmd)

        obj_to_print = {}
        obj_to_print["traces"] = result

        to_print = stdjson.dumps(obj_to_print, indent=4, sort_keys=True)
        print(to_print)
