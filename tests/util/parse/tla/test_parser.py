"""Tests for the package `tla`."""
import pprint

import modelator.util.parse.tla._combinators as pco
import modelator.util.parse.tla._expr_parser as ep
import modelator.util.parse.tla._module_parser as mp
import modelator.util.parse.tla.visit
from modelator.util.parse.tla import _tla_combinators, lex, parser, to_str

expr_tests = [
    " FALSE ",
    " TRUE ",
    " FALSE /\\ TRUE ",
    " FALSE \\/ TRUE ",
    " FALSE => TRUE ",
    " IF FALSE THEN FALSE ELSE FALSE ",
    " IF x = 1 THEN 2 ELSE 3 ",
    " Nat ",
    " 15 ",
    ' "15" ',
    " @ ",
    " x + y ",
    " x - y ",
    " x / y ",
    " x % y ",
    " (x + 1) ",
    # quantification
    " \\A y \\in R:  <<u, v>> \\in S:  G(y, u, v) ",
    " \\E x, y:  x + y < 0 ",
    " \\AA x: TRUE ",
    " \\EE x, y: TRUE ",
    # `CHOOSE`
    " CHOOSE foo: FALSE ",
    # " CHOOSE <<u, v>> \in S:  F(u, v) ",
    # set theory
    " {1, 2, 3, 4 / 5} ",
    " {Foo \\in FALSE: FALSE} ",
    " {FALSE: x \\in {1, 2}} ",
    " {FALSE, FALSE} ",
    " SUBSET A.r ",
    " UNION {S \\in A:  S \\cap Q # {}} ",
    " {x \in Int:  x < 0} ",
    # functions
    " [foo |-> FALSE] ",
    " [foo |-> FALSE, bar |-> FALSE] ",
    " [FALSE -> FALSE] ",
    " [x, y \in S, uv \in T |-> G(x, y, uv[1], uv[2])] ",
    # " [x, y \in S, <<u, v>> \in T |-> G(x, y, u, v)] ",
    " f[x]' ",
    " f[k + 1, r] ",
    " [(A \cup B) -> C] ",
    " [a |-> u + v, b |-> w] ",
    " [a: Int, b: A \cup B] ",
    # EXCEPT
    " [f EXCEPT !.foo = FALSE] ",
    " [f EXCEPT ![FALSE] = FALSE] ",
    " [f EXCEPT ![FALSE] = FALSE, !.foo = FALSE] ",
    # "[f EXCEPT ![1, u] = e] ",
    " [f EXCEPT ![1].g = 2, ![<<t, 3>>] = u] ",
    # tuples
    " <<TRUE>> ",
    " <<TRUE, TRUE>> ",
    " <<1, 2, 3 + 5 >> ",
    " Int \X (1..2) \X Real ",
    # actions
    " (TRUE + 1)' ",
    " (1 + 2)' /\\ 3 ",
    " [x \\in {1, 2} |-> x' + 1] ",
    " [FALSE]_TRUE ",
    " <<TRUE>>_TRUE ",
    " [x' = x + 1]_<<x, y>> ",
    " <<x' = x + 1>>_<<x, y>> ",
    " [M \/ N]_<<u, v>> ",
    " <<x' = x + 1>>_(x * y) ",
    # liveness formulas
    " WF_TRUE (TRUE) ",
    " WF_<<x, y>>(N /\ M)",
    " WF_x(N) ",
    " SF_TRUE(TRUE) ",
    # `LAMBDA`
    " LAMBDA Foo:  TRUE ",
    # `LET ... IN`
    " LET a == 1 IN a ",
    " LET x == 1  y == 2 IN x + y ",
    " A(y - 1)!B!C ",
    " A!Op(y - 1, B) ",
    # TLC
    " 1 :> 2",
    ' "foo" :> "bar" ',
    " f @@ g ",
    " 1 :> 2 @@ 3 :> 4 ",
]

expr_tests.append(
    r"""
/\ \/ FALSE
   \/ FALSE
/\ FALSE
"""
)
expr_tests.append(
    r"""
/\ (f = [x \in {1, 2} |-> x' + 1])
/\ a = b
"""
)
expr_tests.append(
    r"""
CASE   A -> u
    [] B -> v
    [] OTHER -> w
"""
)
expr_tests.append(
    r"""
LET
    x == y - 1
    f[u \in Int] == u^2
IN
    x + f[v]
"""
)

# tests for defn parser
defn_tests = [
    " a == 1 ",
    " a == INSTANCE M WITH x <- 1 ",
    " Foo(x, y) == x + y ",
    " Foo(x, Bar(_)) == x + y ",
]
defn_tests.append(
    """
a == /\\ f = [x \\in {1, 2} |-> x]
     /\\ g = b
"""
)


