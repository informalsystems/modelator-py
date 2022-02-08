import os

from modelator.util.parse.tla import parser
from modelator.util.parse.tla.to_str import Nodes as to_str_Nodes


def test_tla_state_expression_to_informal_trace_format_state():

    """
    json in the Informal Trace Format contains a state field mapping to a
    list of states.

    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format

    Test the translation of a single state.
    """

    # poetry run pytest tests/util/parse/test_informal_trace_format.py -s -k 'test_tla_state_expression_to_informal_trace_format_state'

    s = """/\ sequence_indexed_map = (<<"one", "two">> :> 42)
/\ one_indexed_sequential_map = <<42, 42, 42, 42, 42>>
/\ string_indexed_map = [two |-> 42, one |-> 42]
/\ record = [foo |-> 42, bar |-> 43]
/\ tuple = <<1, 2>>
/\ bool = TRUE
/\ map_indexed_map = ([foo |-> 42, bar |-> 42] :> 42)
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

    tree = parser.parse_expr(s, nodes=to_str_Nodes)
    assert tree is not None
    text = tree.to_str(width=80)
    print(text)


def test_integer():
    s = "x = 1"
    tree = parser.parse_expr(s, nodes=to_str_Nodes)
    assert tree is not None
    text = tree.to_str(width=80)
    print(text)
