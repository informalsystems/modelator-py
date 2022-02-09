"""TLA+ abstract syntax tree."""
# Copyright 2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the files:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/builtin.ml>
# <https://github.com/tlaplus/tlapm/blob/main/src/expr/e_t.ml>
# <https://github.com/tlaplus/tlapm/blob/main/src/module/m_t.ml>
# <https://github.com/tlaplus/tlapm/blob/main/src/proof/p_t.ml>
# <https://github.com/tlaplus/tlapm/blob/main/src/proof/p_parser.ml>


class Nodes:
    """TLA+ syntax tree node classes."""

    # Builtin operators

    class FALSE:
        """Operator `FALSE`."""

    class TRUE:
        """Operator `TRUE`."""

    class BOOLEAN:
        """Operator `BOOLEAN`."""

    class STRING:
        """Operator `STRING`."""

    class Implies:
        """Operator `=>`."""

    class Equiv:
        """Operator `<=>`."""

    class Conj:
        r"""Operator `/\`."""

    class Disj:
        r"""Operator `\/`."""

    class Neg:
        """Operator `~`."""

    class Eq:
        """Operator `=`."""

    class Neq:
        """Operator `#`."""

    class SUBSET:
        """Operator `SUBSET`."""

    class UNION:
        """Operator `UNION`."""

    class DOMAIN:
        """Operator `DOMAIN`."""

    class Subseteq:
        r"""Operator `\subseteq`."""

    class Mem:
        r"""Operator `\in`."""

    class Notmem:
        r"""Operator `\notin`."""

    class Setminus:
        r"""Operator `\`."""

    class Cap:
        r"""Operator `\cap`."""

    class Cup:
        r"""Operator `\cup`."""

    class Prime:
        """Operator `'`."""

    class LeadsTo:
        """Operator `~>`."""

    class ENABLED:
        """Operator `ENABLED`."""

    class UNCHANGED:
        """Operator `UNCHANGED`."""

    class Cdot:
        r"""Operator `\cdot`."""

    class WhilePlus:
        """Operator `-+->`."""

    class Box:
        """Operator `[]`."""

        def __init__(self, boolean):
            self.boolean = boolean  # `bool` that
            # indicates application to
            # non-temporal formula, added
            # in post-processing step in `tlapm`

    class Diamond:
        """Operator `<>`."""

    # Syntax nodes of expressions

    class Opaque:
        """Named identifier."""

        def __init__(self, name):
            self.name = name

    class Internal:
        """Builtin operator."""

        def __init__(self, value):
            self.value = value

    class Apply:
        """Operator application `Op(arg1, arg2)`."""

        def __init__(self, op, operands):
            self.op = op  # expr
            self.operands = operands
            # `list` of expr

    class Function:
        r"""Function constructor `[x \in S |-> e]`."""

        def __init__(self, bounds, expr):
            self.bounds = bounds  # `list` of
            # `(str, Constant, Domain)`
            self.expr = expr

    class FunctionApply:
        """Function application `f[x]`."""

        def __init__(self, op, args):
            self.op = op  # expr
            self.args = args
            # `list` of expr

    class ShapeExpr:
        """Arity `_`."""

    class ShapeOp:
        """Arity `<<_, ...>>`."""

        def __init__(self, arity):
            self.arity = arity  # `int`

    class Lambda:
        """`LAMBDA` expression."""

        def __init__(self, name_shapes, expr):
            self.name_shapes = name_shapes  # signature
            # `list` of `(str, ShapeExpr | ShapeOp)`
            self.expr = expr

    class TemporalSub:
        """Subscripted temporal expression.

        `[][A]_v` or `<><<A>>_v`.
        """

        def __init__(self, op, action, subscript):
            self.op = op  # `BoxOp` | `DiamondOp`
            self.action = action
            self.subscript = subscript

    class Sub:
        """Subscripted action expression

        `[A]_v` or `<<A>>_v`.
        """

        def __init__(self, op, action, subscript):
            self.op = op  # `BoxOp` | `DiamondOp`
            self.action = action
            self.subscript = subscript

    class BoxOp:
        """Signifies `[][...]_...` or `[...]_...`."""

    class DiamondOp:
        """Signifies `<><<...>>_...` or `<<...>_...`."""

    class Dot:
        """Record field `expr.string`."""

        def __init__(self, expr, string):
            self.expr = expr
            self.string = string

    class Parens:
        """Parentheses or label."""

        def __init__(self, expr, pform):
            self.expr = expr
            self.pform = pform
            # `Syntax` | `NamedLabel`
            # | `IndexedLabel`
            # form of parentheses

        def __str__(self):
            return f"Parens({self.expr}, {self.pform})"

    class Syntax:
        """Signifies actual parentheses in source syntax."""

    class NamedLabel:
        """Represents a named label."""

        def __init__(self, string, name_list):
            self.string = string  # `str`
            self.name_list = name_list
            # `list` of `str`

    class IndexedLabel:
        """Represents an indexed label."""

        def __init__(self, string, name_int_list):
            self.string = string  # `str`
            self.name_int_list = name_int_list

    class If:
        """Ternary conditional expression `IF ... THEN ... ELSE`."""

        def __init__(self, test, then, else_):
            self.test = test  # expr
            self.then = then  # expr
            self.else_ = else_  # expr

    class Let:
        """`LET ... IN` expression."""

        def __init__(self, definitions, expr):
            self.definitions = definitions
            # `list` of `OperatorDef`
            self.expr = expr

    class Forall:
        r"""Universal quantifier `\A`, `\AA`."""

    class Exists:
        r"""Existential quantifier `\E`, `\EE`."""

    class RigidQuantifier:
        r"""Rigid quantification `\E` or `\A`."""

        def __init__(self, quantifier, bounds, expr):
            self.quantifier = quantifier
            # `Forall` | `Exists`
            self.bounds = bounds
            # `list` of
            # `(str, Constant, Domain | NoDomain)`
            self.expr = expr

    class TemporalQuantifier:
        r"""Temporal quantification `\EE` or `\AA`."""

        def __init__(self, quantifier, variables, expr):
            self.quantifier = quantifier
            # `Forall` | `Exists`
            self.variables = variables
            # `list` of `str`
            self.expr = expr

    class Choose:
        """`CHOOSE` expression."""

        def __init__(self, name, bound, expr):
            self.name = name  # `str`
            self.bound = bound  # `None` | expr
            self.expr = expr

    class Case:
        """`CASE` expression."""

        def __init__(self, arms, other):
            self.arms = arms  # `list` of `(expr, expr)`
            self.other = other  # expr | `None`

    class SetEnum:
        """Set enumeration `{1, 2, 3}`."""

        def __init__(self, exprs):
            self.exprs = exprs  # `list` of expr

    class SetSt:
        r"""Set such that `{x \in S:  e(x)}`."""

        def __init__(self, name, bound, expr):
            self.name = name  # `str`
            self.bound = bound  # expr
            self.expr = expr

    class SetOf:
        r"""Set of `{e(x):  x \in S}`."""

        def __init__(self, expr, boundeds):
            self.expr = expr
            self.boundeds = boundeds
            # `list` of
            # `(str, Constant, Domain)`

    # type of junction list
    class And:
        """Conjunction list operator."""

    class Or:
        """Disjunction list operator."""

    # junction list (conjunction or disjunction)
    class List:
        """Conjunction or disjunction list."""

        def __init__(self, op, exprs):
            self.op = op  # `And` | `Or`
            self.exprs = exprs

    class Record:
        """Record constructor `[h |-> v, ...]`."""

        def __init__(self, items):
            self.items = items
            # `list` of `(str, expr)`

    class RecordSet:
        """Set of records `[h: V, ...]`."""

        def __init__(self, items):
            self.items = items
            # `list` of `(str, expr)`

    class Except_dot:
        """Dot syntax in `EXCEPT` `!.name = `."""

        def __init__(self, name):
            self.name = name

    class Except_apply:
        """Apply syntax in `EXCEPT` `![expr] = `."""

        def __init__(self, expr):
            self.expr = expr

    class Except:
        """`[expr EXCEPT exspec_list]`."""

        def __init__(self, expr, exspec_list):
            self.expr = expr
            self.exspec_list = exspec_list
            # `exspec` is a tuple
            # `(expoint list, expr)`
            # where `expoint` is
            # `Except_dot` | `Except_apply`

    class Domain:
        """Domain bound."""

        def __init__(self, expr):
            self.expr = expr

    class NoDomain:
        """Unbounded domain."""

    class Ditto:
        """Same bound domain."""

    class Bounded:
        """Bounded operator declaration."""

        def __init__(self, expr, visibility):
            self.expr = expr
            self.visibility = visibility
            # `Visible` | `Hidden`

    class Unbounded:
        """Operator declaration without bound."""

    class Visible:
        """Visible element.

        Facts, operator declarations.
        """

    class Hidden:
        """Hidden element.

        Operator definitions.
        """

    class NotSet:
        """Unspecified attribute."""

    class At:
        def __init__(self, boolean):
            self.boolean = boolean  # `True` if `@`
            # from `EXCEPT`, `False` if `@` from
            # proof step.

    class Arrow:
        """Function set `[expr -> expr]`."""

        def __init__(self, expr1, expr2):
            self.expr1 = expr1
            self.expr2 = expr2

    class Tuple:
        """Tuple constructor `<<1, 2>>`."""

        def __init__(self, exprs):
            self.exprs = exprs

    class Bang:
        """Label constructor `!`."""

        def __init__(self, expr, sel_list):
            self.expr = expr
            self.sel_list = sel_list
            # `list` of selector

    class WeakFairness:
        """Signifies operator `WF_`."""

    class StrongFairness:
        """Signifies operator `SF_`."""

    class String:
        """String constructor `"foo"`."""

        def __init__(self, value):
            self.value = value

    class Number:
        """Number constructor `."""

        def __init__(self, integer, mantissa):
            self.integer = integer  # characteristic
            self.mantissa = mantissa

    class Fairness:
        """Fairness expression.

        `WF_v(A)` or `SF_v(A)`.
        """

        def __init__(self, op, subscript, expr):
            self.op = op
            self.subscript = subscript
            self.expr = expr

    class SelLab:
        def __init__(self, string, exprs):
            self.string = string
            self.exprs = exprs
            # `list` of expr

    class SelInst:
        def __init__(self, exprs):
            self.exprs = exprs
            # `list` of expr

    class SelNum:
        def __init__(self, num):
            self.num = num  # `int`

    class SelLeft:
        pass

    class SelRight:
        pass

    class SelDown:
        pass

    class SelAt:
        pass

    class Sequent:
        """`ASSUME ... PROVE ...`."""

        def __init__(self, context, goal):
            self.context = context  # `list` of
            # `Fact` | `Flex` | `Fresh` | `Sequent`
            self.goal = goal

    class Fact:
        def __init__(self, expr, visibility, time):
            self.expr = expr
            self.visibility = visibility
            # `Visible` | `Hidden`
            self.time = time  # `NotSet`

    # operator declarations

    class Flex:
        """Flexible `VARIABLE`."""

        def __init__(self, name):
            self.name = name  # `str`

    # constant, state, action, and
    # temporal level operators
    class Fresh:
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
    class Constant:
        """`CONSTANT` declaration."""

    class State:
        """`STATE` declaration."""

    class Action:
        """`ACTION` declaration."""

    class Temporal:
        """`TEMPORAL` declaration."""

    class OperatorDef:
        """Operator definition `Op == x + 1`."""

        def __init__(self, name, expr):
            self.name = name  # `str`
            self.expr = expr  # `Lambda` or expr

    class Instance:
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

    class Constants:
        """`CONSTANT` declarations in module scope."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `(str, ShapeExpr | ShapeOp)`

    class Variables:
        """`VARIABLE` declarations in module scope."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `str`

    class Recursives:
        """Recursive operator definition."""

        def __init__(self, declarations):
            self.declarations = declarations
            # `list` of `(str, ShapeExpr | ShapeOp)`

    class Local:
        """Keyword `LOCAL`."""

    class Export:
        """Absence of keyword `LOCAL`."""

    class User:
        pass

    class Definition:
        """Operator definition as module unit."""

        def __init__(self, definition, wheredef, visibility, local):
            self.definition = definition
            self.wheredef = wheredef
            # builtin | `User`
            self.visibility = visibility
            # `Visible` | `Hidden`
            self.local = local
            # `Local` | `Export`

    class AnonymousInstance:
        """`INSTANCE` statement without definition."""

        def __init__(self, instance, local):
            self.instance = instance  # `Instance`
            self.local = local  # `Local` | `Export`

    class Mutate:
        """Module-scope `USE` or `HIDE`."""

        def __init__(self, kind, usable):
            self.kind = kind
            # `Hide` | `Use`
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`

    class ModuleHide:
        """Module-scope `HIDE`."""

    class ModuleUse:
        """Module-scope `USE`."""

        def __init__(self, boolean):
            self.boolean = boolean

    class Module:
        """`MODULE`s and submodules."""

        def __init__(self, name, extendees, instancees, body):
            self.name = name  # `str`
            self.extendees = extendees
            # `list` of `str`
            self.instancees = instancees  # `list`
            self.body = body  # `list` of
            # `Definition` | `Mutate`
            # `Submodule` | `Theorem`

    class Submodule:
        """Submodule as module unit."""

        def __init__(self, module):
            self.module = module

    class Suppress:
        pass

    class Emit:
        pass

    class StepStar:
        """Step identifier `<*>label`."""

        def __init__(self, label):
            self.label = label

    class StepPlus:
        """Step identifier `<+>label`."""

        def __init__(self, label):
            self.label = label

    class StepNum:
        """Step identifier `<level>label`."""

        def __init__(self, level, label):
            self.level = level
            self.label = label

    class Only:
        """`ONLY` statement."""

    class Default:
        """`ONLY` attribute in `PreBy`."""

    class PreBy:
        """`BY` statement."""

        def __init__(self, supp, only, usable, method):
            self.supp = supp
            self.only = only  # `Default` | `Only`
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.method = method

    class PreObvious:
        """`OBVIOUS` statement."""

        def __init__(self, supp, method):
            self.supp = supp
            self.method = method

    class PreOmitted:
        """`OMITTED` statement."""

        def __init__(self, omission):
            self.omission = omission
            # `Explicit` | `Implicit`

    class Explicit:
        """Explicitly omitted proof."""

    class Implicit:
        """Implicitly omitted proof."""

    class PreStep:
        """Proof step."""

        def __init__(self, boolean, preno, prestep):
            self.boolean = boolean  # `PROOF` keyword ?
            self.preno = preno
            self.prestep = prestep

    class PreHide:
        """`HIDE` statement."""

        def __init__(self, usable):
            self.usable = usable

    class PreUse:
        """`USE` statement."""

        def __init__(self, supp, only, usable, method):
            self.supp = supp
            self.only = only
            self.usable = usable
            self.method = method

    class PreDefine:
        """`DEFINE` statement."""

        def __init__(self, defns):
            self.definitions = defns

    class PreAssert:
        """Assertion statement.

        Sequent or expression in proof step.
        """

        def __init__(self, sequent):
            self.sequent = sequent

    class PreSuffices:
        """`SUFFICES` statement."""

        def __init__(self, sequent):
            self.sequent = sequent

    class PreCase:
        """`CASE` proof statement."""

        def __init__(self, expr):
            self.expr = expr

    class PrePick:
        """`PICK` statement."""

        def __init__(self, bounds, expr):
            self.bounds = bounds
            self.expr = expr

    class PreHave:
        """`HAVE` statement."""

        def __init__(self, supp, expr, method):
            self.supp = supp
            self.expr = expr
            self.method = method

    class PreTake:
        """`TAKE` statement."""

        def __init__(self, supp, bounds, method):
            self.supp = supp
            self.bounds = bounds
            self.method = method

    class PreWitness:
        """`WITNESS` statement."""

        def __init__(self, supp, exprs, method):
            self.supp = supp
            self.exprs = exprs
            self.method = method

    class PreQed:
        """`QED` statement."""

    class Axiom:
        """`AXIOM`."""

        def __init__(self, name, expr):
            self.name = name
            self.expr = expr

    class Theorem:
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

    class Named:
        """Step number with label."""

        def __init__(self, level, label, boolean):
            self.level = level  # `int`
            self.label = label  # `str`
            self.boolean = boolean  # `bool`

    class Unnamed:
        """Step number without label."""

        def __init__(self, level, uuid):
            self.level = level  # `int`
            self.uuid = uuid

    # Proofs

    class Obvious:
        """`OBVIOUS` statement."""

    class Omitted:
        """`OMITTED` statement."""

        def __init__(self, omission):
            self.omission = omission

    class By:
        """`BY` statement."""

        def __init__(self, usable, only):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.only = only  # `bool`

    class Steps:
        """Proof steps in a proof."""

        def __init__(self, steps, qed_step):
            self.steps = steps  # step `list`
            self.qed_step = qed_step

    # Proof steps
    # The attribute `step_number` stores
    # the step number:  `Named` | `Unnamed`

    class Hide:
        """`HIDE` statement."""

        def __init__(self, usable):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`

    class Define:
        """`DEFINE` statement."""

        def __init__(self, defns):
            self.definitions = defns

    class Assert:
        """Assertion statement.

        Sequent with proof.
        """

        def __init__(self, sequent, proof):
            self.sequent = sequent  # `Sequent`
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Suffices:
        """`SUFFICES` statement."""

        def __init__(self, sequent, proof):
            self.sequent = sequent
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Pcase:
        """`CASE` proof statement."""

        def __init__(self, expr, proof):
            self.expr = expr
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Pick:
        """`PICK` statement."""

        def __init__(self, bounds, expr, proof):
            self.bounds = bounds  # `list` of
            # `(str, Constant,
            #   Domain | NoDomain | Ditto)`
            self.expr = expr
            self.proof = proof
            # `Omitted` | `Obvious`
            # | `Steps` | `By`

    class Use:
        """`USE` statement."""

        def __init__(self, usable, only):
            self.usable = usable
            # `dict(facts=list of expr,
            #       defs=list of Dvar)`
            self.only = only  # `bool`

    class Have:
        """`HAVE` statement."""

        def __init__(self, expr):
            self.expr = expr

    class Take:
        """`TAKE` statement."""

        def __init__(self, bounds):
            self.bounds = bounds
            # `list` of
            # `(str, Constant,
            #   Domain | NoDomain | Ditto)`

    class Witness:
        """`WITNESS` statement."""

        def __init__(self, exprs):
            self.exprs = exprs
            # `list` of expr

    class Qed:
        """`QED` statement."""

        def __init__(self, proof):
            self.proof = proof

    class Dvar:
        """Item in `BY DEF ...` or `USE DEF ...`."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bstring:
        """Backend pragma string."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bfloat:
        """Backend pragma float."""

        def __init__(self, value):
            self.value = value  # `str`

    class Bdef:
        """`@` in backend pragma."""

    class BackendPragma:
        """Backend pragma."""

        def __init__(self, name, expr, backend_args):
            self.name = name  # as in `OperatorDef`
            self.expr = expr  # as in `OperatorDef`
            self.backend_args = backend_args
            # `list` of `(str, Bstring | Bfloat | Bdef)`
