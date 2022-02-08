import os

from modelator.util.parse.tlc.state_to_informal_trace_format import (
    state_to_informal_trace_format_state,
)

from ....helper import get_resource_dir


def test_create_ast_from_tlc_state_expressions():

    """
    json in the Informal Trace Format contains a state field mapping to a
    list of states.

    https://apalache.informal.systems/docs/adr/015adr-trace.html?highlight=trace%20format#the-itf-format

    Test the translation of a single state.
    """

    # poetry run pytest tests/util/parse/tlc/state_to_informal_trace_format.py -s -k 'test_tla_state_expression_to_informal_trace_format_state'

    fns = [
        "TlcStateExpressionExample0.txt",
        "TlcStateExpressionExample1.txt",
        "TlcStateExpressionExample2.txt",
        "TlcStateExpressionExample3.txt",
        "TlcStateExpressionExample4.txt",
        "TlcStateExpressionExample5.txt",
        "TlcStateExpressionExample6.txt",
        "TlcStateExpressionExample7.txt",
    ]

    expressions = []

    for fn in fns:
        path = os.path.join(get_resource_dir(), fn)
        with open(path, "r") as fd:
            content = fd.read()
            expressions.append(content)

    for s in expressions:
        res = state_to_informal_trace_format_state(s)
        assert res is not None
