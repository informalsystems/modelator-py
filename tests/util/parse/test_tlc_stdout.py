import os

from modelator.util.parse.tlc_stdout import (
    extract_traces,
    tla_trace_to_informal_trace_format_trace,
)

from ...helper import get_resource_dir
from modelator.util.parse.tla import parser
from modelator.util.parse.tla.to_str import Nodes as to_str_Nodes


def test_extract_traces():

    fn = "TlcMultipleTraceParse.txt"
    fn = os.path.join(get_resource_dir(), fn)
    content = None
    with open(fn, "r") as fd:
        content = fd.read()

    result = extract_traces(content)
    assert len(result) == 4


def test_tla_trace_to_informal_trace_format_trace():

    trace = """State 1: <Initial predicate>
/\ steps = 0
/\ x = "hello"
/\ y = 42
/\ z = { [a |-> 1, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 1, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>] }

State 2: <Next line 18, col 5 to line 21, col 50 of module TlcMultipleTraceParse>
/\ steps = 1
/\ x = "hello"
/\ y = 42
/\ z = { [a |-> 1, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 1, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>] }

State 3: <Next line 18, col 5 to line 21, col 50 of module TlcMultipleTraceParse>
/\ steps = 2
/\ x = "hello"
/\ y = 42
/\ z = { [a |-> 1, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 1, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "foo", c |-> <<1, "cat", [dog |-> 3]>>],
  [a |-> 2, b |-> "bar", c |-> <<1, "cat", [dog |-> 3]>>] }"""

    result = tla_trace_to_informal_trace_format_trace(trace)
    print(result)


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
