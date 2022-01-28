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

    # poetry run pytest tests/util/parse/test_informal_trace_format.py -s -k 'test_translate_tla_state_simple'

    state = """Foo == 
/\ one_indexed_sequential_map = <<42, 42, 42, 42, 42>>
/\ string_indexed_map = [two |-> 42, one |-> 42]
/\ record = [foo |-> 42, bar |-> 43]
/\ tuple = <<1, 2>>
/\ bool = FALSE
/\ set = {1, 2, 3}
/\ list = <<1, "two">>
/\ json_int = 123
/\ string_literal = "hello"
/\ map = ( 0 :> 42 @@
  1 :> 42 @@
  2 :> 42 @@
  3 :> 42 @@
  4 :> 42 @@
  5 :> 42 @@
  6 :> "forty-two" @@
  8 :> "forty-two" @@
  13 :> "forty-two" )
/\ zero_indexed_sequential_map = (0 :> 42 @@ 1 :> 42 @@ 2 :> 42 @@ 3 :> 42 @@ 4 :> 42 @@ 5 :> 42)"""

    module = """---- MODULE Foo ----
Foo == 
/\ one_indexed_sequential_map = <<42, 42, 42, 42, 42>>
/\ string_indexed_map = [two |-> 42, one |-> 42]
/\ record = [foo |-> 42, bar |-> 43]
/\ tuple = <<1, 2>>
/\ bool = FALSE
/\ set = {1, 2, 3}
/\ list = <<1, "two">>
/\ json_int = 123
/\ string_literal = "hello"
/\ map = 0 :> 42 @@
  1 :> 42 @@
  2 :> 42 @@
  3 :> 42 @@
  4 :> 42 @@
  5 :> 42 @@
  6 :> "forty-two" @@
  8 :> "forty-two" @@
  13 :> "forty-two"
===================="""

    tree = parser.parse(module, nodes=to_str_Nodes)
    # tree = parser.parse_expr(state, nodes=to_str_Nodes)
    text = tree.to_str(width=80)
    print(text)