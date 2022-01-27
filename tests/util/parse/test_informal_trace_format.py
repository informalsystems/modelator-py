import os

from modelator.util.parse.tla import parser
from modelator.util.parse.tla.to_str import Nodes as to_str_Nodes


def test_parse_tla_state():

    state = """/\ steps = 0
/\ x = "hello"
/\ y = 42
/\ z = { [a |-> 1, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 1, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>] }"""

    tree = parser.parse_expr(state, nodes=to_str_Nodes)
    text = tree.to_str(width=80)
    print(text)
