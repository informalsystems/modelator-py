"""Tokens and operator precedence."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/tla_parser.ml>


# type token_ =
#     | BOF                               (* beginning of file *)
#     | ID of string                      (* identifiers *)
#     | OP of string                      (* operators *)
#     | KWD of string                     (* keywords *)
#     | NUM of string * string            (* numbers *)
#     | STR of string                     (* strings *)
#     | PUNCT of string                   (* misc. punctuation *)
#     | ST of [`Star | `Plus | `Num of int] * string * int
#                                         (* step token *)
#
#   and token = { form : token_ ;
#                 mutable rep : string ;
#                 loc  : Loc.locus }
class Token_:
    """Type of tokens."""

    def __str__(self):
        return f"{type(self).__name__}({self.string})"

    def __eq__(self, other):
        return self.string == other.string


class BOF(Token_):
    """Beginning of file."""

    def __eq__(self, other):
        return isinstance(other, BOF)


class ID(Token_):
    """Identifiers."""

    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        return isinstance(other, ID) and self.string == other.string


class OP(Token_):
    """Operators."""

    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        return isinstance(other, OP) and self.string == other.string


class KWD(Token_):
    """Keywords."""

    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        return isinstance(other, KWD) and self.string == other.string


class NUM(Token_):
    """Numbers."""

    def __init__(self, string1, string2):
        self.string1 = string1
        self.string2 = string2

    def __str__(self):
        if self.string2 is None:
            return self.string1
        else:
            return f"{self.string1}.{self.string2}"

    def __eq__(self, other):
        return (
            isinstance(other, NUM)
            and self.string1 == other.string1
            and self.string2 == other.string2
        )


class STR(Token_):
    """Strings."""

    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        return isinstance(other, STR) and self.string == other.string


class PUNCT(Token_):
    """Miscellaneous punctuation."""

    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        return isinstance(other, PUNCT) and self.string == other.string


#     | ST of [`Star | `Plus | `Num of int] * string * int
class StepStar:
    def __str__(self):
        return "<*>"

    def __eq__(self, other):
        return isinstance(other, StepStar)


class StepPlus:
    def __str__(self):
        return "<+>"

    def __eq__(self, other):
        return isinstance(other, StepPlus)


class StepNum:
    def __init__(self, value):
        self.value = value  # int

    def __str__(self):
        level = self.value
        return f"<{level}>"

    def __eq__(self, other):
        return isinstance(other, StepNum) and self.value == other.value


class ST(Token_):
    """Step token."""

    def __init__(self, kind, string, i):
        self.kind = kind  # StepStar | StepPlus | StepNum
        self.string = string
        self.i = i  # int

    def __str__(self):
        a = str(self.kind)
        b = "" if self.string is None else self.string
        c = "." * self.i
        return a + b + c

    def __eq__(self, other):
        return (
            isinstance(other, ST)
            and self.kind == other.kind
            and self.string == other.string
            and self.i == other.i
        )


#   and token = { form : token_ ;
#                 mutable rep : string ;
#                 loc  : Loc.locus }
class Token:
    """Type of tokens."""

    def __init__(self, token_, rep, loc):
        self.form = token_  # Token_
        self.rep = rep  # str | None
        self.loc = loc  # location.Locus

    def __repr__(self):
        return f"Token({rep(self)}, {self.loc!r})"

    def __eq__(self, other):
        return self.form == other.form


#   let bof loc = { form = BOF ; rep = "start of file" ; loc = loc }
def bof(locus):
    """Token representing beginning of file."""
    return Token(form=BOF(), rep="start of file", loc=locus)


#   let rep t = match t.rep with
#     | "" ->
#         let trep = begin match t.form with
#           | BOF -> "start of file"
#           | ID x -> "identifier " ^ x
#           | KWD x -> "keyword " ^ x
#           | OP x -> "operator " ^ x
#           | PUNCT x -> x
#           | NUM (m, "") -> m
#           | NUM (m, n) -> m ^ "." ^ n
#           | STR s -> "\"" ^ s ^ "\""
#           | ST (`Star, sl, ds) -> "<*>" ^ sl ^ String.make ds '.'
#           | ST (`Plus, sl, ds) -> "<+>" ^ sl ^ String.make ds '.'
#           | ST (`Num m, sl, ds) -> "<" ^ string_of_int m ^ ">" ^ sl ^ String.make ds '.'
#         end in
#         t.rep <- trep ;
#         trep
#     | rep -> rep
def rep(token):
    """String representation of token."""
    if token.rep is not None:
        return token.rep
    form = token.form
    if isinstance(form, BOF):
        return "start of file"
    elif isinstance(form, ID):
        return "identifier " + form.string
    elif isinstance(form, KWD):
        return "keyword " + form.string
    elif isinstance(form, OP):
        return "operator " + form.string
    elif isinstance(form, PUNCT):
        return form.string
    elif isinstance(form, NUM):
        if form.string2 is None:
            return form.string1
        else:
            return form.string1 + "." + form.string2
    elif isinstance(form, STR):
        assert form.string.startswith('"')
        assert form.string.endswith('"')
        return form.string
    elif isinstance(form, ST):
        kind = form.kind
        if isinstance(kind, StepStar):
            return "<*>" + form.string + (form.i * ".")
        elif isinstance(kind, StepPlus):
            return "<+>" + form.string + (form.i * ".")
        elif isinstance(kind, StepNum):
            return "<" + kind.value + ">" + form.string + (form.i * ".")
    else:
        raise Exception(f"Unknown case of token {form}")


#   let locus t = t.loc
def locus(token):
    """Location of the token in text."""
    return token.loc


#   let eq s t = s.form = t.form
# def eq(token, other_token):
#     """Whether tokens are equivalent."""
#     return token.form == other_token.form
#
# NOTE: implemented above as the method `Token.__eq__`.


#   let pp_print_token ff t =
#     Format.pp_print_string ff (rep t)
def pp_print_token(formatter, token):
    """For use in format strings."""
    print(rep(token))


#   (** A precedence is a range of values. Invariant: the first
#       component must be less than or equal to the second component. *)
#   type prec = int * int
# class Prec:
#     """Precedence as range of values."""
#
#     def __init__(self, n1, n2):
#         assert (n1 <= n2)
#         self.n1 = n1
#         self.n2 = n2
# implemented by tuples
def is_prec(prec):
    return isinstance(prec, tuple) and len(prec) == 2


#   (** Check that the first precedence range is completely below the
#       second range. *)
#   let below (a, b) (c, d) = b < c
def below(prec, other_prec):
    """Whether `prec` is entirely below `other_prec`."""
    return prec[1] < other_prec[0]


#   (** Check if the two given precedence ranges overlap. *)
#   let conflict (a, b) (c, d) =
#     (a <= c && c <= b) || (c <= a && a <= d)
def conflict(prec, other_prec):
    """Whether the ranges `prec` and `other_prec` overlap."""
    a, b = prec
    c, d = other_prec
    return (a <= c and c <= b) or (c <= a and a <= d)


def token_basic_test():
    buffer = list()
    token_ = PUNCT("----")
    buffer.append(token_)
    token_ = KWD("MODULE")
    buffer.append(token_)
    token_ = PUNCT("----")
    buffer.append(token_)
    # representation
    buffer_repr = "".join(rep(Token(token_, None, None)) for token_ in buffer)
    buffer_repr_ = "----keyword MODULE----"
    assert buffer_repr == buffer_repr_, buffer_repr


if __name__ == "__main__":
    token_basic_test()
