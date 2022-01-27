from .tla.parser import parse_expr


def tla_expression_to_informal_trace_format(expression: str):
    """TODO:"""
    tree = parse_expr(expression)
