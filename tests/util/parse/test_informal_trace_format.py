import os

from modelator.util.parse.tla import parser
from modelator.util.parse.tla.to_str import Nodes as to_str_Nodes
from modelator.util.parse.informal_trace_format import (
    tla_expression_to_informal_trace_format,
)

from ...helper import get_resource_dir


def test_translate_tla_state_simple():

    """
    json in the Informal Trace Format contains a state field mapping to a
    list of states.

    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format

    Test the translation of a single state.
    """

    state = None
    FN = "TlcTraceParseSimpleState.tla"
    path = os.path.join(get_resource_dir(), FN)
    with open(path, "r") as fd:
        state = fd.read()
    assert state is not None, f"Could not load test data from {FN}"

    # tree = parser.parse_expr(state, nodes=to_str_Nodes)
    tree = parser.parse_expr(state)
    # text = tree.to_str(width=80)
    print(tree)
    # print(text)


def test_parse_tla_module_simple():

    content = None
    FN = "TlcTraceParse.tla"
    path = os.path.join(get_resource_dir(), FN)
    with open(path, "r") as fd:
        content = fd.read()
    assert content is not None, f"Could not load test data from {FN}"

    tree = parser.parse(content, nodes=to_str_Nodes)
    s = tree.to_str(width=80)
