"""Table of operators."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/optable.ml>
#

from .ast import Nodes as nodes

# open Builtin


# type fixity =
#   | Nonfix
#   | Prefix | Postfix
#   | Infix of assoc
class Fixity:
    pass


class Nonfix(Fixity):
    pass


class Prefix(Fixity):
    pass


class Postfix(Fixity):
    pass


class Infix(Fixity):
    def __init__(self, assoc):
        self.assoc = assoc


# and assoc =
#   | Left | Non | Right
class Assoc:
    pass


class Left(Assoc):
    pass


class Right(Assoc):
    pass


class Non(Assoc):
    pass


# and dom =
#     (* primitive operators *)
#   | Logic | Sets | Modal
#     (* user-definable operators *)
#   | User
dom = {"Logic", "Sets", "Modal", "User"}


# type prec = int * int
class Prec:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# let withdef (name, prec, fix, als, defn) = (
#              name, prec, fix, als, Some defn);;
def withdef(tuple_):
    name, prec, fix, als, defn = tuple_
    return (name, prec, fix, als, defn)


# let tlaops = [
#   Logic,
#   List.map withdef [
#     '=>',            ( 1, 1), Infix(Non()),   [],                   Implies ;
#     '<=>',           ( 2, 2), Infix(Non()),   [ '\\equiv' ],        Equiv ;
#     '/\\',           ( 3, 3), Infix(Left()),  [ '\\land' ],         Conj ;
#     '\\/',           ( 3, 3), Infix(Left()),  [ '\\lor' ],          Disj ;
#     '~',             ( 4, 4),   Prefix,      [ '\\neg' ; '\\lnot' ], Neg ;
#     '=',             ( 5, 5), Infix(Non()),   [],                   Eq ;
#     '#',             ( 5, 5), Infix(Non()),   [ '/=' ],             Neq ;
#   ] ;
#   Sets,
#   List.map withdef [
#     'SUBSET',        ( 8, 8),   Prefix,      [],                   SUBSET ;
#     'UNION',         ( 8, 8),   Prefix,      [],                   UNION ;
#     'DOMAIN',        ( 9, 9),   Prefix,      [],                   DOMAIN ;
#     '\\subseteq',    ( 5, 5), Infix(Non()),   [],                   Subseteq ;
#     '\\in',          ( 5, 5), Infix(Non()),   [],                   Mem ;
#     '\\notin',       ( 5, 5), Infix(Non()),   [],                   Notmem ;
#     '\\',            ( 8, 8), Infix(Non()),   [],                   Setminus ;
#     '\\cap',         ( 8, 8), Infix(Left()),  [ '\\intersect' ],    Cap ;
#     '\\cup',         ( 8, 8), Infix(Left()),  [ '\\union' ],        Cup ;
#   ] ;
#   Sets,
#   [ '\\X',           (10,13),   Prefix,      [ '\\times' ],        None ] ;
#   Modal,
#   List.map withdef [
#     ''',             (15,15),   Postfix,     [],                   Prime ;
#     '~>',            ( 2, 2), Infix(Non()),   [ '\\leadsto' ],      Leadsto ;
#     'ENABLED',       ( 4,15),   Prefix,      [],                   ENABLED ;
#     'UNCHANGED',     ( 4,15),   Prefix,      [],                   UNCHANGED ;
#     '\\cdot',        ( 5,14), Infix(Left()),  [],                   Cdot ;
#     '-+->',          ( 2, 2), Infix(Non()),   [],                   Actplus ;
#     '[]',            ( 4,15),   Prefix,      [],                   Box true ;
#     '<>',            ( 4,15),   Prefix,      [],                   Diamond ;
#   ] ;
#   User,
#   List.map (fun (name, prec, fix, als) -> (name, prec, fix, als, None)) [
#     '^',             (14,14), Infix(Non()),   [] ;
#     '/',             (13,13), Infix(Non()),   [] ;
#     '*',             (13,13), Infix(Left()),  [] ;
#     '-.',            (12,12),   Prefix,      [ '-' ] ;
#     '-',             (11,11), Infix(Left()),  [] ;
#     '+',             (10,10), Infix(Left()),  [] ;
#     '^+',            (15,15),   Postfix,     [] ;
#     '^*',            (15,15),   Postfix,     [] ;
#     '^#',            (15,15),   Postfix,     [] ;
#     '<',             ( 5, 5), Infix(Non()),   [] ;
#     '=<',            ( 5, 5), Infix(Non()),   [ '<=' ; '\\leq' ] ;
#     '>',             ( 5, 5), Infix(Non()),   [] ;
#     '>=',            ( 5, 5), Infix(Non()),   [ '\\geq' ] ;
#     '...',           ( 9, 9), Infix(Non()),   [] ;
#     '..',            ( 9, 9), Infix(Non()),   [] ;
#     '|',             (10,11), Infix(Left()),  [] ;
#     '||',            (10,11), Infix(Left()),  [] ;
#     '&&',            (13,13), Infix(Left()),  [] ;
#     '&',             (13,13), Infix(Left()),  [] ;
#     '$$',            ( 9,13), Infix(Left()),  [] ;
#     '$',             ( 9,13), Infix(Left()),  [] ;
#     '??',            ( 9,13), Infix(Left()),  [] ;
#     '%%',            (10,11), Infix(Left()),  [] ;
#     '%',             (10,11), Infix(Non()),  [ '\\mod' ] ;
#     '##',            ( 9,13), Infix(Left()),  [] ;
#     '++',            (10,10), Infix(Left()),  [] ;
#     '--',            (11,11), Infix(Left()),  [] ;
#     '**',            (13,13), Infix(Left()),  [] ;
#     '//',            (13,13), Infix(Non()),   [] ;
#     '^^',            (14,14), Infix(Non()),   [] ;
#     '@@',            ( 6, 6), Infix(Left()),  [] ;
#     '!!',            ( 9,13), Infix(Non()),   [] ;
#     '|-',            ( 5, 5), Infix(Non()),   [] ;
#     '|=',            ( 5, 5), Infix(Non()),   [] ;
#     '-|',            ( 5, 5), Infix(Non()),   [] ;
#     '=|',            ( 5, 5), Infix(Non()),   [] ;
#     '<:',            ( 7, 7), Infix(Non()),   [] ;
#     ':>',            ( 7, 7), Infix(Non()),   [] ;
#     ':=',            ( 5, 5), Infix(Non()),   [] ;
#     '::=',           ( 5, 5), Infix(Non()),   [] ;
#     '(+)',           (10,10), Infix(Left()),  [ '\\oplus' ] ;
#     '(-)',           (11,11), Infix(Left()),  [ '\\ominus' ] ;
#     '(.)',           (13,13), Infix(Left()),  [ '\\odot' ] ;
#     '(/)',           (13,13), Infix(Non()),   [ '\\oslash' ] ;
#     '(\\X)',         (13,13), Infix(Left()),  [ '\\otimes' ] ;
#     '\\uplus',       ( 9,13), Infix(Left()),  [] ;
#     '\\sqcap',       ( 9,13), Infix(Left()),  [] ;
#     '\\sqcup',       ( 9,13), Infix(Left()),  [] ;
#     '\\div',         (13,13), Infix(Non()),   [] ;
#     '\\wr',          ( 9,14), Infix(Non()),   [] ;
#     '\\star',        (13,13), Infix(Left()),  [] ;
#     '\\o',           (13,13), Infix(Left()),  [ '\\circ' ] ;
#     '\\bigcirc',     (13,13), Infix(Left()),  [] ;
#     '\\bullet',      (13,13), Infix(Left()),  [] ;
#     '\\prec',        ( 5, 5), Infix(Non()),   [] ;
#     '\\succ',        ( 5, 5), Infix(Non()),   [] ;
#     '\\preceq',      ( 5, 5), Infix(Non()),   [] ;
#     '\\succeq',      ( 5, 5), Infix(Non()),   [] ;
#     '\\sim',         ( 5, 5), Infix(Non()),   [] ;
#     '\\simeq',       ( 5, 5), Infix(Non()),   [] ;
#     '\\ll',          ( 5, 5), Infix(Non()),   [] ;
#     '\\gg',          ( 5, 5), Infix(Non()),   [] ;
#     '\\asymp',       ( 5, 5), Infix(Non()),   [] ;
#     '\\subset',      ( 5, 5), Infix(Non()),   [] ;
#     '\\supset',      ( 5, 5), Infix(Non()),   [] ;
#     '\\supseteq',    ( 5, 5), Infix(Non()),   [] ;
#     '\\approx',      ( 5, 5), Infix(Non()),   [] ;
#     '\\cong',        ( 5, 5), Infix(Non()),   [] ;
#     '\\sqsubset',    ( 5, 5), Infix(Non()),   [] ;
#     '\\sqsubseteq',  ( 5, 5), Infix(Non()),   [] ;
#     '\\sqsupset',    ( 5, 5), Infix(Non()),   [] ;
#     '\\sqsupseteq',  ( 5, 5), Infix(Non()),   [] ;
#     '\\doteq',       ( 5, 5), Infix(Non()),   [] ;
#     '\\propto',      ( 5, 5), Infix(Non()),   [] ;
#   ] ;
# ]
def _generate_tlaops():
    tlaops = [
        (
            "Logic",
            [
                ("=>", (1, 1), Infix(Non()), list(), nodes.Implies()),
                ("<=>", (2, 2), Infix(Non()), ["\\equiv"], nodes.Equiv()),
                ("/\\", (3, 3), Infix(Left()), ["\\land"], nodes.Conj()),
                ("\\/", (3, 3), Infix(Left()), ["\\lor"], nodes.Disj()),
                ("~", (4, 4), Prefix(), ["\\neg", "\\lnot"], nodes.Neg()),
                ("=", (5, 5), Infix(Non()), list(), nodes.Eq()),
                ("#", (5, 5), Infix(Non()), ["/="], nodes.Neq()),
            ],
        ),
        (
            "Sets",
            [
                ("SUBSET", (8, 8), Prefix(), list(), nodes.SUBSET()),
                ("UNION", (8, 8), Prefix(), list(), nodes.UNION()),
                ("DOMAIN", (9, 9), Prefix(), list(), nodes.DOMAIN()),
                ("\\subseteq", (5, 5), Infix(Non()), list(), nodes.Subseteq()),
                ("\\in", (5, 5), Infix(Non()), list(), nodes.Mem()),
                ("\\notin", (5, 5), Infix(Non()), [], nodes.Notmem()),
                ("\\", (8, 8), Infix(Non()), ["\\setminus"], nodes.Setminus()),
                ("\\cap", (8, 8), Infix(Left()), ["\\intersect"], nodes.Cap()),
                ("\\cup", (8, 8), Infix(Left()), ["\\union"], nodes.Cup()),
                ("\\X", (10, 13), Infix(Left()), ["\\times"], None),
            ],
        ),
        (
            "Modal",
            [
                ("'", (15, 15), Postfix(), list(), nodes.Prime()),
                ("~>", (2, 2), Infix(Non()), ["\\leadsto"], nodes.LeadsTo()),
                ("ENABLED", (4, 15), Prefix(), list(), nodes.ENABLED()),
                ("UNCHANGED", (4, 15), Prefix(), list(), nodes.UNCHANGED()),
                ("\\cdot", (5, 14), Infix(Left()), list(), nodes.Cdot()),
                ("-+->", (2, 2), Infix(Non()), list(), nodes.WhilePlus()),
                ("[]", (4, 15), Prefix(), list(), nodes.Box(True)),
                ("<>", (4, 15), Prefix(), list(), nodes.Diamond()),
            ],
        ),
        (
            "User",
            [
                (name, prec, fix, als, None)
                for name, prec, fix, als in [
                    ("^", (14, 14), Infix(Non()), list()),
                    ("/", (13, 13), Infix(Non()), list()),
                    ("*", (13, 13), Infix(Left()), list()),
                    ("-.", (12, 12), Prefix(), ["-"]),
                    ("-", (11, 11), Infix(Left()), list()),
                    ("+", (10, 10), Infix(Left()), list()),
                    ("^+", (15, 15), Postfix(), list()),
                    ("^*", (15, 15), Postfix(), list()),
                    ("^#", (15, 15), Postfix(), list()),
                    ("<", (5, 5), Infix(Non()), list()),
                    ("=<", (5, 5), Infix(Non()), ["<=", "\\leq"]),
                    (">", (5, 5), Infix(Non()), list()),
                    (">=", (5, 5), Infix(Non()), ["\\geq"]),
                    ("...", (9, 9), Infix(Non()), list()),
                    ("..", (9, 9), Infix(Non()), list()),
                    ("|", (10, 11), Infix(Left()), list()),
                    ("||", (10, 11), Infix(Left()), list()),
                    ("&&", (13, 13), Infix(Left()), list()),
                    ("&", (13, 13), Infix(Left()), list()),
                    ("$$", (9, 13), Infix(Left()), list()),
                    ("$", (9, 13), Infix(Left()), list()),
                    ("??", (9, 13), Infix(Left()), list()),
                    ("%%", (10, 11), Infix(Left()), list()),
                    ("%", (10, 11), Infix(Non()), ["\\mod"]),
                    ("##", (9, 13), Infix(Left()), list()),
                    ("++", (10, 10), Infix(Left()), list()),
                    ("--", (11, 11), Infix(Left()), list()),
                    ("**", (13, 13), Infix(Left()), list()),
                    ("//", (13, 13), Infix(Non()), list()),
                    ("^^", (14, 14), Infix(Non()), list()),
                    ("@@", (6, 6), Infix(Left()), list()),
                    ("!!", (9, 13), Infix(Non()), list()),
                    ("|-", (5, 5), Infix(Non()), list()),
                    ("|=", (5, 5), Infix(Non()), list()),
                    ("-|", (5, 5), Infix(Non()), list()),
                    ("=|", (5, 5), Infix(Non()), list()),
                    ("<:", (7, 7), Infix(Non()), list()),
                    (":>", (7, 7), Infix(Non()), list()),
                    (":=", (5, 5), Infix(Non()), list()),
                    ("::=", (5, 5), Infix(Non()), list()),
                    ("(+)", (10, 10), Infix(Left()), ["\\oplus"]),
                    ("(-)", (11, 11), Infix(Left()), ["\\ominus"]),
                    ("(.)", (13, 13), Infix(Left()), ["\\odot"]),
                    ("(/)", (13, 13), Infix(Non()), ["\\oslash"]),
                    ("(\\X)", (13, 13), Infix(Left()), ["\\otimes"]),
                    ("\\uplus", (9, 13), Infix(Left()), list()),
                    ("\\sqcap", (9, 13), Infix(Left()), list()),
                    ("\\sqcup", (9, 13), Infix(Left()), list()),
                    ("\\div", (13, 13), Infix(Non()), list()),
                    ("\\wr", (9, 14), Infix(Non()), list()),
                    ("\\star", (13, 13), Infix(Left()), list()),
                    ("\\o", (13, 13), Infix(Left()), ["\\circ"]),
                    ("\\bigcirc", (13, 13), Infix(Left()), list()),
                    ("\\bullet", (13, 13), Infix(Left()), list()),
                    ("\\prec", (5, 5), Infix(Non()), list()),
                    ("\\succ", (5, 5), Infix(Non()), list()),
                    ("\\preceq", (5, 5), Infix(Non()), list()),
                    ("\\succeq", (5, 5), Infix(Non()), list()),
                    ("\\sim", (5, 5), Infix(Non()), list()),
                    ("\\simeq", (5, 5), Infix(Non()), list()),
                    ("\\ll", (5, 5), Infix(Non()), list()),
                    ("\\gg", (5, 5), Infix(Non()), list()),
                    ("\\asymp", (5, 5), Infix(Non()), list()),
                    ("\\subset", (5, 5), Infix(Non()), list()),
                    ("\\supset", (5, 5), Infix(Non()), list()),
                    ("\\supseteq", (5, 5), Infix(Non()), list()),
                    ("\\approx", (5, 5), Infix(Non()), list()),
                    ("\\cong", (5, 5), Infix(Non()), list()),
                    ("\\sqsubset", (5, 5), Infix(Non()), list()),
                    ("\\sqsubseteq", (5, 5), Infix(Non()), list()),
                    ("\\sqsupset", (5, 5), Infix(Non()), list()),
                    ("\\sqsupseteq", (5, 5), Infix(Non()), list()),
                    ("\\doteq", (5, 5), Infix(Non()), list()),
                    ("\\propto", (5, 5), Infix(Non()), list()),
                ]
            ],
        ),
    ]
    return tlaops


# type tlaop = {
#   name   : string ;
#   prec   : prec ;
#   fix    : fixity ;
#   dom    : dom ;
#   defn   : Builtin.builtin option ;
# }
class TLAOP:
    def __init__(self, name, prec, fixity, dom, defn):
        self.name = name  # str
        self.prec = prec  # Prec
        self.fix = fixity  # Fixity
        self.dom = dom
        self.defn = defn

    def __repr__(self):
        return (
            f"TLAOP({self.name}, {self.prec}, " f"{self.fix}, {self.dom}, {self.defn})"
        )


# let optable =
#   let module H = Hashtbl in
#   let tab = H.create 109 in
#     List.iter begin
#       fun (dom, ops) ->
#         List.iter begin
#           fun (name, prec, fix, als, defn) ->
#             let op = { name = name ;
#                        prec = prec ;
#                        fix  = fix ;  dom  = dom  ;
#                        defn = defn }
#             in
#               H.add tab name op ;
#               List.iter (fun s -> H.add tab s op) als
#         end ops
#     end tlaops ;
#     tab
def _generate_optable():
    tlaops = _generate_tlaops()
    optable = dict()
    for dom, ops in tlaops:
        for name, prec, fixity, alternatives, defn in ops:
            op = TLAOP(name, prec, fixity, dom, defn)
            optable.setdefault(name, list())
            optable[name].append(op)
            for s in alternatives:
                optable.setdefault(s, list())
                optable[s].append(op)
    return optable


optable = _generate_optable()
# pprint.pprint(optable)


# let nonfix name defn =
#   { name = name ; prec = (-1, -1) ;
#     fix  = Nonfix ; dom = User ; defn = defn }
#
# let lookup name =
#   if Hashtbl.mem optable name then
#     Hashtbl.find optable name
#   else
#     nonfix name None
#
# (** Mapping from builtins to standard tlaops *)
# let standard_form b =
#   match b with
#   | TRUE          -> nonfix 'TRUE' (Some TRUE)
#   | FALSE         -> nonfix 'FALSE' (Some FALSE)
#   | Implies       -> lookup '=>'
#   | Equiv         -> lookup '<=>'
#   | Conj          -> lookup '/\\'
#   | Disj          -> lookup '\\/'
#   | Neg           -> lookup '~'
#   | Eq            -> lookup '='
#   | Neq           -> lookup '#'
#   | Divides       ->
#      {
#        name = '?|';
#        prec = (10, 11);
#        fix = Infix(Non());
#        dom = Logic;
#        defn = Some Divides;
#      }
#
#   | STRING        -> nonfix 'STRING' (Some STRING)
#   | BOOLEAN       -> nonfix 'BOOLEAN' (Some BOOLEAN)
#   | SUBSET        -> lookup 'SUBSET'
#   | UNION         -> lookup 'UNION'
#   | DOMAIN        -> lookup 'DOMAIN'
#   | Subseteq      -> lookup '\\subseteq'
#   | Mem           -> lookup '\\in'
#   | Notmem        -> lookup '\\notin'
#   | Setminus      -> lookup '\\'
#   | Cap           -> lookup '\\cap'
#   | Cup           -> lookup '\\cup'
#
#   | Prime         -> lookup '''
#   | StrongPrime   -> lookup '''
#   | Leadsto       -> lookup '~>'
#   | ENABLED       -> lookup 'ENABLED'
#   | UNCHANGED     -> lookup 'UNCHANGED'
#   | Cdot          -> lookup '\\cdot'
#   | Actplus       -> lookup '-+->'
#   | Box _         -> lookup '[]'
#   | Diamond       -> lookup '<>'
#
#   | Plus          -> { (lookup '+') with defn = Some Plus }
#   | Minus         -> { (lookup '-') with defn = Some Minus }
#   | Uminus        -> { (lookup '-.') with defn = Some Uminus ; name = '-' }
#   | Times         -> { (lookup '*') with defn = Some Times }
#   | Ratio         -> { (lookup '/') with defn = Some Ratio }
#   | Quotient      -> { (lookup '\\div') with defn = Some Quotient }
#   | Remainder     -> { (lookup '%') with defn = Some Remainder }
#   | Exp           -> { (lookup '^') with defn = Some Exp }
#   | Lteq          -> { (lookup '=<') with defn = Some Lteq }
#   | Lt            -> { (lookup '<') with defn = Some Lt }
#   | Gteq          -> { (lookup '>=') with defn = Some Gteq }
#   | Gt            -> { (lookup '>') with defn = Some Gt }
#   | Range         -> { (lookup '..') with defn = Some Range }
#   | Nat           -> nonfix 'Nat' (Some Nat)
#   | Int           -> nonfix 'Int' (Some Int)
#   | Real          -> nonfix 'Real' (Some Real)
#   | Infinity      -> nonfix 'Infinity' (Some Infinity)
#
#   | Seq           -> nonfix 'Seq' (Some Seq)
#   | Len           -> nonfix 'Len' (Some Len)
#   | BSeq          -> nonfix 'BSeq' (Some BSeq)
#   | Append        -> nonfix 'Append' (Some Append)
#   | Cat           -> { (lookup '\\o') with defn = Some Cat }
#   | Head          -> nonfix 'Head' (Some Head)
#   | Tail          -> nonfix 'Tail' (Some Tail)
#   | SubSeq        -> nonfix 'SubSeq' (Some SubSeq)
#   | SelectSeq     -> nonfix 'SelectSeq' (Some SelectSeq)
#
#   | OneArg        -> { (lookup ':>') with defn = Some OneArg }
#   | Extend        -> { (lookup '@@') with defn = Some Extend }
#   | Print         -> nonfix 'Print' (Some Print)
#   | PrintT        -> nonfix 'PrintT' (Some PrintT)
#   | Assert        -> nonfix 'Assert' (Some Assert)
#   | JavaTime      -> nonfix 'JavaTime' (Some JavaTime)
#   | TLCGet        -> nonfix 'TLCGet' (Some TLCGet)
#   | TLCSet        -> nonfix 'TLCSet' (Some TLCSet)
#   | Permutations  -> nonfix 'Permutations' (Some Permutations)
#   | SortSeq       -> nonfix 'SortSeq' (Some SortSeq)
#   | RandomElement -> nonfix 'RandomElement' (Some RandomElement)
#   | Any           -> nonfix 'Any' (Some Any)
#   | ToString      -> nonfix 'ToString' (Some ToString)
#
#   | Unprimable    -> nonfix 'Unprimable' None
#   | Irregular     -> nonfix 'Irregular' None
# ;;
