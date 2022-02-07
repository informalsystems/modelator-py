"""Visitor pattern over TLA+ syntax trees."""
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
import copy

from .to_str import Nodes as _Nodes


def _visit_bounds(visitor, bounds, *arg, **kw):
    """Call the `visit` method of each bound."""
    bounds_ = list()
    for name, kind, dom in bounds:
        name_ = copy.copy(name)
        kind_ = visitor.visit(kind, *arg, **kw)
        dom_ = visitor.visit(dom, *arg, **kw)
        bound = (name_, kind_, dom_)
        bounds_.append(bound)
    return bounds_


def _visit_usable(visitor, usable, *arg, **kw):
    facts = list()
    for fact in usable["facts"]:
        fact_ = visitor.visit(fact, *arg, **kw)
        facts.append(fact_)
    defs = list()
    for defn in usable["defs"]:
        defn_ = visitor.visit(defn, *arg, **kw)
        defs.append(defn_)
    usable = dict(facts=facts, defs=defs)
    return usable


class NodeTransformer:
    def __init__(self):
        self.nodes = _Nodes

    def visit(self, node, *arg, **kw):
        """Call the implementation method for `node`.

        For each `node` of class named `ClsName`,
        there is a method named `visit_ClsName`.

        Override the `visit_*` methods to change
        the visitor's behavior, by subclassing it.
        """
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node, *arg, **kw)

    def visit_FALSE(self, node, *arg, **kw):
        return self.nodes.FALSE()

    def visit_TRUE(self, node, *arg, **kw):
        return self.nodes.TRUE()

    def visit_BOOLEAN(self, node, *arg, **kw):
        return self.nodes.BOOLEAN()

    def visit_STRING(self, node, *arg, **kw):
        return self.nodes.STRING()

    def visit_Implies(self, node, *arg, **kw):
        return self.nodes.Implies()

    def visit_Equiv(self, node, *arg, **kw):
        return self.nodes.Equiv()

    def visit_Conj(self, node, *arg, **kw):
        return self.nodes.Conj()

    def visit_Disj(self, node, *arg, **kw):
        return self.nodes.Disj()

    def visit_Neg(self, node, *arg, **kw):
        return self.nodes.Neg()

    def visit_Eq(self, node, *arg, **kw):
        return self.nodes.Eq()

    def visit_Neq(self, node, *arg, **kw):
        return self.nodes.Neq()

    def visit_SUBSET(self, node, *arg, **kw):
        return self.nodes.SUBSET()

    def visit_UNION(self, node, *arg, **kw):
        return self.nodes.UNION()

    def visit_DOMAIN(self, node, *arg, **kw):
        return self.nodes.DOMAIN()

    def visit_Subseteq(self, node, *arg, **kw):
        return self.nodes.Subseteq()

    def visit_Mem(self, node, *arg, **kw):
        return self.nodes.Mem()

    def visit_Notmem(self, node, *arg, **kw):
        return self.nodes.Notmem()

    def visit_Setminus(self, node, *arg, **kw):
        return self.nodes.Setminus()

    def visit_Cap(self, node, *arg, **kw):
        return self.nodes.Cap()

    def visit_Cup(self, node, *arg, **kw):
        return self.nodes.Cup()

    def visit_Prime(self, node, *arg, **kw):
        return self.nodes.Prime()

    def visit_LeadsTo(self, node, *arg, **kw):
        return self.nodes.LeadsTo()

    def visit_ENABLED(self, node, *arg, **kw):
        return self.nodes.ENABLED()

    def visit_UNCHANGED(self, node, *arg, **kw):
        return self.nodes.UNCHANGED()

    def visit_Cdot(self, node, *arg, **kw):
        return self.nodes.Cdot()

    def visit_WhilePlus(self, node, *arg, **kw):
        return self.nodes.WhilePlus()

    def visit_Box(self, node, *arg, **kw):
        return self.nodes.Box()

    def visit_Diamond(self, node, *arg, **kw):
        return self.nodes.Diamond()

    def visit_Opaque(self, node, *arg, **kw):
        return self.nodes.Opaque(node.name)

    def visit_Internal(self, node, *arg, **kw):
        return self.nodes.Internal(node.value)

    def visit_Apply(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        operands = list()
        for operand in node.operands:
            res = self.visit(operand, *arg, **kw)
            operands.append(res)
        return self.nodes.Apply(op, operands)

    def visit_Function(self, node, *arg, **kw):
        bounds = _visit_bounds(self, node.bounds, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Function(bounds, expr)

    def visit_FunctionApply(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        args = list()
        for arg_ in node.args:
            res = self.visit(arg_, *arg, **kw)
            args.append(res)
        return self.nodes.FunctionApply(op, args)

    def visit_ShapeExpr(self, node, *arg, **kw):
        return self.nodes.ShapeExpr()

    def visit_ShapeOp(self, node, *arg, **kw):
        return self.nodes.ShapeOp(node.arity)

    def visit_Lambda(self, node, *arg, **kw):
        name_shapes = list()
        for name, shape in node.name_shapes:
            name_ = copy.copy(name)
            shape_ = self.visit(shape, *arg, **kw)
            name_shapes.append((name_, shape_))
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Lambda(name_shapes, expr)

    def visit_TemporalSub(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        action = self.visit(node.action, *arg, **kw)
        subscript = self.visit(node.subscript, *arg, **kw)
        return self.nodes.TemporalSub(op, action, subscript)

    def visit_Sub(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        action = self.visit(node.action, *arg, **kw)
        subscript = self.visit(node.subscript, *arg, **kw)
        return self.nodes.Sub(op, action, subscript)

    def visit_BoxOp(self, node, *arg, **kw):
        return self.nodes.BoxOp()

    def visit_DiamondOp(self, node, *arg, **kw):
        return self.nodes.DiamondOp()

    def visit_Dot(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        string = copy.copy(node.string)
        return self.nodes.Dot(expr, string)

    def visit_Parens(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        pform = self.visit(node.pform, *arg, **kw)
        return self.nodes.Parens(expr, pform)

    def visit_Syntax(self, node, *arg, **kw):
        return self.nodes.Syntax()

    def visit_NamedLabel(self, node, *arg, **kw):
        string = copy.copy(node.string)
        name_list = [copy.copy(name) for name in node.name_list]
        return self.nodes.NamedLabel(string, name_list)

    def visit_IndexedLabel(self, node, *arg, **kw):
        string = copy.copy(node.string)
        name_int_list = list()
        for name, i in node.name_int_list:
            name_ = copy.copy(name)
            i_ = copy.copy(i)
            pair = (name_, i_)
            name_int_list.append(pair)
        return self.nodes.IndexedLabel(string, name_int_list)

    def visit_If(self, node, *arg, **kw):
        test = self.visit(node.test, *arg, **kw)
        then = self.visit(node.then, *arg, **kw)
        else_ = self.visit(node.else_, *arg, **kw)
        return self.nodes.If(test, then, else_)

    def visit_Let(self, node, *arg, **kw):
        definitions = list()
        for defn in node.definitions:
            defn_ = self.visit(defn, *arg, **kw)
            definitions.append(defn_)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Let(definitions, expr)

    def visit_Forall(self, node, *arg, **kw):
        return self.nodes.Forall()

    def visit_Exists(self, node, *arg, **kw):
        return self.nodes.Exists()

    def visit_RigidQuantifier(self, node, *arg, **kw):
        quantifier = self.visit(node.quantifier, *arg, **kw)
        bounds = _visit_bounds(self, node.bounds, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.RigidQuantifier(quantifier, bounds, expr)

    def visit_TemporalQuantifier(self, node, *arg, **kw):
        quantifier = self.visit(node.quantifier, *arg, **kw)
        variables = [copy.copy(var) for var in node.variables]
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.TemporalQuantifier(quantifier, variables, expr)

    def visit_Choose(self, node, *arg, **kw):
        if node.bound is None:
            bound = None
        else:
            bound = self.visit(node.bound, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Choose(bound, expr)

    def visit_Case(self, node, *arg, **kw):
        arms = list()
        for guard, expr in node.arms:
            guard_ = self.visit(guard, *arg, **kw)
            expr_ = self.visit(expr, *arg, **kw)
            arms.append((guard_, expr_))
        other = self.visit(node.other, *arg, **kw)
        return self.nodes.Case(arms, other)

    def visit_SetEnum(self, node, *arg, **kw):
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        return self.nodes.SetEnum(exprs)

    def visit_SetSt(self, node, *arg, **kw):
        name = copy.copy(node.name)
        bound = self.visit(node.bound, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.SetSt(name, bound, expr)

    def visit_SetOf(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        bounds = _visit_bounds(self, node.boundeds, *arg, **kw)
        return self.nodes.SetOf(expr, bounds)

    def visit_And(self, node, *arg, **kw):
        return self.nodes.And()

    def visit_Or(self, node, *arg, **kw):
        return self.nodes.Or()

    def visit_List(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        return self.nodes.List(op, exprs)

    def visit_Record(self, node, *arg, **kw):
        items = list()
        for name, expr in node.items:
            name_ = copy.copy(name)
            expr_ = self.visit(expr, *arg, **kw)
            pair = (name_, expr_)
            items.append(pair)
        return self.nodes.Record(items)

    def visit_RecordSet(self, node, *arg, **kw):
        items = list()
        for name, expr in node.items:
            name_ = copy.copy(name)
            expr_ = self.visit(expr, *arg, **kw)
            pair = (name_, expr_)
            items.append(pair)
        return self.nodes.RecordSet(items)

    def visit_Except_dot(self, node, *arg, **kw):
        name = copy.copy(node.name)
        return self.nodes.Except_dot(name)

    def visit_Except_apply(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Except_apply(expr)

    def visit_Except(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        exspec_list = list()
        for expoints, e in node.exspec_list:
            e_ = self.visit(e, *arg, **kw)
            expoints_ = list()
            for expoint in expoints:
                expoint_ = self.visit(expoint, *arg, **kw)
                expoints_.append(expoint_)
            pair = (expoints_, e_)
            exspec_list.append(pair)
        return self.nodes.Except(expr, exspec_list)

    def visit_Domain(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Domain(expr)

    def visit_NoDomain(self, node, *arg, **kw):
        return self.nodes.NoDomain()

    def visit_Ditto(self, node, *arg, **kw):
        return self.nodes.Ditto()

    def visit_Bounded(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        vis = self.visit(node.visibility, *arg, **kw)
        return self.nodes.Bounded(expr, vis)

    def visit_Unbounded(self, node, *arg, **kw):
        return self.nodes.Unbounded()

    def visit_Visible(self, node, *arg, **kw):
        return self.nodes.Visible()

    def visit_Hidden(self, node, *arg, **kw):
        return self.nodes.Hidden()

    def visit_NotSet(self, node, *arg, **kw):
        return self.nodes.NotSet()

    def visit_At(self, node, *arg, **kw):
        return self.nodes.At(node.boolean)

    def visit_Arrow(self, node, *arg, **kw):
        expr1 = self.visit(node.expr1, *arg, **kw)
        expr2 = self.visit(node.expr2, *arg, **kw)
        return self.nodes.Arrow(expr1, expr2)

    def visit_Tuple(self, node, *arg, **kw):
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        return self.nodes.Tuple(exprs)

    def visit_Bang(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        sel_list = list()
        for sel in node.sel_list:
            sel_ = self.visit(sel, *arg, **kw)
            sel_list.append(sel_)
        return self.nodes.Bang(expr, sel_list)

    def visit_WeakFairness(self, node, *arg, **kw):
        return self.nodes.WeakFairness()

    def visit_StrongFairness(self, node, *arg, **kw):
        return self.nodes.StrongFairness()

    def visit_String(self, node, *arg, **kw):
        return self.nodes.String(node.value)

    def visit_Number(self, node, *arg, **kw):
        return self.nodes.Number(node.integer, node.mantissa)

    def visit_Fairness(self, node, *arg, **kw):
        op = self.visit(node.op, *arg, **kw)
        subscript = self.visit(node.subscript, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Fairness(op, subscript, expr)

    def visit_SelLab(self, node, *arg, **kw):
        string = copy.copy(node.string)
        exprs = list()
        for e in node.exprs:
            expr = self.visit(e, *arg, **kw)
            exprs.append(expr)
        return self.nodes.SelLab(string, exprs)

    def visit_SelInst(self, node, *arg, **kw):
        exprs = list()
        for e in node.exprs:
            expr = self.visit(e, *arg, **kw)
            exprs.append(expr)
        return self.nodes.SelInst(exprs)

    def visit_SelNum(self, node, *arg, **kw):
        return self.nodes.SelNum(node.num)

    def visit_SelLeft(self, node, *arg, **kw):
        return self.nodes.SelLeft()

    def visit_SelRight(self, node, *arg, **kw):
        return self.nodes.SelRight()

    def visit_SelDown(self, node, *arg, **kw):
        return self.nodes.SelDown()

    def visit_SelAt(self, node, *arg, **kw):
        return self.nodes.SelAt()

    def visit_Sequent(self, node, *arg, **kw):
        context = list()
        for item in node.context:
            item_ = self.visit(item, *arg, **kw)
            context.append(item_)
        goal = self.visit(node.goal, *arg, **kw)
        return self.nodes.Sequent(context, goal)

    def visit_Fact(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        vis = self.visit(node.visibility, *arg, **kw)
        time = self.visit(node.time, *arg, **kw)
        return self.nodes.Fact(expr, vis, time)

    def visit_Flex(self, node, *arg, **kw):
        name = copy.copy(node.name)
        return self.nodes.Flex(name)

    def visit_Fresh(self, node, *arg, **kw):
        name = copy.copy(node.name)
        shape = self.visit(node.shape, *arg, **kw)
        kind = self.visit(node.kind, *arg, **kw)
        domain = self.visit(node.domain, *arg, **kw)
        return self.nodes.Fresh(name, shape, kind, domain)

    def visit_Constant(self, node, *arg, **kw):
        return self.nodes.Constant()

    def visit_State(self, node, *arg, **kw):
        return self.nodes.State()

    def visit_Action(self, node, *arg, **kw):
        return self.nodes.Action()

    def visit_Temporal(self, node, *arg, **kw):
        return self.nodes.Temporal()

    def visit_OperatorDef(self, node, *arg, **kw):
        name = copy.copy(node.name)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.OperatorDef(name, expr)

    def visit_Instance(self, node, *arg, **kw):
        name = copy.copy(node.name)
        args = [copy.copy(arg_) for arg_ in node.args]
        module = copy.copy(node.module)
        sub = list()
        for name, expr in node.sub:
            name_ = copy.copy(name)
            expr_ = self.visit(expr, *arg, **kw)
            sub.append((name_, expr_))
        return self.nodes.Instance(name, args, module, sub)

    def visit_Constants(self, node, *arg, **kw):
        declarations = list()
        for name, shape in node.declarations:
            name_ = copy.copy(name)
            shape_ = self.visit(shape, *arg, **kw)
            pair = (name_, shape_)
            declarations.append(pair)
        return self.nodes.Constants(declarations)

    def visit_Variables(self, node, *arg, **kw):
        declarations = [copy.copy(name) for name in node.declarations]
        return self.nodes.Variables(declarations)

    def visit_Recursives(self, node, *arg, **kw):
        declarations = list()
        for name, shape in node.declarations:
            name_ = copy.copy(name)
            shape_ = self.visit(shape, *arg, **kw)
            pair = (name_, shape_)
            declarations.append(pair)
        return self.nodes.Recursives(declarations)

    def visit_Local(self, node, *arg, **kw):
        return self.nodes.Local()

    def visit_Export(self, node, *arg, **kw):
        return self.nodes.Export()

    def visit_User(self, node, *arg, **kw):
        return self.nodes.User()

    def visit_Definition(self, node, *arg, **kw):
        defn = self.visit(node.definition, *arg, **kw)
        wd = self.visit(node.wheredef, *arg, **kw)
        vis = self.visit(node.visibility, *arg, **kw)
        local = self.visit(node.local, *arg, **kw)
        return self.nodes.Definition(defn, wd, vis, local)

    def visit_AnonymousInstance(self, node, *arg, **kw):
        instance = self.visit(node.instance, *arg, **kw)
        local = self.visit(node.local, *arg, **kw)
        return self.nodes.AnonymousInstance(instance, local)

    def visit_Mutate(self, node, *arg, **kw):
        kind = self.visit(node.kind, *arg, **kw)
        usable = _visit_usable(self, node.usable, *arg, **kw)
        return self.nodes.Mutate(kind, usable)

    def visit_ModuleHide(self, node, *arg, **kw):
        return self.nodes.ModuleHide()

    def visit_ModuleUse(self, node, *arg, **kw):
        return self.nodes.ModuleUse(node.boolean)

    def visit_Module(self, node, *arg, **kw):
        name = copy.copy(node.name)
        extendees = [copy.copy(s) for s in node.extendees]
        instancees = [copy.copy(s) for s in node.instancees]
        body = list()
        for unit in node.body:
            unit_ = self.visit(unit, *arg, **kw)
            body.append(unit_)
        return self.nodes.Module(name, extendees, instancees, body)

    def visit_Submodule(self, node, *arg, **kw):
        module = self.visit(node.module, *arg, **kw)
        return self.nodes.Submodule(module)

    def visit_Suppress(self, node, *arg, **kw):
        return self.nodes.Suppress()

    def visit_Emit(self, node, *arg, **kw):
        return self.nodes.Emit()

    def visit_Only(self, node, *arg, **kw):
        return self.nodes.Only()

    def visit_Default(self, node, *arg, **kw):
        return self.nodes.Default()

    def visit_Explicit(self, node, *arg, **kw):
        return self.nodes.Explicit()

    def visit_Implicit(self, node, *arg, **kw):
        return self.nodes.Implicit()

    def visit_Axiom(self, node, *arg, **kw):
        if node.name is None:
            name = None
        else:
            name = copy.copy(node.name)
        expr = self.visit(node.expr, *arg, **kw)
        return self.nodes.Axiom(name, expr)

    def visit_Theorem(self, node, *arg, **kw):
        if node.name is None:
            name = None
        else:
            name = copy.copy(node.name)
        body = self.visit(node.body, *arg, **kw)
        proof = self.visit(node.proof, *arg, **kw)
        return self.nodes.Theorem(name, body, proof)

    def visit_Named(self, node, *arg, **kw):
        level = copy.copy(node.level)
        label = copy.copy(node.label)
        return self.nodes.Named(level, label, node.boolean)

    def visit_Unnamed(self, node, *arg, **kw):
        level = copy.copy(node.level)
        uuid = copy.copy(node.uuid)
        return self.nodes.Unnamed(level, uuid)

    def visit_Obvious(self, node, *arg, **kw):
        return self.nodes.Obvious()

    def visit_Omitted(self, node, *arg, **kw):
        omission = self.visit(node.omission, *arg, **kw)
        return self.nodes.Omitted(omission)

    def visit_By(self, node, *arg, **kw):
        usable = _visit_usable(self, node, *arg, **kw)
        return self.nodes.By(usable, node.only)

    def visit_Steps(self, node, *arg, **kw):
        steps = list()
        for step in node.steps:
            step_ = self.visit(step, *arg, **kw)
            steps.append(step_)
        qed_step = self.visit(node.qed_step, *arg, **kw)
        return self.nodes.Steps(steps, qed_step)

    def visit_Hide(self, node, *arg, **kw):
        usable = _visit_usable(self, node.usable, *arg, **kw)
        res = self.nodes.Hide(usable)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Define(self, node, *arg, **kw):
        definitions = list()
        for defn in node.definitions:
            defn_ = self.visit(defn, *arg, **kw)
            definitions.append(defn_)
        res = self.nodes.Define(definitions)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Assert(self, node, *arg, **kw):
        sequent = self.visit(node.sequent, *arg, **kw)
        proof = self.visit(node.proof, *arg, **kw)
        res = self.nodes.Assert(sequent, proof)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Suffices(self, node, *arg, **kw):
        sequent = self.visit(node.sequent, *arg, **kw)
        proof = self.visit(node.proof, *arg, **kw)
        res = self.nodes.Suffices(sequent, proof)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Pcase(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        proof = self.visit(node.proof, *arg, **kw)
        res = self.nodes.Pcase(expr, proof)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Pick(self, node, *arg, **kw):
        bounds = _visit_bounds(self, node.bounds, *arg, **kw)
        expr = self.visit(node.expr, *arg, **kw)
        proof = self.visit(node.proof, *arg, **kw)
        res = self.nodes.Pick(bounds, expr, proof)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Use(self, node, *arg, **kw):
        usable = _visit_usable(self, node.usable, *arg, **kw)
        res = self.nodes.Use(usable, node.only)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Have(self, node, *arg, **kw):
        expr = self.visit(node.expr, *arg, **kw)
        res = self.nodes.Have(expr)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Take(self, node, *arg, **kw):
        bounds = _visit_bounds(self, node.bounds, *arg, **kw)
        res = self.nodes.Take(bounds)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Witness(self, node, *arg, **kw):
        exprs = list()
        for expr in node.exprs:
            expr_ = self.visit(expr, *arg, **kw)
            exprs.append(expr_)
        res = self.nodes.Witness(exprs)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Qed(self, node, *arg, **kw):
        proof = self.visit(node.proof, *arg, **kw)
        res = self.nodes.Qed(proof)
        res.step_number = self.visit(node.step_number, *arg, **kw)
        return res

    def visit_Dvar(self, node, *arg, **kw):
        value = copy.copy(node.value)
        return self.nodes.Dvar(value)

    def visit_Bstring(self, node, *arg, **kw):
        value = copy.copy(node.value)
        return self.nodes.Bstring(value)

    def visit_Bfloat(self, node, *arg, **kw):
        value = copy.copy(node.value)
        return self.nodes.Bfloat(value)

    def visit_Bdef(self, node, *arg, **kw):
        return self.nodes.Bdef()

    def visit_BackendPragma(self, node, *arg, **kw):
        name = copy.copy(node.name)
        expr = self.visit(node.expr, *arg, **kw)
        backend_args = list()
        for s, backend_arg in node.backend_args:
            s_ = copy.copy(s)
            backend_arg_ = self.visit(backend_arg, *arg, **kw)
            pair = (s_, backend_arg_)
            backend_args.append(pair)
        return self.BackendPragma(name, expr, backend_args)
