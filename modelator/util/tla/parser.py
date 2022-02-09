"""TLA+ parser using combinators."""
# Copyright 2020 by California Institute of Technology
# All rights reserved. Licensed under 3-clause BSD.
#
from . import _combinators as pco
from . import _expr_parser as ep
from . import _module_parser as mp
from . import _optable
from . import _proof_parser as pfp
from . import _tla_combinators, lex


def parse(module_text, nodes=None):
    """Return abstract syntax tree for `str`ing `module_text`.

    `module_text` is a module specification.
    Use the syntax tree classes from `nodes`.
    For example:

    ```python
    from . import parser
    from .to_str import Nodes

    module_text = r'''
    ---- MODULE Foo ----
    A == 1
    ====================
    '''

    tree = parser.parse(module_text, nodes=Nodes)
    ```
    """
    memo = _save(nodes)
    parser = mp.parse()
    init = _tla_combinators.init
    tokens = lex.tokenize(module_text, omit_preamble=True)
    tree, pst = pco.run(parser, init=init, source=tokens)
    _restore(memo)
    return tree


def parse_expr(expr, nodes=None):
    r"""Return abstract syntax tree for `str`ing `expr`.

    `expr` is an expression string.
    Use the syntax tree classes from `nodes`.
    For example:

    ```python
    from . import parser
    from .to_str import Nodes

    expr = r'x = 1 /\ y = 2'

    tree = parser.parse_expr(expr, nodes=Nodes)
    ```
    """
    memo = _save(nodes)
    parser = ep.expr(False)
    init = _tla_combinators.init
    tokens = lex.tokenize(expr, omit_preamble=False)
    tree, pst = pco.run(parser, init=init, source=tokens)
    _restore(memo)
    return tree


def _save(nodes):
    """Store the `tla_ast` attribute of parser modules.

    Set the AST nodes that are used by parser modules
    to the classes of `nodes`.
    """
    if nodes is None:
        return None
    assert nodes is not None
    memo = (ep.tla_ast, mp.nodes, pfp.tla_ast, _optable.nodes)
    ep.tla_ast = nodes
    mp.nodes = nodes
    pfp.tla_ast = nodes
    _optable.nodes = nodes
    _optable.optable = _optable._generate_optable()
    ep.fixities = ep._generate_fixities()
    return memo


def _restore(memo):
    """Set the `tla_ast` attribute of parser modules."""
    if memo is None:
        return
    assert memo is not None
    (ep.tla_ast, mp.nodes, pfp.tla_ast, _optable.nodes) = memo
    _optable.optable = _optable._generate_optable()
    ep.fixities = ep._generate_fixities()
