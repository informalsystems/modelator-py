"""String representation of TLA+ syntax tree."""
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
import math
import textwrap

from . import _combinators as pco
from . import _optable
from .ast import Nodes as _Nodes

LINE_WIDTH = 80
INDENT_WIDTH = 4


def _box_dimensions(string):
    r"""Return width, height of `string`.

    Width is the number of characters in the
    longest line. Height is the number of lines,
    which includes a newline (`\n`) at the end.
    """
    lines = string.split("\n")  # counts `\n` at end
    widths = [len(line) for line in lines]
    width = max(widths)
    height = len(lines)
    return width, height


def _glue_prefix_box(prefix, box, indent_width=None):
    """Concatenate strings with proper indentation."""
    lines = box.split("\n")
    if indent_width is None:
        prefix_lines = prefix.split("\n")
        indent_width = len(prefix_lines[-1])
    indent = indent_width * " "
    res_lines = [prefix + lines[0]]
    res_lines.extend(indent + line for line in lines[1:])
    res = "\n".join(res_lines)
    return res


def _concatenate_boxes(
    box1, box2, width, indent_width=INDENT_WIDTH, alt_indent_width=INDENT_WIDTH
):
    """Concatenate `box1` and `box2` within `width`.

    Introduce a newline if the result would be
    wider than `width`. Use `indent_width` to indent
    `box2` if concatenated without newline,
    otherwise `alt_indent_width`.
    """
    res = _glue_prefix_box(box1, box2, indent_width)
    res_width, _ = _box_dimensions(res)
    if res_width <= width:
        return res
    res = _glue_prefix_box(box1, "\n" + box2, alt_indent_width)
    return res


def _join_boxes_sep(boxes, sep):
    """Join boxes by iterative gluing."""
    res = ""
    for box in boxes:
        if res:
            res += sep
        res = _glue_prefix_box(res, box)
    return res


def _format_lambda_signature(name_shapes, width):
    """Return `str` of `LAMBDA` signature."""
    args = list()
    for name, shape in name_shapes:
        shape_str = shape.to_str()
        s = name + shape_str
        args.append(s)
    res = ", ".join(args)
    res_width, _ = _box_dimensions(res)
    if res_width > width:
        res = ",\n".join(args)
    return res


def _format_boundeds(bounds, *arg, width=None, **kw):
    """Return `str` of `bounds`.

    `bounds` is a `list` of
    `(str, Nodes.Constant, expr)`.
    """
    bound_str = list()
    last_dom = None
    for name, kind, dom in bounds:
        assert isinstance(kind, Nodes.Constant), kind
        if isinstance(dom, Nodes.Ditto):
            dom = last_dom
        else:
            last_dom = dom
        dom = dom.to_str(*arg, width=width, **kw)
        bound = _glue_prefix_box(str(name) + " \\in ", dom)
        bound_str.append(bound)
    widths = [_box_dimensions(s)[0] for s in bound_str]
    total_width = sum(widths)
    if total_width > width:
        bounds_str = ",\n".join(bound_str)
    else:
        bounds_str = ", ".join(bound_str)
    return bounds_str


def _format_bounds(bounds_list, *arg, width=None, **kw):
    """Return `str` of `bounds_list`.

    `bounds_list` is a `list` of
    `(str, Nodes.Constant,
    Nodes.Domain | Nodes.NoDomain | Nodes.Ditto`.
    """
    bounds = list()
    old_dom = None
    for name, kind, dom in bounds_list:
        assert isinstance(kind, Nodes.Constant), kind
        if isinstance(dom, Nodes.Domain):
            bound = dom.expr.to_str(*arg, width=width, **kw)
            bound = f"{name} \\in {bound}"
            old_dom = dom
        elif isinstance(dom, Nodes.NoDomain):
            bound = str(name)
        elif isinstance(dom, Nodes.Ditto):
            bound = old_dom.expr.to_str(*arg, width=width, **kw)
            bound = f"{name} \\in {bound}"
        else:
            raise ValueError(dom)
        bounds.append(bound)
    bounds_str = ", ".join(bounds)
    bounds_str_width, _ = _box_dimensions(bounds_str)
    if bounds_str_width > width:
        bounds_str = ",\n".join(bounds)
    return bounds_str


def _format_definitions(definitions, *arg, width=None, **kw):
    r"""Return `str` of `definitions`.

    Concatenate vertically the `to_str`
    representations of `definitions` by
    inserting newlines `\n`.

    @type definitions: `list` of expr
    """
    defns = list()
    for defn in definitions:
        defn_str = defn.to_str(*arg, width=width, **kw)
        defns.append(defn_str)
    defns_str = "\n".join(defns)
    return defns_str


def _format_usable(usable, prefix, *arg, width=None, **kw):
    """Return `str` of `usable` with `prefix`.

    @type usable: `dict(facts=list of expr,
                        defs=list of Nodes.Dvar)`
    @type prefix: `str`
    """
    # facts
    facts = list()
    for f in usable["facts"]:
        fact = f.to_str(*arg, width=width, **kw)
        facts.append(fact)
    facts_str = ", ".join(facts)
    new_width = width - len(prefix) - INDENT_WIDTH
    facts_str = textwrap.fill(facts_str, width=new_width)
    # defs
    defs = list()
    for d in usable["defs"]:
        defn = d.to_str(*arg, width=width, **kw)
        defs.append(defn)
    defs_str = ", ".join(defs)
    new_width = width - len("DEF ") - len(prefix) - INDENT_WIDTH
    defs_str = textwrap.fill(defs_str, width=new_width)
    # combine
    if defs:
        defs_str = f"DEF {defs_str}"
    res = _glue_prefix_box(prefix, " " + facts_str, indent_width=INDENT_WIDTH)
    res = _glue_prefix_box(res, " " + defs_str, indent_width=INDENT_WIDTH)
    res_width, _ = _box_dimensions(res)
    if res_width > width:
        res = _glue_prefix_box(prefix + " ", facts_str, indent_width=len(prefix) + 1)
        res = _glue_prefix_box(res, "\n" + defs_str, indent_width=len(prefix) + 1)
    return res


