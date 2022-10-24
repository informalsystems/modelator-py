"""Parser of expressions."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/expr/e_parser.ml>
#
import functools

from . import _combinators as pco
from . import _optable
from . import _tla_combinators as intf
from . import tokens
from ._combinators import (
    alt,
    apply,
    apply_question,
    attempt,
    bang,
    choice,
    choice_iter,
    commit,
    enabled,
    fail,
    first,
    get,
    lookahead,
    optional,
    return_,
    second,
    second_commit,
    sep,
    sep1,
    shift_eq,
    shift_plus,
    star,
    star1,
    succeed,
    times,
    times2,
    use,
    using,
)
from .ast import Nodes as tla_ast


# open Ext
# open Property
# open E_t
# open Tla_parser.P
# open Tla_parser
# open Token
#
# module Prop = Property
#
# module Op = Optable
# module B = Builtin
#
# (*let b = ref false*)
#
# let fixities =
#   let fixities = Hashtbl.create 109 in
#   let infix op prec assoc =
#     Opr begin
#       prec, Infix begin
#         assoc, fun oploc a b ->
#           let op = Util.locate op oploc in
#           let loc = Loc.merge
#                 oploc
#                 (Loc.merge
#                     (Util.get_locus a)
#                     (Util.get_locus b)) in
#             Util.locate (Apply (op, [a ; b])) loc
#       end
#     end in
def infix(op, prec, assoc):
    def f(oploc, a, b):
        # TODO: location annotations
        return tla_ast.Apply(op, [a, b])

    return pco.Opr(prec, pco.Infix(assoc, f))


#   let bin_prod =
#     Opr begin
#       (10, 13), Infix begin
#         Left, fun oploc a b ->
#           let loc = Loc.merge
#                 oploc
#                 (Loc.merge
#                     (Util.get_locus a)
#                     (Util.get_locus b)) in
#             Util.locate begin
#               match a.core with
#                 | Product es -> Product (es @ [b])
#                 | _ -> Product [a ; b]
#             end loc
#       end
#     end in


#   let prefix op prec =
#     Opr begin
#       prec, Prefix begin
#         fun oploc a ->
#           let op = Util.locate op oploc in
#           let loc = Loc.merge oploc (Util.get_locus a) in
#             Util.locate (Apply (op, [a])) loc
#       end
#     end in
def prefix(op, prec):
    def f(oploc, a):
        # TODO: location annotations
        return tla_ast.Apply(op, [a])

    return pco.Opr(prec, pco.Prefix(f))  # pco.Prefix


#   let postfix op prec =
#     Opr begin
#       prec, Postfix begin
#         fun oploc a ->
#          let op = Util.locate op oploc in
#           let loc = Loc.merge oploc (Util.get_locus a) in
#             Util.locate (Apply (op, [a])) loc
#       end
#     end
def postfix(op, prec):
    def f(oploc, a):
        # TODO: location annotations
        return tla_ast.Apply(op, [a])

    return pco.Opr(prec, pco.Postfix(f))  # pco.Postfix


#   in
#     Hashtbl.iter begin
#       fun form top ->
#         Hashtbl.add fixities form begin
#           match top.defn with
#             | _ -> begin
#                 let defn = match top.defn with
#                   | Some bltin -> Internal bltin
#                   | None -> Opaque top.name
#                 in match top.fix with
#                   | Op.Prefix -> prefix defn top.prec
#                   | Op.Postfix -> postfix defn top.prec
#                   | Op.Infix ass ->
#                       infix defn top.prec begin
#                         match ass with
#                           | Op.Left -> Left
#                           | Op.Right -> Right
#                           | Op.Non -> Non
#                       end
#                   | _ ->
#                       failwith "Nonfix operator in optable?!"
#               end
#         end
#     end Op.optable ;
def _generate_fixities():
    fixities = dict()
    for form, alternatives in _optable.optable.items():
        fixities.setdefault(form, list())
        for top in alternatives:
            if top.defn is None:
                defn = tla_ast.Opaque(top.name)
            else:
                # defn = tla_ast.Internal(top.defn)
                defn = top.defn
            if isinstance(top.fix, _optable.Prefix):
                res = prefix(defn, top.prec)
            elif isinstance(top.fix, _optable.Postfix):
                res = postfix(defn, top.prec)
            elif isinstance(top.fix, _optable.Infix):
                assoc = top.fix.assoc
                if isinstance(assoc, _optable.Left):
                    assoc = pco.Left()
                elif isinstance(assoc, _optable.Right):
                    assoc = pco.Right()
                elif isinstance(assoc, _optable.Non):
                    assoc = pco.Non()
                else:
                    raise ValueError(assoc)
                res = infix(defn, top.prec, assoc)
            else:
                raise ValueError(top.fix)
            fixities[form].append(res)
    return fixities


#     Hashtbl.replace fixities "\\X" bin_prod ;
#     Hashtbl.replace fixities "\\times" bin_prod ;
#     fixities
fixities = _generate_fixities()
#
# let distinct =
#   let module S = Set.Make (String) in
#   let rec check seen = function
#     | [] -> true
#     | v :: vs ->
#         not (S.mem v.core seen)
#         && check (S.add v.core seen) vs
#   in
#     fun vs -> check S.empty vs
#
# let hint = locate anyident


def hint():
    return intf.locate(intf.anyident())


# let rec expr b = lazy begin
#   resolve (expr_or_op b);
# end
def expr(b):
    while True:
        f = functools.partial(expr_or_op, b)
        r = pco.resolve(f)
        yield r


#     attempt anyop >>+ begin fun p pts ->
#       match Hashtbl.find_all fixities p with
#         | [] -> fail ("unknown operator " ^ p)
#         | ops ->
#             let non_test = function
#               | Opr (_, Infix (_, ix)) ->
#                   attempt (punct "("
#                       >>> (use (expr b)
#                       <*> (punct "," >>> use (expr b)))
#                       <<< punct ")")
#                   (* <<! [Printf.sprintf "args of nonfix_%s" p] *)
#                   <$> (fun (e, f) -> [P.Atm (ix pts e f)])
#               | Opr (_, Postfix ix) ->
#                   attempt (punct "("
#                       >>> use (expr b)
#                       <<< punct ")")
#                   (* <<! [Printf.sprintf "args of nonfix_%s" p] *)
#                   <$> (fun e -> [P.Atm (ix pts e)])
#               | _ -> fail "Unnonable"
#             in
#               choice (List.map non_test ops @ [return ops pts])
def choice_fix_operators(b, p, pts):
    ops = fixities[p]
    assert isinstance(ops, list), ops
    if not ops:
        return fail(f"unknown operator {p}")
    assert ops, ops

    def non_test(op):
        if isinstance(op, pco.Opr) and isinstance(op.opr, pco.Infix):
            ix = op.opr.value
            return (
                attempt(
                    intf.punct("(")
                    << second
                    >> use(expr(b))
                    << times
                    >> (intf.punct(",") << second >> use(expr(b)))
                    << first
                    >> intf.punct(")")
                )
                << apply
                >> (lambda e_f: [pco.Atm(ix(pts, e_f[0], e_f[1]))])
            )
        elif isinstance(op, pco.Opr) and isinstance(op.opr, pco.Postfix):
            ix = op.opr.value
            return (
                attempt(
                    intf.punct("(")
                    << second
                    >> use(expr(b))
                    << first
                    >> intf.punct(")")
                )
                << apply
                >> (lambda e: [pco.Atm(ix(pts, e))])
            )
        else:
            return fail("Unnonable")

    new_ops = [non_test(op) for op in ops] + [return_(ops, pts)]
    return choice(new_ops)


#     (* record fields *)
#     if not is_start then
#       attempt begin
#         locate (punct "." >>> anyname)
#       end <$> begin
#         fun sw ->
#           [ P.Opr begin
#               (17, 17),
#               P.Postfix begin
#                 fun _ r ->
#                   let loc = Loc.merge (Util.get_locus r)
#                                       (Util.get_locus sw) in
#                     Util.locate (Dot (r, sw.core)) loc
#               end
#             end ]
#       end
#     else fail "not a rproj" ;
def record_fields(is_start):
    if is_start:
        return fail("not a rproj")
    assert not is_start, is_start
    # def f(sw, _, r):
    #     return tla_ast.Dot(r, sw)

    def f():
        return (
            attempt(intf.locate(intf.punct(".") << second >> intf.anyname()))
            << apply
            >> (
                lambda sw: [
                    pco.Opr(
                        (17, 17),
                        # Postfix(functools.partial(f, sw))
                        pco.Postfix(lambda _, r: tla_ast.Dot(r, sw)),
                    )
                ]
            )
        )

    return ((tokens.PUNCT("."),), f)


#     (* function arguments *)
#
#     if not is_start then
#       attempt begin
#         locate (
#               punct "["
#               >>> sep1 (punct ",") (use (expr b))
#               <<< punct "]")
#       end
#       <$> begin
#         fun esw ->
#           [ P.Opr begin
#               (17, 17),
#               P.Postfix begin
#                 fun oploc f ->
#                   let loc = Loc.merge (Util.get_locus f)
#                                       (Util.get_locus esw) in
#                     Util.locate (FcnApp (f, esw.core)) loc
#               end
#             end ]
#       end
#     else fail "not a farg" ;
def function_arguments(b, is_start):
    if is_start:
        return fail("not a farg")

    def f():
        return (
            attempt(
                intf.locate(
                    intf.punct("[")
                    << second
                    >> sep1(intf.punct(","), use(expr(b)))
                    << first
                    >> intf.punct("]")
                )
            )
            << apply
            >> (
                lambda esw: [
                    pco.Opr(
                        (17, 17),
                        pco.Postfix(lambda oploc, f: tla_ast.FunctionApply(f, esw)),
                    )
                ]
            )
        )

    return ((tokens.PUNCT("["),), f)


#     if is_start then
#       locate begin
#         attempt (use (operator b))
#         <*> use (opargs b)
#         <*> optional (use (subref b))
#       end <$> begin
#         fun prs ->
#           let ((op, args), sr) = prs.core in
#           let e = match args with
#             | [] -> op
#             | _ -> Apply (op, args) @@ prs
#           in match sr, op.core with
#             | None, Opaque x when x.[0] = '<' ->
#                (* A step name is more like an empty subref than an ident. *)
#                [ P.Atm (Bang (e, []) @@ prs) ]
#             | None, _ -> [ P.Atm e ]
#             | Some sr, _ -> [ P.Atm (Bang (e, sr) @@ prs) ]
#       end
#     else fail "not an opapp" ;
def nonfix_operators(b, is_start):
    if not is_start:
        return fail("not an opapp")
    assert is_start, is_start

    def f(prs):
        ((op, args), sr) = prs
        if not args:
            e = op
        else:
            e = tla_ast.Apply(op, args)
        if sr is None and isinstance(op, tla_ast.Opaque) and op.name[0] == "<":
            return [pco.Atm(tla_ast.Bang(e, list()))]
        elif sr is None:
            return [pco.Atm(e)]
        elif sr is not None:
            return [pco.Atm(tla_ast.Bang(e, sr))]
        else:
            raise ValueError()

    return (
        intf.locate(
            attempt(use(operator(b)))
            << times
            >> use(opargs(b))
            << times
            >> optional(use(subref(b)))
        )
        << apply
        >> f
    )


# and expr_or_op b is_start =
def expr_or_op(b, is_start):
    def choices():
        #   choice [
        #
        #     (* labels *)
        #
        #     if is_start then
        #       locate (attempt (use label) <**> use (expr b))
        #       <$> (function {core = (l, e)} as bl ->
        #              [ Atm (Parens (e, l) @@ bl) ])
        #     else fail "not a labelled expression" ;
        def f():
            return (
                intf.locate(attempt(use(label())) << times2 >> use(expr(b)))
                << apply
                >> (lambda l_e: [pco.Atm(tla_ast.Parens(l_e[1], l_e[0]))])
                if is_start
                else fail("not a labelled expression")
            )

        yield ((tokens.ID,), f)

        # starts with token `ID`

        #     (* bulleted lists *)
        #
        #     if is_start then
        #       locate (use (bulleted_list b))
        #       <$> (fun bl -> [Atm bl])
        #     else fail "not a bulleted list" ;
        def f():
            return (
                intf.locate(use(bulleted_list(b)))
                << apply
                >> (lambda bl: [pco.Atm(bl)])
                if is_start
                else fail("not a bulleted list")
            )

        yield (
            (
                tokens.OP("/\\"),
                tokens.OP("\\/"),
            ),
            f,
        )

        #     (* temporal subscripting *)
        #
        #     if is_start then
        #       attempt begin
        #         locate (prefix "[]" >>> punct "[" >*>
        #                    use (expr b) <<< punct "]_" <**> use (sub_expr b))
        #         <$> begin
        #           fun { core = (e, v) ; props = props } ->
        #             [Atm { core = Tsub (Box, e, v) ; props = props }]
        #         end
        #       end
        #     else fail "not a [] [_]_" ;

        # RULE: [][expr(b)]_sub_expr(b)
        def f():
            return (
                attempt(
                    intf.locate(
                        intf.prefix("[]")
                        << second
                        >> intf.punct("[")
                        << second_commit
                        >> use(expr(b))
                        << first
                        >> intf.punct("]_")
                        << times2
                        >> use(sub_expr(b))
                    )
                    << apply
                    >> (
                        lambda e_v: [
                            pco.Atm(
                                tla_ast.TemporalSub(tla_ast.BoxOp(), e_v[0], e_v[1])
                            )
                        ]
                    )
                )
                if is_start
                else fail("not a [] [_]_")
            )

        yield ((tokens.OP("[]"),), f)

        #     if is_start then
        #       attempt begin
        #         locate (prefix "<>"
        #                   >>> punct "<<"
        #                   >>> use (expr b)
        #                   <<< punct ">>_"
        #                   <*> use (sub_expr b))
        #         <$> begin
        #           fun { core = (e, v) ; props = props } ->
        #             [Atm { core = Tsub (Dia, e, v) ; props = props }]
        #         end
        #       end
        #     else fail "not a <> <<_>>_" ;
        def f():
            return attempt(
                intf.locate(
                    intf.prefix("<>")
                    << second
                    >> intf.punct("<<")
                    << second
                    >> use(expr(b))
                    << first
                    >> intf.punct(">>_")
                    << times
                    >> use(sub_expr(b))
                )
                << apply
                >> (
                    lambda e_v: [
                        pco.Atm(
                            tla_ast.TemporalSub(tla_ast.DiamondOp(), e_v[0], e_v[1])
                        )
                    ]
                )
            )

        yield ((tokens.OP("<>"),), f)

        #     (* ?fix operators *)
        #
        #     attempt anyop >>+ begin fun p pts ->
        #       match Hashtbl.find_all fixities p with
        #         | [] -> fail ("unknown operator " ^ p)
        #         | ops ->
        #             let non_test = function
        #               | Opr (_, Infix (_, ix)) ->
        #                   attempt (punct "("
        #                       >>> (use (expr b)
        #                       <*> (punct "," >>> use (expr b)))
        #                       <<< punct ")")
        #                   (* <<! [Printf.sprintf "args of nonfix_%s" p] *)
        #                   <$> (fun (e, f) -> [P.Atm (ix pts e f)])
        #               | Opr (_, Postfix ix) ->
        #                   attempt (punct "("
        #                       >>> use (expr b)
        #                       <<< punct ")")
        #                   (* <<! [Printf.sprintf "args of nonfix_%s" p] *)
        #                   <$> (fun e -> [P.Atm (ix pts e)])
        #               | _ -> fail "Unnonable"
        #             in
        #               choice (List.map non_test ops @ [return ops pts])
        #     end ;
        def f():
            return (
                attempt(intf.anyop())
                << shift_plus
                >> functools.partial(choice_fix_operators, b)
            )

        yield ((tokens.OP,), f)

        #
        #     (* record fields *)
        #     if not is_start then
        #       attempt begin
        #         locate (punct "." >>> anyname)
        #       end <$> begin
        #         fun sw ->
        #           [ P.Opr begin
        #               (17, 17),
        #               P.Postfix begin
        #                 fun _ r ->
        #                   let loc = Loc.merge (Util.get_locus r)
        #                                       (Util.get_locus sw) in
        #                     Util.locate (Dot (r, sw.core)) loc
        #               end
        #             end ]
        #       end
        #     else fail "not a rproj" ;
        yield record_fields(is_start)
        #
        #     (* function arguments *)
        #
        #     if not is_start then
        #       attempt begin
        #         locate (punct "[" >>> sep1 (punct ",") (use (expr b)) <<< punct "]")
        #       end
        #       <$> begin
        #         fun esw ->
        #           [ P.Opr begin
        #               (17, 17),
        #               P.Postfix begin
        #                 fun oploc f ->
        #                   let loc = Loc.merge (Util.get_locus f)
        #                                       (Util.get_locus esw) in
        #                     Util.locate (FcnApp (f, esw.core)) loc
        #               end
        #             end ]
        #       end
        #     else fail "not a farg" ;
        yield function_arguments(b, is_start)

        #     (* nonfix operators *)
        #
        #     if is_start then
        #       locate begin
        #         attempt (use (operator b))
        #         <*> use (opargs b)
        #         <*> optional (use (subref b))
        #       end <$> begin
        #         fun prs ->
        #           let ((op, args), sr) = prs.core in
        #           let e = match args with
        #             | [] -> op
        #             | _ -> Apply (op, args) @@ prs
        #           in match sr, op.core with
        #             | None, Opaque x when x.[0] = '<' ->
        #                (* A step name is more like an empty subref than an ident. *)
        #                [ P.Atm (Bang (e, []) @@ prs) ]
        #             | None, _ -> [ P.Atm e ]
        #             | Some sr, _ -> [ P.Atm (Bang (e, sr) @@ prs) ]
        #       end
        #     else fail "not an opapp" ;
        def f():
            return nonfix_operators(b, is_start)

        yield (
            (
                tokens.ID,
                tokens.ST,
            ),
            f,
        )
        yield (
            (
                tokens.KWD("LAMBDA"),
                tokens.PUNCT("("),
            ),
            f,
        )

        #     (* complex expressions *)
        #
        #     use (complex_expr b) <$> (fun e -> [P.Atm e]) ;
        yield use(complex_expr(b)) << apply >> (lambda e: [pco.Atm(e)])

    # intf.kwd('FALSE') <<apply>> (lambda e: [Atm(e)])  # for testing
    #   ]
    while True:
        yield choice_iter(choices)


#
# and label = lazy begin
#   locate begin
#     anyident <*> choice [
#       punct "("
#           >>> sep1 (punct ",") (locate anyident)
#           <<< punct ")" ;
#       succeed [] ;
#     ] <<< punct "::"
#     <$> (fun (l, ns) -> Nlabel (l, ns))
#   end
# end
def label():
    while True:
        yield intf.locate(
            # RULE: anyident ['(' anyident (',' anyident)* ')'] '::'
            intf.anyident()
            << times
            >> choice(
                [
                    intf.punct("(")
                    << second
                    >> sep1(intf.punct(","), intf.locate(intf.anyident()))
                    << first
                    >> intf.punct(")"),
                    succeed(list()),
                ]
            )
            << first
            >> intf.punct("::")
        ) << apply >> (lambda l_ns: tla_ast.NamedLabel(l_ns[0], l_ns[1]))


# and opargs b = lazy begin
#   optional begin
#     punct "("
#       >*> sep1 (punct ",") (use (oparg b))
#       <<< punct ")"
#   end <$> Option.default []
# end
def opargs(b):
    while True:
        yield optional(
            intf.punct("(")
            << second_commit
            >> sep1(intf.punct(","), use(oparg(b)))
            << first
            >> intf.punct(")")
        ) << apply >> (lambda x: [] if x is None else x)


# and subref b = lazy begin
#   punct "!" >*> sep1 (punct "!") (use (sel b))
# end
def subref(b):
    while True:
        yield (intf.punct("!") << second_commit >> sep1(intf.punct("!"), use(sel(b))))


#     <$> (fun (l, args) -> match args with
#            | None -> Sel_lab (l, [])
#            | Some args -> Sel_lab (l, args)) ;
def apply_sel(l_args):
    l, args = l_args
    if args is None:
        return tla_ast.SelLab(l, list())
    else:
        return tla_ast.SelLab(l, args)


# and sel b = lazy begin
#   choice [
#     choice [ anyident ; anyop ] <**>
#      optional (
#           punct "("
#           >>> sep1 (punct ",") (use (oparg b))
#           <<< punct ")")
#     <$> (fun (l, args) -> match args with
#            | None -> Sel_lab (l, [])
#            | Some args -> Sel_lab (l, args)) ;
#
#     punct "(" >*> sep1 (punct ",") (use (oparg b)) <<< punct ")"
#     <$> (fun args -> Sel_inst args) ;
#
#     nat <$> (fun n -> Sel_num n) ;
#
#     punct "<<" <!> Sel_left ;
#
#     punct ">>" <!> Sel_right ;
#
#     punct ":" <!> Sel_down ;
#
#     punct "@" <!> Sel_at ;
#   ]
# end
def sel(b):
    def choices():
        # RULE: (anyident | anyop) ('(' oparg (',' oparg)* ')')?
        def f():
            return (
                choice([intf.anyident(), intf.anyop()])
                << times2
                >> optional(
                    intf.punct("(")
                    << second
                    >> sep1(intf.punct(","), use(oparg(b)))
                    << first
                    >> intf.punct(")")
                )
                << apply
                >> apply_sel
            )

        yield (
            (
                tokens.ID,
                tokens.OP,
            ),
            f,
        )

        # RULE: '(' oparg (',' oparg)* ')'
        def f():
            return (
                intf.punct("(")
                << second_commit
                >> sep1(intf.punct(","), use(oparg(b)))
                << first
                >> intf.punct(")")
                << apply
                >> (lambda args: tla_ast.SelInst(args))
            )

        yield ((tokens.PUNCT("("),), f)

        # RULE: nat
        yield intf.nat() << apply >> (lambda n: tla_ast.SelNum(n))

        # RULE: '<<'
        yield intf.punct("<<") << bang >> tla_ast.SelLeft()
        # RULE: '>>'
        yield intf.punct(">>") << bang >> tla_ast.SelRight()
        # RULE: ':'
        yield intf.punct(":") << bang >> tla_ast.SelDown()
        # RULE: '@'
        yield intf.punct("@") << bang >> tla_ast.SelAt()

    while True:
        yield choice_iter(choices)


# and complex_expr b = lazy begin
def complex_expr(b):
    def choices():
        #   choice [
        #     (* IF ... THEN ... ELSE *)
        #
        #     locate begin
        #       (kwd "IF" >*> use (expr b))
        #       <**> (kwd "THEN" >>> use (expr b))
        #       <**> (kwd "ELSE" >>> use (expr b))
        #     end <$> begin
        #       fun ({core = ((a, b), c)} as ite) ->
        #         { ite with core = If (a, b, c) }
        #     end ;
        def f():
            return (
                intf.locate(
                    intf.kwd("IF")
                    << second_commit
                    >> use(expr(b))
                    << times2
                    >> (intf.kwd("THEN") << second >> use(expr(b)))
                    << times2
                    >> (intf.kwd("ELSE") << second >> use(expr(b)))
                )
                << apply
                >> (lambda abc: tla_ast.If(abc[0][0], abc[0][1], abc[1]))
            )

        yield ((tokens.KWD("IF"),), f)
        #
        #     (* LET ... IN ... *)
        #
        #     locate begin
        #       kwd "LET" >*> star1 (use (defn b))
        #       <**> (kwd "IN" >>> use (expr b))
        #     end <$> begin
        #       fun ({core = (ds, e)} as letin) ->
        #         { letin with core =  Let (ds, e) }
        #     end;

        def f():
            return (
                intf.locate(
                    intf.kwd("LET")
                    << second_commit
                    >> star1(use(defn(b)))
                    << times2
                    >> (intf.kwd("IN") << second >> use(expr(b)))
                )
                << apply
                >> (lambda ds_e: tla_ast.Let(ds_e[0], ds_e[1]))
            )

        yield ((tokens.KWD("LET"),), f)

        #     (* use sequent <$> (fun sq -> Sequent sq) ; *)
        #
        #     (* quantifiers *)
        #
        #     locate begin
        #       choice [ punct "\\A" <!> Forall ;
        #                punct "\\E" <!> Exists ;
        #              ]
        #       <**> use (bounds b)
        #       <**> (punct ":" >>> use (expr b))
        #     end <$> begin
        #       fun ({core = ((q, bs), e)} as quant) ->
        #         { quant with core = Quant (q, bs, e) }
        #     end ;

        # [\\A|\\E] bounds : expr
        def f():
            return (
                intf.locate(
                    choice(
                        [
                            intf.punct("\\A") << bang >> tla_ast.Forall(),
                            intf.punct("\\E") << bang >> tla_ast.Exists(),
                        ]
                    )
                    << times2
                    >> use(bounds(b))
                    << times2
                    >> (intf.punct(":") << second >> use(expr(b)))
                )
                << apply
                >> (
                    lambda qbse: tla_ast.RigidQuantifier(
                        qbse[0][0], qbse[0][1], qbse[1]
                    )
                )
            )

        yield (
            (
                tokens.PUNCT("\\A"),
                tokens.PUNCT("\\E"),
            ),
            f,
        )

        #     locate begin
        #       choice [ punct "\\AA" <!> Forall ;
        #                punct "\\EE" <!> Exists ]
        #       <**> (sep1 (punct ",") hint <?> distinct)
        #       <**> (punct ":" >>> use (expr b))
        #     end <$> begin
        #       fun ({core = ((q, vs), e)} as tquant) ->
        #         { tquant with core = Tquant (q, vs, e) }
        #     end ;

        # [\\AA|\\EE] hint [, hint]* : expr
        def f():
            return (
                intf.locate(
                    choice(
                        [
                            intf.punct("\\AA") << bang >> tla_ast.Forall(),
                            intf.punct("\\EE") << bang >> tla_ast.Exists(),
                        ]
                    )
                    << times2
                    >> sep1(intf.punct(","), hint())
                    << times2
                    >> (intf.punct(":") << second >> use(expr(b)))
                )
                << apply
                >> (
                    lambda qvse: tla_ast.TemporalQuantifier(
                        qvse[0][0], qvse[0][1], qvse[1]
                    )
                )
            )

        yield (
            (
                tokens.PUNCT("\\AA"),
                tokens.PUNCT("\\EE"),
            ),
            f,
        )

        #     locate begin
        #       kwd "CHOOSE" >*> hint
        #       <*> optional (infix "\\in" >*> use (expr b))
        #       <**> (punct ":" >>> use (expr b))
        #     end <$> begin
        #       fun ({core = ((v, ran), e)} as choose) ->
        #         { choose with core = Choose (v, ran, e) }
        #     end ;

        # CHOOSE hint [\in expr] : expr
        def f():
            return (
                (
                    intf.kwd("CHOOSE")
                    << second_commit
                    >> hint()
                    << times
                    >> optional(intf.infix("\\in") << second_commit >> use(expr(b)))
                    << times2
                    >> (intf.punct(":") << second >> use(expr(b)))
                )
                << apply
                >> (
                    lambda v_ran_e: tla_ast.Choose(
                        v_ran_e[0][0], v_ran_e[0][1], v_ran_e[1]
                    )
                )
            )

        yield ((tokens.KWD("CHOOSE"),), f)

        #     locate begin
        #       kwd "CASE"
        #           >*> sep1 (prefix "[]") (use (expr b)
        #           <**> (
        #               punct "->"
        #               >>> use (expr b)))
        #           <*> optional (
        #               prefix "[]"
        #               >*> kwd "OTHER"
        #               >*> punct "->"
        #               >*> use (expr b))
        #     end <$> begin
        #       fun ({core = (arms, oth)} as case) ->
        #         { case with core = Case (arms, oth) }
        #     end ;

        # CASE expr -> expr ([] expr -> expr)+ [[] OTHER -> expr]
        def f():
            return (
                (
                    intf.kwd("CASE")
                    << second_commit
                    >> sep1(
                        intf.prefix("[]"),
                        use(expr(b))
                        << times2
                        >> (intf.punct("->") << second >> use(expr(b))),
                    )
                    << times
                    >> optional(
                        intf.prefix("[]")
                        << second_commit
                        >> intf.kwd("OTHER")
                        << second_commit
                        >> intf.punct("->")
                        << second_commit
                        >> use(expr(b))
                    )
                )
                << apply
                >> (lambda arms_oth: tla_ast.Case(arms_oth[0], arms_oth[1]))
            )

        yield ((tokens.KWD("CASE"),), f)

        #     use (atomic_expr b);
        yield use(atomic_expr(b))

        # WF_ sub_expr (expr)
        def f():
            return intf.locate(
                intf.punct("WF_")
                << second_commit
                >> use(sub_expr(b))
                << times2
                >> optional(
                    intf.punct("(")
                    << second
                    >> use(expr(b))
                    << first
                    >> intf.punct(")")
                )
                << apply
                >> apply_wf
            )

        yield ((tokens.PUNCT("WF_"),), f)

        # SF_ sub_expr (expr)
        def f():
            return intf.locate(
                intf.punct("SF_")
                << second_commit
                >> use(sub_expr(b))
                << times2
                >> optional(
                    intf.punct("(")
                    << second
                    >> use(expr(b))
                    << first
                    >> intf.punct(")")
                )
                << apply
                >> apply_strong_fair
            )

        yield ((tokens.PUNCT("SF_"),), f)

    #   ]
    while True:
        yield choice_iter(choices)


# end


#
# begin
#   let rec exspec b = lazy begin
#   punct "!" >>> use (trail b) <<< infix "=" <*> (use (expr true))
#   (* choice [ attempt (punct "@" <!> At true);  use expr ] *)
# end
def exspec(b):
    while True:
        yield (
            # '!' trail '=' expr
            intf.punct("!")
            << second
            >> use(trail(b))
            << first
            >> intf.infix("=")
            << times
            >> use(expr(True))
        )


#             and trail b = lazy begin
#               star1 begin
#                 choice [
#                   punct "."
#                       >>> anyname
#                       <$> (fun x -> Except_dot x) ;
#
#                   punct "[" >>> use (expr b) <<< punct "]"
#                   <$> (fun e -> Except_apply e) ;
#                 ]
#               end
def trail(b):
    while True:
        yield star1(
            choice(
                [
                    # '.' anyname
                    intf.punct(".")
                    << second
                    >> intf.anyname()
                    << apply
                    >> (lambda x: tla_ast.Except_dot(x)),
                    # '[' expr ']'
                    intf.punct("[")
                    << second
                    >> use(expr(b))
                    << first
                    >> intf.punct("]")
                    << apply
                    >> (lambda e: tla_ast.Except_apply(e)),
                ]
            )
        )


#           function
#             | [e] ->
#                 choice [
#                   punct ">>_" >*> use (sub_expr b)
#                   <$> (fun v -> Sub (Dia, e, v)) ;
#
#                   punct ">>" <!> Tuple [e] ;
#                 ]
#             | es ->
#                 punct ">>" <!> Tuple es
def apply_tuple(b, es):
    if len(es) == 1:
        return choice(
            [
                intf.punct(">>_")
                << second_commit
                >> use(sub_expr(b))
                << apply
                >> (lambda v: tla_ast.Sub(tla_ast.DiamondOp(), es[0], v)),
                intf.punct(">>") << bang >> tla_ast.Tuple(es),
            ]
        )
    else:
        return intf.punct(">>") << bang >> tla_ast.Tuple(es)


#       <$> (fun (v, e) ->
#                match e with
#                  | Some ex -> Fair (Weak, v, ex)
#                  | None ->
#                      begin match v.core with
#                        | Bang (a,sr) -> let srev = List.rev sr in
#                            begin match List.hd srev with
#                              | Sel_lab (h,el) ->
#                                   (*if List.length el = 1 then*)
#                                  Fair (Weak,
#                                   (Bang(a, (List.rev
#                                       ((Sel_lab(h,[]))
#                                           ::(List.tl srev)))) @@ v),
#                                           List.hd el)
#                              | _ -> Errors.bug ~at:v "Expr.Parser.WF:1"
#                            end
#                        | _ -> Errors.set v "Expr.Parser.WF:2";
#                               failwith "Expr.Parser.WF:2"
#                      end
#              )
def apply_wf(v_e):
    v, e = v_e
    if e is not None:
        return tla_ast.Fairness(tla_ast.WeakFairness(), v, e)
    assert e is None, e
    if not isinstance(v, tla_ast.Bang):
        raise ValueError(v.operands, e)
    a = v.expr
    sr = v.sel_list
    srev = list(reversed(sr))
    hd = srev[0]
    if not isinstance(hd, tla_ast.SelLab):
        raise ValueError(v, e, srev)
    h = hd.string
    el = hd.exprs
    g = [tla_ast.SelLab(h, list())] + srev[1:]
    g = list(reversed(g))
    return tla_ast.Fairness(
        tla_ast.WeakFairness(), tla_ast.Bang(a, g), el[0]  # TODO: @@v
    )


#       <$> (fun (v, e) ->
#                match e with
#                  | Some ex -> Fair (Strong, v, ex)
#                  | None ->
#                      begin match v.core with
#                        | Bang (a,sr) -> let srev = List.rev sr in
#                            begin match List.hd srev with
#                              | Sel_lab (h,el) ->
#                                   (*if List.length el = 1 then*)
#                                  Fair (Strong,
#                                   (Bang(a, (List.rev
#                                       ((Sel_lab(h,[]))
#                                           ::(List.tl srev)))) @@ v),
#                                           List.hd el)
#                              | _ -> Errors.bug ~at:v "Expr.Parser.SF:1"
#                            end
#                        | _ -> Errors.set v "Expr.Parser.SF:2";
#                               failwith "Expr.Parser.SF:2"
#                      end
#              )
def apply_strong_fair(v_e):
    v, e = v_e
    if e is not None:
        return tla_ast.Fairness(tla_ast.StrongFairness(), v, e)
    assert e is None, e
    if not isinstance(v, tla_ast.Bang):
        raise ValueError(v, e)
    assert isinstance(v, tla_ast.Bang), v
    a = v.expr
    sr = v.sel_list
    srev = list(reversed(sr))
    hd = srev[0]
    if not isinstance(hd, tla_ast.SelLab):
        raise ValueError(v, e, srev)
    h = hd.string
    el = hd.exprs
    g = [tla_ast.SelLab(h, list())] + srev[1:]
    g = list(reversed(g))
    return tla_ast.Fairness(
        tla_ast.StrongFairness(), tla_ast.Bang(a, g), el[0]  # TODO @@ v
    )


# and atomic_expr b = lazy begin
def atomic_expr(b):
    def choices():
        #   choice [
        #     locate begin
        #       punct "{" >>>
        #         choice [
        #           attempt (hint
        #               <*> (infix "\\in" >*> use (expr b))
        #               )
        #           <*> (punct ":" >*> use (expr b))
        #           <$> (fun ((v, ran), e) -> SetSt (v, ran, e)) ;
        #
        #           attempt (
        #               use (expr b)
        #               <<< punct ":")
        #           <*> use (boundeds b)
        #           <$> (fun (e, bs) -> SetOf (e, bs)) ;
        #
        #           sep (punct ",") (use (expr b))
        #           <$> (fun es -> SetEnum es)
        #         ]
        #       <<< punct "}"
        #     end ;
        def f():
            return intf.locate(
                intf.punct("{")
                << second
                >> choice(
                    [
                        # RULE: '{' hint '\\in' expr ':' expr '}'
                        attempt(
                            hint()
                            << times
                            >> (intf.infix("\\in") << second_commit >> use(expr(b)))
                        )
                        << times
                        >> (intf.punct(":") << second_commit >> use(expr(b)))
                        << apply
                        >> (
                            lambda v_ran_e: tla_ast.SetSt(
                                v_ran_e[0][0], v_ran_e[0][1], v_ran_e[1]
                            )
                        ),
                        # RULE: '{' expr ':' boundeds '}'
                        attempt(use(expr(b)) << first >> intf.punct(":"))
                        << times
                        >> use(boundeds(b))
                        << apply
                        >> (lambda e_bs: tla_ast.SetOf(e_bs[0], e_bs[1])),
                        # RULE: '{' [expr] (',' expr)* '}'
                        sep(intf.punct(","), use(expr(b)))
                        << apply
                        >> (lambda es: tla_ast.SetEnum(es)),
                    ]
                )
                << first
                >> intf.punct("}")
            )

        yield ((tokens.PUNCT("{"),), f)

        #
        #     locate begin
        def f():
            return intf.locate(
                intf.punct("[")
                << second
                >> choice(
                    [
                        #       punct "[" >>>
                        #         choice [
                        #           enabled (anyname <<< punct "|->") >*>
                        #             sep1 (punct ",") (anyname <<< punct "|->" <**> use (expr b))
                        #           <<< punct "]"
                        #           <$> (fun fs -> Record fs) ;
                        #
                        #           enabled (anyname <<< punct ":") >*>
                        #             sep1 (punct ",") (anyname <<< punct ":" <*> use (expr b))
                        #           <<< punct "]"
                        #           <$> (fun fs -> Rect fs) ;
                        # [ [anyname |-> expr]+ ]
                        enabled(intf.anyname() << first >> intf.punct("|->"))
                        << second_commit
                        >> sep1(
                            intf.punct(","),
                            intf.anyname()
                            << first
                            >> intf.punct("|->")
                            << times2
                            >> use(expr(b)),
                        )
                        << first
                        >> intf.punct("]")
                        << apply
                        >> (lambda fs: tla_ast.Record(fs)),
                        enabled(intf.anyname() << first >> intf.punct(":"))
                        << second_commit
                        >> sep1(
                            intf.punct(","),
                            intf.anyname()
                            << first
                            >> intf.punct(":")
                            << times
                            >> use(expr(b)),
                        )
                        << first
                        >> intf.punct("]")
                        << apply
                        >> (lambda fs: tla_ast.RecordSet(fs)),
                        #
                        #           begin
                        #             let rec exspec b = lazy begin
                        #               punct "!" >>> use (trail b) <<< infix "=" <*> (use (expr true))
                        #                (* choice [ attempt (punct "@" <!> At true);  use expr ] *)
                        #             end
                        #
                        #             and trail b = lazy begin
                        #               star1 begin
                        #                 choice [
                        #                   punct "."
                        #                       >>> anyname
                        #                       <$> (fun x -> Except_dot x) ;
                        #
                        #                   punct "[" >>> use (expr b) <<< punct "]"
                        #                   <$> (fun e -> Except_apply e) ;
                        #                 ]
                        #               end
                        #
                        #             end in
                        #               attempt (use (expr b) <<< kwd "EXCEPT")
                        #               <**> sep1 (punct ",") (use (exspec b)) <<< punct "]"
                        #               <$> (fun (e, xs) -> Except (e, xs))
                        #           end ;
                        # [ expr EXCEPT exspec [exspec]* ]
                        attempt(use(expr(b)) << first >> intf.kwd("EXCEPT"))
                        << times2
                        >> sep1(intf.punct(","), use(exspec(b)))
                        << first
                        >> intf.punct("]")
                        << apply
                        >> (lambda e_xs: tla_ast.Except(e_xs[0], e_xs[1])),
                        #           attempt (use (boundeds b) <<< punct "|->") <**> use (expr b)
                        #           <<< punct "]"
                        #           <$> (fun (bs, e) -> Fcn (bs, e)) ;
                        # [ boundeds |-> expr ]
                        attempt(use(boundeds(b)) << first >> intf.punct("|->"))
                        << times2
                        >> use(expr(b))
                        << first
                        >> intf.punct("]")
                        << apply
                        >> (lambda bs_e: tla_ast.Function(bs_e[0], bs_e[1])),
                        #           use (expr b) >>= begin fun e ->
                        #             choice [
                        #               punct "->" >*> use (expr b) <<< punct "]"
                        #               <$> (fun f -> Arrow (e, f)) ;
                        #
                        #               punct "]_" >>> use (sub_expr b)
                        #               <$> (fun v -> Sub (Box, e, v)) ;
                        #             ]
                        #           end ;
                        use(expr(b))
                        << shift_eq
                        >> (
                            lambda e: choice(
                                [
                                    # [ expr -> expr ]
                                    intf.punct("->")
                                    << second_commit
                                    >> use(expr(b))
                                    << first
                                    >> intf.punct("]")
                                    << apply
                                    >> (lambda f: tla_ast.Arrow(e, f)),
                                    # [ expr ]_ sub_expr
                                    intf.punct("]_")
                                    # TODO: This was `commit`
                                    # but allowed unexpected behavior
                                    << second_commit
                                    >> use(sub_expr(b))
                                    << apply
                                    >> (lambda v: tla_ast.Sub(tla_ast.BoxOp(), e, v)),
                                ]
                            )
                        )
                        #         ]
                    ]
                )
            )

        yield ((tokens.PUNCT("["),), f)
        #     end ;

        #     locate begin
        #       punct "<<" >>>
        #         sep (punct ",") (use (expr b)) >>= begin
        #           function
        #             | [e] ->
        #                 choice [
        #                   punct ">>_" >*> use (sub_expr b)
        #                   <$> (fun v -> Sub (Dia, e, v)) ;
        #
        #                   punct ">>" <!> Tuple [e] ;
        #                 ]
        #             | es ->
        #                 punct ">>" <!> Tuple es
        #         end
        #     end ;

        # '<<' expr '>>_' sub_expr
        #  | '<<' (expr)? (, expr)* '>>'
        def f():
            return intf.locate(
                intf.punct("<<")
                << second
                >> sep(intf.punct(","), use(expr(b)))
                << shift_eq
                >> functools.partial(apply_tuple, b)
            )

        yield ((tokens.PUNCT("<<"),), f)

        #     locate begin
        #       punct "WF_" >*>
        #         use (sub_expr b)
        #           <**> optional (punct "(" >>> use (expr b) <<< punct ")")
        #       <$> (fun (v, e) ->
        #                match e with
        #                  | Some ex -> Fair (Weak, v, ex)
        #                  | None ->
        #                      begin match v.core with
        #                        | Bang (a,sr) -> let srev = List.rev sr in
        #                            begin match List.hd srev with
        #                              | Sel_lab (h,el) ->
        #                                   (*if List.length el = 1 then*)
        #                                  Fair (Weak,
        #                                   (Bang(a, (List.rev
        #                                       ((Sel_lab(h,[]))
        #                                           ::(List.tl srev)))) @@ v),
        #                                           List.hd el)
        #                              | _ -> Errors.bug ~at:v "Expr.Parser.WF:1"
        #                            end
        #                        | _ -> Errors.set v "Expr.Parser.WF:2";
        #                               failwith "Expr.Parser.WF:2"
        #                      end
        #              )
        #     end ;

        # This production rule has been moved to
        # `complex_expr` to avoid an infinite recursion
        # via the `atomic_expr`.
        # intf.locate(
        #     intf.punct('WF_')
        #         <<second_commit>> use(sub_expr(b))
        #         <<times2>> optional (
        #             intf.punct('(')
        #             <<second>> use(expr(b))
        #             <<first>> intf.punct(')'))
        #     <<apply>> apply_wf
        # ),

        #     locate begin
        #       punct "SF_" >*>
        #         use (sub_expr b)
        #           <**> optional (punct "(" >>> use (expr b) <<< punct ")")
        #       <$> (fun (v, e) ->
        #                match e with
        #                  | Some ex -> Fair (Strong, v, ex)
        #                  | None ->
        #                      begin match v.core with
        #                        | Bang (a,sr) -> let srev = List.rev sr in
        #                            begin match List.hd srev with
        #                              | Sel_lab (h,el) ->
        #                                   (*if List.length el = 1 then*)
        #                                  Fair (Strong,
        #                                   (Bang(a, (List.rev
        #                                       ((Sel_lab(h,[]))
        #                                           ::(List.tl srev)))) @@ v),
        #                                           List.hd el)
        #                              | _ -> Errors.bug ~at:v "Expr.Parser.SF:1"
        #                            end
        #                        | _ -> Errors.set v "Expr.Parser.SF:2";
        #                               failwith "Expr.Parser.SF:2"
        #                      end
        #              )
        #     end ;
        # (*        use (sub_expr b) <**> (punct "(" >>> use (expr b) <<< punct ")")
        #       <$> (fun (v, e) -> Fair (Strong, v, e))
        #     end ;*)

        # This production rule has been moved to
        # `complex_expr` to avoid an infinite recursion
        # intf.locate(
        #     intf.punct('SF_')
        #         <<second_commit>> use(sub_expr(b))
        #         <<times2>> optional (
        #             intf.punct('(')
        #             <<second>> use(expr(b))
        #             <<first>> intf.punct(')')
        #         ) <<apply>> apply_strong_fair
        # ),

        #
        #     locate begin
        #       punct "@" <!> (At b)
        #     end ;
        # '@'
        yield intf.locate(intf.punct("@") << bang >> tla_ast.At(b))

        #     use (reduced_expr b) ;
        yield use(reduced_expr(b))

    #   ]
    while True:
        yield choice_iter(choices)


# end


def string_scan(form):
    if isinstance(form, tokens.STR):
        return tla_ast.String(form.string)
    else:
        return None


def number_scan(form):
    if isinstance(form, tokens.NUM):
        return tla_ast.Number(form.string1, form.string2)
    else:
        return None


# and reduced_expr b = lazy begin
#   choice [
#     (* parentheses *)
#     punct "(" >>> use (expr b) <<< punct ")"
#     <$> (fun e -> Parens (e, Syntax @@ e) @@ e) ;
#
#     (* string *)
#     locate begin
#       scan begin
#         function
#           | STR s -> Some (String s)
#           | _ -> None
#       end
#     end ;
#
#     (* number *)
#     locate begin
#       scan begin
#         function
#           | NUM (m, n) -> Some (Num (m, n))
#           | _ -> None
#       end
#     end ;
#
#     locate (kwd "TRUE" <!> Internal B.TRUE) ;
#     locate (kwd "FALSE" <!> Internal B.FALSE) ;
#     locate (kwd "BOOLEAN" <!> Internal B.BOOLEAN) ;
#     locate (kwd "STRING" <!> Internal B.STRING) ;
#
#     (* locate (punct "@" <!> At) ; *)
#   ]
# end
def reduced_expr(b):
    def choices():
        # '(' expr ')'
        def f():
            return (
                intf.punct("(")
                << second
                >> use(expr(b))
                << first
                >> intf.punct(")")
                << apply
                >> (lambda e: tla_ast.Parens(e, tla_ast.Syntax()))
            )

        yield ((tokens.PUNCT("("),), f)
        # STR
        yield intf.locate(intf.scan(string_scan))
        # NUM
        yield intf.locate(intf.scan(number_scan))
        # 'TRUE'
        yield intf.locate(
            intf.kwd("TRUE") << bang >> tla_ast.TRUE()  # tla_ast.Internal(
        )
        # 'FALSE'
        yield intf.locate(
            intf.kwd("FALSE") << bang >> tla_ast.FALSE()  # tla_ast.Internal(
        )
        # 'BOOLEAN'
        yield intf.locate(
            intf.kwd("BOOLEAN") << bang >> tla_ast.BOOLEAN()  # tla_ast.Internal(
        )
        # 'STRING'
        yield intf.locate(
            intf.kwd("STRING") << bang >> tla_ast.STRING()  # tla_ast.Internal(
        )

    while True:
        yield choice_iter(choices)


def apply_sub_expr(prs):
    id, sr = prs
    e = tla_ast.Opaque(id)
    if sr is None:
        return e
    assert sr is not None
    return tla_ast.Bang(e, sr)


# and sub_expr b = lazy begin
#   choice [
#     locate begin
#       hint <*> optional (use (subref b))
#     end <$> begin
#       fun prs ->
#         let (id, sr) = prs.core in
#         let e = Opaque id.core @@ id in
#         match sr with
#           | None -> e
#           | Some sr -> Bang (e, sr) @@ prs
#     end ;
#
#     use (atomic_expr b) ;
#   ]
# end
def sub_expr(b):
    while True:
        yield choice(
            [
                intf.locate(hint() << times >> optional(use(subref(b))))
                << apply
                >> apply_sub_expr,
                # causes infinite recursion
                use(atomic_expr(b))
                # use(expr(b))
            ]
        )


# and bull_at bull where =
#   P.scan begin
#     fun t ->
#       let module Loc = Loc in
#         if t.form = OP bull && Loc.column t.loc.start = where
#         then Some ()
#         else None
#   end
def bull_at(bull, where):
    def f(t):
        if (
            isinstance(t.form, tokens.OP)
            and t.form.string == bull
            and t.loc.start.column == where
        ):
            return tuple()
        else:
            return None

    return pco.scan(f)


# and bulleted_list b = lazy begin
#   lookahead (scan begin
#                function
#                  | OP "/\\" -> Some "/\\"
#                  | OP "\\/" -> Some "\\/"
#                  | _ -> None
#              end)
#   >>+ fun bt loc ->
#     get >>= fun px ->
#       let module Loc = Loc in
#       let bwhere = Loc.column loc.start in
#       let newledge = { px with ledge = Loc.column loc.start + 1 } in
#         star1 (bull_at bt bwhere >>> using newledge (use (expr b)))
#         <$> (fun es -> match bt with
#                | "\\/" -> List (Or, es)
#                | _     -> List (And, es))
# end
def bulleted_list(b):
    def f(op):
        if isinstance(op, tokens.OP) and op.string == "/\\":
            return "/\\"
        elif isinstance(op, tokens.OP) and op.string == "\\/":
            return "\\/"
        else:
            return None

    def g(bt, loc, px):
        bwhere = loc.start.column
        newledge = intf.Pcx(bwhere + 1, px.clean)
        return (
            star1(bull_at(bt, bwhere) << second >> using(newledge, use(expr(b))))
            << apply
            >> (
                lambda es: tla_ast.List(tla_ast.Or(), es)
                if bt == "\\/"
                else tla_ast.List(tla_ast.And(), es)
            )
        )

    while True:
        yield lookahead(intf.scan(f)) << shift_plus >> (
            lambda bt, loc: get() << shift_eq >> functools.partial(g, bt, loc)
        )


# and operator b = lazy begin
#   choice [
#     locate begin
#       kwd "LAMBDA" >*> sep1 (punct ",") hint
#       <**> (punct ":" >>> use (expr b))
#       <$> (fun (vs, e) -> Lambda (
#                           List.map (fun v -> (v, Shape_expr)) vs,
#                           e))
#     end ;
#
#     locate begin
#       choice [
#         anyident ;
#         scan begin
#             function
#               | ST (`Num n, l, 0) -> Some (Printf.sprintf "<%d>%s" n l)
#               | _ -> None
#         end ;
#       ] <$> (fun v -> Opaque v)
#     end ;
#
#     punct "(" >>> use (operator b) <<< punct ")" ;
#   ]
# end
def operator(b):
    # <$> (fun (vs, e) -> Lambda (
    #                     List.map (fun v -> (v, Shape_expr)) vs,
    #                     e))
    def apply_lambda(vs_e):
        vs, e = vs_e
        hint_shapes = [(v, tla_ast.ShapeExpr()) for v in vs]
        return tla_ast.Lambda(hint_shapes, e)

    def scan_step():
        def f(form):
            if isinstance(form, tokens.ST) and isinstance(form.kind, tokens.StepNum):
                n = form.kind.value
                m = form.string
                return "<" + n + ">" + m
            else:
                return None

        return intf.scan(f)

    def choices():
        #     locate begin
        #       kwd "LAMBDA" >*> sep1 (punct ",") hint
        #       <**> (punct ":" >>> use (expr b))
        #       <$> (fun (vs, e) -> Lambda (
        #                           List.map (fun v -> (v, Shape_expr)) vs,
        #                           e))
        #     end ;

        # RULE: 'LAMBDA' hint (, hint)* ':' expr
        def f():
            return intf.locate(
                intf.kwd("LAMBDA")
                << second_commit
                >> sep1(intf.punct(","), hint())
                << times2
                >> (intf.punct(":") << second >> use(expr(b)))
                << apply
                >> apply_lambda
            )

        yield ((tokens.KWD("LAMBDA"),), f)

        #     locate begin
        #       choice [
        #         anyident ;
        #         scan begin
        #             function
        #               | ST (`Num n, l, 0) ->
        #                       Some (Printf.sprintf "<%d>%s" n l)
        #               | _ -> None
        #         end ;
        #       ] <$> (fun v -> Opaque v)
        #     end ;

        # RULE: [anyident | ST ]
        def f():
            return intf.locate(
                choice([intf.anyident(), scan_step()])
                << apply
                >> (lambda v: tla_ast.Opaque(v))
            )

        yield (
            (
                tokens.ID,
                tokens.ST,
            ),
            f,
        )

        # punct "(" >>> use (operator b) <<< punct ")" ;

        # RULE: '(' operator ')'
        def f():
            return (
                intf.punct("(")
                << second
                >> use(operator(b))
                << first
                >> intf.punct(")")
            )

        yield ((tokens.PUNCT("("),), f)

    while True:
        yield choice_iter(choices)


#     fun bss ->
#       let vss = List.map begin
#         fun (vs, dom) -> match dom with
#           | None ->
#               List.map (fun v -> (v, Constant, No_domain)) vs
#           | Some dom ->
#               (List.hd vs, Constant, Domain dom)
#               :: List.map (fun v -> (v, Constant, Ditto)) (List.tl vs)
#       end bss in
#       List.concat vss
def apply_bounds(bss):
    def f(vs_dom):
        vs, dom = vs_dom
        if dom is None:
            return [(v, tla_ast.Constant(), tla_ast.NoDomain()) for v in vs]
        else:
            return [(vs[0], tla_ast.Constant(), tla_ast.Domain(dom))] + [
                (v, tla_ast.Constant(), tla_ast.Ditto()) for v in vs[1:]
            ]

    vss = [f(vs_dom) for vs_dom in bss]
    flat = [i for j in vss for i in j]
    return flat


# and bounds b = lazy begin
#   sep1 (punct ",") (
#       sep1 (punct ",") hint
#       <*> optional (infix "\\in" >*> use (expr b))
#   )
#   <$> begin
#     fun bss ->
#       let vss = List.map begin
#         fun (vs, dom) -> match dom with
#           | None ->
#               List.map (fun v -> (v, Constant, No_domain)) vs
#           | Some dom ->
#               (List.hd vs, Constant, Domain dom)
#               :: List.map (fun v -> (v, Constant, Ditto)) (List.tl vs)
#       end bss in
#       List.concat vss
#   end
# end
def bounds(b):
    # RULE: hint (',' hint)* '\\in' expr
    #           (hint (',' hint)* '\\in' expr)*
    while True:
        yield sep1(
            intf.punct(","),
            sep1(intf.punct(","), hint())
            << times2
            >> optional(intf.infix("\\in") << second_commit >> use(expr(b))),
        ) << apply >> apply_bounds


def apply_boundeds(bss):
    def f(vs_dom):
        vs, dom = vs_dom
        return [(vs[0], tla_ast.Constant(), tla_ast.Domain(dom))] + [
            (v, tla_ast.Constant(), tla_ast.Ditto()) for v in vs[1:]
        ]

    vss = [f(vs_dom) for vs_dom in bss]
    return [i for j in vss for i in j]


# and boundeds b = lazy begin
#   sep1 (punct ",") (
#       sep1 (punct ",") hint <*> (infix "\\in" >*> use (expr b))
#   )
#   <$> begin
#     fun bss ->
#       let vss = List.map begin
#         fun (vs, dom) ->
#           (List.hd vs, Constant, Domain dom)
#           :: List.map (fun v -> (v, Constant, Ditto)) (List.tl vs)
#       end bss in
#       List.concat vss
#   end
# end
def boundeds(b):
    while True:
        yield sep1(
            # hint [, hint]* \in expr [, hint [, hint]*]*
            intf.punct(","),
            sep1(intf.punct(","), hint())
            << times
            >> (intf.infix("\\in") << second_commit >> use(expr(b))),
        ) << apply >> apply_boundeds


# (* pragmas *)
#
# and float =
#   number <$> (fun (m, n) ->
#                 float_of_string (Printf.sprintf "%s.%s0" m n))
def float_():
    while True:
        yield (
            intf.number()
            << apply
            >> (lambda m_n: f"{m_n[0]}.{m_n[1]}" if m_n[1] == "None" else f"{m_n[0]}")
        )


# and read_method_by = lazy begin
#   ident "by" >>> use read_method_args <$> (fun l -> l)
# end
def read_method_by():
    while True:
        yield (intf.ident("by") << second >> use(read_method_args()))


# (* The "set" syntax has been deprecated. *)
# and read_method_set = lazy begin
#   ident "set" >>> use read_method_args <$> (fun l -> l)
# end
#
# and read_new_method = lazy begin
#   pragma (star (choice [use read_method_by; use read_method_set]))
# end
def read_new_method():
    while True:
        yield intf.pragma(star(use(read_method_by())))


# and read_method_args = lazy begin
#     punct "(" >*> sep1 (punct ";") (use (read_method_arg)) <<< punct ")"
# end
def read_method_args():
    while True:
        yield (
            intf.punct("(")
            << second_commit
            >> sep1(intf.punct(";"), use(read_method_arg()))
            << first
            >> intf.punct(")")
        )


# and read_method_arg = lazy begin
#       hint <*> (punct ":" >*> use string_or_float_of_expr)
# end
def read_method_arg():
    while True:
        yield (
            hint()
            << times
            >> (intf.punct(":") << second_commit >> use(string_or_float_of_expr()))
        )


# and string_val = lazy begin
#   str <$> fun s -> Bstring s
# end
def string_val():
    while True:
        yield (intf.str_() << apply >> (lambda s: tla_ast.Bstring(s)))


# and float_val = lazy begin
#   float <$> fun s -> Bfloat s
# end
def float_val():
    while True:
        yield (float_() << apply >> (lambda s: tla_ast.Bfloat(s)))


# and expr_def = lazy begin
#    punct "@" <!> Bdef
# end
def expr_def():
    while True:
        yield intf.punct("@") << bang >> tla_ast.Bdef()


# and string_or_float_of_expr = lazy begin
#   choice [ use string_val;
#            use expr_def;
#            use float_val;
#          ]
# end
def string_or_float_of_expr():
    while True:
        yield choice([use(string_val()), use(expr_def()), use(float_val())])


class Op:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class Fun:
    def __init__(self, name, args):
        self.name = name
        self.args = args


# (* definitions *)
#
# and defn b = lazy begin
def defn(b):
    # <$?> (fun i ->
    #         match head with
    #         | `Op (h, args) ->
    #             let args = List.map fst args in
    #             let loc = Loc.merge
    #                       (Util.get_locus oph)
    #                       (Util.get_locus i) in
    #               Some (Util.locate (
    #                   Instance (h, { i.core with inst_args = args })
    #                   ) loc)
    #         | _ ->
    #             None) ;
    def apply_instance(head, i):
        if not isinstance(head, Op):
            return None
        assert isinstance(head, Op), head
        h = head.name
        args = head.args
        args = [arg[0] for arg in args]
        # loc = Util.get_locus(head).merge(Util.get_locus(i))
        return tla_ast.Instance(
            name=h, args=args, module=i.module, sub=i.sub
        )  # Util.locate ... loc

    # fun (e,o) ->
    def apply_op_def(head, e_o):
        e, o = e_o
        # TODO: location tracking
        #   let loc = Loc.merge
        #               (Util.get_locus oph)
        #               (Util.get_locus e) in
        #   let op =
        # match o with
        # | None ->
        if o is None:
            # match head with
            # | `Op (h, args) ->
            if isinstance(head, Op):
                h = head.name
                args = head.args
                # match args with
                #   | [] -> Operator (h, e)
                #   | _ -> Operator (h, Util.locate (Lambda (args, e)) loc)
                if args:
                    return tla_ast.OperatorDef(
                        h, tla_ast.Lambda(args, e)  # Util.locate ... loc
                    )
                else:
                    return tla_ast.OperatorDef(h, e)
            # | `Fun (h, args) ->
            elif isinstance(head, Fun):
                h = head.name
                args = head.args
                # Operator (h, Util.locate (Fcn (args, e)) loc)
                return tla_ast.OperatorDef(
                    h, tla_ast.Function(args, e)  # Util.locate ... loc
                )
            else:
                raise ValueError(head)
        else:
            # | Some (l) ->
            # match head with
            # | `Op (h, args) ->
            if isinstance(head, Op):
                h = head.name
                args = head.args
                if args:
                    return tla_ast.BackendPragma(
                        h, tla_ast.Lambda(args, e), o  # Util.locate ... loc
                    )
                else:
                    return tla_ast.BackendPragma(h, e, o)
                # match args with
                #   | [] -> Bpragma (h, e, l)
                #   | _ -> Bpragma (h,
                #            (Util.locate (Lambda (args, e)) loc),
                #            l)
            elif isinstance(head, Fun):
                h = head.name
                args = head.args
                assert False
            else:
                raise ValueError(head)

    #               | `Fun (h, args) ->  assert false
    #                     (*** FIXME add error message ***)
    #           end
    #   in Util.locate op loc

    def apply_defn(head):
        def choices():
            # RULE: ophead '==' instance
            # instance definition
            #
            # locate (use (instance b))
            yield (
                intf.locate(use(instance(b)))
                << apply_question
                >> functools.partial(apply_instance, head)
            )

            # RULE: ophead '==' expr [read_new_method]
            # operator definition
            #
            # use (expr b) <*> optional (use read_new_method) <$>
            yield (
                use(expr(b))
                << times
                >> optional(use(read_new_method()))
                << apply
                >> functools.partial(apply_op_def, head)
            )

        return commit(choice_iter(choices))

    while True:
        yield intf.locate(
            use(ophead(b)) << first >> intf.punct("==")
        ) << shift_eq >> apply_defn


#   locate (use (ophead b)
#           <<< punct "==") >>= fun ({core = head} as oph) ->
#     commit begin
#       choice [
#         locate (use (instance b))
#         <$?> (fun i ->
#                 match head with
#                 | `Op (h, args) ->
#                     let args = List.map fst args in
#                     let loc = Loc.merge
#                               (Util.get_locus oph)
#                               (Util.get_locus i) in
#                       Some (Util.locate (
#                           Instance (h, { i.core with inst_args = args })
#                           ) loc)
#                 | _ ->
#                     None) ;
#
#         (* ajout *)
#
#         use (expr b) <*> optional (use read_new_method) <$>
#           begin
#           fun (e,o) ->
#             let loc = Loc.merge (Util.get_locus oph) (Util.get_locus e) in
#             let op =
#               match o with
#                 | Some (l) ->
#                     begin
#                       match head with
#                         | `Op (h, args) ->
#                             begin
#                               match args with
#                                 | [] -> Bpragma (h, e, l)
#                                 | _ -> Bpragma (
#                                       h,
#                                       (Util.locate (Lambda (args, e)) loc),
#                                       l)
#                             end
#                         | `Fun (h, args) ->  assert false
#                               (*** FIXME add error message ***)
#                     end
#                 | None ->
#                     begin
#                       match head with
#                         | `Op (h, args) ->
#                             begin
#                               match args with
#                                 | [] -> Operator (h, e)
#                                 | _ -> Operator (
#                                       h, Util.locate (Lambda (args, e)) loc)
#                             end
#                         | `Fun (h, args) ->
#                             Operator (h, Util.locate (Fcn (args, e)) loc)
#                     end
#             in Util.locate op loc
#           end;
#

#       ]
#     end
# end


# and ophead b = lazy begin
#   choice [
#     locate anyprefix <*> hint
#       <$> (fun (h, u) -> `Op (h, [u, Shape_expr])) ;
#
#     hint >>= fun u ->
#       choice [
#         locate anypostfix
#         <$> (fun h -> `Op (h, [u, Shape_expr])) ;
#
#         locate anyinfix <*> hint
#         <$> (fun (h, v) -> `Op (h, [u, Shape_expr ; v, Shape_expr])) ;
#
#         punct "[" >>> use (bounds b) <<< punct "]"
#         <$> (fun args -> `Fun (u, args)) ;
#
#         optional (
#               punct "("
#               >>> sep1 (punct ",") (use opdecl)
#               <<< punct ")")
#         <$> (function
#                | None -> `Op (u, [])
#                | Some args -> `Op (u, args)) ;
#
#       ] ;
#   ]
# end
def ophead(b):
    def apply_ophead(u):
        return choice(
            [
                # postfix operator definition
                # RULE: hint anypostfix
                #
                # locate anypostfix <$> (fun h -> `Op (h, [u, Shape_expr])) ;
                intf.locate(intf.anypostfix())
                << apply
                >> (lambda h: Op(h, [(u, tla_ast.ShapeExpr())])),
                # infix operator definition
                # RULE: hint anyinfix hint
                #
                # locate anyinfix <*> hint <$>
                intf.locate(intf.anyinfix()) << times >> hint()
                # (fun (h, v) -> `Op (h, [u, Shape_expr ; v, Shape_expr])) ;
                << apply
                >> (
                    lambda h_v: Op(
                        h_v[0],
                        [(u, tla_ast.ShapeExpr()), (h_v[1], tla_ast.ShapeExpr())],
                    )
                ),
                # function definition
                # RULE: hint '[' bounds ']'
                #
                # punct "[" >>> use (bounds b) <<< punct "]"
                intf.punct("[") << second >> use(bounds(b)) << first >> intf.punct("]")
                # <$> (fun args -> `Fun (u, args)) ;
                << apply >> (lambda args: Fun(u, args)),
                # nonfix operator definition
                # RULE: '(' opdecl (',' opdecl)* ')'
                #
                # optional (
                #       punct "("
                #       >>> sep1 (punct ",") (use opdecl)
                #       <<< punct ")")
                optional(
                    intf.punct("(")
                    << second
                    >> sep1(intf.punct(","), use(opdecl()))
                    << first
                    >> intf.punct(")")
                )
                # <$> (function
                #        | None -> `Op (u, [])
                #        | Some args -> `Op (u, args)) ;
                << apply
                >> (lambda args: Op(u, list()) if args is None else Op(u, args)),
            ]
        )

    while True:
        yield choice(
            [
                # prefix operator definition
                # RULE: anyprefix hint
                #
                # locate anyprefix <*> hint
                intf.locate(intf.anyprefix()) << times >> hint()
                # <$> (fun (h, u) -> `Op (h, [u, Shape_expr]))
                << apply >> (lambda h_u: Op(h_u[0], [h_u[1], tla_ast.ShapeExpr()])),
                hint() << shift_eq >> apply_ophead,
            ]
        )


# and opdecl = lazy begin
#   choice [
#     locate anyprefix <<< punct "_"
#     <$> (fun h -> (h, Shape_op 1)) ;
#
#     punct "_" >*>
#       choice [
#         locate anypostfix
#         <$> (fun h -> (h, Shape_op 1)) ;
#
#         locate anyinfix <<< punct "_"
#         <$> (fun h -> (h, Shape_op 2))
#       ] ;
#
#     hint <*> optional (
#           punct "("
#           >>> sep1 (punct ",") (punct "_")
#           <<< punct ")"
#       )
#     <$> begin
#       fun (h, args) -> match args with
#         | None -> (h, Shape_expr)
#         | Some args ->
#             (h, Shape_op (List.length args))
#     end ;
#   ]
# end
def opdecl():
    def apply_op_param(h_args):
        h, args = h_args
        if args is None:
            return (h, tla_ast.ShapeExpr())
        else:
            arity = len(args)
            return (h, tla_ast.ShapeOp(arity))

    def choices():
        # prefix operator parameter
        # RULE: anyprefix '_'
        #
        # locate anyprefix <<< punct "_"
        def f():
            return (
                intf.locate(intf.anyprefix())
                << first
                >> intf.punct("_")
                # <$> (fun h -> (h, Shape_op 1)) ;
                << apply
                >> (lambda h: (h, tla_ast.ShapeOp(1)))
            )

        yield ((tokens.OP,), f)

        # punct "_" >*>
        def f():
            return (
                intf.punct("_")
                # choice [
                << second_commit
                >> choice(
                    [
                        # postfix operator parameter
                        # RULE: '_' anypostfix
                        #
                        # locate anypostfix
                        intf.locate(intf.anypostfix())
                        # <$> (fun h -> (h, Shape_op 1)) ;
                        << apply >> (lambda h: (h, tla_ast.ShapeOp(1))),
                        # infix operator parameter
                        # RULE: '_' anyinfix '_'
                        #
                        # locate anyinfix <<< punct "_"
                        intf.locate(intf.anyinfix()) << first >> intf.punct("_")
                        # <$> (fun h -> (h, Shape_op 2))
                        << apply >> (lambda h: (h, tla_ast.ShapeOp(2))),
                    ]
                )
            )

        yield ((tokens.PUNCT("_"),), f)

        # nonfix operator parameter
        # RULE: hint ['(' '_' (',' '_')* ')']
        # Example: Op(_, _)
        #
        # hint <*> optional (
        #       punct "("
        #       >>> sep1 (punct ",") (punct "_")
        #       <<< punct ")"
        #   )
        def f():
            return (
                hint()
                << times
                >> optional(
                    intf.punct("(")
                    << second
                    >> sep1(intf.punct(","), intf.punct("_"))
                    << first
                    >> intf.punct(")")
                )
                # <$> begin
                #   fun (h, args) -> match args with
                #     | None -> (h, Shape_expr)
                #     | Some args ->
                #         (h, Shape_op (List.length args))
                # end ;
                << apply
                >> apply_op_param
            )

        yield ((tokens.ID,), f)

    while True:
        yield choice_iter(choices)


# and oparg b = lazy begin
#   alt [
#     use (expr b);
#
#     locate anyop
#     <$> (fun op ->
#            if Hashtbl.mem Optable.optable op.core then
#              let top = Hashtbl.find Optable.optable op.core in
#              match top.defn with
#                | Some bin -> { op with core = Internal bin }
#                | None -> { op with core = Opaque op.core }
#            else { op with core = Opaque op.core }) ;
#   ]
# end
def oparg(b):
    def f(op):
        if op in _optable.optable:
            top, *_ = _optable.optable[op]
            if top.defn is None:
                return tla_ast.Opaque(op)
            else:
                # return tla_ast.Internal(top.defn)
                return top.defn
        else:
            return tla_ast.Opaque(op)

    # RULE: [expr | anyop]
    while True:
        yield alt([use(expr(b)), intf.locate(intf.anyop()) << apply >> f])


# and instance b = lazy begin
#   kwd "INSTANCE" >*> anyident
#   <*> optional (kwd "WITH" >*> use (subst b))
#   <$> (fun (m, sub) ->
#          { inst_args = [] ;
#            inst_mod = m ;
#            inst_sub = Option.default [] sub })
# end
def instance(b):
    def apply_instance(m_sub):
        m, sub = m_sub
        if sub is None:
            inst_sub = list()
        else:
            inst_sub = sub
        module = m
        return tla_ast.Instance(name=None, args=None, module=module, sub=inst_sub)

    while True:
        yield (
            intf.kwd("INSTANCE")
            << second_commit
            >> intf.anyident()
            << times
            >> optional(intf.kwd("WITH") << second_commit >> use(subst(b)))
            << apply
            >> apply_instance
        )


# and subst b = lazy begin
#   let exprify op = return (Opaque op) in
#   sep1 (punct ",")
#     (choice [ hint ; locate anyop ]
#      <**> (punct "<-" >>> choice [
#                            use (expr b) ;
#                            locate (anyop >>+ exprify) ]
#           )
#     )
# end
def subst(b):
    def exprify(op):
        return return_(tla_ast.Opaque(op))

    while True:
        yield (
            sep1(
                intf.punct(","),
                choice([hint(), intf.locate(intf.anyop())])
                << times2
                >> (
                    intf.punct("<-")
                    << second
                    >> choice(
                        [
                            use(expr(b)),
                            intf.locate(intf.anyop() << shift_plus >> exprify),
                        ]
                    )
                ),
            )
        )


# and hyp b = lazy begin locate begin
#   choice [
#     optional (kwd "NEW") >>= begin fun nk ->
#       choice [
#         kwd "VARIABLE" >*> hint <$> (fun v -> (Flex v)) ;
#         choice [
#           kwd "STATE" <!> State ;
#           kwd "ACTION" <!> Action ;
#           kwd "TEMPORAL" <!> Temporal ;
#           (if Option.is_some nk then
#              optional (kwd "CONSTANT") <!> 1
#            else
#              kwd "CONSTANT" <!> 2) <!> Constant ;
#         ] <**> alt [
#               hint <*> (infix "\\in" >*> use (expr b))
#               <$> (fun (v, b) -> (v, Shape_expr, Bounded (b, Visible))) ;
#
#               (use opdecl) <$> (fun (v, shp) -> (v, shp, Unbounded)) ]
#         <$> (fun (lev, (v, shp, ran)) -> (Fresh (v, shp, lev, ran))) ;
#       ]
#     end ;
#
#     locate (optional (hint <<< punct "::") <*> use (expr_or_sequent b))
#     <$> begin
#       fun le -> match le.core with
#         | (None, e) -> Fact (e, Visible, NotSet)
#         | (Some l, e) -> Fact (Parens (e, Xlabel (l.core, []) @@ l) @@ le,
#         Visible, NotSet)
#     end ;
#   ]
# end end
def hyp(b):
    def apply_decl(nk):
        # (fun (lev, (v, shp, ran)) -> (Fresh (v, shp, lev, ran))) ;
        def apply_decl_bound(level_v_shp_ran):
            level, (v, shp, ran) = level_v_shp_ran
            return tla_ast.Fresh(v, shp, level, ran)

        return choice(
            [
                # kwd "VARIABLE" >*> hint <$> (fun v -> (Flex v)) ;
                intf.kwd("VARIABLE")
                << second_commit
                >> hint()
                << apply
                >> (lambda v: tla_ast.Flex(v)),
                choice(
                    [
                        # kwd "STATE" <!> State ;
                        intf.kwd("STATE") << bang >> tla_ast.State(),
                        # kwd "ACTION" <!> Action ;
                        intf.kwd("ACTION") << bang >> tla_ast.Action(),
                        # kwd "TEMPORAL" <!> Temporal ;
                        intf.kwd("TEMPORAL") << bang >> tla_ast.Temporal(),
                        # (if Option.is_some nk then
                        #    optional (kwd "CONSTANT") <!> 1
                        #  else
                        #    kwd "CONSTANT" <!> 2) <!> Constant ;
                        (
                            (intf.kwd("CONSTANT") << bang >> 2)
                            if nk is None
                            else (optional(intf.kwd("CONSTANT")) << bang >> 1)
                        )
                        << bang
                        >> tla_ast.Constant()
                        # ] <**> alt [
                    ]
                )
                << times2
                >> alt(
                    [
                        # hint <*> (infix "\\in" >*> use (expr b))
                        hint()
                        << times
                        >> (intf.infix("\\in") << second_commit >> use(expr(b)))
                        # <$> (fun (v, b) ->
                        #             (v, Shape_expr, Bounded (b, Visible))) ;
                        << apply
                        >> (
                            lambda v_b: (
                                v_b[0],
                                tla_ast.ShapeExpr(),
                                tla_ast.Bounded(v_b[1], tla_ast.Visible()),
                            )
                        ),
                        # (use opdecl)
                        use(opdecl())
                        # <$> (fun (v, shp) -> (v, shp, Unbounded)) ]
                        << apply
                        >> (lambda v_shp: (v_shp[0], v_shp[1], tla_ast.Unbounded())),
                    ]
                )
                << apply
                >> apply_decl_bound,
            ]
        )

    #   fun le -> match le.core with
    #     | (None, e) -> Fact (e, Visible, NotSet)
    #     | (Some l, e) -> Fact (Parens (e, Xlabel (l.core, []) @@ l) @@ le,
    #     Visible, NotSet)
    def apply_sequent(label_expr):
        label, expr = label_expr
        if label is None:
            return tla_ast.Fact(expr, tla_ast.Visible(), tla_ast.NotSet())
        else:
            return tla_ast.Fact(
                tla_ast.Parens(
                    expr, tla_ast.IndexedLabel(label, list())  # @@ label
                ),  # @@ label_expr
                tla_ast.Visible(),
                tla_ast.NotSet(),
            )

    while True:
        yield intf.locate(
            choice(
                [
                    #     optional (kwd "NEW") >>= begin fun nk ->
                    optional(intf.kwd("NEW")) << shift_eq >> apply_decl,
                    # locate (optional (hint <<< punct "::") <*> use (expr_or_sequent b))
                    intf.locate(
                        optional(hint() << first >> intf.punct("::"))
                        << times
                        >> use(expr_or_sequent(b))
                    )
                    << apply
                    >> apply_sequent,
                ]
            )
        )


# and sequent b = lazy begin
#   kwd "ASSUME" >*> sep1 (punct ",") (use (hyp b))
#   <**> (kwd "PROVE" >>> use (expr b))
#   <$> (fun (hs, e) -> { context = Deque.of_list hs ; active = e }) ;
# end
def sequent(b):
    while True:
        yield (
            intf.kwd("ASSUME")
            << second_commit
            >> sep1(intf.punct(","), use(hyp(b)))
            << times2
            >> (intf.kwd("PROVE") << second >> use(expr(b)))
            << apply
            >> (lambda hs_e: tla_ast.Sequent(hs_e[0], hs_e[1]))
        )


# and expr_or_sequent b = lazy begin
#   alt [
#     use (expr b) ;
#     locate (use (sequent b))
#     <$> (fun sq -> { sq with core = Sequent sq.core }) ;
#   ]
# end
def expr_or_sequent(b):
    while True:
        yield (
            alt(
                [
                    use(expr(b)),
                    intf.locate(use(sequent(b))) << apply >> (lambda sq: sq)
                    # a `sequent` type is not present,
                    # the class `tla_ast.Sequent` is directly used
                ]
            )
        )