sequent_tests = list()
sequent_tests.append(
    r"""
ASSUME TRUE
PROVE TRUE
"""
)
sequent_tests.append(
    r"""
ASSUME NEW x \in {1, 2}
PROVE x \in {1, 2, 3}
"""
)


module_tests = list()
module_tests.append(
    r"""
---- MODULE Foo ----
x == 1
====================
"""
)
module_tests.append(
    r"""
---- MODULE Bar ----
b == /\ a = 1
     /\ c = d
====================
"""
)
module_tests.append(
    r"""
---- MODULE Foo_Bar ----
EXTENDS Foo

VARIABLE x

Foo == TRUE  (*{ by (prover:"smt3") }*)
Bar == f[<<a, b>>]
OpLabel == label(b):: 1


THEOREM
    \E r, q:  TRUE
PROOF
<1>1. TRUE
    OBVIOUS
<1>2. TRUE
    OMITTED
<1> USE ONLY TRUE, TRUE DEF Foo
<1> USE TRUE
<1> HIDE <1>2
<1> DEFINE r == 1
<1>3. ASSUME TRUE
      PROVE TRUE
<1> QED

------------------------

THEOREM
    ASSUME TRUE, 1, NEW r \in S,
        ASSUME TRUE
        PROVE TRUE
    PROVE TRUE
PROOF
<1>1. TRUE
    OBVIOUS
<1> SUFFICES TRUE
<1> TAKE r \in S, q \in S
<1> QED


(* A multi-line comment.

*)

(*
(* A nested multi-line comment.
*)
*)
========================
"""
)


def test_expr_parser():
    """Testing of expression parser."""
    for expr in expr_tests:
        print(" ")
        print(expr)
        r = run_expr_parser(expr)
        assert r is not None
        print(r)


def test_defn_parser():
    """Testing of definition parser."""
    for defn in defn_tests:
        r = run_defn_parser(defn)
        assert r is not None


def test_sequent_parser():
    """Testing of sequent parser."""
    for seq in sequent_tests:
        r = run_sequent_parser(seq)
        assert r is not None


def test_module_parser():
    """Testing of module parser."""
    for module in module_tests:
        r = run_module_parser(module)
        assert r is not None


def run_expr_parser(text):
    """Apply the expression parser."""
    ap = ep.expr(False)
    return _run_parser(ap, text)


def run_defn_parser(text):
    """Apply the definition parser."""
    ap = ep.defn(True)
    return _run_parser(ap, text)


def run_sequent_parser(text):
    """Apply the sequent parser."""
    ap = ep.sequent(False)
    return _run_parser(ap, text)


def run_module_parser(text):
    """Apply the module parser."""
    ap = mp.parse()
    return _run_parser(ap, text)


def _run_parser(ap, text):
    """Return parse tree from applying parser `ap` to `text`."""
    init = _tla_combinators.init
    tokens = _tokenize(text)
    tree, pst = pco.run(ap, init=init, source=tokens)
    return tree


def _tokenize(text):
    """Count tokens and lines when tokenizing."""
    tokens = lex.tokenize(text, omit_preamble=False)
    print("The input has {n} tokens.".format(n=len(tokens)))
    print("The input has {n} lines.".format(n=text.count("\n")))
    # pprint.pprint(tokens)
    return tokens


def test_parser_parse():
    """Test the function `tla.parser.parse`."""
    for module in module_tests:
        r = parser.parse(module)
        assert r is not None


def test_parser_parse_expr():
    """Test the function `tla.parser.parse_expr`."""
    for expr in expr_tests:
        r = parser.parse_expr(expr)
        assert r is not None


def test_parser_parse_to_str():
    """Test `tla.parser.parse` with `tla.to_str` nodes."""
    for module in module_tests:
        r = _parser_parse_to_str(module)
        assert r is not None


def test_parser_parse_expr_to_str():
    """Test `tla.parser.parse_expr` with `tla.to_str` nodes."""
    for expr in expr_tests:
        r = _parser_parse_expr_to_str(expr)
        assert r is not None


def _parser_parse_to_str(text):
    """Return parse tree from `tla.parser.parse`."""
    r = parser.parse(text, nodes=to_str.Nodes)
    text = r.to_str()
    to_str._print_overwide_lines(text, to_str.LINE_WIDTH)
    return r


def _parser_parse_expr_to_str(text):
    """Return parse tree from `tla.parser.parse_expr`."""
    r = parser.parse_expr(text, nodes=to_str.Nodes)
    text = r.to_str(width=80)
    return r


if __name__ == "__main__":
    test_expr_parser()