def _print_overwide_lines(text, max_width):
    """Print `text` lines wider than `max_width`.

    Print 5 lines of context before and after the
    widest lines in `text`. Print the width of the
    widest line in `text`.
    """
    width, _ = _box_dimensions(text)
    print(f"Width of text: {width}")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if len(line) > max_width:
            s = "\n".join(lines[i - 5 : i + 5])
            print(s)


class Nodes(_Nodes):
    """Translating TLA+ AST nodes to strings."""

    # Builtin operators

    class FALSE(_Nodes.FALSE):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("FALSE"), width
            return "FALSE"

    class TRUE(_Nodes.TRUE):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("TRUE"), width
            return "TRUE"

    class BOOLEAN(_Nodes.BOOLEAN):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("BOOLEAN"), width
            return "BOOLEAN"

    class STRING(_Nodes.STRING):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("STRING"), width
            return "STRING"

    class Implies(_Nodes.Implies):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("=>"), width
            return "=>"

    class Equiv(_Nodes.Equiv):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("<=>"), width
            return "<=>"

    class Conj(_Nodes.Conj):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("/\\"), width
            return "/\\"

    class Disj(_Nodes.Disj):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\/"), width
            return "\\/"

    class Neg(_Nodes.Neg):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("~"), width
            return "~"

    class Eq(_Nodes.Eq):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("="), width
            return "="

    class Neq(_Nodes.Neq):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("#"), width
            return "#"

    class SUBSET(_Nodes.SUBSET):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("SUBSET"), width
            return "SUBSET"

    class UNION(_Nodes.UNION):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("UNION"), width
            return "UNION"

    class DOMAIN(_Nodes.DOMAIN):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("DOMAIN"), width
            return "DOMAIN"

    class Subseteq(_Nodes.Subseteq):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\subseteq"), width
            return "\\subseteq"

    class Mem(_Nodes.Mem):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\in"), width
            return "\\in"

    class Notmem(_Nodes.Notmem):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\notin"), width
            return "\\notin"

    class Setminus(_Nodes.Setminus):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\"), width
            return "\\"

    class Cap(_Nodes.Cap):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\cap"), width
            return "\\cap"

    class Cup(_Nodes.Cup):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\cup"), width
            return "\\cup"

    class Prime(_Nodes.Prime):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("'"), width
            return "'"

    class LeadsTo(_Nodes.LeadsTo):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("~>"), width
            return "~>"

    class ENABLED(_Nodes.ENABLED):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("ENABLED"), width
            return "ENABLED"

    class UNCHANGED(_Nodes.UNCHANGED):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("UNCHANGED"), width
            return "UNCHANGED"

    class Cdot(_Nodes.Cdot):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("\\cdot"), width
            return "\\cdot"

    class WhilePlus(_Nodes.WhilePlus):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("-+->"), width
            return "-+->"

    class Box(_Nodes.Box):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("[]"), width
            return "[]"

    class Diamond(_Nodes.Diamond):
        def to_str(self, *arg, width=None, **kw):
            assert width >= len("<>"), width
            return "<>"

    class Opaque(_Nodes.Opaque):
        def to_str(self, *arg, width=None, **kw):
            # assert width >= len(self.name), width
            return self.name

    class Internal(_Nodes.Internal):
        def to_str(self, *arg, width=None, **kw):
            return self.value.to_str(*arg, width=width, **kw)

    class Apply(_Nodes.Apply):
        def to_str(self, *arg, width=None, **kw):
            op = self.op
            args = self.operands
            # n = 1 + len(args)
            # new_width = math.floor(width / n)
            op_str = op.to_str(*arg, width=width, **kw)
            arg_strings = [arg_.to_str(*arg, width=width, **kw) for arg_ in args]
            if op_str in _optable.optable:
                tlaops = _optable.optable[op_str]
                fixities = [u.fix for u in tlaops]
            else:
                fixities = None
            if op_str == "-.":
                op_str = "-"
            n_args = len(arg_strings)
            if fixities is None:
                pass
            elif n_args == 2:
                assert pco.any_isinstance(fixities, _optable.Infix), (
                    op,
                    args,
                    op_str,
                    arg_strings,
                    fixities,
                )
                res = f"{arg_strings[0]} {op_str} {arg_strings[1]}"
                res_width, _ = _box_dimensions(res)
                if res_width > width:
                    res = _glue_prefix_box(arg_strings[0], " " + op_str)
                    res = _glue_prefix_box(res + "\n", arg_strings[1])
                return res
            elif n_args != 1:
                raise ValueError(
                    f"operator `{op_str}` applied to "
                    f"{n_args} arguments (expected 1)"
                )
            elif pco.any_isinstance(fixities, _optable.Prefix):
                assert len(arg_strings) == 1, arg_strings
                assert not pco.any_isinstance(fixities, _optable.Postfix), op_str
                return f"{op_str} {arg_strings[0]}"
            elif pco.any_isinstance(fixities, _optable.Postfix):
                assert len(arg_strings) == 1, arg_strings
                assert not pco.any_isinstance(fixities, _optable.Prefix), op_str
                return f"{arg_strings[0]}{op_str}"
            args_str = ", ".join(arg_strings)
            res = f"{op_str}({args_str})"
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                args_str = ",\n".join("    " + arg for arg in arg_strings)
                res = f"{op_str}(\n{args_str})"
            return res

    class Function(_Nodes.Function):
        def to_str(self, *arg, width=None, **kw):
            new_width = width - INDENT_WIDTH
            bounds_str = _format_boundeds(self.bounds, *arg, width=new_width, **kw)
            expr = self.expr.to_str(*arg, width=new_width, **kw)
            part1 = _glue_prefix_box("[", bounds_str, indent_width=INDENT_WIDTH)
            # combine with expr
            res = _concatenate_boxes(
                part1 + " |-> ", expr + "]", width, INDENT_WIDTH, INDENT_WIDTH
            )
            return res

    class FunctionApply(_Nodes.FunctionApply):
        def to_str(self, *arg, width=None, **kw):
            op = self.op.to_str(*arg, width=width, **kw)
            args = [arg_.to_str(*arg, width=width, **kw) for arg_ in self.args]
            args_str = ", ".join(args)
            res = f"{op}[{args_str}]"
            res_width, _ = _box_dimensions(res)
            if res_width <= width:
                return res
            assert res_width > width, (res_width, width)
            args_str = ",\n".join(
                [arg_.to_str(*arg, width=width, **kw) for arg_ in self.args]
            )
            res = f"{op}[{args_str}]"
            return res

    class ShapeExpr(_Nodes.ShapeExpr):
        def to_str(self, *arg, width=None, **kw):
            return ""

    class ShapeOp(_Nodes.ShapeOp):
        def to_str(self, *arg, width=None, **kw):
            args = ["_"] * self.arity
            s = ", ".join(args)
            return f"({s})"

    class Lambda(_Nodes.Lambda):
        def to_str(self, *arg, width=None, **kw):
            args = _format_lambda_signature(self.name_shapes, width)
            expr = self.expr.to_str(width=width)
            s = _glue_prefix_box("LAMBDA(", args)
            s = _glue_prefix_box(s + "):", expr)
            return s

    class TemporalSub(_Nodes.TemporalSub):
        def to_str(self, *arg, **kw):
            action = self.action.to_str(*arg, **kw)
            sub = self.subscript.to_str(*arg, **kw)
            if isinstance(self.op, Nodes.BoxOp):
                res = f"[][{action}]_{sub}"
            elif isinstance(self.op, Nodes.DiamondOp):
                res = f"<><<{action}>>_{sub}"
            else:
                raise ValueError(self.op)
            return res

    class Sub(_Nodes.Sub):
        def to_str(self, *arg, **kw):
            action = self.action.to_str(*arg, **kw)
            sub = self.subscript.to_str(*arg, **kw)
            if isinstance(self.op, Nodes.BoxOp):
                res = f"[{action}]_{sub}"
            elif isinstance(self.op, Nodes.DiamondOp):
                res = f"<<{action}>>_{sub}"
            else:
                raise ValueError(self.op)
            return res

    class BoxOp(_Nodes.BoxOp):
        pass

    class DiamondOp(_Nodes.DiamondOp):
        pass

    class Dot(_Nodes.Dot):
        def to_str(self, *arg, width=None, **kw):
            expr = self.expr.to_str(*arg, width=width, **kw)
            string = str(self.string)
            return f"{expr}.{string}"

    class Parens(_Nodes.Parens):
        def to_str(self, *arg, width=None, **kw):
            new_width = width - len("()")
            expr = self.expr.to_str(*arg, width=new_width, **kw)
            if isinstance(self.pform, Nodes.Syntax):
                return f"({expr})"
            elif isinstance(self.pform, Nodes.IndexedLabel):
                label = self.pform.to_str(*arg, **kw)
                return f"{label}::{expr}"
            elif isinstance(self.pform, Nodes.NamedLabel):
                label = self.pform.to_str(*arg, **kw)
                return f"{label}::{expr}"
            else:
                raise ValueError(self.pform)

    class Syntax(_Nodes.Syntax):
        pass

    class NamedLabel(_Nodes.NamedLabel):
        def to_str(self, *arg, width=None, **kw):
            if self.name_list:
                args = ", ".join(self.name_list)
                args = f"({args})"
            else:
                args = ""
            return f"{self.string}{args}"

    class IndexedLabel(_Nodes.IndexedLabel):
        def to_str(self, *arg, width=None, **kw):
            assert not self.name_int_list, self.name_int_list
            return str(self.string)

    class If(_Nodes.If):
        def to_str(self, *arg, width=None, **kw):
            test = self.test.to_str(*arg, width=width, **kw)
            then = self.then.to_str(*arg, width=width, **kw)
            else_ = self.else_.to_str(*arg, width=width, **kw)
            res = f"IF {test} THEN {then} " f"ELSE {else_}"
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                res = _glue_prefix_box(
                    "IF " + test, "\nTHEN " + then, indent_width=INDENT_WIDTH
                )
                res = _glue_prefix_box(
                    res, "\nELSE " + else_, indent_width=INDENT_WIDTH
                )
            return res

    class Let(_Nodes.Let):
        def to_str(self, *arg, width=None, **kw):
            defns_str = _format_definitions(self.definitions, *arg, width=width, **kw)
            expr = self.expr.to_str(*arg, width=width, **kw)
            indent_width = len("LET ")
            res = _glue_prefix_box("\nLET", "\n" + defns_str, indent_width=indent_width)
            res += "\nIN "
            res = _glue_prefix_box(res, "\n" + expr, indent_width=indent_width)
            return res

    class Forall(_Nodes.Forall):
        pass

    class Exists(_Nodes.Exists):
        pass

    class RigidQuantifier(_Nodes.RigidQuantifier):
        def to_str(self, *arg, width=None, **kw):
            if isinstance(self.quantifier, Nodes.Forall):
                quantifier = "\\A"
            elif isinstance(self.quantifier, Nodes.Exists):
                quantifier = "\\E"
            else:
                raise ValueError(self.quantifier)
            # bounds
            bounds_width = width - len(quantifier) - len(" :")
            bounds_str = _format_bounds(self.bounds, *arg, width=bounds_width, **kw)
            # expr
            expr_width = width - INDENT_WIDTH
            expr = self.expr.to_str(*arg, width=expr_width, **kw)
            # combine
            res = _concatenate_boxes(
                quantifier + " ", bounds_str + ":  ", width, INDENT_WIDTH, INDENT_WIDTH
            )
            res = _concatenate_boxes(res, expr, width, INDENT_WIDTH, INDENT_WIDTH)
            return res

    class TemporalQuantifier(_Nodes.TemporalQuantifier):
        def to_str(self, *arg, width=None, **kw):
            if isinstance(self.quantifier, Nodes.Forall):
                quantifier = "\\AA"
            elif isinstance(self.quantifier, Nodes.Exists):
                quantifier = "\\EE"
            else:
                raise ValueError(self.quantifier)
            # variables
            vars_width = width - len(quantifier) - len(":  ")
            assert vars_width <= width - INDENT_WIDTH, (vars_width, width, INDENT_WIDTH)
            vars_str = ", ".join(self.variables)
            vars_str = textwrap.fill(vars_str, width=vars_width)
            qprefix = _concatenate_boxes(
                quantifier + " ", vars_str + ":  ", width, INDENT_WIDTH, INDENT_WIDTH
            )
            # expr
            expr_width = width - INDENT_WIDTH
            expr = self.expr.to_str(*arg, width=expr_width, **kw)
            # combine
            res = _concatenate_boxes(qprefix, expr, width, INDENT_WIDTH, INDENT_WIDTH)
            return res

    class Choose(_Nodes.Choose):
        def to_str(self, *arg, width=None, **kw):
            name = str(self.name)
            expr_width = width - INDENT_WIDTH
            expr = self.expr.to_str(*arg, width=expr_width, **kw)
            if self.bound is None:
                choose = f"CHOOSE {name}:  "
            else:
                bound = self.bound.to_str(*arg, width=width, **kw)
                choose = f"CHOOSE {name} \\in {bound}:  "
            res = _concatenate_boxes(choose, expr, width)
            return res

    class Case(_Nodes.Case):
        def to_str(self, *arg, width=None, **kw):
            indent_width = 2
            arms = list()
            for t, e in self.arms:
                test = t.to_str(*arg, width=width, **kw)
                expr = e.to_str(*arg, width=width, **kw)
                arm = test + " -> " + expr
                arms.append(arm)
            arms_str = " [] ".join(arms)
            res = "CASE " + arms_str
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                arms_str = "\n[] ".join(arms)
                res = _glue_prefix_box("CASE ", arms_str, indent_width=indent_width)
            if self.other is None:
                return res
            other = self.other.to_str(*arg, width=width, **kw)
            if res_width > width:
                res = _glue_prefix_box(
                    res, "\n[] OTHER -> " + other, indent_width=indent_width
                )
            else:
                res = res + " [] OTHER -> " + other
            return res

    class SetEnum(_Nodes.SetEnum):
        def to_str(self, *arg, width=None, **kw):
            exprs = list()
            for e in self.exprs:
                expr = e.to_str(*arg, width=width, **kw)
                exprs.append(expr)
            exprs_str = ", ".join(exprs)
            exprs_width, _ = _box_dimensions(exprs_str)
            if exprs_width > width:
                exprs_str = ",\n".join(exprs)
            res = "{" + exprs_str + "}"
            return res

    class SetSt(_Nodes.SetSt):
        def to_str(self, *arg, width=None, **kw):
            name = str(self.name)
            bound = self.bound.to_str(*arg, width=width, **kw)
            expr = self.expr.to_str(*arg, width=width, **kw)
            bound_str = "{" + name + " \\in " + bound + ":  "
            res = _glue_prefix_box(bound_str, expr + "}", indent_width=INDENT_WIDTH)
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                res = _glue_prefix_box(
                    bound_str, "\n" + expr + "}", indent_width=INDENT_WIDTH
                )
            return res

    class SetOf(_Nodes.SetOf):
        def to_str(self, *arg, width=None, **kw):
            expr = self.expr.to_str(width=width)
            bounds_str = _format_boundeds(self.boundeds, *arg, width=width, **kw)
            res = _glue_prefix_box("{" + expr + ":  ", bounds_str + "}")
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                res = _glue_prefix_box(
                    "{" + expr + ":", "\n" + bounds_str + "}", indent_width=INDENT_WIDTH
                )
            return res

    # type of junction list
    class And(_Nodes.And):
        def to_str(self, *arg, **kw):
            return "/\\"

    class Or(_Nodes.Or):
        def to_str(self, *arg, **kw):
            return "\\/"

    class List(_Nodes.List):
        def to_str(self, *arg, width=None, **kw):
            # op
            op = self.op.to_str()
            # blocks
            new_width = width - INDENT_WIDTH
            blocks = list()
            for e in self.exprs:
                expr = e.to_str(*arg, width=new_width, **kw)
                block = _glue_prefix_box(op + " ", expr)
                blocks.append(block)
            # combine
            res = "\n" + "\n".join(blocks)
            return res

    class Record(_Nodes.Record):
        def to_str(self, *arg, width=None, **kw):
            items = list()
            for name, e in self.items:
                expr = e.to_str(*arg, width=width, **kw)
                item = f"{name} |-> {expr}"
                items.append(item)
            items_str = ", ".join(items)
            res = f"[{items_str}]"
            return res

    class RecordSet(_Nodes.RecordSet):
        def to_str(self, *arg, width=None, **kw):
            items = list()
            for name, e in self.items:
                expr = e.to_str(*arg, width=width, **kw)
                item = f"{name}: {expr}"
                items.append(item)
            items_str = ", ".join(items)
            res = f"[{items_str}]"
            return res

    class Except_dot(_Nodes.Except_dot):
        def to_str(self, *arg, width=None, **kw):
            return f".{self.name}"

    class Except_apply(_Nodes.Except_apply):
        def to_str(self, *arg, width=None, **kw):
            expr = self.expr.to_str(*arg, width=width, **kw)
            return f"[{expr}]"

    class Except(_Nodes.Except):
        def to_str(self, *arg, width=None, **kw):
            expr = self.expr.to_str(*arg, width=width, **kw)
            exspecs = list()
            for expoints, e in self.exspec_list:
                name = "".join(
                    expoint.to_str(*arg, width=width, **kw) for expoint in expoints
                )
                expr_ = e.to_str(*arg, width=width, **kw)
                exspec = "!" + name + " = " + expr_
                exspecs.append(exspec)
            exspecs_str = ", ".join(exspecs)
            exspecs_width, _ = _box_dimensions(exspecs_str)
            if exspecs_width > width:
                exspecs_str = ",\n".join(exspecs)
                res = _glue_prefix_box(
                    f"[{expr} EXCEPT", "\n" + exspecs_str, indent_width=INDENT_WIDTH
                )
            else:
                res = f"[{expr} EXCEPT {exspecs_str}]"
            return res

    class Domain(_Nodes.Domain):
        def to_str(self, *arg, **kw):
            return self.expr.to_str(*arg, **kw)

    class NoDomain(_Nodes.NoDomain):
        pass

    class Ditto(_Nodes.Ditto):
        """Same bound domain."""

    class Bounded(_Nodes.Bounded):
        def to_str(self, *arg, width=None, **kw):
            return self.expr.to_str(*arg, width=width, **kw)

    class Unbounded(_Nodes.Unbounded):
        """Operator declaration without bound."""

    class Visible(_Nodes.Visible):
        pass

    class Hidden(_Nodes.Hidden):
        pass

    class NotSet(_Nodes.NotSet):
        pass

    class At(_Nodes.At):
        def to_str(*arg, **kw):
            return "@"

    class Arrow(_Nodes.Arrow):
        def to_str(self, *arg, width=None, **kw):
            expr1 = self.expr1.to_str(*arg, width=width, **kw)
            expr2_width = width - INDENT_WIDTH
            expr2 = self.expr2.to_str(*arg, width=expr2_width, **kw)
            res = _concatenate_boxes(
                "[" + expr1 + " -> ", expr2 + "]", width, INDENT_WIDTH, INDENT_WIDTH
            )
            return res

    class Tuple(_Nodes.Tuple):
        def to_str(self, *arg, width=None, **kw):
            expr_str = [e.to_str(*arg, width=width, **kw) for e in self.exprs]
            tpl = ", ".join(expr_str)
            tpl = f"<<{tpl}>>"
            tpl_width, _ = _box_dimensions(tpl)
            if tpl_width > width:
                tpl = ",\n".join(expr_str)
                tpl = _glue_prefix_box("<<", "\n" + tpl + ">>")
            return tpl

    class Bang(_Nodes.Bang):
        def to_str(self, *arg, width=None, **kw):
            expr = self.expr.to_str(*arg, width=width, **kw)
            sel_str = "!".join(
                [sel.to_str(*arg, width=width, **kw) for sel in self.sel_list]
            )
            return f"{expr}!{sel_str}"

    class WeakFairness(_Nodes.WeakFairness):
        """Signifies operator `WF_`."""

    class StrongFairness(_Nodes.StrongFairness):
        """Signifies operator `SF_`."""

    class String(_Nodes.String):
        def to_str(self, *arg, width=None, **kw):
            return f"{self.value}"

    class Number(_Nodes.Number):
        def to_str(self, *arg, **kw):
            if self.mantissa is None:
                return str(self.integer)
            else:
                return f"{self.integer}.{self.mantissa}"

    class Fairness(_Nodes.Fairness):
        def to_str(self, *arg, width=None, **kw):
            if isinstance(self.op, Nodes.WeakFairness):
                op = "WF_"
            elif isinstance(self.op, Nodes.StrongFairness):
                op = "SF_"
            else:
                raise ValueError(self.op)
            sub = self.subscript.to_str(*arg, width=width, **kw)
            expr = self.expr.to_str(*arg, width=width, **kw)
            res = op + sub + "(" + expr + ")"
            return res

    class SelLab(_Nodes.SelLab):
        def to_str(self, *arg, width=None, **kw):
            exprs = [e.to_str(*arg, width=width, **kw) for e in self.exprs]
            exprs_str = ", ".join(exprs)
            if exprs_str:
                return f"{self.string}({exprs_str})"
            else:
                return f"{self.string}"

    class SelInst(_Nodes.SelInst):
        def to_str(self, *arg, width=None, **kw):
            exprs = [e.to_str(*arg, width=width, **kw) for e in self.exprs]
            exprs_str = ", ".join(exprs)
            return f"({exprs_str})"

    class SelNum(_Nodes.SelNum):
        def to_str(self, *arg, width=None, **kw):
            return str(self.num)

    class SelLeft(_Nodes.SelLeft):
        def to_str(self, *arg, width=None, **kw):
            return "<<"

    class SelRight(_Nodes.SelRight):
        def to_str(self, *arg, width=None, **kw):
            return ">>"

    class SelDown(_Nodes.SelDown):
        def to_str(self, *arg, width=None, **kw):
            return ":"

    class SelAt(_Nodes.SelAt):
        def to_str(self, *arg, width=None, **kw):
            return "@"

    class Sequent(_Nodes.Sequent):
        def to_str(self, *arg, width=None, **kw):
            new_width = width - INDENT_WIDTH
            ctx = list()
            for c in self.context:
                ctx_unit = c.to_str(*arg, width=new_width, **kw)
                ctx.append(ctx_unit)
            goal = self.goal.to_str(*arg, width=new_width, **kw)
            if not ctx:
                return goal
            res = _glue_prefix_box(
                "ASSUME",
                "\n" + _join_boxes_sep(ctx, sep=", "),
                indent_width=INDENT_WIDTH,
            )
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                res = _glue_prefix_box(
                    "ASSUME", "\n" + ",\n".join(ctx), indent_width=INDENT_WIDTH
                )
            res = _glue_prefix_box(
                res + "\nPROVE", "\n" + goal, indent_width=INDENT_WIDTH
            )
            return res

    class Fact(_Nodes.Fact):
        def to_str(self, *arg, width=None, **kw):
            return self.expr.to_str(*arg, width=width, **kw)

    # operator declarations

    class Flex(_Nodes.Flex):
        def to_str(self, *arg, width=None, **kw):
            return f"VARIABLE {self.name}"

    class Fresh(_Nodes.Fresh):
        def to_str(self, *arg, width=None, **kw):
            kind = self.kind.to_str(*arg, width=width, **kw)
            name = str(self.name)
            shape = self.shape.to_str(*arg, width=width, **kw)
            if isinstance(self.domain, Nodes.Unbounded):
                return kind + " " + name + shape
            domain = self.domain.to_str(*arg, width=width, **kw)
            return kind + " " + name + " \\in " + domain

    class Constant(_Nodes.Constant):
        def to_str(self, *arg, width=None, **kw):
            return "CONSTANT"

    class State(_Nodes.State):
        def to_str(self, *arg, width=None, **kw):
            return "STATE"

    class Action(_Nodes.Action):
        def to_str(self, *arg, width=None, **kw):
            return "ACTION"

    class Temporal(_Nodes.Temporal):
        def to_str(self, *arg, width=None, **kw):
            return "TEMPORAL"

    class OperatorDef(_Nodes.OperatorDef):
        def to_str(self, *arg, width=None, **kw):
            name = self.name
            sig_width = width - len(name)
            expr_width = width - INDENT_WIDTH
            # TODO: proper indentation
            if isinstance(self.expr, Nodes.Lambda):
                sig = _format_lambda_signature(self.expr.name_shapes, sig_width)
                expr = self.expr.expr.to_str(width=expr_width)
                res = _glue_prefix_box(name + "(", sig + ") == ")
            else:
                sig = ""
                expr = self.expr.to_str(width=expr_width)
                res = name + " == "
            res2 = _glue_prefix_box(res, expr, indent_width=INDENT_WIDTH)
            res2_width, _ = _box_dimensions(res2)
            if res2_width > width:
                res2 = _glue_prefix_box(res, "\n" + expr, indent_width=INDENT_WIDTH)
            return res2

    class Instance(_Nodes.Instance):
        def to_str(self, *arg, width=None, **kw):
            subs = list()
            for name, e in self.sub:
                expr = e.to_str(*arg, width=width, **kw)
                sub = name + " <- " + expr
                subs.append(sub)
            subs_str = ", ".join(subs)
            if subs_str:
                inst = f"INSTANCE {self.module} WITH {subs_str}"
            else:
                inst = f"INSTANCE {self.module}"
            if self.name is None:
                return inst
            sig = ", ".join(self.args)
            if sig:
                res = f"{self.name}({sig}) == {inst}"
            else:
                res = f"{self.name} == {inst}"
            return res

    # Syntax nodes of module elements

    class Constants(_Nodes.Constants):
        def to_str(self, *arg, width=None, **kw):
            assert self.declarations
            decls = list()
            for name, shape in self.declarations:
                decl = name + shape.to_str(*arg, width=width, **kw)
                decls.append(decl)
            decls_str = ", ".join(decls)
            decls_str = textwrap.fill(decls_str, width=width - len("CONSTANT "))
            res = _glue_prefix_box("CONSTANT ", decls_str, indent_width=INDENT_WIDTH)
            return res

    class Variables(_Nodes.Variables):
        def to_str(self, *arg, width=None, **kw):
            assert self.declarations
            vrs_str = ", ".join(self.declarations)
            vrs_str = textwrap.fill(vrs_str, width=width - len("VARIABLE "))
            res = _glue_prefix_box("VARIABLE ", vrs_str, indent_width=INDENT_WIDTH)
            return res

    class Recursives(_Nodes.Recursives):
        """Recursive operator definition."""

        def to_str(self, *arg, width=None, **kw):
            raise NotImplementedError("RECURSIVE")

    class Local(_Nodes.Local):
        def to_str(self, *arg, width=None, **kw):
            return "LOCAL"

    class Export(_Nodes.Export):
        def to_str(self, *arg, width=None, **kw):
            return ""

    class User(_Nodes.User):
        pass

    class Definition(_Nodes.Definition):
        def to_str(self, *arg, width=None, **kw):
            local = self.local.to_str()
            new_width = width - len(local)
            def_str = self.definition.to_str(width=new_width)
            if local:
                return " ".join([local, def_str])
            else:
                return def_str

    class AnonymousInstance(_Nodes.AnonymousInstance):
        def to_str(self, *arg, width=None, **kw):
            inst = self.instance.to_str(*arg, width=width, **kw)
            local = self.local.to_str(*arg, width=width, **kw)
            if local:
                return "LOCAL " + inst
            else:
                return inst

    class Mutate(_Nodes.Mutate):
        def to_str(self, *arg, width=None, **kw):
            if isinstance(self.kind, Nodes.Hide):
                kind = "HIDE"
            elif isinstance(self.kind, Nodes.Use):
                kind = "USE"
            else:
                raise ValueError(self.kind)
            res = _format_usable(self.usable, kind, *arg, width=width, **kw)
            return res

    class ModuleHide(_Nodes.Hide):
        pass

    class ModuleUse(_Nodes.Use):
        pass

    class Module(_Nodes.Module):
        def to_str(self, *arg, width=None, **kw):
            if width is None:
                width = LINE_WIDTH
            n = (width - len(self.name) - len(" MODULE  ")) / 2
            left = math.floor(n)
            right = math.ceil(n)
            title = "".join(["-" * left, " MODULE ", self.name, " ", "-" * right])
            if self.extendees:
                indent = " " * INDENT_WIDTH
                se = [indent + e for e in self.extendees]
                extends = "EXTENDS\n" + ",\n".join(se)
            else:
                extends = ""
            body = "\n".join([unit.to_str(width=width) for unit in self.body])
            endline = width * "="
            if extends:
                return "\n".join([title, extends, body, endline])
            else:
                return "\n".join([title, body, endline])

    class Submodule(_Nodes.Submodule):
        def to_str(self, *arg, width=None, **kw):
            return self.module.to_str(*arg, width=width, **kw)

    class Suppress(_Nodes.Suppress):
        pass

    class Emit(_Nodes.Emit):
        pass

    class StepStar(_Nodes.StepStar):
        def to_str(self, *arg, width=None, **kw):
            return f"<*>{self.label}."

    class StepPlus(_Nodes.StepPlus):
        def to_str(self, *arg, width=None, **kw):
            return f"<+>{self.label}."

    class StepNum(_Nodes.StepNum):
        def to_str(self, *arg, width=None, **kw):
            return f"<{self.level}>{self.label}."

    class Only(_Nodes.Only):
        def to_str(self, *arg, width=None, **kw):
            return "ONLY"

    class Default(_Nodes.Default):
        def to_str(self, *arg, width=None, **kw):
            return ""

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
        def to_str(self, *arg, width=None, **kw):
            expr_str = self.expr.to_str(*arg, width=width, **kw)
            if self.name is None:
                axiom = "AXIOM"
            else:
                axiom = f"AXIOM {self.name} =="
            return _glue_prefix_box(axiom, "\n" + expr_str, indent_width=INDENT_WIDTH)

    class Theorem(_Nodes.Theorem):
        def to_str(self, *arg, width=None, **kw):
            body = self.body.to_str(*arg, width=width - INDENT_WIDTH, **kw)
            if self.name is None:
                theorem = "THEOREM"
            else:
                theorem = f"THEOREM {self.name} =="
            res = _glue_prefix_box(theorem, "\n" + body, indent_width=INDENT_WIDTH)
            if not self.proof:
                return res
            proof_str = self.proof.to_str(*arg, width=width, **kw)
            res = _glue_prefix_box(res, "\nPROOF", indent_width=0)
            res = _glue_prefix_box(res, "\n" + proof_str, indent_width=0)
            return res

    class Named(_Nodes.Named):
        def to_str(self, *arg, width=None, **kw):
            return f"<{self.level}>{self.label}."

    class Unnamed(_Nodes.Unnamed):
        def to_str(self, *arg, width=None, **kw):
            return f"<{self.level}>"

    # Proofs

    class Obvious(_Nodes.Obvious):
        def to_str(self, *arg, width=None, **kw):
            res = "OBVIOUS"
            res = textwrap.indent(res, " " * INDENT_WIDTH)
            return res
            # self.supp = supp
            # self.method = method

    class Omitted(_Nodes.Omitted):
        def to_str(*arg, width=None, **kw):
            # if isinstance(self.omission, Nodes.Explicit):
            #     comment = ''
            # elif isinstance(self.omission, Nodes.Implicit):
            #     comment = ' (* implicit *)'
            # else:
            #     raise ValueError(self.omission)
            # res = 'OMITTED' + comment
            res = "OMITTED"
            res = textwrap.indent(res, " " * INDENT_WIDTH)
            return res

    class By(_Nodes.By):
        def to_str(self, *arg, width=None, **kw):
            indent = " " * INDENT_WIDTH
            if self.only:
                only = " ONLY"
            else:
                only = ""
            prefix = f"{indent}BY{only}"
            res = _format_usable(self.usable, prefix, *arg, width=width, **kw)
            return res

    class Steps(_Nodes.Steps):
        def to_str(self, *arg, width=None, **kw):
            # other steps
            steps = list()
            for s in self.steps:
                step = s.to_str(*arg, width=width - INDENT_WIDTH, **kw)
                steps.append(step)
            steps_str = "\n".join(steps)
            # QED step
            qed_step = self.qed_step.to_str(*arg, width=width, **kw)
            res = steps_str + "\n" + qed_step
            res = textwrap.indent(res, " " * INDENT_WIDTH)
            return res

    # Proof steps

    class Hide(_Nodes.Hide):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            prefix = f"{step_number} HIDE"
            res = _format_usable(self.usable, prefix, *arg, width=width, **kw)
            return res

    class Define(_Nodes.Define):
        def to_str(self, *arg, width=None, **kw):
            indent_width = 2 * INDENT_WIDTH
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            defns_str = _format_definitions(
                self.definitions, *arg, width=width - 3 * INDENT_WIDTH, **kw
            )
            res = _glue_prefix_box(
                f"{step_number} DEFINE", "\n" + defns_str, indent_width=indent_width
            )
            return res

    class Assert(_Nodes.Assert):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            new_width = width - len(step_number) - 1
            sequent = self.sequent.to_str(*arg, width=new_width, **kw)
            proof = self.proof.to_str(*arg, width=width, **kw)
            res = _glue_prefix_box(step_number + " ", sequent)
            res = _glue_prefix_box(res, "\n" + proof, indent_width=0)
            return res

    class Suffices(_Nodes.Suffices):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            new_width = width - len(step_number) - 1 - 2 * INDENT_WIDTH
            sequent = self.sequent.to_str(*arg, width=new_width, **kw)
            proof = self.proof.to_str(*arg, width=width, **kw)
            res = _glue_prefix_box(
                step_number + " SUFFICES", "\n" + sequent, indent_width=2 * INDENT_WIDTH
            )
            res = _glue_prefix_box(res, "\n" + proof, indent_width=0)
            return res

    class Pcase(_Nodes.Pcase):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            new_width = width - len(step_number) - 1
            expr = self.expr.to_str(*arg, width=new_width, **kw)
            proof = self.proof.to_str(*arg, width=width, **kw)
            res = f"{step_number} CASE {expr}"
            res = _glue_prefix_box(res, "\n" + proof, indent_width=0)
            return res

    class Pick(_Nodes.Pick):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            new_width = width - len(step_number) - 1
            bounds_str = _format_bounds(self.bounds, *arg, width=new_width, **kw)
            expr = self.expr.to_str(*arg, width=new_width, **kw)
            proof = self.proof.to_str(*arg, width=width, **kw)
            pick = f"{step_number} PICK {bounds_str}:  "
            pick_width, _ = _box_dimensions(pick)
            if pick_width > width:
                pick = _glue_prefix_box(f"{step_number} PICK", "\n{bounds_str}:  ")
            res = _glue_prefix_box(pick, expr, indent_width=INDENT_WIDTH)
            res_width, _ = _box_dimensions(res)
            if res_width > width:
                res = _glue_prefix_box(pick, "\n" + expr, indent_width=INDENT_WIDTH)
            res = _glue_prefix_box(res, "\n" + proof, indent_width=0)
            return res

    class Use(_Nodes.Use):
        def to_str(self, *arg, width=None, **kw):
            if self.only:
                only = " ONLY"
            else:
                only = ""
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            prefix = f"{step_number} USE{only}"
            res = _format_usable(self.usable, prefix, *arg, width=width, **kw)
            return res

    class Have(_Nodes.Have):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            expr = self.expr.to_str(*arg, width=width, **kw)
            res = _glue_prefix_box(
                f"{step_number} HAVE ", expr, indent_width=2 * INDENT_WIDTH
            )
            return res

    class Take(_Nodes.Take):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            bounds_str = _format_bounds(self.bounds, *arg, width=width, **kw)
            res = _glue_prefix_box(
                f"{step_number} TAKE ", bounds_str, indent_width=2 * INDENT_WIDTH
            )
            return res

    class Witness(_Nodes.Witness):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            exprs = [e.to_str(*arg, width=width, **kw) for e in self.exprs]
            exprs_str = ", ".join(exprs)
            exprs_str_width, _ = _box_dimensions(exprs_str)
            if exprs_str_width > width:
                exprs_str = ",\n".join(exprs)
            res = _glue_prefix_box(
                f"{step_number} WITNESS ", exprs_str, indent_width=2 * INDENT_WIDTH
            )
            return res

    class Qed(_Nodes.Qed):
        def to_str(self, *arg, width=None, **kw):
            step_number = self.step_number.to_str(*arg, width=width, **kw)
            proof = self.proof.to_str(*arg, width=width - INDENT_WIDTH, **kw)
            res = f"{step_number} QED\n{proof}"
            return res

    class Dvar(_Nodes.Dvar):
        def to_str(self, *arg, width=None, **kw):
            return str(self.value)

    class Bstring(_Nodes.Bstring):
        def to_str(self, *arg, width=None, **kw):
            return str(self.value)

    class Bfloat(_Nodes.Bfloat):
        def to_str(self, *arg, width=None, **kw):
            return str(self.value)

    class Bdef(_Nodes.Bdef):
        def to_str(self, *arg, width=None, **kw):
            return "@"

    class BackendPragma(_Nodes.BackendPragma):
        def to_str(self, *arg, width=None, **kw):
            opdef = Nodes.OperatorDef(self.name, self.expr)
            opdef_str = opdef.to_str(*arg, width=width, **kw)
            # backend args
            methods = list()
            for backend_args in self.backend_args:
                bkargs = list()
                for name, arg_ in self.backend_args[0]:
                    # (*{ by (prover:"smt3") }*)
                    arg_str = arg_.to_str(*arg, width=width, **kw)
                    bkarg = f"{name}:{arg_str}"
                    bkargs.append(bkarg)
                bkargs_str = (";\n" + INDENT_WIDTH * " ").join(bkargs)
                method_str = " by (" + bkargs_str + ") "
                methods.append(method_str)
            methods_str = ("\n" + INDENT_WIDTH * " ").join(methods)
            # combine
            pragma_str = "  (*{" + methods_str + "}*)"
            return opdef_str + pragma_str
