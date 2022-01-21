"""TLA+ abstract syntax tree."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the files:
#
# https://github.com/tlaplus/tlapm/blob/master/src/builtin.ml
# https://github.com/tlaplus/tlapm/blob/master/src/expr/e_t.ml
# https://github.com/tlaplus/tlapm/blob/master/src/module/m_t.ml
# https://github.com/tlaplus/tlapm/blob/master/src/proof/p_t.ml
# https://github.com/tlaplus/tlapm/blob/master/src/proof/p_parser.ml


class Nodes(object):
    """TLA+ syntax tree node classes."""

    # Builtin operators

    class FALSE(object):
        """Operator `FALSE`."""

    class TRUE(object):
        """Operator `TRUE`."""

    class BOOLEAN(object):
        """Operator `BOOLEAN`."""

    class STRING(object):
        """Operator `STRING`."""

    class Implies(object):
        """Operator `=>`."""

    class Equiv(object):
        """Operator `<=>`."""

    class Conj(object):
        r"""Operator `/\`."""

    class Disj(object):
        r"""Operator `\/`."""

    class Neg(object):
        """Operator `~`."""

    class Eq(object):
        """Operator `=`."""

    class Neq(object):
        """Operator `#`."""

    class SUBSET(object):
        """Operator `SUBSET`."""

    class UNION(object):
        """Operator `UNION`."""

    class DOMAIN(object):
        """Operator `DOMAIN`."""

    class Subseteq(object):
        r"""Operator `\subseteq`."""

    class Mem(object):
        r"""Operator `\in`."""

    class Notmem(object):
        r"""Operator `\notin`."""

    class Setminus(object):
        r"""Operator `\`."""

    class Cap(object):
        r"""Operator `\cap`."""

    class Cup(object):
        r"""Operator `\cup`."""

    class Prime(object):
        """Operator `'`."""

    class LeadsTo(object):
        """Operator `~>`."""

    class ENABLED(object):
        """Operator `ENABLED`."""

    class UNCHANGED(object):
        """Operator `UNCHANGED`."""

    class Cdot(object):
        r"""Operator `\cdot`."""

    class WhilePlus(object):
        """Operator `-+->`."""

    class Box(object):
        """Operator `[]`."""

        def __init__(self, boolean):
            self.boolean = boolean  # `bool` that
            # indicates application to
            # non-temporal formula, added
            # in post-processing step in `tlapm`

    class Diamond(object):
        """Operator `<>`."""

    # Syntax nodes of expressions

    class Opaque(object):
        """Named identifier."""

        def __init__(self, name):
            self.name = name

    class Internal(object):
        """Builtin operator."""

        def __init__(self, value):
            self.value = value

    class Apply(object):
        """Operator application `Op(arg1, arg2)`."""

        def __init__(self, op, operands):
            self.op = op  # expr
            self.operands = operands
            # `list` of expr

    class Function(object):
        r"""Function constructor `[x \in S |-> e]`."""

        def __init__(self, bounds, expr):
            self.bounds = bounds  # `list` of
            # `(str, Constant, Domain)`
            self.expr = expr

    class FunctionApply(object):
        """Function application `f[x]`."""

        def __init__(self, op, args):
            self.op = op  # expr
            self.args = args
            # `list` of expr

    class ShapeExpr(object):
        """Arity `_`."""

    class ShapeOp(object):
        """Arity `<<_, ...>>`."""

        def __init__(self, arity):
            self.arity = arity  # `int`

    class Lambda(object):
        """`LAMBDA` expression."""

        def __init__(self, name_shapes, expr):
            self.name_shapes = name_shapes  # signature
            # `list` of `(str, ShapeExpr | ShapeOp)`
            self.expr = expr

    class TemporalSub(object):
        """Subscripted temporal expression.

        `[][A]_v` or `<><<A>>_v`.
        """

        def __init__(self, op, action, subscript):
            self.op = op  # `BoxOp` | `DiamondOp`
            self.action = action
            self.subscript = subscript

    class Sub(object):
        """Subscripted action expression

        `[A]_v` or `<<A>>_v`.
        """

        def __init__(self, op, action, subscript):
            self.op = op  # `BoxOp` | `DiamondOp`
            self.action = action
            self.subscript = subscript

    class BoxOp(object):
        """Signifies `[][...]_...` or `[...]_...`."""

    class DiamondOp(object):
        """Signifies `<><<...>>_...` or `<<...>_...`."""

    class Dot(object):
        """Record field `expr.string`."""

        def __init__(self, expr, string):
            self.expr = expr
            self.string = string

    class Parens(object):
        """Parentheses or label."""

        def __init__(self, expr, pform):
            self.expr = expr
            self.pform = pform
            # `Syntax` | `NamedLabel`
            # | `IndexedLabel`
            # form of parentheses

        def __str__(self):
            return "Parens({e}, {p})".format(e=str(self.expr), p=str(self.pform))

    class Syntax(object):
        """Signifies actual parentheses in source syntax."""

    class NamedLabel(object):
        """Represents a named label."""

        def __init__(self, string, name_list):
            self.string = string  # `str`
            self.name_list = name_list
            # `list` of `str`

    class IndexedLabel(object):
        """Represents an indexed label."""

        def __init__(self, string, name_int_list):
            self.string = string  # `str`
            self.name_int_list = name_int_list

    class If(object):
        """Ternary conditional expression `IF ... THEN ... ELSE`."""

        def __init__(self, test, then, else_):
            self.test = test  # expr
            self.then = then  # expr
            self.else_ = else_  # expr

    class Let(object):
        """`LET ... IN` expression."""

        def __init__(self, definitions, expr):
            self.definitions = definitions
            # `list` of `OperatorDef`
            self.expr = expr

    class Forall(object):
        r"""Universal quantifier `\A`, `\AA`."""

    class Exists(object):
        r"""Existential quantifier `\E`, `\EE`."""

    class RigidQuantifier(object):
        r"""Rigid quantification `\E` or `\A`."""

        def __init__(self, quantifier, bounds, expr):
            self.quantifier = quantifier
            # `Forall` | `Exists`
            self.bounds = bounds
            # `list` of
            # `(str, Constant, Domain | NoDomain)`
            self.expr = expr

    class TemporalQuantifier(object):
        r"""Temporal quantification `\EE` or `\AA`."""

        def __init__(self, quantifier, variables, expr):
            self.quantifier = quantifier
            # `Forall` | `Exists`
            self.variables = variables
            # `list` of `str`
            self.expr = expr

    class Choose(object):
        """`CHOOSE` expression."""

        def __init__(self, name, bound, expr):
            self.name = name  # `str`
            self.bound = bound  # `None` | expr
            self.expr = expr

    class Case(object):
        """`CASE` expression."""

        def __init__(self, arms, other):
            self.arms = arms  # `list` of `(expr, expr)`
            self.other = other  # expr | `None`

    class SetEnum(object):
        """Set enumeration `{1, 2, 3}`."""

        def __init__(self, exprs):
            self.exprs = exprs  # `list` of expr

    class SetSt(object):
        r"""Set such that `{x \in S:  e(x)}`."""

        def __init__(self, name, bound, expr):
            self.name = name  # `str`
            self.bound = bound  # expr
            self.expr = expr

    class SetOf(object):
        r"""Set of `{e(x):  x \in S}`."""

        def __init__(self, expr, boundeds):
            self.expr = expr
            self.boundeds = boundeds
            # `list` of
            # `(str, Constant, Domain)`

    # type of junction list
    class And(object):
        """Conjunction list operator."""

    class Or(object):
        """Disjunction list operator."""

    # junction list (conjunction or disjunction)
    class List(object):
        """Conjunction or disjunction list."""

        def __init__(self, op, exprs):
            self.op = op  # `And` | `Or`
            self.exprs = exprs

    class Record(object):
        """Record constructor `[h |-> v, ...]`."""

        def __init__(self, items):
            self.items = items
            # `list` of `(str, expr)`

    class RecordSet(object):
        """Set of records `[h: V, ...]`."""

        def __init__(self, items):
            self.items = items
            # `list` of `(str, expr)`

    class Except_dot(object):
        """Dot syntax in `EXCEPT` `!.name = `."""

        def __init__(self, name):
            self.name = name

    class Except_apply(object):
        """Apply syntax in `EXCEPT` `![expr] = `."""

        def __init__(self, expr):
            self.expr = expr

    class Except(object):
        """`[expr EXCEPT exspec_list]`."""

        def __init__(self, expr, exspec_list):
            self.expr = expr
            self.exspec_list = exspec_list
            # `exspec` is a tuple
            # `(expoint list, expr)`
            # where `expoint` is
            # `Except_dot` | `Except_apply`

    class Domain(object):
        """Domain bound."""

        def __init__(self, expr):
            self.expr = expr

    class NoDomain(object):
        """Unbounded domain."""

    class Ditto(object):
        """Same bound domain."""

    class Bounded(object):
        """Bounded operator declaration."""

        def __init__(self, expr, visibility):
            self.expr = expr
            self.visibility = visibility
            # `Visible` | `Hidden`

    class Unbounded(object):
        """Operator declaration without bound."""

    class Visible(object):
        """Visible element.

        Facts, operator declarations.
        """

    class Hidden(object):
        """Hidden element.

        Operator definitions.
        """

    class NotSet(object):
        """Unspecified attribute."""

    class At(object):
        def __init__(self, boolean):
            self.boolean = boolean  # `True` if `@`
            # from `EXCEPT`, `False` if `@` from
            # proof step.

    class Arrow(object):
        """Function set `[expr -> expr]`."""

        def __init__(self, expr1, expr2):
            self.expr1 = expr1
            self.expr2 = expr2

    class Tuple(object):
        """Tuple constructor `<<1, 2>>`."""

        def __init__(self, exprs):
            self.exprs = exprs

    class Bang(object):
        """Label constructor `!`."""

        def __init__(self, expr, sel_list):
            self.expr = expr
            self.sel_list = sel_list
            # `list` of selector

    class WeakFairness(object):
        """Signifies operator `WF_`."""

    class StrongFairness(object):
        """Signifies operator `SF_`."""

    class String(object):
        """String constructor `"foo"`."""

        def __init__(self, value):
            self.value = value

    class Number(object):
        """Number constructor `."""

        def __init__(self, integer, mantissa):
            self.integer = integer  # characteristic
            self.mantissa = mantissa

    class Fairness(object):
        """Fairness expression.

        `WF_v(A)` or `SF_v(A)`.
        """

        def __init__(self, op, subscript, expr):
            self.op = op
            self.subscript = subscript
            self.expr = expr

    class SelLab(object):
        def __init__(self, string, exprs):
            self.string = string
            self.exprs = exprs
            # `list` of expr

    class SelInst(object):
        def __init__(self, exprs):
            self.exprs = exprs
            # `list` of expr

    class SelNum(object):
        def __init__(self, num):
            self.num = num  # `int`

    class SelLeft(object):
        pass

    class SelRight(object):
        pass

    class SelDown(object):
        pass

    class SelAt(object):
        pass

    class Sequent(object):
        """`ASSUME ... PROVE ...`."""

        def __init__(self, context, goal):
            self.context = context  # `list` of
            # `Fact` | `Flex` | `Fresh` | `Sequent`
            self.goal = goal

    class Fact(object):
        def __init__(self, expr, visibility, time):
            self.expr = expr
            self.visibility = visibility
            # `Visible` | `Hidden`
            self.time = time  # `NotSet`

    # operator declarations

    class Flex(object):
        """Flexible `VARIABLE`."""

        def __init__(self, name):
            self.name = name  # `str`

    # constant, state, action, and
    # temporal level operators
    class Fresh(object):
        """Operator declaration (in sequent).

        `CONSTANT`, `STATE`, `ACTION`,
        `TEMPORAL`.
        """

        def __init__(self, name, shape, kind, domain):
            self.name = name  # `str`
            self.shape = shape
            # `ShapeExpr` | `ShapeOp`
            self.kind = kind
            # `Constant` | `State`
            # | `Action` | `Temporal`
            self.domain = domain
            # `Bounded` | `Unbounded`

    # expression levels for operator declarations
    class Constant(object):
        """`CONSTANT` declaration."""

    class State(object):
        """`STATE` declaration."""

    class Action(object):
        """`ACTION` declaration."""

    class Temporal(object):
        """`TEMPORAL` declaration."""

    class OperatorDef(object):
        """Operator definition `Op == x + 1`."""

        def __init__(self, name, expr):
            self.name = name  # `str`
            self.expr = expr  # `Lambda` or expr

    class Instance(object):
        """`INSTANCE` statement."""

        def __init__(self, name, args, module, sub):
            self.name = name  # name of operator
            # in `INSTANCE` definition
            # `str` | `None`
            self.args = args  # arguments of
            # operator signature in
            # `INSTANCE` definition
            # `list` of `str` | `None`
            self.module = module  # `str`
            self.sub = sub  # `list` of `(str, expr)`

    # Syntax nodes of module elements

    class Constants(object):
        """`CONSTANT` declarations in module scope."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `(str, ShapeExpr | ShapeOp)`

    class Variables(object):
        """`VARIABLE` declarations in module scope."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `str`

    class Recursives(object):
        """Recursive operator definition."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `(str, ShapeExpr | ShapeOp)`

    class Local(object):
        """Keyword `LOCAL`."""

    class Export(object):
        """Absence of keyword `LOCAL`."""

    class User(object):
        pass

    class Definition(object):
        """Operator definition as module unit."""

        def __init__(self, definition, wheredef, visibility, local):
            self.definition = definition
            self.wheredef = wheredef
            # builtin | `User`
            self.visibility = visibility
            # `Visible` | `Hidden`
            self.local = local
            # `Local` | `Export`

    class AnonymousInstance(object):
        """`INSTANCE` statement without definition."""

        def __init__(self, instance, local):
            self.instance = instance  # `Instance`
            self.local = local  # `Local` | `Export`

    class Mutate(object):
        """Module-scope `USE` or `HIDE`."""

        def __init__(self, kind, usable):
            self.kind = kind
            # `Hide` | `Use`
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`

    class ModuleHide(object):
        """Module-scope `HIDE`."""

    class ModuleUse(object):
        """Module-scope `USE`."""

        def __init__(self, boolean):
            self.boolean = boolean

    class Module(object):
        """`MODULE`s and submodules."""

        def __init__(self, name, extendees, instancees, body):
            self.name = name  # `str`
            self.extendees = extendees
            # `list` of `str`
            self.instancees = instancees  # `list`
            self.body = body  # `list` of
            # `Definition` | `Mutate`
            # `Submodule` | `Theorem`

    class Submodule(object):
        """Submodule as module unit."""

        def __init__(self, module):
            self.module = module

    class Suppress(object):
        pass

    class Emit(object):
        pass

    class StepStar(object):
        """Step identifier `<*>label`."""

        def __init__(self, label):
            self.label = label

    class StepPlus(object):
        """Step identifier `<+>label`."""

        def __init__(self, label):
            self.label = label

    class StepNum(object):
        """Step identifier `<level>label`."""

        def __init__(self, level, label):
            self.level = level
            self.label = label

    class Only(object):
        """`ONLY` statement."""

    class Default(object):
        """`ONLY` attribute in `PreBy`."""

    class PreBy(object):
        """`BY` statement."""

        def __init__(self, supp, only, usable, method):
            self.supp = supp
            self.only = only  # `Default` | `Only`
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.method = method

    class PreObvious(object):
        """`OBVIOUS` statement."""

        def __init__(self, supp, method):
            self.supp = supp
            self.method = method

    class PreOmitted(object):
        """`OMITTED` statement."""

        def __init__(self, omission):
            self.omission = omission
            # `Explicit` | `Implicit`

    class Explicit(object):
        """Explicitly omitted proof."""

    class Implicit(object):
        """Implicitly omitted proof."""

    class PreStep(object):
        """Proof step."""

        def __init__(self, boolean, preno, prestep):
            self.boolean = boolean  # `PROOF` keyword ?
            self.preno = preno
            self.prestep = prestep

    class PreHide(object):
        """`HIDE` statement."""

        def __init__(self, usable):
            self.usable = usable

    class PreUse(object):
        """`USE` statement."""

        def __init__(self, supp, only, usable, method):
            self.supp = supp
            self.only = only
            self.usable = usable
            self.method = method

    class PreDefine(object):
        """`DEFINE` statement."""

        def __init__(self, defns):
            self.definitions = defns

    class PreAssert(object):
        """Assertion statement.

        Sequent or expression in proof step.
        """

        def __init__(self, sequent):
            self.sequent = sequent

    class PreSuffices(object):
        """`SUFFICES` statement."""

        def __init__(self, sequent):
            self.sequent = sequent

    class PreCase(object):
        """`CASE` proof statement."""

        def __init__(self, expr):
            self.expr = expr

    class PrePick(object):
        """`PICK` statement."""

        def __init__(self, bounds, expr):
            self.bounds = bounds
            self.expr = expr

    class PreHave(object):
        """`HAVE` statement."""

        def __init__(self, supp, expr, method):
            self.supp = supp
            self.expr = expr
            self.method = method

    class PreTake(object):
        """`TAKE` statement."""

        def __init__(self, supp, bounds, method):
            self.supp = supp
            self.bounds = bounds
            self.method = method

    class PreWitness(object):
        """`WITNESS` statement."""

        def __init__(self, supp, exprs, method):
            self.supp = supp
            self.exprs = exprs
            self.method = method

    class PreQed(object):
        """`QED` statement."""

    class Theorem(object):
        """`THEOREM` together with its proof.

        ```
        THEOREM name == body
        PROOF
        proof
        ```
        """

        def __init__(self, name, body, proof):
            self.name = name  # `str` | `None`
            self.body = body  # `Sequent`
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    # Step numbers

    class Named(object):
        """Step number with label."""

        def __init__(self, level, label, boolean):
            self.level = level  # `int`
            self.label = label  # `str`
            self.boolean = boolean  # `bool`

    class Unnamed(object):
        """Step number without label."""

        def __init__(self, level, uuid):
            self.level = level  # `int`
            self.uuid = uuid

    # Proofs

    class Obvious(object):
        """`OBVIOUS` statement."""

    class Omitted(object):
        """`OMITTED` statement."""

        def __init__(self, omission):
            self.omission = omission

    class By(object):
        """`BY` statement."""

        def __init__(self, usable, only):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.only = only  # `bool`

    class Steps(object):
        """Proof steps in a proof."""

        def __init__(self, steps, qed_step):
            self.steps = steps  # step `list`
            self.qed_step = qed_step

    # Proof steps
    # The attribute `step_number` stores
    # the step number:  `Named` | `Unnamed`

    class Hide(object):
        """`HIDE` statement."""

        def __init__(self, usable):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`

    class Define(object):
        """`DEFINE` statement."""

        def __init__(self, defns):
            self.definitions = defns

    class Assert(object):
        """Assertion statement.

        Sequent with proof.
        """

        def __init__(self, sequent, proof):
            self.sequent = sequent  # `Sequent`
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Suffices(object):
        """`SUFFICES` statement."""

        def __init__(self, sequent, proof):
            self.sequent = sequent
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Pcase(object):
        """`CASE` proof statement."""

        def __init__(self, expr, proof):
            self.expr = expr
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Pick(object):
        """`PICK` statement."""

        def __init__(self, bounds, expr, proof):
            self.bounds = bounds  # `list` of
            # `(str, Constant,
            #   Domain | NoDomain | Ditto)`
            self.expr = expr
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Use(object):
        """`USE` statement."""

        def __init__(self, usable, only):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.only = only  # `bool`

    class Have(object):
        """`HAVE` statement."""

        def __init__(self, expr):
            self.expr = expr

    class Take(object):
        """`TAKE` statement."""

        def __init__(self, bounds):
            self.bounds = bounds
            # `list` of
            # `(str, Constant,
            #   Domain | NoDomain | Ditto)`

    class Witness(object):
        """`WITNESS` statement."""

        def __init__(self, exprs):
            self.exprs = exprs
            # `list` of expr

    class Qed(object):
        """`QED` statement."""

        def __init__(self, proof):
            self.proof = proof

    class Dvar(object):
        """Item in `BY DEF ...` or `USE DEF ...`."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bstring(object):
        """Backend pragma string."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bfloat(object):
        """Backend pragma float."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bdef(object):
        """`@` in backend pragma."""

    class BackendPragma(object):
        """Backend pragma."""

        def __init__(self, name, expr, backend_args):
            self.name = name  # as in `OperatorDef`
            self.expr = expr  # as in `OperatorDef`
            self.backend_args = backend_args
            # `list` of `(str, Bstring | Bfloat | Bdef)`
