"""Apply a function to nodes of TLA+ syntax tree."""
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

from .to_str import Nodes as _Nodes

LINE_WIDTH = 80
INDENT_WIDTH = 4


def _visit_bounds(bounds, *arg, visitor=None, **kw):
    """Call the `visit` method of each bound."""
    for name, kind, dom in bounds:
        dom.visit(*arg, visitor=visitor, **kw)


def _visit_usable(usable, *arg, visitor=None, **kw):
    for fact in usable["facts"]:
        fact.visit(*arg, visitor=visitor, **kw)
    for defn in usable["defs"]:
        defn.visit(*arg, visitor=visitor, **kw)


class Nodes(_Nodes):
    """Translating TLA+ AST nodes to strings."""

    # Builtin operators

    class FALSE(_Nodes.FALSE):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class TRUE(_Nodes.TRUE):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class BOOLEAN(_Nodes.BOOLEAN):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class STRING(_Nodes.STRING):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Implies(_Nodes.Implies):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Equiv(_Nodes.Equiv):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Conj(_Nodes.Conj):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Disj(_Nodes.Disj):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Neg(_Nodes.Neg):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Eq(_Nodes.Eq):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Neq(_Nodes.Neq):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SUBSET(_Nodes.SUBSET):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class UNION(_Nodes.UNION):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class DOMAIN(_Nodes.DOMAIN):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Subseteq(_Nodes.Subseteq):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Mem(_Nodes.Mem):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Notmem(_Nodes.Notmem):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Setminus(_Nodes.Setminus):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Cap(_Nodes.Cap):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Cup(_Nodes.Cup):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Prime(_Nodes.Prime):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class LeadsTo(_Nodes.LeadsTo):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class ENABLED(_Nodes.ENABLED):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class UNCHANGED(_Nodes.UNCHANGED):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Cdot(_Nodes.Cdot):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class WhilePlus(_Nodes.WhilePlus):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Box(_Nodes.Box):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Diamond(_Nodes.Diamond):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Opaque(_Nodes.Opaque):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Internal(_Nodes.Internal):
        def visit(self, *arg, visitor=None, **kw):
            self.value.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Apply(_Nodes.Apply):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            for arg_ in self.operands:
                arg_.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Function(_Nodes.Function):
        def visit(self, *arg, visitor=None, **kw):
            _visit_bounds(self.bounds, *arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class FunctionApply(_Nodes.FunctionApply):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            for arg_ in self.args:
                arg_.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class ShapeExpr(_Nodes.ShapeExpr):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class ShapeOp(_Nodes.ShapeOp):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Lambda(_Nodes.Lambda):
        def visit(self, *arg, visitor=None, **kw):
            for name, shape in self.name_shapes:
                shape.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class TemporalSub(_Nodes.TemporalSub):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            self.action.visit(*arg, visitor=visitor, **kw)
            self.subscript.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Sub(_Nodes.Sub):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            self.action.visit(*arg, visitor=visitor, **kw)
            self.subscript.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class BoxOp(_Nodes.BoxOp):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class DiamondOp(_Nodes.DiamondOp):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Dot(_Nodes.Dot):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Parens(_Nodes.Parens):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            self.pform.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Syntax(_Nodes.Syntax):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class NamedLabel(_Nodes.NamedLabel):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class IndexedLabel(_Nodes.IndexedLabel):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class If(_Nodes.If):
        def visit(self, *arg, visitor=None, **kw):
            self.test.visit(*arg, visitor=visitor, **kw)
            self.then.visit(*arg, visitor=visitor, **kw)
            self.else_.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Let(_Nodes.Let):
        def visit(self, *arg, visitor=None, **kw):
            for defn in self.definitions:
                defn.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Forall(_Nodes.Forall):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Exists(_Nodes.Exists):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class RigidQuantifier(_Nodes.RigidQuantifier):
        def visit(self, *arg, visitor=None, **kw):
            self.quantifier.visit(*arg, visitor=visitor, **kw)
            _visit_bounds(self.bounds, *arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class TemporalQuantifier(_Nodes.TemporalQuantifier):
        def visit(self, *arg, visitor=None, **kw):
            self.quantifier.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Choose(_Nodes.Choose):
        def visit(self, *arg, visitor=None, **kw):
            if self.bound is not None:
                self.bound.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Case(_Nodes.Case):
        def visit(self, *arg, visitor=None, **kw):
            for guard, expr in self.arms:
                guard.visit(*arg, visitor=visitor, **kw)
                expr.visit(*arg, visitor=visitor, **kw)
            self.other.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class SetEnum(_Nodes.SetEnum):
        def visit(self, *arg, visitor=None, **kw):
            for expr in self.exprs:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class SetSt(_Nodes.SetSt):
        def visit(self, *arg, visitor=None, **kw):
            self.bound.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class SetOf(_Nodes.SetOf):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            _visit_bounds(self.boundeds, *arg, visitor=visitor, **kw)
            visitor(self)

    # type of junction list
    class And(_Nodes.And):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Or(_Nodes.Or):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class List(_Nodes.List):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            for expr in self.exprs:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Record(_Nodes.Record):
        def visit(self, *arg, visitor=None, **kw):
            for name, expr in self.items:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class RecordSet(_Nodes.RecordSet):
        def visit(self, *arg, visitor=None, **kw):
            for name, expr in self.items:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Except_dot(_Nodes.Except_dot):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Except_apply(_Nodes.Except_apply):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Except(_Nodes.Except):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            for expoints, expr in self.exspec_list:
                expr.visit(*arg, visitor=visitor, **kw)
                for expoint in expoints:
                    expoint.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Domain(_Nodes.Domain):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class NoDomain(_Nodes.NoDomain):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Ditto(_Nodes.Ditto):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Bounded(_Nodes.Bounded):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            self.visibility.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Unbounded(_Nodes.Unbounded):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Visible(_Nodes.Visible):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Hidden(_Nodes.Hidden):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class NotSet(_Nodes.NotSet):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class At(_Nodes.At):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Arrow(_Nodes.Arrow):
        def visit(self, *arg, visitor=None, **kw):
            self.expr1.visit(*arg, visitor=visitor, **kw)
            self.expr2.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Tuple(_Nodes.Tuple):
        def visit(self, *arg, visitor=None, **kw):
            for expr in self.exprs:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Bang(_Nodes.Bang):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            for sel in self.sel_list:
                sel.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class WeakFairness(_Nodes.WeakFairness):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class StrongFairness(_Nodes.StrongFairness):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class String(_Nodes.String):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Number(_Nodes.Number):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Fairness(_Nodes.Fairness):
        def visit(self, *arg, visitor=None, **kw):
            self.op.visit(*arg, visitor=visitor, **kw)
            self.subscript.visit(*arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class SelLab(_Nodes.SelLab):
        def visit(self, *arg, visitor=None, **kw):
            for expr in self.exprs:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class SelInst(_Nodes.SelInst):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SelNum(_Nodes.SelNum):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SelLeft(_Nodes.SelLeft):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SelRight(_Nodes.SelRight):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SelDown(_Nodes.SelDown):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class SelAt(_Nodes.SelAt):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Sequent(_Nodes.Sequent):
        def visit(self, *arg, visitor=None, **kw):
            for item in self.context:
                item.visit(*arg, visitor=visitor, **kw)
            self.goal.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Fact(_Nodes.Fact):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            self.visibility.visit(*arg, visitor=visitor, **kw)
            self.time.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    # operator declarations

    class Flex(_Nodes.Flex):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Fresh(_Nodes.Fresh):
        def visit(self, *arg, visitor=None, **kw):
            self.shape.visit(*arg, visitor=visitor, **kw)
            self.kind.visit(*arg, visitor=visitor, **kw)
            self.domain.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Constant(_Nodes.Constant):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class State(_Nodes.State):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Action(_Nodes.Action):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Temporal(_Nodes.Temporal):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class OperatorDef(_Nodes.OperatorDef):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Instance(_Nodes.Instance):
        def visit(self, *arg, visitor=None, **kw):
            for name, expr in self.sub:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    # Syntax nodes of module elements

    class Constants(_Nodes.Constants):
        def visit(self, *arg, visitor=None, **kw):
            for name, shape in self.declarations:
                shape.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Variables(_Nodes.Variables):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Recursives(_Nodes.Recursives):
        def visit(self, *arg, visitor=None, **kw):
            raise NotImplementedError("RECURSIVE")

    class Local(_Nodes.Local):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Export(_Nodes.Export):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class User(_Nodes.User):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Definition(_Nodes.Definition):
        def visit(self, *arg, visitor=None, **kw):
            self.definition.visit(*arg, visitor=visitor, **kw)
            self.wheredef.visit(*arg, visitor=visitor, **kw)
            self.visibility.visit(*arg, visitor=visitor, **kw)
            self.local.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class AnonymousInstance(_Nodes.AnonymousInstance):
        def visit(self, *arg, visitor=None, **kw):
            self.instance.visit(*arg, visitor=visitor, **kw)
            self.local.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Mutate(_Nodes.Mutate):
        def visit(self, *arg, visitor=None, **kw):
            self.kind.visit(*arg, visitor=visitor, **kw)
            _visit_usable(self.usable, *arg, visitor=visitor, **kw)
            visitor(self)

    class ModuleHide(_Nodes.Hide):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class ModuleUse(_Nodes.Use):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Module(_Nodes.Module):
        def visit(self, *arg, visitor=None, **kw):
            for unit in self.body:
                unit.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Submodule(_Nodes.Submodule):
        def visit(self, *arg, visitor=None, **kw):
            self.module.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Suppress(_Nodes.Suppress):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Emit(_Nodes.Emit):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class StepStar(_Nodes.StepStar):
        pass

    class StepPlus(_Nodes.StepPlus):
        pass

    class StepNum(_Nodes.StepNum):
        pass

    class Only(_Nodes.Only):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Default(_Nodes.Default):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class PreBy(_Nodes.PreBy):
        pass

    class PreObvious(_Nodes.PreObvious):
        pass

    class PreOmitted(_Nodes.PreOmitted):
        pass

    class Explicit(_Nodes.Explicit):
        pass

    class Implicit(_Nodes.Implicit):
        pass

    class PreStep(_Nodes.PreStep):
        pass

    class PreHide(_Nodes.PreHide):
        pass

    class PreUse(_Nodes.PreUse):
        pass

    class PreDefine(_Nodes.PreDefine):
        pass

    class PreAssert(_Nodes.PreAssert):
        pass

    class PreSuffices(_Nodes.PreSuffices):
        pass

    class PreCase(_Nodes.PreCase):
        pass

    class PrePick(_Nodes.PrePick):
        pass

    class PreHave(_Nodes.PreHave):
        pass

    class PreTake(_Nodes.PreTake):
        pass

    class PreWitness(_Nodes.PreWitness):
        pass

    class PreQed(_Nodes.PreQed):
        pass

    class Axiom(_Nodes.Axiom):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            return visitor(self)

    class Theorem(_Nodes.Theorem):
        def visit(self, *arg, visitor=None, **kw):
            self.body.visit(*arg, visitor=visitor, **kw)
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Named(_Nodes.Named):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Unnamed(_Nodes.Unnamed):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    # Proofs

    class Obvious(_Nodes.Obvious):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Omitted(_Nodes.Omitted):
        def visit(self, *arg, visitor=None, **kw):
            self.omission.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class By(_Nodes.By):
        def visit(self, *arg, visitor=None, **kw):
            _visit_usable(self.usable, *arg, visitor=visitor, **kw)
            visitor(self)

    class Steps(_Nodes.Steps):
        def visit(self, *arg, visitor=None, **kw):
            for step in self.steps:
                step.visit(*arg, visitor=visitor, **kw)
            self.qed_step.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    # Proof steps

    class Hide(_Nodes.Hide):
        def visit(self, *arg, visitor=None, **kw):
            _visit_usable(self.usable, *arg, visitor=visitor, **kw)
            visitor(self)

    class Define(_Nodes.Define):
        def visit(self, *arg, visitor=None, **kw):
            for defn in self.definitions:
                defn.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Assert(_Nodes.Assert):
        def visit(self, *arg, visitor=None, **kw):
            self.sequent.visit(*arg, visitor=visitor, **kw)
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Suffices(_Nodes.Suffices):
        def visit(self, *arg, visitor=None, **kw):
            self.sequent.visit(*arg, visitor=visitor, **kw)
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Pcase(_Nodes.Pcase):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Pick(_Nodes.Pick):
        def visit(self, *arg, visitor=None, **kw):
            _visit_bounds(self.bounds, *arg, visitor=visitor, **kw)
            self.expr.visit(*arg, visitor=visitor, **kw)
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Use(_Nodes.Use):
        def visit(self, *arg, visitor=None, **kw):
            _visit_usable(self.usable, *arg, visitor=visitor, **kw)
            visitor(self)

    class Have(_Nodes.Have):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Take(_Nodes.Take):
        def visit(self, *arg, visitor=None, **kw):
            _visit_bounds(self.bounds, *arg, visitor=visitor, **kw)
            visitor(self)

    class Witness(_Nodes.Witness):
        def visit(self, *arg, visitor=None, **kw):
            for expr in self.exprs:
                expr.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Qed(_Nodes.Qed):
        def visit(self, *arg, visitor=None, **kw):
            self.proof.visit(*arg, visitor=visitor, **kw)
            visitor(self)

    class Dvar(_Nodes.Dvar):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Bstring(_Nodes.Bstring):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Bfloat(_Nodes.Bfloat):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class Bdef(_Nodes.Bdef):
        def visit(self, *arg, visitor=None, **kw):
            visitor(self)

    class BackendPragma(_Nodes.BackendPragma):
        def visit(self, *arg, visitor=None, **kw):
            self.expr.visit(*arg, visitor=visitor, **kw)
            for name, arg_ in self.backend_args:
                arg_.visit(*arg, visitor=visitor, **kw)
            visitor(self)
