import os

from modelator.util.parse.tla import parser, to_str
from modelator.util.parse.tlc_stdout import extract_traces

from ...helper import get_resource_dir


def test_extract_traces():

    fn = "TlcMultipleTraceParse.txt"
    fn = os.path.join(get_resource_dir(), fn)
    content = None
    with open(fn, "r") as fd:
        content = fd.read()

    result = extract_traces(content)
    assert len(result) == 4


def test_parse_state_expression():
    """
    Test the tla_python library capabilities to parse TLA+ snippets
    included in counterexamples generated by TLC.
    """

    fns = [
        "TlcStateExpressionExample0.txt",
        "TlcStateExpressionExample1.txt",
        "TlcStateExpressionExample2.txt",
        "TlcStateExpressionExample3.txt",
    ]
    expressions = []
    for fn in fns:
        path = os.path.join(get_resource_dir(), fn)
        with open(path, "r") as fd:
            content = fd.read()
            expressions.append(content)

    for expr in expressions:
        tree = parser.parse_expr(expr, nodes=to_str.Nodes)
        assert tree is not None
        s = tree.to_str(width=80)
