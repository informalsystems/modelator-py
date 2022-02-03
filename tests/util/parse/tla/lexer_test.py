"""Tests of module `tla.lex`."""
import pprint

import tla.lex as lex

MODULE_FOO = r"""
comments
---- MODULE Foo ----
VARIABLE x

\* a one-line comment
\* a nested \* one-line comment

(* This is a multi-line comment. *)
(* This is a multi-line
comment. * (
*)
(* A nested
(* multi-line *)
comment. *)
a == 1.0
b == a + 2

A == x' = x + 1

P == SF_x(A)

THEOREM Thm ==
    ASSUME x = 1
    PROVE x + 1 = 2
PROOF
<1>1. x = 1
    OBVIOUS
<1>2. x + 1 = 1 + 1
    BY <1>1
<1>3. 1 + 1 = 2
    OBVIOUS
<1> QED
    BY <1>2, <1>3
====================
"""


def test_lexer():
    """Test lexing and conversions between tokens."""
    data = MODULE_FOO
    data = lex._omit_preamble(data)
    lextokens = lex._lex(data)
    # Token_ instances
    tokens_ = [lex._map_to_token_(token) for token in lextokens]
    pprint.pprint(tokens_)
    for token_ in tokens_:
        print(token_)
        print(str(token_))
    str_of_tokens_ = [str(token_) for token_ in tokens_]
    pprint.pprint(str_of_tokens_)
    # Token instances
    tokens = [lex._map_to_token(data, token) for token in lextokens]
    pprint.pprint(tokens)
    # join raw strings
    print("".join(str_of_tokens_))
    # join with newlines in between
    s = lex._join_with_newlines(tokens)
    print(s)
    # check location information
    for token in tokens:
        print(token.loc)


if __name__ == "__main__":
    test_lexer()
