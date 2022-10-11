"""Parser combinators."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/pars/pco.ml>
#
from __future__ import absolute_import, division

import collections.abc
import copy
import functools
import logging
import types

from infix import shift_infix as infix

from . import _error, _location
from . import tokens as intf

logger = logging.getLogger(__name__)


# module Make (Tok : Intf.Tok) (Prec : Intf.Prec) = struct

#   module Tok = Tok
#   module Prec = Prec

#  include Tok

# type 's pstate = {
#     (* input *)
#     mutable source : token LL.t ;
#
#     (* last read token *)
#     mutable lastpos : Loc.locus ;
#
#     (* user state *)
#     mutable user_state : 's ;
#   }
class Pstate:
    def __init__(self, source, lastpos, user_state):
        self.source = source  # list
        self.lastpos = lastpos  # Loc.locus
        self.user_state = user_state  # 's

    def __repr__(self):
        return f"Pstate({self.source}, {self.lastpos}, " f"{self.user_state})"


#   (* kind of failure *)
#   type kind =
#     | Unexpected of string
#         (** encountered an unexpected token *)
#     | Message of string
#         (** failed with user-provided reason *)
#     | Internal of string
#         (** failed with internal reason *)
class FailureKind:
    pass


class Unexpected(FailureKind):
    def __init__(self, string):
        self.string = string


class Message(FailureKind):
    def __init__(self, string):
        self.string = string


class Internal(FailureKind):
    def __init__(self, string):
        self.string = string


#   (* severity of failure *)
#   type severity =
#     | Backtrack
#         (** normal failure attempting inapplicable rule *)
#     | Abort
#         (** partially applied rule giving unambiguous failure *)
class Severity:
    pass


class Backtrack(Severity):
    pass


class Abort(Severity):
    pass


# type 'a result =
#     | Parsed of 'a
#     | Failed of kind * severity * string option
class Result:
    pass


class Parsed(Result):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Failed(Result):
    def __init__(self, kind, severity, string):
        self.kind = kind
        self.severity = severity
        self.string = string

    def __repr__(self):
        return f"Failed({self.kind}, " f"{self.severity}, " f"{self.string})"


# type ('s, 'a) reply = {
#     res : 'a result ;
#     loc : Loc.locus ;
#   }
class Reply:
    def __init__(self, res, loc):
        self.res = res  # 'a result  # 'a Result
        self.loc = loc  # Loc.locus

    def __repr__(self):
        return f"Reply({self.res}, {self.loc})"


# type ('s, 'a) prs = Prs of ('s pstate -> ('s, 'a) reply)
class Prs:
    """Parser: 's Pstate -> 'a Reply."""

    def __init__(self, value, name=None):
        self.value = value  # 's Pstate -> 'a Reply
        self.name = name


# let fuse aloc bloc =
#     if aloc = Loc.unknown || aloc.start = aloc.stop then bloc
#     else if bloc = Loc.unknown || bloc.start = bloc.stop then aloc
#     else Loc.merge aloc bloc
def fuse(aloc, bloc):
    if aloc == _location.unknown or aloc.start == aloc.stop:
        return bloc
    elif bloc == _location.unknown or bloc.start == bloc.stop:
        return aloc
    else:
        return aloc.merge(bloc)


# Running a parser

# let exec (Prs ap) pst = ap pst
# ap: parser
# pst: parser state
def exec_(ap, pst):
    # if isinstance(ap, tuple):
    #     ap = ap[0](*ap[1:])
    if isinstance(ap, types.GeneratorType):
        ap = next(ap)
    assert not isinstance(ap, types.GeneratorType), ap
    if isinstance(
        ap,
        (
            types.FunctionType,
            functools.partial,
        ),
    ):
        f = ap
    elif not hasattr(ap, "value"):
        # print(ap)
        raise ValueError(ap)
    else:
        f = ap.value
    return f(pst)


#   let execute ap pst =
#     let rep = exec ap pst in
#       match rep.res with
#         | Parsed a -> Some a
#         | Failed (fk, _, msg) ->
#             let err = Error.error pst.lastpos in
#             let err = match fk with
#               | Unexpected un -> Error.err_set_unexpected un err
#               | Message msg -> Error.err_add_message msg err
#               | Internal msg -> Error.err_add_internal msg err
#             in
#               Error.print_error ~verbose:true stderr err ;
#               None
def execute(ap, pst):
    rep = exec_(ap, pst)  # Reply
    res = rep.res
    if isinstance(res, Parsed):
        return res.value
    elif isinstance(res, Failed):
        kind = res.kind
        msg = res.string
        err = _error.error(pst.lastpos)
        if isinstance(kind, Unexpected):
            un = kind.string
            err = _error.err_set_unexpected(un, err)
        elif isinstance(kind, Message):
            msg = kind.string
            err = _error.err_add_message(msg, err)
        elif isinstance(kind, Internal):
            msg = kind.string
            err = _error.err_add_internal(msg, err)
        _error.print_error(True, None, err)
        return None


#   let run ap ~init ~source =
#     let pst = { source = source ;
#                 ustate = init ;
#                 lastpos = begin
#                   match LL.expose source with
#                     | LL.Nil -> failwith "No tokens in file"
#                     | LL.Cons (t, _) ->
#                         let loc = Tok.locus t in
#                             { loc with Loc.start = loc.Loc.stop }
#                 end ;
#               }
#     in execute ap pst
def run(ap, init, source):
    if not source:
        raise Exception("No tokens in file")
    else:
        t = source[0]  # token
        loc = t.loc  # locus of token (intf.locus())
        lastpos = _location.Locus(start=loc.stop, stop=loc.stop, filename=loc.file)
        # lastpos = {loc with Loc.start = loc.Loc.stop}
    src = ListSlice(source, start=0)
    pst = Pstate(source=src, lastpos=lastpos, user_state=init)
    r = execute(ap, pst)
    # print('parsing stopped at:')
    # print(pst.lastpos)
    # print('remaining input:')
    # pprint.pprint(pst.source)
    return r, pst


# Primitive parsers

#   let return a loc = Prs begin
#     fun pst ->
#       (* pst.lastpos <- { loc with start = loc.stop } ; *)
#       { res = Parsed a ;
#         loc = loc }
#   end
def return_(a, loc):
    def f(pst):
        return Reply(res=Parsed(a), loc=loc)

    # return Prs(f)
    return f


#   let succeed a = Prs begin
#     fun pst ->
#       { res = Parsed a ;
#         loc = pst.lastpos ;
#       }
#   end
def succeed(a):
    def f(pst):
        return Reply(res=Parsed(a), loc=pst.lastpos)

    # return Prs(f)
    return f


#   let fail msg = Prs begin
#     fun pst ->
#       { res = Failed (Message msg, Backtrack, None) ;
#         loc = pst.lastpos }
#   end
def fail(msg):
    def f(pst):
        res = Failed(Message(msg), Backtrack(), None)
        return Reply(res=res, loc=pst.lastpos)

    # return Prs(f)
    return f


#   let internal msg = Prs begin
#     fun pst ->
#       { res = Failed (Internal msg, Backtrack, None) ;
#         loc = pst.lastpos }
#   end
def internal(msg):
    def f(pst):
        res = Failed(Internal(msg), Backtrack(), None)
        return Reply(res=res, loc=pst.lastpos)

    # return Prs(f)
    return f


#   let debug msg = Prs begin
#     fun pst ->
#       let err = Error.error pst.lastpos in
#       let err = Error.err_add_message (Printf.sprintf "[debug] following token is %s"
#                                          (match LL.expose pst.source with
#                                             | LL.Nil -> "EOF"
#                                             | LL.Cons (t, _) -> Tok.rep t)) err in
#       let err = Error.err_add_message (Printf.sprintf "[debug] %s" msg) err in
#         Error.print_error stderr err ;
#         exec (succeed ()) pst
#   end
def debug(msg):
    def f(pst):
        err = _error.error(pst.lastpos)
        s = "EOF" if not pst.source else intf.rep(pst.source[0])
        dbg_msg = f"[debug] following token is {s}"
        _error.err_add_message(dbg_msg, err)
        err = _error.err_add_message(f"[debug] {msg}", err)
        _error.print_error(False, None, err)
        return exec_(succeed(None), pst)

    return Prs(f)


#   let report ?(verb=1) msg ap = Prs begin
#     fun pst ->
#       let yell what =
#         let err = Error.error pst.lastpos in
#         let err = Error.err_add_message (Printf.sprintf "[debug] %s" what) err in
#           Error.print_error stderr err
#       in
#       if verb > 3 then
#         yell (msg ^ " start") ;
#       let rep = exec ap pst in
#       if verb > 2 then
#         yell (msg ^ " end") ;
#       begin match rep.res with
#         | Parsed _ ->
#             if verb > 2 then
#               yell (msg ^ " success")
#         | Failed (_, Backtrack, _) ->
#             if verb > 1 then
#               yell (msg ^ " backtrack")
#         | Failed (_, Abort, _) ->
#             yell (msg ^ " ABORT")
#       end ;
#       rep
#   end
#
#   (* state *)
#
#   let get = Prs begin
#     fun pst -> exec (succeed pst.user_state) pst
#   end
def get():
    """Embed the user state."""

    def f(pst):
        return exec_(succeed(pst.user_state), pst)
        # return Reply(Parsed(pst.user_state), pst.lastpos)

    # return Prs(f)
    return f


#   let morph f = Prs begin
#     fun pst ->
#       pst.user_state <- f pst.user_state ;
#       exec (succeed ()) pst
#   end
def morph(f):
    def g(pst):
        # TODO: different semantics ?
        pst.user_state = f(pst.user_state)
        return exec_(succeed(None), pst)
        # return Reply(Parsed(None), pst.lastpos)


#   let put s = morph (fun _ -> s)
def put(s):
    return morph(lambda _: s)


#   let using s ap = Prs begin
#     fun pst ->
#       let oldst = pst.user_state in
#         pst.user_state <- s ;
#         let rep = exec ap pst in
#           pst.user_state <- oldst ;
#           rep
#   end
def using(s, ap):
    def f(pst):
        oldst = pst.user_state
        pst.user_state = s
        rep = exec_(ap, pst)
        # TODO: different semantics ?
        pst.user_state = oldst
        return rep

    return Prs(f)


# delay

#   let use apf = Prs begin
#     fun pst -> exec (Lazy.force apf) pst
#   end
def use(apf):
    def f(pst):
        # TODO: different semantics (not lazy)
        return exec_(apf, pst)

    # return Prs(f)
    return f


#   let thunk apf = Prs begin
#     fun pst -> exec (apf ()) pst
#   end
def thunk(apf):
    def f(pst):
        return exec_(apf(None), pst)

    return Prs(f)


# table of translation
#
# >>+  shift_plus
# >>=  shift_eq
# <|>  or_
# <*>  times
# <**>  times2
# <$>  apply
# <$?> apply_question
# >>>  second
# >*>  second_commit
# <<<  first
# <!>  bang
# <::>  cons
# <@>  concat


# primitive combinators


#   let ( >>+ ) ap bpf = Prs begin
#     fun pst ->
#       let arep = exec ap pst in  (* a reply *)
#         match arep.res with
#           | Parsed a ->
#               let brep = exec (bpf a arep.loc) pst in  (* b reply *)
#                 brep
#           | Failed (kind, sev, fn)->
#               { arep with res = Failed (kind, sev, fn) }
#   end
def f_shift_plus(ap, bpf, pst):
    arep = exec_(ap, pst)
    res = arep.res
    if isinstance(res, Parsed):
        bp = bpf(res.value, arep.loc)
        brep = exec_(bp, pst)
        return brep
    elif isinstance(res, Failed):
        kind = res.kind
        sev = res.severity
        fn = res.string
        res = Failed(kind, sev, fn)
        return Reply(res=res, loc=arep.loc)
    else:
        raise ValueError(res)


@infix
def shift_plus(ap, bpf):
    """Apply `ap`, then if it succeeds apply `bp` that results from `bpf`.

    `bp` results by applying the parser generator function `bpf` to
    the result and location of the reply by parser `ap`.
    """
    # bind function applied to reply's result and location
    return functools.partial(f_shift_plus, ap, bpf)
    # return Prs(f)


#   let ( >>= ) ap bpf = ap >>+ (fun a _ -> bpf a)
@infix
def shift_eq(ap, bpf):
    """Apply parser function `bpf` to only the result, not the location.

    The result is from the reply of parser `ap`.
    """
    # bind function applied to reply's result
    return shift_plus(ap, lambda a, _: bpf(a))


#   let ( <|> ) ap bp = Prs begin
#     fun pst ->
#       let arep = exec ap pst in
#       match arep.res with
#         | Failed (_, Backtrack, _) ->
#             exec bp pst
#         | _ -> arep
#   end
def f_or_(ap, bp, pst):
    memo = save(pst)
    arep = exec_(ap, pst)
    if isinstance(arep.res, Failed) and isinstance(arep.res.severity, Backtrack):
        restore(memo, pst)
        memo_ = save(pst)
        assert memo == memo_
        # pprint.pprint(pst.source.start)
        return exec_(bp, pst)
    else:
        return arep


@infix
def or_(ap, bp):
    """Apply `ap`, if it fails then apply `bp`."""
    # return Prs(f)
    return functools.partial(f_or_, ap, bp)


#   let ( <*> ) ap bp =
#     ap >>+ fun a aloc ->
#       bp >>+ fun b bloc ->
#         return (a, b) (fuse aloc bloc)
@infix
def times(ap, bp):
    """Apply `ap`, if it succeeds then `bp`, return tuple of results."""
    # This combinator is known also as `seq`.
    return shift_plus(
        ap,
        lambda a, aloc: shift_plus(
            bp, lambda b, bloc: return_((a, b), fuse(aloc, bloc))
        ),
    )


# Explanations
#
#   let commit ap = Prs begin
#     fun pst ->
#       match exec ap pst with
#         | { res = Failed (fk, sev, msg) } as rep ->
#             (*
#              * if sev = Backtrack then
#              *   ignore (exec (debug "abort!") pst) ;
#              *)
#             { rep with res = Failed (fk, Abort, msg) }
#         | rep -> rep
#   end
def f_commit(ap, pst):
    reply = exec_(ap, pst)
    if isinstance(reply.res, Failed):
        res = reply.res
        res = Failed(res.kind, Abort(), res.string)
        return Reply(res=res, loc=reply.loc)
    else:
        return reply


def commit(ap):
    """Change severity of failure to abort."""
    # return Prs(f)
    return functools.partial(f_commit, ap)


#   let ( <**> ) ap bp =
#     ap <*> commit bp
@infix
def times2(ap, bp):
    return times(ap, commit(bp))


#   let explain name ap = Prs begin
#     fun pst ->
#       let arep = exec ap pst in
#         match arep.res with
#           | Failed (fk, sev, None) ->
#               { arep with res = Failed (fk, sev, Some name) }
#           | _ ->
#               arep
#   end
def explain(name, ap):
    def f(pst):
        a_reply = exec_(ap, pst)
        if isinstance(a_reply.res, Failed):
            res = a_reply.res
            res = Failed(res.kind, res.severity, name)
            return Reply(res=res, loc=a_reply.loc)

    return Prs(f)


#   let ( <$> ) ap f =
#     ap >>+ fun a loc -> return (f a) loc
@infix
def apply(ap, f):
    """Apply function `f` to the value returned by parser `ap`."""
    return shift_plus(ap, lambda a, loc: return_(f(a), loc))


# def shift_plus(ap, bpf):
#     def ff(pst):
#         arep = exec(ap, pst)
#         if isinstance(arep.res, Parsed):
#             value = arep.res.value
#             # p = bpf(value, arep.loc)
#             # def g(pst):
#             #     return Reply(res=Parsed(f(value)), loc=arep.loc)
#             # p = Prs(g)
#             # brep = exec_(p, pst)
#             brep = Reply(res=Parsed(f(value)), loc=arep.loc)
#             return brep
#         elif isinstance(arep.res, Failed):
#             kind = arep.res.kind
#             sev = arep.res.severity
#             fn = arep.res.string
#             res = Failed(kind, sev, fn)
#             return Reply(res=res, loc=arep.loc)
#     return Prs(ff)


#   let ( >>> ) ap bp = (ap <*> bp) <$> snd
@infix
def second(ap, bp):
    return apply(times(ap, bp), lambda x: x[1])


#   let ( >*> ) ap bp = (ap <*> commit bp) <$> snd
@infix
def second_commit(ap, bp):
    return apply(times(ap, commit(bp)), lambda x: x[1])


#   let ( <<< ) ap bp = (ap <*> bp) <$> fst
@infix
def first(ap, bp):
    return apply(times(ap, bp), lambda x: x[0])


#   let ( <!> ) ap x = ap >>> succeed x
@infix
def bang(ap, x):
    return second(ap, succeed(x))


#   let ( <::> ) ap lp =
#     ap <*> lp <$> (fun (a, l) -> a :: l)
@infix
def cons(ap, lp):
    # ap: 'a parser
    # lp: list parser
    return apply(times(ap, lp), lambda al: [al[0]] + al[1])


#   let ( <@> ) alp blp =
#     alp <*> blp <$> (fun (al, bl) -> al @ bl)
@infix
def concat(alp, blp):
    return apply(times(alp, blp), lambda albl: albl[0] + albl[1])


#   let withloc ap = Prs begin
#     fun pst ->
#       let rep = exec ap pst in
#         { rep with res =
#             match rep.res with
#               | Parsed a ->
#                   Parsed (a, rep.loc)
#               | Failed (fk, sev, msg) ->
#                   Failed (fk, sev, msg) }
#   end
def withloc(ap):
    def f(pst):
        rep = exec_(ap, pst)
        res = rep.res
        if isinstance(res, Parsed):
            value = (res.value, rep.loc)
            res = Parsed(value)
        elif isinstance(res, Failed):
            res = Failed(res.kind, res.severity, res.string)
        rep = Reply(res=res, loc=rep.loc)
        return rep

    # return Prs(f)
    return f


#   let save pst =
#     (pst.source, pst.lastpos, pst.user_state)
def save(pst):
    return (pst.source, pst.lastpos, pst.user_state)


#   let restore (s, l, u) pst =
#     pst.source <- s ;
#     pst.lastpos <- l ;
#     pst.ustate <- u ;
#   ;;
def restore(slu, pst):
    source, lastpos, user_state = slu
    pst.source = source
    pst.lastpos = lastpos
    pst.user_state = user_state


# comment from `pco.mli`
# Infinite lookahead parsers

#   let lookahead ap = Prs begin
#     fun pst ->
#       let locus = save pst in
#       let rep = exec ap pst in
#         restore locus pst ;
#         rep
#   end
def lookahead(ap):
    def f(pst):
        locus = save(pst)
        rep = exec_(ap, pst)
        restore(locus, pst)
        return rep

    # return Prs(f)
    return f


#   let enabled ap =
#     lookahead ap >>= fun _ -> succeed ()
def enabled(ap):
    return lookahead(ap) << shift_eq >> (lambda _: succeed(None))


#   let disabled ap =
#     (lookahead ap >>= (fun _ -> fail "not disabled")) <|> succeed ()
def disabled(ap):
    neg = shift_eq(lookahead(ap), lambda _: fail("not disabled"))
    return or_(neg, succeed(None))


#   let attempt ap = Prs begin
#     fun pst ->
#       let memo = save pst in
#       let arep = exec ap pst in
#         match arep.res with
#           | Failed _ ->
#               restore memo pst ;
#               arep
#           | _ -> arep
#   end
def f_attempt(ap, pst):
    memo = save(pst)
    arep = exec_(ap, pst)
    if isinstance(arep.res, Failed):
        restore(memo, pst)
        return arep
    else:
        return arep


def attempt(ap):
    # return Prs(f)
    return functools.partial(f_attempt, ap)


#   let optional ap = (attempt ap <$> fun n -> Some n) <|> succeed None
def optional(ap):
    return (attempt(ap) << apply >> (lambda n: n)) << or_ >> succeed(None)


#   let (<?>) ap g =
#     attempt begin
#       ap >>+ fun a loc ->
#         if g a then return a loc else internal "<?>"
#     end
@infix
def question(ap, g):
    f = (
        ap
        << shift_plus
        >> (lambda a, loc: return_(a, loc) if g(a) else internal("<?>"))
    )
    return attempt(f)


#   let (<$?>) ap g =
#     attempt begin
#       ap >>+ fun a loc ->
#         match g a with
#           | Some b -> return b loc
#           | None -> internal "<?>"
#     end
@infix
def apply_question(ap, g):
    def f(a, loc):
        ga = g(a)
        if ga is None:
            return internal("<?>")
        else:
            return return_(ga, loc)

    h = ap << shift_plus >> f
    return attempt(h)


# alternation


#   let rec choice = function
#     | [] -> invalid_arg "null alternative"
#     | [ap] -> ap
#     | ap :: aps ->
#         ap <|> choice aps
def choice(alternatives):
    assert len(alternatives) >= 1, "null alternative"
    # ap = alternatives[0]
    # if len(alternatives) == 1:
    #     return ap
    # else:
    #     aps = alternatives[1:]
    #     return ap <<or_>> choice(aps)

    def f(pst):
        memo = save(pst)
        for ap in alternatives:
            restore(memo, pst)
            arep = exec_(ap, pst)
            if not isinstance(arep.res, Failed) or not isinstance(
                arep.res.severity, Backtrack
            ):
                break
        return arep

    return f


parsers_memo = dict()  # type: ignore


def f_choice_iter(alternatives, pst):
    at_least_one = False
    for alt in alternatives():
        if isinstance(alt, tuple):
            start, fap = alt
            if len(pst.source) > 0 and (
                (
                    not isinstance(start[0], intf.Token_)
                    and not isinstance(pst.source[0].form, start)
                )
                or (
                    isinstance(start[0], intf.Token_)
                    and pst.source[0].form not in start
                )
            ):
                continue
            ap = fap()
        else:
            ap = alt
        at_least_one = True
        arep = exec_(ap, pst)
        if not isinstance(arep.res, Failed) or not isinstance(
            arep.res.severity, Backtrack
        ):
            break
    if not at_least_one:
        ap = fap()
        arep = exec_(ap, pst)
        # res = Failed(Unexpected(None), Backtrack(), None)
        # arep = Reply(res=res, loc=pst.lastpos)
    return arep


# return Prs(f)


def choice_iter(alternatives):
    """Choice with lookahead 1 before building parser."""
    return functools.partial(f_choice_iter, alternatives)


#   let rec alt = function
#     | [] -> invalid_arg "null alternative"
#     | [ap] -> ap
#     | ap :: aps ->
#         attempt ap <|> alt aps
def alt(alternatives):
    assert len(alternatives) >= 1, "null alternative"
    ap = alternatives[0]
    if len(alternatives) == 1:
        return ap
    else:
        aps = alternatives[1:]
        # the precedence of  `attempt ap <|> alt aps`
        # if `(attempt ap) <|> (alt aps)
        return attempt(ap) << or_ >> alt(aps)


# sequence parsers


#   let rec seq = function
#     | [] -> succeed []
#     | ap :: aps ->
#         ap <::> seq aps
def seq(seq_aps):
    """Sequence of parsers `seq_aps`."""
    if not seq_aps:
        return succeed(list())
    else:
        ap = seq_aps[0]
        aps = seq_aps[1:]
        return ap << cons >> seq(aps)


#   let ix f =
#     let rec run n =
#       (f n <::> run (n + 1)) <|> succeed []
#     in
#       run 0
def ix(f):
    def run(n):
        return (f(n) << cons >> run(n + 1)) << or_ >> succeed(list())

    return run(0)


#   (* Kleene star *)
#
#   let star ap =
#     let rec aps = lazy begin
#       alt [
#         ap <::> use aps ;
#         ap <$> (fun x -> [x]) ;
#         succeed [] ;
#       ]
#     end in
#     (* let rec aps = lazy (attempt (ap <::> use aps) <|> succeed []) in *)
#       use aps
def star(ap):
    """Zero or more `ap` repetitions."""
    # def aps():
    #     alts = [
    #         ap <<cons>> use(aps()),
    #         ap <<apply>> (lambda x: [x]),
    #         succeed(list())
    #         ]
    #     return alt(alts)
    # return use(aps())

    def f(pst):
        nonlocal ap
        results = list()
        if isinstance(ap, types.GeneratorType):
            ap = next(ap)
        while True:
            memo = save(pst)
            arep = exec_(ap, pst)
            res = arep.res
            if isinstance(res, Failed):
                restore(memo, pst)
                break
            else:
                results.append(arep)
        res = Parsed(list())
        rep = Reply(res=res, loc=pst.lastpos)
        results.append(rep)

        def reducer(arep, brep):
            a, aloc = arep.res.value, arep.loc
            b, bloc = brep.res.value, brep.loc
            ab = [a] + b
            loc = fuse(aloc, bloc)
            return Reply(res=Parsed(ab), loc=loc)

        while len(results) > 1:
            r = reducer(results[-2], results[-1])
            results = results[:-2] + [r]
        return results[0]

    return Prs(f)


#   (*
#    * let star ap =
#    *   fix (fun st -> attempt (ap <::> st) <|> succeed [])
#    *)
#
#   let star1 ap = ap <::> star ap
def star1(ap):
    """At least one `ap` repetition."""
    return ap << cons >> star(ap)


#   let sep1 sp ap =
#     ap <::> star (sp >>> ap)
def sep1(sp, ap):
    """List of at least one `ap`, with separator `sp`."""
    return ap << cons >> star(sp << second >> ap)


#   let sep sp ap =
#     sep1 sp ap <|> succeed []
def sep(sp, ap):
    """List of none or more `ap`, with separator `sp`."""
    return sep1(sp, ap) << or_ >> succeed(list())


#   (* token parsers *)
#
#   (*
#    * let peek = Prs begin
#    *   fun pst ->
#    *     match LL.expose pst.source with
#    *       | LL.Cons (t, src) ->
#    *           let tloc = Tok.locus t in
#    *             pst.lastpos <- { tloc with Loc.start = tloc.Loc.stop } ;
#    *             { res = Parsed (Some t) ;
#    *               loc = pst.lastpos }
#    *       | LL.Nil ->
#    *           { res = Parsed None ;
#    *             loc = pst.lastpos }
#    * end
#    *)


class ListSlice(collections.abc.Sequence):
    def __init__(self, alist, start):
        self.alist = alist
        self.start = start

    def __repr__(self):
        return f"ListSlice({self.alist}, {self.start})"

    def __len__(self):
        return len(self.alist) - self.start

    def __getitem__(self, slc):
        if isinstance(slc, slice):
            start = slc.start
            # stop = slc.stop
            step = slc.step
            assert start >= 0, start
            assert step is None or step == 1
            return ListSlice(self.alist, self.start + start)
        else:
            i = slc
            if i >= 0:
                return self.alist[self.start + i]
            else:
                return self.alist[i]

    def __eq__(self, other):
        return self.alist == other.alist and self.start == other.start


#   let scan check = Prs begin
#     fun pst ->
#       match LL.expose pst.source with
#         | LL.Cons (t, src) -> begin
#             let tloc = Tok.locus t in
#               match check t with
#                 | Some a ->
#                     pst.source <- src ;
#                     pst.lastpos <- { tloc with start = tloc.stop } ;
#                     { res = Parsed a ;
#                       loc = tloc }
#                 | None ->
#                     { res = Failed (Unexpected (Tok.rep t), Backtrack, None) ;
#                       loc = tloc }
#
#           end
#         | LL.Nil ->
#             { res = Failed (Unexpected "EOF", Backtrack, None) ;
#               loc = pst.lastpos }
#   end


def scan(check):
    def f(pst):
        if not pst.source:
            res = Failed(Unexpected("EOF"), Backtrack(), None)
            return Reply(res=res, loc=pst.lastpos)
        assert pst.source
        t = pst.source[0]
        tloc = t.loc  # intf.locus(t)
        a = check(t)
        if a is None:
            res = Failed(Unexpected(intf.rep(t)), Backtrack(), None)
            return Reply(res=res, loc=tloc)
        assert a is not None
        src = pst.source[1:]
        pst.source = src
        pst.lastpos = copy.copy(tloc)
        pst.lastpos.start = tloc.stop
        res = Parsed(a)
        return Reply(res=res, loc=tloc)

    # return Prs(f)
    return f


#   let satisfy tf = scan (fun t -> if tf t then Some t else None)
def satisfy(tf):
    def f(t):
        if tf(t):
            return t
        else:
            return None

    return scan(f)


#   (* has to be written this way because of the value restriction *)
#   let any = Prs (fun pst -> exec (satisfy (fun _ -> true)) pst)
def any_():
    def f(pst):
        ap = satisfy(lambda _: True)
        return exec_(ap, pst)

    return Prs(f)


#   let literal c = satisfy (fun t -> c = t) <!> ()
def literal(c):
    return satisfy(lambda t: t == c) << bang >> None


#   let string cs =
#     seq (List.map literal cs) <!> ()
#
#   (* lifts *)
#
#   let lift1 f ap =
#     ap >>= fun a ->
#       succeed (f a)
#
#   let lift2 f ap bp =
#     ap >>= fun a ->
#       bp >>= fun b ->
#         succeed (f a b)
#
#   let lift3 f ap bp cp =
#     ap >>= fun a ->
#       bp >>= fun b ->
#         cp >>= fun c ->
#           succeed (f a b c)
#
#   let lift4 f ap bp cp dp =
#     ap >>= fun a ->
#       bp >>= fun b ->
#         cp >>= fun c ->
#           dp >>= fun d ->
#             succeed (f a b c d)
#
#   let lift5 f ap bp cp dp ep =
#     ap >>= fun a ->
#       bp >>= fun b ->
#         cp >>= fun c ->
#           dp >>= fun d ->
#             ep >>= fun e ->
#               succeed (f a b c d e)
#
#   include Prec


#   type assoc = Left | Right | Non
#
#   type 'a item =
#     | Atm of 'a
#     | Opr of prec * 'a opr


class Assoc:
    pass


class Left(Assoc):
    pass


class Right(Assoc):
    pass


class Non(Assoc):
    pass


class Item:
    pass


class Atm(Item):
    def __init__(self, value):
        self.value = value  # 'a


class Opr(Item):
    def __init__(self, prec, opr):
        self.prec = prec  # prec  # Prec
        self.opr = opr  # 'a opr  # Prefix | Postfix | Infix


# and 'a opr =
#   | Prefix of (Loc.locus -> 'a -> 'a)
#   | Postfix of (Loc.locus -> 'a -> 'a)
#   | Infix of assoc * (Loc.locus -> 'a -> 'a -> 'a)
class Prefix:
    def __init__(self, value):
        self.value = value  # location.Locus -> 'a -> 'a


class Postfix:
    def __init__(self, value):
        self.value = value  # location.Locus -> 'a -> 'a


class Infix:
    def __init__(self, assoc, value):
        self.assoc = assoc
        self.value = value  # location.Locus -> 'a -> 'a -> 'a


#   let resolve (item_prs : bool -> ('s, 'a item list) prs) : ('s, 'a) prs =
def resolve(item_prs):
    #     let rec next stack startp =
    #       attempt (item_prs startp >>+ decide_fork stack) <|>
    #                    use (lazy (finish stack))
    def next_(stack, startp):
        return (
            attempt(
                item_prs(startp)
                << shift_plus
                >> functools.partial(decide_fork, stack)  # (items, loc)
            )
            << or_
            >> use(finish(stack))
        )

    #     and decide_fork stack items loc = match items with
    #       | [item] -> decide stack (item, loc)
    #       | _ -> choice (List.map
    #                        (fun item -> decide stack (item, loc))
    #                        items)
    def decide_fork(stack, items, loc):
        assert isinstance(items, list), items
        if len(items) == 1:
            return decide(stack, (items[0], loc))
        else:
            parsers = [decide(stack, (item, loc)) for item in items]
            return choice(parsers)

    #     and decide stack (item, loc) = match item with
    #       | Atm _ | Opr (_, Prefix _) -> begin
    #           match stack with
    #             | (Atm _, _) :: _ ->
    #                 fail "missing operator"
    #             | _ ->
    #                 commit begin
    #                   next ((item, loc) :: stack) begin
    #                     match item with
    #                       | Atm _ -> false    (* cannot start exp following atom *)
    #                       | _ -> true         (* can start exp following prefix  *)
    #                   end
    #                 end
    #         end
    def decide(stack, item_loc):
        # print('decide')
        item, loc = item_loc
        # match item with
        if isinstance(item, Atm) or (
            isinstance(item, Opr) and isinstance(item.opr, Prefix)
        ):
            # | Atm _ | Opr (_, Prefix _) -> begin
            # match stack with
            if (len(stack) >= 1) and isinstance(stack[0][0], Atm):
                # | (Atm _, _) :: _ ->
                return fail("missing operator")
            else:
                # | _ ->
                # ((item, loc) :: stack)
                new_stack = [(item, loc)] + stack
                # match item with
                if isinstance(item, Atm):
                    # | Atm _ -> false
                    startp = False  # cannot start exp following atom
                else:
                    # | _ -> true
                    startp = True  # can start exp following prefix
                return commit(next_(new_stack, startp))
        elif isinstance(item, Opr) and isinstance(item.opr, Infix):
            #       | Opr (oprec, Infix (assoc, _)) -> begin
            oprec = item.prec
            assoc = item.opr.assoc
            #           let rec normalize stack = match stack with
            #             | _ :: (Opr (pprec, _), _) :: _
            #                 when below oprec pprec ->
            #                 normalize (reduce_one stack)
            #             | _ :: (Opr (pprec, Infix (Left, _)), _) :: _
            #                 when assoc = Left && not (below pprec oprec) ->
            #                 reduce_one stack
            #             | _ -> stack
            #           in

            def normalize(stack):
                if (
                    (len(stack) >= 2)
                    and isinstance(stack[1][0], Opr)
                    and intf.below(oprec, stack[1][0].prec)
                ):
                    return normalize(reduce_one(stack))
                elif (
                    (len(stack) >= 2)
                    and isinstance(stack[1][0], Opr)
                    and isinstance(stack[1][0].opr, Infix)
                    and isinstance(stack[1][0].opr.assoc, Left)
                    and isinstance(assoc, Left)
                    and not intf.below(stack[1][0].prec, oprec)
                ):
                    return reduce_one(stack)
                else:
                    return stack

            n_stack = normalize(stack)
            #           let stack = normalize stack in
            #             match stack with
            if (len(n_stack) >= 1) and isinstance(n_stack[0][0], Atm):
                #               | (Atm _, _) :: _ ->
                new_stack = [(item, loc)] + n_stack
                return commit(next_(new_stack, True))
            #                   commit (next ((item, loc) :: stack) true)
            #               | _ :: _ ->
            elif len(n_stack) >= 1:
                return fail("missing operator")
            #                   fail "missing operator"
            elif not n_stack:
                return fail("insufficient arguments")
            #               | [] ->
            #                   fail "insufficient arguments"
            else:
                raise ValueError(n_stack)
        #         end
        #       | Opr (oprec, Postfix _) -> begin
        elif isinstance(item, Opr) and isinstance(item.opr, Postfix):
            oprec = item.prec
            #           let rec normalize stack = match stack with
            #             | _ :: (Opr (pprec, _), _) :: _ when below oprec pprec ->
            #                 normalize (reduce_one stack)
            #             | _ -> stack
            #           in

            def normalize(stack):
                if (
                    (len(stack) >= 2)
                    and isinstance(stack[1][0], Opr)
                    and intf.below(oprec, stack[1][0].prec)
                ):
                    return normalize(reduce_one(stack))
                else:
                    return stack

            #           let stack = normalize stack in
            n_stack = normalize(stack)
            #             match stack with
            if (len(n_stack) >= 1) and isinstance(n_stack[0][0], Atm):
                #             | (Atm _, _) :: _ ->
                new_stack = [(item, loc)] + n_stack
                arg = reduce_one(new_stack)
                return commit(next_(arg, False))
            #                commit (next (reduce_one ((item, loc) :: stack)) false)
            elif len(n_stack) >= 1:
                #             | _ :: _ ->
                return fail("missing operator")
            #                fail "missing operator"
            elif not n_stack:
                #             | [] ->
                return fail("insufficient arguments")
            #                   fail "insufficient arguments"
            else:
                raise ValueError(n_stack)

    #         end
    #
    #     and reduce_one = function
    def reduce_one(stack):
        if (
            (len(stack) >= 2)
            and isinstance(stack[0][0], Opr)
            and isinstance(stack[0][0].opr, Postfix)
            and isinstance(stack[1][0], Atm)
        ):
            #       | (Opr (_, Postfix px), oloc)
            #         :: (Atm a, aloc)
            #         :: stack ->
            #           (Atm (px oloc a), fuse aloc oloc)
            #           :: stack
            px = stack[0][0].opr.value
            oloc = stack[0][1]
            a = stack[1][0].value
            aloc = stack[1][1]
            item = (Atm(px(oloc, a)), fuse(aloc, oloc))
            return [item] + stack[2:]
        elif (
            (len(stack) >= 3)
            and isinstance(stack[0][0], Atm)
            and isinstance(stack[1][0], Opr)
            and isinstance(stack[1][0].opr, Infix)
            and isinstance(stack[2][0], Atm)
        ):
            #       | (Atm b, bloc)
            #         :: (Opr (_, Infix (_, ix)), oloc)
            #         :: (Atm a, aloc)
            #         :: stack ->
            #           (Atm (ix oloc a b), fuse aloc (fuse oloc bloc))
            #           :: stack
            atm, bloc = stack[0]
            b = atm.value
            oloc = stack[1][1]
            ix = stack[1][0].opr.value
            atm, aloc = stack[2]
            a = atm.value
            item = (Atm(ix(oloc, a, b)), fuse(aloc, fuse(oloc, bloc)))
            return [item] + stack[3:]
        elif (
            (len(stack) >= 2)
            and isinstance(stack[0][0], Atm)
            and isinstance(stack[1][0], Opr)
            and isinstance(stack[1][0].opr, Prefix)
        ):
            #       | (Atm a, aloc)
            #         :: (Opr (_, Prefix px), oloc)
            #         :: stack ->
            #           (Atm (px oloc a), fuse oloc aloc)
            #           :: stack
            atm, aloc = stack[0]
            a = atm.value
            opr, oloc = stack[1]
            px = opr.opr.value
            item = (Atm(px(oloc, a)), fuse(oloc, aloc))
            return [item] + stack[2:]
        #       | _ ->
        else:
            raise Exception("reduce_one")

    #           failwith "reduce_one"

    #     and finish stack = match stack with
    #         | [(Atm a, loc)] -> return a loc
    #         | [] ->
    #             lookahead any >>= fun t ->
    #               fail ("required expressions(s) missing before '" ^ Tok.rep t ^ "'")
    #         | _ -> begin
    #             try finish (reduce_one stack) with
    #               | Failure "reduce_one" -> fail "incomplete expression"
    #           end
    def finish(stack):
        if (len(stack) == 1) and isinstance(stack[0][0], Atm):
            # | [(Atm a, loc)] -> return a loc
            atm, loc = stack[0]
            a = atm.value
            return return_(a, loc)
        elif not stack:
            # | [] ->
            return (
                lookahead(any_())
                << shift_eq
                >> (
                    lambda t: fail(
                        f"required expression(s) missing before {intf.rep(t)}"
                    )
                )
            )
        # _ ->
        else:
            try:
                return finish(reduce_one(stack))
            except Exception as e:
                return fail("incomplete expression" + str(e))

    #
    #     in next [] true
    return next_(list(), True)


def any_isinstance(items, cls):
    """`True` if any item is of type `cls`."""
    return any(isinstance(item, cls) for item in items)


def get_instance(items, cls):
    """Return instance of `cls`, if any."""
    for item in items:
        if isinstance(item, cls):
            if item is not None:
                return item
            raise ValueError("`cls` must not be `type(None)`")
    return None
