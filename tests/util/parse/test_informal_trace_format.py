import os
import copy

from modelator.util.parse.tla import parser, visit
from modelator.util.parse.tla.to_str import Nodes as Nodes
from ...helper import get_resource_dir

from collections import defaultdict


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

    # poetry run pytest tests/util/parse/test_informal_trace_format.py -s -k 'test_tla_state_expression_to_informal_trace_format_state'

    s = get_expr()
    tree = parser.parse_expr(s, nodes=Nodes)
    assert tree is not None
    text = tree.to_str(width=80)


def test_debug():
    print()
    s = get_expr()
    tree = parser.parse_expr(s, nodes=Nodes)
    assert tree is not None
    text = tree.to_str(width=80)
    # print(text)
    visitor = Experiment()
    variable_pairs = visitor.visit(tree)
    for key, value in variable_pairs:
        print(key)
        print(value)
