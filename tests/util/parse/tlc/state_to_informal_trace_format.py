import os

from modelator.util.parse.tlc.state_to_informal_trace_format import (
    state_to_informal_trace_format_state,
)

from ....helper import get_resource_dir


def get_expr():
    fn = "TlcStateExpressionExample0.txt"
    path = os.path.join(get_resource_dir(), fn)
    with open(path, "r") as fd:
        return fd.read()


def test_tla_state_expression_to_informal_trace_format_state():

    """
    json in the Informal Trace Format contains a state field mapping to a
    list of states.

    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format

    Test the translation of a single state.
    """

    # poetry run pytest tests/util/parse/tlc/state_to_informal_trace_format.py -s -k 'test_tla_state_expression_to_informal_trace_format_state'

    s = get_expr()
    res = state_to_informal_trace_format_state(s)
    assert res is not None
    print(res)
