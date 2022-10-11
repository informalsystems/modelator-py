"""Proof parser."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/proof/p_parser.ml>
import functools
import uuid

from . import _expr_parser as ep
from . import _tla_combinators as intf
from . import tokens
from ._combinators import (
    apply,
    attempt,
    bang,
    choice,
    optional,
    or_,
    second,
    second_commit,
    sep,
    sep1,
    shift_eq,
    star1,
    succeed,
    times,
    times2,
    use,
)
from ._tla_combinators import kwd, punct
from .ast import Nodes as tla_ast


# open Ext
# open Property
# open Expr.T
#
# open P_t
#
# let enlarge_loc x y =
#   Util.locate x (Loc.merge (Util.get_locus x) (Util.get_locus y))
def enlarge_loc(x, y):
    pass


# type preno =
#   | Star of string
#   | Plus of string
#   | Num of int * string


# let set_level n = function
#   | Star l | Plus l | Num (_, l) ->
#       match l with
#         | "" -> Unnamed (n, Std.unique ())
#         | _ -> Named (n, l, false)
def set_level(n, preno):
    label = preno.label
    if label == "":
        return tla_ast.Unnamed(n, uuid.uuid4())
    else:
        return tla_ast.Named(n, label, False)


# type supp = Emit | Suppress
# type only = Default | Only


# let annotate supp meth x =
#   let x = match supp with
#     | Suppress -> assign x Props.supp ()
#     | _ -> x
#   in
#   let x = match meth with
#     | Some meth -> assign x Props.meth [meth]
#     | _ -> x
#   in x
def annotate(supp, meth, x):
    if isinstance(supp, tla_ast.Suppress):
        x.supp = supp
    if meth:
        x.meth = meth


# type preproof_ =
#   | PreBy       of supp * only * usable * Method.t option
#   | PreObvious  of supp * Method.t option
#   | PreOmitted  of omission
#   | PreStep     of bool * preno * prestep
#
# and prestep =
#   | PreHide     of usable
#   | PreUse      of supp * only * usable * Method.t option
#   | PreDefine   of defn list
#   | PreAssert   of sequent
#   | PreSuffices of sequent
#   | PreCase     of expr
#   | PrePick     of bound list * expr
#   | PreHave     of supp * expr * Method.t option
#   | PreTake     of supp * bound list * Method.t option
#   | PreWitness  of supp * expr list * Method.t option
#   | PreQed
#
# type step_or_qed =
#   | STEP of step
#   | QED of proof
class STEP:
    def __init__(self, step):
        self.step = step


class QED:
    def __init__(self, proof):
        self.proof = proof


# exception Backtrack
class Backtrack(Exception):
    pass


# let rec to_proof currlv = function
def to_proof(currlv, arg):
    #   | [] ->
    if not arg:
        #       (Omitted Implicit @@ currlv, [])
        omitted = tla_ast.Omitted(tla_ast.Implicit())
        return (omitted, list())
    #   | {core = PreBy (supp, onl, use, meth)} as p :: ps ->
    elif isinstance(arg[0], tla_ast.PreBy):
        p = arg[0]
        ps = arg[1:]
        supp = p.supp
        only = p.only
        usable = p.usable
        meth = p.method
        #       let p = By (use, onl = Only) @@ p in
        p = tla_ast.By(usable, isinstance(only, tla_ast.Only))
        #       let p = Property.assign p Props.step
        #                   (Unnamed (currlv.core, 0)) in
        p.step_number = tla_ast.Unnamed(currlv, 0)
        #       (annotate supp meth p, ps)
        annotate(supp, meth, p)
        return (p, ps)
    #   | {core = PreObvious (supp, meth)} as p :: ps ->
    elif isinstance(arg[0], tla_ast.PreObvious):
        p = arg[0]
        ps = arg[1:]
        supp = p.supp
        meth = p.method
        #       let p = Obvious @@ p in
        obvious = tla_ast.Obvious()
        #       (annotate supp meth p, ps)
        annotate(supp, meth, obvious)
        return (obvious, ps)
    #   | {core = PreOmitted om} as p :: ps ->
    elif isinstance(arg[0], tla_ast.PreOmitted):
        p = arg[0]
        ps = arg[1:]
        om = p.omission
        #       (Omitted om @@ p, ps)
        omitted = tla_ast.Omitted(om)
        return (omitted, ps)
    else:
        #   | ps -> begin
        ps = arg
        #       try
        try:
            #         let (ss, qp, ps) = to_steps ~first:true currlv ps in
            (ss, qp, ps) = to_steps(first=True, currlv=currlv, ps=ps)
            #         let sloc = List.fold_left begin
            #           fun l s -> Loc.merge l (Util.get_locus s)
            #         end (try
            #               Util.get_locus qp.core
            #              with _ -> Util.get_locus
            #                           (get_qed_proof qp.core)) ss in
            # TODO: locus
            #         let prf = Util.locate (Steps (ss, qp.core)) sloc in
            prf = tla_ast.Steps(ss, qp)
            #         let prf = Property.assign prf Props.step
            #                   (Property.get qp Props.step) in
            prf.step_number = qp.step_number
            #         (prf, ps)
            return (prf, ps)
        #       with Backtrack ->
        except Backtrack:
            #         (Omitted Implicit @@ currlv, ps)
            omitted = tla_ast.Omitted(tla_ast.Implicit())
            return (omitted, ps)


#     end


# and to_steps ?(first = false) currlv ps = match ps with
def to_steps(first, currlv, ps):
    #   | {core = PreStep (kwd, sn, st)} as p :: ps ->
    p = ps[0]
    ps = ps[1:]
    kwd = p.boolean  # PROOF keyword
    sn = p.preno  # step number
    st = p.prestep
    #       if not first && kwd then begin
    #         Errors.set p
    #             ("PROOF keyword found in step that "
    #              "does not begin subproof");
    #         Util.eprintf ~at:p
    #             ("PROOF keyword found in step that " ^
    #              "does not begin subproof\n%!");
    #         failwith "Proof.Parser"
    #       end ;
    assert first or not kwd
    #       let thislv = match sn, kwd, first with
    #         | Num (n, _), _, _ -> n
    if isinstance(sn, tla_ast.StepNum):
        n = sn.level
        thislv = int(n)
    #         | Star _, true, true ->
    elif isinstance(sn, tla_ast.StepStar) and kwd and first:
        #             (*
        #              * Util.eprintf ~at:p
        #              *   "%d: <*> -> %d (because first and PROOF)\n%!"
        #              *   currlv.core currlv.core ;
        #              *)
        #             currlv.core
        thislv = currlv
    #         | Star _, false, true ->
    elif isinstance(sn, tla_ast.StepStar) and not kwd and first:
        #             (*
        #              * Util.eprintf ~at:p
        #              *   "%d: <*> -> %d (because first and no PROOF)\n%!"
        #              *   currlv.core (currlv.core - 1) ;
        #              *)
        #             currlv.core - 1
        thislv = currlv - 1
    #         | Star _, _, false ->
    elif isinstance(sn, tla_ast.StepStar) and not first:
        #             assert (not kwd) ;
        assert not kwd
        #             (*
        #              * Util.eprintf ~at:p
        #              *   "%d: <*> -> %d (because not first)\n%!"
        #              *   currlv.core currlv.core ;
        #              *)
        #             currlv.core
        thislv = currlv
    #         | Plus _, _, false ->
    elif isinstance(sn, tla_ast.StepPlus) and not first:
        #             Errors.set p "<+> used but no subproof expected" ;
        #               Util.eprintf ~at:p
        #                   "<+> used but no subproof expected\n%!" ;
        #             failwith "Proof.Parser"
        raise Exception("<+> usedd but no subproof expected")
    #         | Plus _, _, _ ->
    elif isinstance(sn, tla_ast.StepPlus):
        #             (*
        #              * Util.eprintf ~at:p
        #              *   "%d: <+> -> %d\n%!"
        #              *   currlv.core currlv.core ;
        #              *)
        #             currlv.core
        thislv = currlv
    else:
        raise ValueError(sn, kwd, first)
    #       in
    #       if thislv < currlv.core then
    if thislv < currlv:
        #           raise Backtrack ;
        raise Backtrack()
    #       if not first && thislv > currlv.core then
    if not first and thislv > currlv:
        #           raise Backtrack ;
        raise Backtrack()
    #       let sn = set_level thislv sn in begin
    sn = set_level(thislv, sn)
    #         match to_step thislv (st @@ p) ps with
    to_stp = to_step(thislv, st, ps)
    #           | (STEP s, nps) ->
    if isinstance(to_stp[0], STEP):
        s = to_stp[0].step
        nps = to_stp[1]
        #               let s = Property.assign s Props.step sn in
        s.step_number = sn
        #               let thislv = Util.locate thislv
        #                       (Loc.right_of (Util.get_locus s)) in
        # TODO: locate
        #               let (ss, qp, ps) = to_steps thislv nps in
        ss, qp, ps = to_steps(first=False, currlv=thislv, ps=nps)
        #               (s :: ss, qp, ps)
        return ([s] + ss, qp, ps)
    #           | (QED qp, ps) ->
    elif isinstance(to_stp[0], QED):
        qp = to_stp[0].proof
        ps = to_stp[1]
        #               let qp = { core =
        #                           {core = Qed qp;
        #                            props = [Props.step.Property.set sn]} ;
        #                          props = [Props.step.Property.set sn] } in
        #               ([], qp, ps)
        qed = tla_ast.Qed(qp)
        qed.step_number = sn
        return (list(), qed, ps)


#       end
#   | p :: _ ->
#       let found = match p.core with
#            | PreObvious _ -> "n OBVIOUS"
#            | PreOmitted _ -> "n OMITTED"
#            | PreBy _ -> " BY"
#            | _ -> Errors.bug ~at:p "to_steps: is a step after all?"
#       in
#       Errors.set p (Printf.sprintf
#           "Expecting a proof step but found a%s leaf proof\n" found);
#       Util.eprintf ~at:p
#            "Expecting a proof step but found a%s leaf proof\n" found;
#       failwith "Proof.Parser"
#   | [] ->
#       Util.eprintf ~at:currlv
#         "Unexpected end of (sub)proof at level %d before QED step\n%!"
#             currlv.core ;
#       Errors.set currlv
#         ("Unexpected end of (sub)proof at level "
#          ^ (string_of_int currlv.core) ^ " before QED step\n");
#       failwith "Proof.Parser"


# and to_step currlv st ps = match st.core with
def to_step(currlv, st, ps):
    #   | PreQed ->
    if isinstance(st, tla_ast.PreQed):
        #       let (p, ps) = to_proof (currlv + 1 @@ st) ps in
        p, ps = to_proof(currlv + 1, ps)
        #       (QED p, ps)
        return (QED(p), ps)
    #   | PreHide use ->
    elif isinstance(st, tla_ast.PreHide):
        use = st.usable
        #       (STEP (Hide use @@ st), ps)
        hide = tla_ast.Hide(use)
        return (STEP(hide), ps)
    #   | PreUse (supp, onl, use, meth) ->
    elif isinstance(st, tla_ast.PreUse):
        supp = st.supp
        only = st.only
        usable = st.usable
        meth = st.method
        #       let u = Use (use, onl = Only) @@ st in
        use = tla_ast.Use(usable, isinstance(only, tla_ast.Only))
        #       (STEP (annotate supp meth u), ps)
        annotate(supp, meth, use)
        return (STEP(use), ps)
    #   | PreDefine dfs ->
    elif isinstance(st, tla_ast.PreDefine):
        dfs = st.definitions
        #       (STEP (Define dfs @@ st), ps)
        define = tla_ast.Define(dfs)
        return (STEP(define), ps)
    #   | PreHave (supp, e, meth) ->
    elif isinstance(st, tla_ast.PreHave):
        supp = st.supp
        e = st.expr
        meth = st.method
        #       let h = Have e @@ st in
        have = tla_ast.Have(e)
        #       (STEP (annotate supp meth h), ps)
        annotate(supp, meth, have)
        return (STEP(have), ps)
    #   | PreTake (supp, bs, meth) ->
    elif isinstance(st, tla_ast.PreTake):
        supp = st.supp
        bs = st.bounds
        meth = st.method
        #       let t = Take bs @@ st in
        take = tla_ast.Take(bs)
        #       (STEP (annotate supp meth t), ps)
        annotate(supp, meth, take)
        return (STEP(take), ps)
    #   | PreWitness (supp, es, meth) ->
    elif isinstance(st, tla_ast.PreWitness):
        supp = st.supp
        es = st.exprs
        meth = st.method
        #       let w = Witness es @@ st in
        witness = tla_ast.Witness(es)
        #       (STEP (annotate supp meth w), ps)
        annotate(supp, meth, witness)
        return (STEP(witness), ps)
    #   | PreAssert sq ->
    elif isinstance(st, tla_ast.PreAssert):
        sq = st.sequent
        #       let (p, ps) = to_proof (currlv + 1 @@ st) ps in
        p, ps = to_proof(currlv + 1, ps)
        #       let st = enlarge_loc st p in
        enlarge_loc(st, p)
        #       (STEP (Assert (sq, p) @@ st), ps)
        assert_ = tla_ast.Assert(sq, p)
        return (STEP(assert_), ps)
    #   | PreSuffices sq ->
    elif isinstance(st, tla_ast.PreSuffices):
        sq = st.sequent
        #       let (p, ps) = to_proof (currlv + 1 @@ st) ps in
        p, ps = to_proof(currlv + 1, ps)
        #       let st = enlarge_loc st p in
        enlarge_loc(st, p)
        #       (STEP (Suffices (sq, p) @@ st), ps)
        suffices = tla_ast.Suffices(sq, p)
        return (STEP(suffices), ps)
    #   | PreCase e ->
    elif isinstance(st, tla_ast.PreCase):
        e = st.expr
        #       let (p, ps) = to_proof (currlv + 1 @@ st) ps in
        p, ps = to_proof(currlv + 1, ps)
        #       let st = enlarge_loc st p in
        enlarge_loc(st, p)
        #       (STEP (Pcase (e, p) @@ st), ps)
        pcase = tla_ast.Pcase(e, p)
        return (STEP(pcase), ps)
    #   | PrePick (bs, e) ->
    elif isinstance(st, tla_ast.PrePick):
        bs = st.bounds
        e = st.expr
        #       let (p, ps) = to_proof (currlv + 1 @@ st) ps in
        p, ps = to_proof(currlv + 1, ps)
        #       let st = enlarge_loc st p in
        enlarge_loc(st, p)
        #       (STEP (Pick (bs, e, p) @@ st), ps)
        pick = tla_ast.Pick(bs, e, p)
        return (STEP(pick), ps)
    else:
        raise TypeError(st)


# let toplevel ps =
#   let ps = match ps with
#     | [] -> failwith "toplevel"
#     | p :: ps ->
#         let pc = match p.core with
#           | PreStep (_, pn, pstp) ->
#               PreStep (true, pn, pstp)
#           | _ -> p.core
#         in { p with core = pc } :: ps
#   in
#   match to_proof (0 @@ (List.hd ps)) ps with
#     | (p, []) -> p
#     | (_, p :: _) ->
#         Errors.set p "extra step(s) after finished proof" ;
#         Util.eprintf ~at:p "extra step(s) after finished proof" ;
#         failwith "Proof.Parser.toplevel"
def toplevel(ps):
    assert ps, ps
    p = ps[0]
    if isinstance(p, tla_ast.PreStep):
        p.boolean = True
    tp = to_proof(0, ps)
    p, lst = tp
    assert not lst, lst
    return p


# module Parser = struct
#   open Expr.Parser
#   open Tla_parser.P
#   open Tla_parser


def method_prs_read_method():
    while True:
        yield use(ep.read_new_method())


#   let read_method = optional (use Method_prs.read_method)
def read_method():
    # TODO: method parser
    while True:
        yield optional(use(method_prs_read_method()))


#   let suppress = lazy begin
#     choice [
#       pragma (punct "_" <|> ident "suppress") <!> Suppress ;
#       succeed Emit ;
#     ]
#   end
def suppress():
    while True:
        yield choice(
            [
                intf.pragma(punct("_") << or_ >> intf.ident("suppress"))
                << bang
                >> tla_ast.Suppress(),
                succeed(tla_ast.Emit()),
            ]
        )


#   let preno =
#     scan begin
#       function
#         | Token.ST (sn, sl, nd) -> Some begin
#             match sn with
#               | `Star -> Star sl
#               | `Plus -> Plus sl
#               | `Num n -> Num (n, sl)
#           end
#         | _ ->
#             None
#     end
def preno():
    def f(form):
        if isinstance(form, tokens.ST):
            step_name = form.kind
            step_label = form.string
            # ndots = form.i
            if isinstance(step_name, tokens.StepStar):
                return tla_ast.StepStar(step_label)
            elif isinstance(step_name, tokens.StepPlus):
                return tla_ast.StepPlus(step_label)
            elif isinstance(step_name, tokens.StepNum):
                return tla_ast.StepNum(step_name.value, step_label)
            else:
                raise TypeError(step_name)
        else:
            return None

    return intf.scan(f)


#   let only =
#     choice [ kwd "ONLY" <!> Only ;
#              succeed Default ]
def only():
    while True:
        yield choice(
            [kwd("ONLY") << bang >> tla_ast.Only(), succeed(tla_ast.Default())]
        )


#   let proof_kwd =
#     choice [ kwd "PROOF" <!> true ;
#              succeed false ]
def proof_kwd():
    while True:
        yield choice([kwd("PROOF") << bang >> True, succeed(False)])


#   let sequent = lazy begin
#     choice [
#       use (Expr.Parser.sequent false);
#       use (expr false)
#       <$> (fun e -> { context = Deque.empty ; active = e })
#     ]
#   end
def sequent():
    while True:
        yield choice(
            [
                use(ep.sequent(False)),
                use(ep.expr(False)) << apply >> (lambda e: tla_ast.Sequent(list(), e)),
            ]
        )


#   let rec preproof = lazy begin
#     proof_kwd >>= fun pk ->
#       choice [
#         use suppress >>= begin fun supp ->
#           choice [
#             locate (kwd "BY")
#               <**> only
#               <**> use usebody
#               <*> read_method
#             <$> (fun (((by, onl), use), meth) ->
#                   PreBy (supp, onl, use, meth) @@ by) ;
#
#             locate begin
#               kwd "OBVIOUS" >>> read_method
#               <$> (fun meth -> PreObvious (supp, meth))
#             end ;
#           ]
#         end ;
#
#         locate (kwd "OMITTED" <!> (PreOmitted Explicit)) ;
#
#         locate begin
#           preno <**> use prestep
#           <$> (fun (pn, stp) -> PreStep (pk, pn, stp))
#         end ;
#       ]
#   end
def preproof():
    while True:
        yield (
            proof_kwd()
            << shift_eq
            >> (
                lambda pk: choice(
                    [
                        use(suppress())
                        << shift_eq
                        >> (
                            lambda supp: choice(
                                [
                                    intf.locate(kwd("BY"))
                                    << times2
                                    >> only()
                                    << times2
                                    >> use(usebody())
                                    << times
                                    >> read_method()
                                    << apply
                                    >> (
                                        lambda args: tla_ast.PreBy(
                                            supp, args[0][0][1], args[0][1], args[1]
                                        )
                                    ),
                                    intf.locate(
                                        kwd("OBVIOUS")
                                        << second
                                        >> read_method()
                                        << apply
                                        >> (lambda meth: tla_ast.PreObvious(supp, meth))
                                    ),
                                ]
                            )
                        ),
                        # locate (kwd "OMITTED" <!> (PreOmitted Explicit)) ;
                        intf.locate(
                            kwd("OMITTED")
                            << bang
                            >> tla_ast.PreOmitted(tla_ast.Explicit())
                        ),
                        #  locate begin
                        #           preno <**> use prestep
                        #           <$> (fun (pn, stp) ->
                        #                   PreStep (pk, pn, stp))
                        #         end ;
                        intf.locate(
                            preno()
                            << times2
                            >> use(prestep())
                            << apply
                            >> (
                                lambda pn_stp: tla_ast.PreStep(pk, pn_stp[0], pn_stp[1])
                            )
                        ),
                    ]
                )
            )
        )


#   and prestep = lazy begin
def prestep():
    while True:
        yield choice(
            [
                #     choice [
                #       kwd "QED" <!> PreQed ;
                kwd("QED") << bang >> tla_ast.PreQed(),
                #
                #       kwd "HIDE"
                #       >*> use usebody
                #       <$> (fun use -> PreHide use) ;
                kwd("HIDE")
                << second_commit
                >> use(usebody())
                << apply
                >> (lambda use: tla_ast.PreHide(use)),
                #
                #       kwd "SUFFICES"
                #       >*> use sequent
                #       <$> (fun sq -> PreSuffices sq) ;
                kwd("SUFFICES")
                << second_commit
                >> use(sequent())
                << apply
                >> (lambda sq: tla_ast.PreSuffices(sq)),
                #
                #       kwd "CASE"
                #       >*> use (expr false)
                #       <$> (fun e -> PreCase e) ;
                kwd("CASE")
                << second_commit
                >> use(ep.expr(False))
                << apply
                >> (lambda e: tla_ast.PreCase(e)),
                #
                #       kwd "PICK"
                #       >*> use (bounds false)
                #       <**> (punct ":"
                #             >>> use (expr false))
                #       <$> (fun (bs, e) -> PrePick (bs, e)) ;
                kwd("PICK")
                << second_commit
                >> use(ep.bounds(False))
                << times2
                >> (punct(":") << second >> use(ep.expr(False)))
                << apply
                >> (lambda bs_e: tla_ast.PrePick(bs_e[0], bs_e[1])),
                #
                #       use suppress >>= begin fun supp ->
                use(suppress())
                << shift_eq
                >> (
                    lambda supp: choice(
                        [
                            #         choice [
                            #           kwd "USE"
                            #           >*> only
                            #           <*> use usebody
                            #           <*> read_method
                            #           <$> (fun ((onl, use), meth) ->
                            #                   PreUse (supp, onl, use, meth)) ;
                            kwd("USE")
                            << second_commit
                            >> only()
                            << times
                            >> use(usebody())
                            << times
                            >> read_method()
                            << apply
                            >> (
                                lambda args: tla_ast.PreUse(
                                    supp, args[0][0], args[0][1], args[1]
                                )
                            ),
                            #
                            #           kwd "HAVE"
                            #           >*> use (expr false)
                            #           <*> read_method
                            #           <$> (fun (e, meth) -> PreHave (supp, e, meth)) ;
                            kwd("HAVE")
                            << second_commit
                            >> use(ep.expr(False))
                            << times
                            >> read_method()
                            << apply
                            >> (
                                lambda e_meth: tla_ast.PreHave(
                                    supp, e_meth[0], e_meth[1]
                                )
                            ),
                            #
                            #           kwd "TAKE"
                            #           >*> use (bounds false)
                            #           <*> read_method
                            #           <$> (fun (bs, meth) -> PreTake (supp, bs, meth)) ;
                            kwd("TAKE")
                            << second_commit
                            >> use(ep.bounds(False))
                            << times
                            >> read_method()
                            << apply
                            >> (
                                lambda bs_meth: tla_ast.PreTake(
                                    supp, bs_meth[0], bs_meth[1]
                                )
                            ),
                            #
                            #           kwd "WITNESS"
                            #           >*> sep1 (punct ",") (use (expr false))
                            #           <*> read_method
                            #           <$> (fun (es, meth) -> PreWitness (supp, es, meth)) ;
                            kwd("WITNESS")
                            << second_commit
                            >> sep1(punct(","), use(ep.expr(False)))
                            << times
                            >> read_method()
                            << apply
                            >> (
                                lambda es_meth: tla_ast.PreWitness(
                                    supp, es_meth[0], es_meth[1]
                                )
                            )
                            #         ]
                            #       end ;
                        ]
                    )
                ),
                #
                #       attempt (optional (kwd "DEFINE") >>> star1 (use (defn false)))
                #       <$> (fun dfs -> PreDefine dfs) ;
                attempt(optional(kwd("DEFINE")) << second >> star1(use(ep.defn(False))))
                << apply
                >> (lambda defns: tla_ast.PreDefine(defns)),
                #
                #       use sequent <$> (fun sq -> PreAssert sq) ;
                use(sequent()) << apply >> (lambda sq: tla_ast.PreAssert(sq))
                #     ]
            ]
        )


#   end
#
#   (* In a usebody, a step name has special meaning, so we strip the
#      Bang and let it be the underlying Opaque identifier, which will
#      be bound to the assumptions of the corresponding step.  Only
#      step names can be represented by a Bang with an empty list of
#      selectors.
#      See the "operator" case at the end of function expr_or_op
#      in file e_parser.ml.
#   *)
#   and filter_usebody_fact f =
#     match f.core with
#     | Bang ({core = Opaque v} as e, []) when v.[0] = '<' -> e
#     | _ -> f
def filter_usebody_fact(f):
    if (
        isinstance(f, tla_ast.Bang)
        and isinstance(f.expr, tla_ast.Opaque)
        and f.expr.name.startswith("<")
    ):
        return f.expr
    else:
        return f


#   and usebody = lazy begin
def usebody():
    #     let defs =
    #       (kwd "DEF" <|> kwd "DEFS")
    #       >*> sep1 (punct ",") (use definable)
    defns = (
        (kwd("DEF") << or_ >> kwd("DEFS"))
        << second_commit
        >> sep1(punct(","), use(definable()))
    )
    #     in
    #     sep (punct ",") (use (expr false)) >>= function
    #       | [] ->
    #           defs <$> (fun ds -> { facts = [] ; defs = ds })
    #       | fs ->
    #           optional defs <$> begin function
    #             | None -> {
    #                   facts = List.map filter_usebody_fact fs ;
    #                   defs = [] }
    #             | Some ds -> {
    #                   facts = List.map filter_usebody_fact fs ;
    #                   defs = ds }
    #           end

    def apply_usebody(fs, ds):
        if ds is None:
            return dict(facts=[filter_usebody_fact(f) for f in fs], defs=list())
        else:
            return dict(facts=[filter_usebody_fact(f) for f in fs], defs=ds)

    def shift_usebody(fs):
        if fs:
            return optional(defns) << apply >> functools.partial(apply_usebody, fs)
        else:
            return defns << apply >> (lambda ds: dict(facts=list(), defs=ds))

    while True:
        yield sep(punct(","), use(ep.expr(False))) << shift_eq >> shift_usebody


#   end
#
#   and definable = lazy begin
#     locate begin
#       sep1 (punct "!") (choice [ anyop ; anyident ])
#       <$> (fun ids -> Dvar (String.concat "!" ids))
#     end
#   end
def definable():
    while True:
        yield intf.locate(
            sep1(intf.punct("!"), choice([intf.anyop(), intf.anyident()]))
            << apply
            >> (lambda ids: tla_ast.Dvar("!".join(ids)))
        )


#   let rec preproofs = lazy begin
#     choice [
#       use preproof <**> use preproofs
#       <$> (fun (p, ps) -> p :: ps) ;
#
#       succeed [] ;
#     ]
#   end
#
#   let proof = lazy begin
#     choice [
#       use preproof <**> use preproofs
#       <$> (fun (p, ps) -> p :: ps) ;
#
#       locate (succeed (PreOmitted Implicit))
#       <$> (fun pp -> [pp])
#     ] <$> toplevel
#   end
def proof():
    while True:
        yield choice(
            [
                star1(use(preproof())),
                intf.locate(succeed(tla_ast.PreOmitted(tla_ast.Implicit())))
                << apply
                >> (lambda pp: [pp]),
            ]
        ) << apply >> toplevel


#
# end
#
# let usebody = Parser.usebody
# let proof = Parser.proof
# let suppress = Parser.suppress
