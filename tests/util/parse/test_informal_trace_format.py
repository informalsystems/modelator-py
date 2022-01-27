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

    # TODO: this is not currently working due to a bug in tla_parser
    #

    state = None
    FN = "TlcTraceParseSimpleState.tla"
    path = os.path.join(get_resource_dir(), FN)
    with open(path, "r") as fd:
        state = fd.read()
    assert state is not None, f"Could not load test data from {FN}"

    state = """/\ one_indexed_sequential_map = <<42, 42, 42, 42, 42>>
/\ string_indexed_map = [two |-> 42, one |-> 42]
/\ record = [foo |-> 42, bar |-> 43]
/\ tuple = <<1, 2>>
/\ bool = FALSE
/\ set = {1, 2, 3}
/\ list = <<1, "two">>
/\ map = ( 0 :> 42 @@
  1 :> 42 @@
  2 :> 42 @@
  3 :> 42 @@
  4 :> 42 @@
  5 :> 42 @@
  6 :> "forty-two" @@
  8 :> "forty-two" @@
  13 :> "forty-two" )
/\ json_int = 123
/\ string_literal = "hello"
/\ zero_indexed_sequential_map = (0 :> 42 @@ 1 :> 42 @@ 2 :> 42 @@ 3 :> 42 @@ 4 :> 42 @@ 5 :> 42)"""

    tree = parser.parse_expr(state, nodes=to_str_Nodes)
    text = tree.to_str(width=80)
    print(text)
