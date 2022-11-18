from dataclasses import dataclass
from typing import Optional

from modelator_py.helper import parallel_map

from ..informal_trace_format import JsonSerializer, with_lists, with_records
from .stdout_to_informal_trace_format import (
    extract_traces,
    tlc_trace_to_informal_trace_format_trace,
)

# mypy: ignore-errors


@dataclass
class TlcITFCmd:
    stdout: Optional[str] = None  # Captured stdout from TLC execution
    lists: Optional[str] = None  # Transform 1-indexed TLA+ functions into lists
    records: Optional[str] = None  # Transform string indexed functions into records


def json_to_cmd(json) -> TlcITFCmd:
    json = {"stdout": None, "lists": True, "records": True} | json
    cmd = TlcITFCmd()
    cmd.stdout = json["stdout"]
    cmd.lists = json["lists"]
    cmd.records = json["records"]
    return cmd


def tlc_itf(*, cmd=None, json=None):  # types: ignore
    """
    Extract a list of execution traces in the Informal Trace Format from the
    stdout of a TLC execution.

    Returns a list of ITFTrace objects.

    Benefits from multiple cpu cores as parallelizes TLA+ raw text to AST parsing.
    """

    if json is not None:
        cmd = json_to_cmd(json)

    assert cmd.stdout is not None, "tlc_itf requires TLC's stdout as input data"

    tlc_traces = extract_traces(cmd.stdout)

    itf_traces = parallel_map(tlc_trace_to_informal_trace_format_trace, tlc_traces)

    if cmd.lists:
        itf_traces = parallel_map(with_lists, itf_traces)
    if cmd.records:
        itf_traces = parallel_map(with_records, itf_traces)

    itf_traces_objects = parallel_map(lambda t: JsonSerializer().visit(t), itf_traces)

    return itf_traces_objects
