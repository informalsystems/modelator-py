"""Parser combinators and state for TLA+."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/tla_parser.ml>
#
from . import _combinators as pco
from . import _optable, tokens


# (** The [pcx] is the state carried by the parsers. The [ledge] field
#     contains the left edge of the active rectangle of input. *)
# type pcx = {
#   ledge : int ;
#   clean : bool ;
# }
class Pcx:
    """State carried by the parsers."""

    def __init__(self, ledge, clean):
        self.ledge = ledge
        self.clean = clean

    def __repr__(self):
        return f"Pcx({self.ledge}, {self.clean})"


init = Pcx(-1, True)


class WrappedStr(str):
    pass


class WrappedTuple(tuple):
    pass


class WrappedList(list):
    pass


builtins = (bool, str, int, float, tuple, list, dict)

# let locate p =
#   withloc p <$> begin
#     fun (a, loc) -> Util.set_locus (Property.noprops a) loc
#   end


def locate(p):
    def apply_location(a_loc):
        a, loc = a_loc
        if isinstance(a, str):
            a = WrappedStr(a)
        elif isinstance(a, tuple):
            a = WrappedTuple(a)
        elif isinstance(a, list):
            a = WrappedList(a)
        else:
            assert type(a) not in builtins
        a.loc = loc  # Util.set_locus ... loc
        return a

    return pco.withloc(p) << pco.apply >> apply_location


# let scan ts =
#   get >>= fun px ->
#     P.scan begin
#       fun t ->
#         if px.ledge <= Loc.column t.loc.start then ts t.form
#         else None
#     end
def scan(ts):
    return (
        pco.get()
        << pco.shift_eq
        >> (
            lambda px: pco.scan(
                lambda t: ts(t.form) if px.ledge <= t.loc.start.column else None
            )
        )
    )


# open Token

# let punct p = scan begin
#   function
#     | PUNCT q when q = p -> Some p
#     | _ -> None
# end
def punct(p):
    def f(form):
        # print('punct', p)
        if isinstance(form, tokens.PUNCT) and form.string == p:
            return p
        else:
            return None

    return scan(f)


# let kwd k = scan begin
#   fun tok ->
#     match tok with
#       | KWD j when j = k -> Some k
#       | _ -> None
# end
def kwd(k):
    def f(form):
        # print('kwd', k)
        if isinstance(form, tokens.KWD) and form.string == k:
            return k
        else:
            return None

    return scan(f)


# module Op = Optable


# let anyinfix = scan begin
#   function
#     | OP p ->
#         let rec loop = function
#           | [] -> None
#           | ({ Op.fix = Op.Infix _ } as top) :: _ -> Some (top.name)
#           | _ :: tops -> loop tops
#         in loop (Hashtbl.find_all Op.optable p)
#     | _ -> None
# end
def anyinfix():
    def f(form):
        if not isinstance(form, tokens.OP):
            return None
        name = form.string
        ops = _optable.optable[name]
        fixities = [op.name for op in ops if isinstance(op.fix, _optable.Infix)]
        if fixities:
            (name,) = fixities
            return name
        return None

    return scan(f)


# let infix o = anyinfix <?> (fun p -> o = p)
def infix(op):
    return anyinfix() << pco.question >> (lambda p: op == p)


# let anyprefix = scan begin
#   function
#     | OP p ->
#         let rec loop = function
#           | [] -> None
#           | ({ Op.fix = Op.Prefix } as top) :: _ -> Some (top.name)
#           | _ :: tops -> loop tops
#         in loop (Hashtbl.find_all Op.optable p)
#     | _ -> None
# end
def anyprefix():
    def f(form):
        if not isinstance(form, tokens.OP):
            return None
        name = form.string
        ops = _optable.optable[name]
        fixities = [op.name for op in ops if isinstance(op.fix, _optable.Prefix)]
        if fixities:
            (name,) = fixities
            return name
        return None

    return scan(f)


# let prefix o = anyprefix <?> (fun p -> o = p)
def prefix(op):
    return anyprefix() << pco.question >> (lambda p: op == p)


# let anypostfix = scan begin
#   function
#     | OP p ->
#         let rec loop = function
#           | [] -> None
#           | ({ Op.fix = Op.Postfix } as top) :: _ -> Some (top.name)
#           | _ :: tops -> loop tops
#         in loop (Hashtbl.find_all Op.optable p)
#     | _ -> None
# end
def anypostfix():
    def f(form):
        if not isinstance(form, tokens.OP):
            return None
        name = form.string
        ops = _optable.optable[name]
        fixities = [op.name for op in ops if isinstance(op.fix, _optable.Postfix)]
        if fixities:
            (name,) = fixities
            return name
        return None

    return scan(f)


# let anyop = scan begin
#   function
#     | OP o ->
#         let op = Hashtbl.find Optable.optable o in
#           Some op.Optable.name
#     | _ -> None
# end
def anyop():
    def f(form):
        if isinstance(form, tokens.OP):
            name = form.string
            *_, op = _optable.optable[name]
            return op.name
        else:
            return None

    return scan(f)


# let anyident = scan begin
#   function
#     | ID i -> Some i
#     | _ -> None
# end
def anyident():
    def f(form):
        if isinstance(form, tokens.ID):
            return form.string
        else:
            return None

    return scan(f)


# let ident i = anyident <?> (fun j -> i = j)
def ident(i):
    return anyident() << pco.question >> (lambda j: i == j)


# let anyname = scan begin
#   function
#     | ID nm | KWD nm -> Some nm
#     | _ -> None
# end
def anyname():
    def f(form):
        if isinstance(form, tokens.ID) or isinstance(form, tokens.KWD):
            return form.string
        else:
            return None

    return scan(f)


# let number = scan begin
#   function
#     | NUM (m, n) -> Some (m, n)
#     | _ -> None
# end
def number():
    def f(form):
        if isinstance(form, tokens.NUM):
            return (form.string1, form.string2)
        else:
            return None

    return scan(f)


# let nat = scan begin
#   function
#     | NUM (m, "") -> Some (int_of_string m)
#     | _ -> None
# end
def nat():
    def f(form):
        if isinstance(form, tokens.NUM) and form.string2 is None:
            return int(form.string1)
        else:
            return None

    return scan(f)


# let str = scan begin
#   function
#     | STR (s) -> Some (s)
#     | _ -> None
# end
def str_():
    def f(form):
        if isinstance(form, tokens.STR):
            return form.string
        else:
            return None

    return scan(f)


# let pragma p = punct "(*{" >>> p <<< punct "}*)"
def pragma(p):
    return punct("(*{") << pco.second >> p << pco.first >> punct("}*)")
