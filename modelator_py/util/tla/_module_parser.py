"""Parser for modules."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/module/m_parser.ml>
#
from . import _expr_parser as ep
from . import _proof_parser as pfp
from . import _tla_combinators as intf  # avoid shadowing by `_combinators`
from . import tokens
from ._combinators import (
    apply,
    bang,
    choice,
    choice_iter,
    enabled,
    first,
    optional,
    or_,
    second,
    second_commit,
    sep1,
    shift_eq,
    star,
    times,
    times2,
    use,
)
from ._tla_combinators import kwd, locate, punct
from .ast import Nodes as nodes


#
# open Ext
# open Property
#
# open Tla_parser.P
# open Tla_parser
#
# open Expr.T
# open Expr.Parser
#
# open M_t
#
# let with_meth e meth = match meth with
#   | Some meth -> { e with core = With (e, meth) }
#   | None -> e
def with_meth(e, meth):
    if meth is None:
        return e
    else:
        return nodes.With(e, meth)


# let rec modunit = lazy begin
def modunit():
    def apply_def(local):
        # let ex = if Option.is_some l then Local else Export in
        if local is None:
            ex = nodes.Export()
        else:
            ex = nodes.Local()

        def choices():
            # NOTE: The order of choices was INSTANCE, def
            # changed for efficiency reasons
            #
            # use (defn false)
            yield use(
                ep.defn(False)
                # <$> (fun df -> [ Definition (df, User, Hidden, ex) ]) ;
            ) << apply >> (
                lambda df: [nodes.Definition(df, nodes.User(), nodes.Hidden(), ex)]
            )
            # use (instance false)
            yield use(
                ep.instance(False)
                # <$> (fun inst -> [ Anoninst (inst, ex) ]) ;
            ) << apply >> (lambda inst: [nodes.AnonymousInstance(inst, ex)])

        return choice_iter(choices)

    #     <$> (fun ((supp, uh), use) -> match uh with
    #            | "USE" -> [Mutate (`Use (supp = Proof.Parser.Suppress), use)]
    #            | _ -> [ Mutate (`Hide, use) ]) ;
    def apply_use_hide(args):
        ((supp, uh), use) = args
        if uh == "USE":
            return [nodes.Mutate(nodes.ModuleUse(nodes.Suppress()), use)]
        else:
            return [nodes.Mutate(nodes.ModuleHide(), use)]

    # <$> (fun ((nm, e), meth) -> [ Axiom (nm, with_meth e meth) ]) ;
    def apply_axiom(args):
        ((nm, e), meth) = args
        return [nodes.Axiom(nm, with_meth(e, meth))]

    #     <$> (fun (((nm, bod), meth), prf) ->
    #            [ Theorem (nm, {
    #                   bod with active = with_meth bod.active meth },
    #               0, prf, prf, empty_summary) ])
    def apply_theorem_proof(args):
        (((name, body), meth), prf) = args
        ctx = body.context
        goal = body.goal
        goal_ = with_meth(goal, meth)
        body_ = nodes.Sequent(ctx, goal_)
        return [nodes.Theorem(name, body_, prf)]

    def choices():
        #   choice [
        #     choice [
        #       (kwd "CONSTANT" <|> kwd "CONSTANTS") >*>
        #         sep1 (punct ",") (use opdecl)
        #       <$> (fun cs -> [ Constants cs ]) ;
        #
        #       (kwd "RECURSIVE") >*>
        #         sep1 (punct ",") (use opdecl)
        #       <$> (fun cs -> [ Recursives cs ]) ;
        #
        #       (kwd "VARIABLE" <|> kwd "VARIABLES") >*>
        #         sep1 (punct ",") (locate anyident)
        #       <$> (fun vs -> [ Variables vs ]) ;
        #     ] ;
        # variable and constant declarations, and recursive operators
        def f():
            return choice(
                [
                    # ['CONSTANT' | 'CONSTANTS'] opdecl (',' opdecl)*
                    kwd("CONSTANT")
                    << or_
                    >> kwd("CONSTANTS")
                    << second_commit
                    >> sep1(punct(","), use(ep.opdecl()))
                    << apply
                    >> (lambda cs: [nodes.Constants(cs)]),
                    # 'RECURSIVE' opdecl (',' opdecl)*
                    kwd("RECURSIVE")
                    << second_commit
                    >> sep1(punct(","), use(ep.opdecl()))
                    << apply
                    >> (lambda cs: [nodes.Recursives(cs)]),
                    # ['VARIABLE' | 'VARIABLES'] anyident (',' anyident)*
                    kwd("VARIABLE")
                    << or_
                    >> kwd("VARIABLES")
                    << second_commit
                    >> sep1(punct(","), locate(intf.anyident()))
                    << apply
                    >> (lambda vs: [nodes.Variables(vs)]),
                ]
            )

        yield ((tokens.KWD,), f)

        #     optional (kwd "LOCAL") >>= begin fun l ->
        #       let ex = if Option.is_some l then Local else Export in
        #         choice [
        #           use (instance false)
        #           <$> (fun inst -> [ Anoninst (inst, ex) ]) ;
        #
        #           use (defn false)
        #           <$> (fun df -> [ Definition (df, User, Hidden, ex) ]) ;
        #         ]
        #     end ;
        yield optional(kwd("LOCAL")) << shift_eq >> apply_def

        #     use Proof.Parser.suppress
        #     <*> (kwd "USE" <|> kwd "HIDE")
        #     <**> use Proof.Parser.usebody
        #     <$> (fun ((supp, uh), use) -> match uh with
        #            | "USE" -> [ Mutate (`Use (supp = Proof.Parser.Suppress), use) ]
        #            | _ -> [ Mutate (`Hide, use) ]) ;
        def f():
            return (
                use(pfp.suppress())
                << times
                >> (kwd("USE") << or_ >> kwd("HIDE"))
                << times2
                >> pfp.usebody()
                << apply
                >> apply_use_hide
            )

        yield (
            (
                tokens.KWD("USE"),
                tokens.KWD("HIDE"),
                tokens.PUNCT("_"),
                tokens.ID("suppress"),
            ),
            f,
        )

        #     (kwd "AXIOM" <|> kwd "ASSUME" <|> kwd "ASSUMPTION") >*>
        #       optional (locate anyident <<< punct "==") <**> use (expr false)
        #     <*> optional (use Method_prs.read_method)
        #     <$> (fun ((nm, e), meth) -> [ Axiom (nm, with_meth e meth) ]) ;
        def f():
            # RULE: ('AXIOM' | 'ASSUME' | 'ASSUMPTION')
            #       [anyident '=='] expr [read_method]
            return (
                (kwd("AXIOM") << or_ >> kwd("ASSUME") << or_ >> kwd("ASSUMPTION"))
                << second_commit
                >> optional(
                    intf.locate(
                        intf.anyident()
                        << first
                        >> punct("==")
                        << times2
                        >> use(ep.expr(False))
                    )
                )
                << times
                >> optional(use(pfp.read_method()))
                << apply
                >> apply_axiom
            )

        yield (
            (
                tokens.KWD("AXIOM"),
                tokens.KWD("ASSUME"),
                tokens.KWD("ASSUMPTION"),
            ),
            f,
        )

        #     (kwd "THEOREM" <|> kwd "PROPOSITION" <|>
        #      kwd "COROLLARY" <|> kwd "LEMMA") >*>
        #       optional (locate anyident <<< punct "==")
        #     <*> choice [ use (sequent false) ;
        #                  use (expr false)
        #                  <$> (fun e -> { context = Deque.empty ; active = e }) ]
        #     <*> optional (use Method_prs.read_method)
        #     <*> use Proof.Parser.proof
        #     <$> (fun (((nm, bod), meth), prf) ->
        #            [ Theorem (nm, {
        #                   bod with active = with_meth bod.active meth },
        #               0, prf, prf, empty_summary) ]) ;
        def f():
            return (
                (
                    kwd("THEOREM")
                    << or_
                    >> kwd("PROPOSITION")
                    << or_
                    >> kwd("COROLLARY")
                    << or_
                    >> kwd("LEMMA")
                )
                << second_commit
                >> optional(intf.locate(intf.anyident() << first >> punct("==")))
                << times
                >> choice(
                    [
                        use(ep.sequent(False)),
                        use(ep.expr(False))
                        << apply
                        >> (lambda e: nodes.Sequent(list(), e)),
                    ]
                )
                << times
                >> optional(use(pfp.method_prs_read_method()))
                << times
                >> use(pfp.proof())
                << apply
                >> apply_theorem_proof
            )

        yield (
            (
                tokens.KWD("THEOREM"),
                tokens.KWD("PROPOSITION"),
                tokens.KWD("COROLLARY"),
                tokens.KWD("LEMMA"),
            ),
            f,
        )
        #
        #     enabled (punct "----" <*> kwd "MODULE")
        #       >*> use parse <$> (fun m -> [ Submod m ]) ;
        yield (
            enabled(punct("----") << times >> kwd("MODULE"))
            << second_commit
            >> use(parse())
            << apply
            >> (lambda mod: [nodes.Submodule(mod)])
        )
        #
        #     punct "----" <!> [] ;
        yield intf.punct("----") << bang >> list()

    #   ]
    while True:
        yield choice_iter(choices)


# end
#
# and flat_locate p =
#   locate p <$> fun xsw ->
#     List.map (fun x -> { core = x ; props = xsw.props }) xsw.core


# and modunits = lazy begin
#   choice [
#     flat_locate (use modunit) <::> use modunits ;
#     succeed [] ;
#   ]
# end
def modunits():
    # while True: yield choice([
    #     use(modunit()) <<cons>> use(modunits()),
    #     succeed(list())
    # ])
    while True:
        yield star(use(modunit()))


# and parse = lazy begin
#   locate (use parse_)
# end
def parse():
    while True:
        yield intf.locate(use(parse_()))


# (* submodules --- See above *)
# and parse_ = lazy begin
#   (punct "----" >*> kwd "MODULE" >*> locate anyname <<< punct "----")
#   <*> optional (kwd "EXTENDS" >>> sep1 (punct ",") (locate anyident))
#   <**> use modunits <<< punct "===="
#   <$> begin fun ((nm, exs), mus) ->
#     let extends = Option.default [] exs in
#     { name = nm
#     ; extendees = extends
#     ; instancees = []
#     ; defdepth = 0
#     ; important = true
#     ; body = List.concat mus
#     ; stage = Parsed }
#   end
def parse_():
    def apply_module(nm_exs_mus):
        (name, extends), modunits = nm_exs_mus
        extends = list() if extends is None else extends
        return nodes.Module(
            name=name,
            extendees=extends,
            instancees=list(),
            body=[i for j in modunits for i in j],
        )

    while True:
        yield (
            intf.punct("----")
            << second_commit
            >> intf.kwd("MODULE")
            << second_commit
            >> intf.locate(intf.anyname())
            << first
            >> intf.punct("----")
            << times
            >> optional(
                intf.kwd("EXTENDS")
                << second
                >> sep1(intf.punct(","), intf.locate(intf.anyident()))
            )
            << times2
            >> use(modunits())
            << first
            >> intf.punct("====")
            << apply
            >> apply_module
        )


# end
