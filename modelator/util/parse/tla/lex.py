"""Lexer for TLA+, using Python Lex-Yacc (PLY)."""
# Copyright 2016-2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# <https://github.com/tlaplus/tlapm/blob/main/src/alexer.mll>
#
import logging
import re

import ply.lex

from . import _location
from . import tokens as intf

logger = logging.getLogger(__name__)


RESERVED = {
    "ACTION",
    "ASSUME",
    "ASSUMPTION",
    "AXIOM",
    "BOOLEAN",  # operator
    "BY",
    "CASE",
    "CHOOSE",
    "CONSTANT",
    "CONSTANTS",
    "COROLLARY",
    "DEF",
    "DEFINE",
    "DEFS",
    # 'DOMAIN',  # prefix operator
    "ELSE",
    # 'ENABLED',  # prefix operator
    "EXCEPT",
    "EXTENDS",
    "FALSE",  # operator
    "HAVE",
    "HIDE",
    "IF",
    "IN",
    "INSTANCE",
    "LAMBDA",
    "LEMMA",
    "LET",
    "LOCAL",
    "MODULE",
    "NEW",
    "OBVIOUS",
    "OMITTED",
    "ONLY",
    "OTHER",
    "PICK",
    "PROOF",
    "PROPOSITION",
    "PROVE",
    "QED",
    "RECURSIVE",
    # 'SF_',  # separate lexer rule
    "STATE",
    "STRING",  # operator
    # 'SUBSET',  # prefix operator
    "SUFFICES",
    "TAKE",
    "TEMPORAL",
    "THEN",
    "THEOREM",
    "TRUE",  # operator
    # 'UNCHANGED',  # prefix operator
    # 'UNION',  # prefix operator
    "USE",
    "VARIABLE",
    "VARIABLES",
    # 'WF_',  # separate lexer rule
    "WITH",
    "WITNESS",
}
PREFIX_OPERATORS = {
    "DOMAIN",
    "ENABLED",
    "SUBSET",
    "UNCHANGED",
    "UNION",
}
letter = "[a-zA-Z]"
numeral = "[0-9]"
# namechar = letter | numeral | _
namechar = "[a-zA-Z0-9_]"
name = f"({namechar})*{letter}({namechar})*"


class Lexer:
    """Lexer for the TLA+ specification language."""

    states = (
        ("multilinecomment", "exclusive"),
        ("string", "exclusive"),
    )

    reserved = {k: k for k in RESERVED}
    delimiters = [
        "DASH_LINE",
        "EQ_LINE",
        "PUNCTUATION",
        "PUNCTUATION_DOT",
        "STEP_NUMBER",
        "STEP_NUMBER_PLUS",
        "STEP_NUMBER_STAR",
    ]
    # remember to check precedence
    operators = [
        "ALWAYS",
        "FAIRNESS",
        "INFIX_OPERATOR",
        "INFIX_OPERATOR_LEADSTO",
        "NAME",
        "PAREN_OPERATOR",
        "PREFIX_OPERATOR",
        "POSTFIX_OPERATOR",
    ]
    misc = [
        "BINARY_INTEGER",
        "COMMENT",
        "FLOAT",
        "HEXADECIMAL_INTEGER",
        "IDENTIFIER",
        "DECIMAL_INTEGER",
        "LINECOMMENT",
        "OCTAL_INTEGER",
        "PRAGMAS",
        "RESERVED",
    ]

    whitesp = " "
    tab = "\t"
    newline = r"\r|\n|\r\n"

    def __init__(self, debug=False):
        self.tokens = self.delimiters + self.operators + self.misc + list(self.reserved)
        self.build(debug=debug)
        self._initialize_state()

    def build(self, debug=False, debuglog=None, **kwargs):
        """Create a lexer.

        @param kwargs: Same arguments as `ply.lex.lex`:

          - except for `module` (fixed to `self`)
          - `debuglog` defaults to the module's logger.
        """
        if debug and debuglog is None:
            debuglog = logger
        self._lexer = ply.lex.lex(module=self, debug=debug, debuglog=debuglog, **kwargs)

    def input(self, string):
        """Set data to `string` and reset state."""
        self._lexer.input(string)
        self._initialize_state()

    def _initialize_state(self):
        """Reset the lexer's state."""
        self._lexer.lineno = 1
        self._string_start = None

    def __iter__(self):
        return self

    def __next__(self):
        token = self._lexer.token()
        if token is None:
            raise StopIteration
        return token

    # State "token" of the `tlapm` lexer

    # (* pragmas *)
    #   | ("(*{"|"}*)" as prag)
    #       { [ PUNCT prag ] }
    def t_PRAGMAS(self, t):
        r"\(\*\{|\}\*\)"
        return t

    # (* comments *)
    #   | "\\*"
    #       { linecom lexbuf }
    def t_LINECOMMENT(self, t):
        r"\\\*.*"
        return None

    #   | "(*"
    #       { comment 1 lexbuf }
    # def t_COMMENT(self, t):
    #     r'\(\*(.|\n)*?\*\)'
    #     t.lineno += t.value.count('\n')
    def t_COMMENT(self, t):
        r"\(\*"
        t.lexer.comment_level = 1
        t.lexer.begin("multilinecomment")

    def t_multilinecomment_left_paren(self, t):
        r"\(\*"
        t.lexer.comment_level += 1

    def t_multilinecomment_right_paren(self, t):
        r"\*\)"
        t.lexer.comment_level -= 1
        # if matching the outer left parenthesis,
        # then return to INITIAL-state lexing
        if t.lexer.comment_level == 0:
            t.lexer.begin("INITIAL")

    def t_multilinecomment_newline(self, t):
        r"\n"
        t.lexer.lineno += 1

    def t_multilinecomment_other(self, t):
        r"[^\n(\*]+"
        return None

    def t_multilinecomment_lparen(self, t):
        r"\("
        return None

    def t_multilinecomment_star(self, t):
        r"\*"
        return None

    def t_multilinecomment_error(self, t):
        raise ValueError(f'Illegal character "{t.value[0]}"')

    t_multilinecomment_ignore = ""

    # (* exceptions *)
    # | ("[]" as op)
    #   { [ OP op ] }
    def t_ALWAYS(self, t):
        r"\[\]"
        return t

    # | ("(+)"|"(-)"|"(/)"|"(\\X)"|"(.)" as op)
    #   { [ OP op ] }
    def t_PAREN_OPERATOR(self, t):
        r"\(\+\)|\(-\)|\(/\)|\(\\X\)|\(\.\)"
        return t

    # (* strict punctuation *)
    # | "----" '-'*
    #   { [ PUNCT "----" ] }
    def t_DASH_LINE(self, t):
        r"----(-)*"
        return t

    # | "====" '='*
    #   { [ PUNCT "====" ] }
    def t_EQ_LINE(self, t):
        r"====(=)*"
        return t

    # | "<*>" ('.'* as dots)
    #   { [ ST ( `Star, "", String.length dots) ] }
    def t_STEP_NUMBER_STAR(self, t):
        r"<\*>(\.)*"
        return t

    # | "<+>" ('.'* as dots)
    #   { [ ST ( `Plus, "", String.length dots) ] }
    def t_STEP_NUMBER_PLUS(self, t):
        r"<\+>(\.)*"
        return t

    # | '<' (numeral+ as num) '>' (namechar* as lab)
    #       ('.'* as dots)
    #   { [ ST (`Num (int_of_string num),
    #       lab, String.length dots) ] }
    step_number = rf"<{numeral}+>{namechar}*\.*"

    @ply.lex.TOKEN(step_number)
    def t_STEP_NUMBER(self, t):
        return t

    # | (","|"."|"_"|"("|")"|"["|"]"|"{"|"}"
    #   |"<<"|">>"|"]_"|">>_"|"=="|"!"
    # |"@"|":"|"::"|";"|"->"|"<-"|"|->"|"\\A"
    #   |"\\AA"|"\\E"|"\\EE"|'_' as p)
    #   { [ PUNCT p ] }
    # See also '_' in NAME
    # TODO: change \\A \\A \\E \\EE to prefix operators
    # in the grammar ?
    def t_PUNCTUATION(self, t):
        (r",|\(|\)|\[|\]_|\]|\{|\}|<<|>>_|>>|==" r"|;|->|<-|\|->|\\AA|\\A|\\EE|\\E")
        return t

    # (* numbers *)
    # | (numeral+ as ch) '.' (numeral+ as man)
    #   { [ NUM (ch, man) ] }
    float_numeric_literal = rf"{numeral}+\.{numeral}+"

    @ply.lex.TOKEN(float_numeric_literal)
    def t_FLOAT(self, t):
        return t

    # | (numeral+ as i)
    #   { [ NUM (i, "") ] }
    integer = f"{numeral}+"

    @ply.lex.TOKEN(integer)
    def t_DECIMAL_INTEGER(self, t):
        return t

    # | ("\\b" ['0' '1']+ as b)
    #   { Bytes.set (Bytes.of_string b) 0 '0' ;
    #     [ NUM (string_of_int (int_of_string b), "") ] }
    def t_BINARY_INTEGER(self, t):
        r"(\\b|\\B)[0-1]+"
        return t

    # | ("\\o" ['0'-'7']+ as o)
    #   { Bytes.set (Bytes.of_string o) 0 '0' ;
    #     [ NUM (string_of_int (int_of_string o), "") ] }
    def t_OCTAL_INTEGER(self, t):
        r"(\\o|\\O)[0-7]+"
        return t

    # | ("\\h" (numeral | ['A'-'F'])+ as h)
    #   { Bytes.set (Bytes.of_string h) 0 '0' ;
    #     Bytes.set (Bytes.of_string h) 1 'x' ;
    #     [ NUM (string_of_int (int_of_string h), "") ] }
    hexadecimal = f"(\\h,\\H)({numeral}|[A-F])+"

    @ply.lex.TOKEN(hexadecimal)
    def HEXADECIMAL_INTEGER(self, t):
        return t

    # def t_STRING(self, t):
    #     r'"[^"\']*"'
    #     return t

    def t_STRING(self, t):
        r'"'
        self._string_start = t.lexpos
        t.lexer.begin("string")

    def t_string_escaped_quotes(self, t):
        r'\\"|\\t|\\n|\\f|\\r|\\\\'

    def t_string_newline(self, t):
        r"\n"
        raise ValueError("Newline within string.")

    def t_string_other_characters(self, t):
        r'[^"\\]+'

    def t_string_closing(self, t):
        r'"'
        start = self._string_start
        end = t.lexpos + len(t.value)
        t.value = t.lexer.lexdata[start:end]
        t.lexer.begin("INITIAL")
        t.type = "STRING"
        t.lexpos = start
        return t

    def t_string_error(self, t):
        raise ValueError(f'Illegal character "{t.value[0]}"')

    t_string_ignore = ""

    # (* prefix operators *)
    #   | ("\\neg"|"\\lnot"|"~"|"-."|"<>"|"UNION"|"SUBSET"
    #     |"ENABLED"|"UNCHANGED"|"DOMAIN" as op)
    #       { [ OP op ] }
    # See also PREFIX_OPERATORS

    #   (* postfix operators *)
    #   | ("'"|"^+"|"^*"|"^#" as op)
    #       { [ OP op ] }

    def t_INFIX_OPERATOR_LEADSTO(self, t):
        r"\~>"
        t.type = "INFIX_OPERATOR"
        return t

    def t_PREFIX_OPERATOR(self, t):
        r"\\neg|\\lnot|~|-\.|<>"
        return t

    def t_POSTFIX_OPERATOR(self, t):
        r"\'|\^\+|\^\*|\^\#"
        return t

    def t_INFIX_OPERATOR(self, t):
        (
            r">=|\\geq|<=>|<=|=<|\\leq|\#\#|\#|/="
            r"|\\oplus|\\ominus|\\otimes|\\oslash"
            r"|\\odot|\\cap|\\intersect"
            r"|\\cup|\\union|\\equiv|\\o|\\circ|\\X|\\times"
            r"|=>|\-\+\->|/\\|\\land"
            r"|\\/|\\lor|\-\||::=|:=|<:|<|=\||>|\\approx"
            r"|\\asymp|\\cong|\\doteq|\\gg|\\notin"
            r"|\\ll|\\preceq|\\prec"
            r"|\\propto|\\simeq|\\sim"
            r"|\\sqsubseteq|\\sqsubset|\\sqsupseteq"
            r"|\\sqsupset|\\subseteq|\\subset"
            r"|\\succeq|\\succ|\\supseteq|\\supset"
            r"|\|\-|\|=|=|\\cdot|@@|:>|\\in"
            r"|\.\.\.|\.\.|!!|\$\$|\$|\?\?|\\sqcap"
            r"|\\sqcup|\\uplus|\\wr|\+\+|\+|%%|%|\|\|"
            r"|\||\-\-|\-|\&\&|\&|\*\*|\*"
            r"|//|/|\\bigcirc|\\bullet"
            r"|\\div|\\star|\^\^|\^|\\"
        )
        return t

    # ensure longest match
    def t_PUNCTUATION_MORE(self, t):
        r"!|::|:|\@|\."
        t.type = "PUNCTUATION"
        return t

    def t_FAIRNESS(self, t):
        r"SF_|WF_"
        return t

    def t_NAME(self, t):
        r"[a-zA-Z_0-9]*[a-zA-Z_][a-zA-Z_0-9]*"
        if t.value in RESERVED:
            t.type = "RESERVED"
        elif t.value in PREFIX_OPERATORS:
            t.type = "PREFIX_OPERATOR"
        elif t.value == "_":
            t.type = "PUNCTUATION"
        else:
            t.type = "IDENTIFIER"
        return t

    # t_ignore is reserved by lex to provide
    # much more efficient
    # internal handling by lex
    #
    # A string containing ignored
    # characters (spaces)
    t_ignore = r" "  # whitesp

    def t_NEWLINE(self, t):
        r"\n+"
        t.lexer.lineno += t.value.count("\n")

    def t_tab(self, t):
        r"\t"
        raise ValueError("TAB characters are unsupported.")

    def t_error(self, t):
        logger.error(f'Illegal character "{t.value[0]}"')
        t.lexer.skip(1)


def tokenize(data, omit_preamble=True):
    """Return `list` of `Token` instances.

    Line numbers are from the start of
    the root module (i.e., the preamble
    is not counted in line numbers).

    @param data: TLA+ source
    @type data: `str`
    @param omit_preamble: if `True`,
        then parse after skipping the preamble.
        Otherwise, if a preamble is present,
        then raise a parsing error.
    @type omit_preamble: `bool`
    @return: `list` of tokens
    @rtype: `list` of `tla.tokens.Token`
    """
    if omit_preamble:
        data = _omit_preamble(data)
    lextokens = _lex(data)
    if len(lextokens) >= 2 and lextokens[1].value == "MODULE":
        module_name = lextokens[2].value
    else:
        module_name = "unknown module"
    tokens = [
        _map_to_token(data, token, module_name=module_name) for token in lextokens
    ]
    return tokens


def lex(data):
    data = _omit_preamble(data)
    return _lex(data)


def _lex(data):
    lexer = Lexer()
    lexer.input(data)
    output = list()
    for token in lexer:
        # print(token)
        output.append(token)
    return output


def _omit_preamble(data):
    regex = r"\-\-\-\-(\-)*\s*MODULE"
    match = re.search(regex, data)
    n = match.start()
    return data[n:]


def _map_to_token(data, token, module_name="dummy_file"):
    # `data` is needed to find
    # the beginning of line
    token_ = _map_to_token_(token)
    # print(token.__dict__)
    # _print_lextoken_info(token)
    # print('\n')
    line_number = token.lineno
    bol = find_beginning_of_line(data, token)
    start_column_offset = token.lexpos
    start_loc = _location.locus_of_position(
        module_name, line_number, bol, start_column_offset
    )
    if "\n" in token.value:
        raise AssertionError(token.type, token.value)
    stop_column_offset = token.lexpos + len(token.value)
    stop_loc = _location.locus_of_position(
        module_name, line_number, bol, stop_column_offset
    )
    if data[start_column_offset:stop_column_offset] != token.value:
        raise AssertionError(data[start_column_offset:stop_column_offset], token.value)
    loc = start_loc.merge(stop_loc)
    if len(token.value) != loc.stop.column - loc.start.column:
        raise AssertionError(token.value, loc.stop.column, loc.start.column)
    return intf.Token(token_, None, loc)


# This mapping is a separate step because `ply.lex`
# checks the type of token returned by each token rule.
def _map_to_token_(token):
    type_ = token.type
    # delimiters
    if type_ == "DASH_LINE":
        return intf.PUNCT("----")
    elif type_ == "EQ_LINE":
        return intf.PUNCT("====")
    elif type_ == "PUNCTUATION":
        return intf.PUNCT(token.value)
    elif type_ == "STEP_NUMBER":
        step_level = re.findall("<([0-9]+)>", token.value)[0]
        match = re.search(r"(\.)+", token.value)
        if match is None:
            n = 0
        else:
            n = len(match.group())
            if n < 1:
                raise AssertionError(match.group())
        step_name_regex = "<[0-9]+>([a-zA-Z0-9_]*)"
        step_name = re.findall(step_name_regex, token.value)[0]
        return intf.ST(intf.StepNum(step_level), step_name, n)
    elif type_ == "STEP_NUMBER_PLUS":
        if token.value[:3] != "<+>":
            raise AssertionError(token.value)
        n = len(token.value[3:])
        return intf.ST(intf.StepPlus(), None, n)
    elif type_ == "STEP_NUMBER_STAR":
        if token.value[:3] != "<*>":
            raise AssertionError(token.value)
        n = len(token.value[3:])
        return intf.ST(intf.StepStar(), None, n)
    # operators
    elif type_ == "ALWAYS":
        return intf.OP(token.value)
    elif type_ == "FAIRNESS":
        # TODO: change grammar to OP here ?
        return intf.PUNCT(token.value)
    elif type_ == "INFIX_OPERATOR":
        return intf.OP(token.value)
    elif type_ == "NAME":
        raise ValueError(
            "expected IDENTIFIER or RESERVED " "or PREFIX_OPERATOR or PUNCTUATION"
        )
    elif type_ == "PAREN_OPERATOR":
        return intf.OP(token.value)
    elif type_ == "PREFIX_OPERATOR":
        return intf.OP(token.value)
    elif type_ == "POSTFIX_OPERATOR":
        return intf.OP(token.value)
    # misc
    elif type_ == "BINARY_INTEGER":
        # TODO: test
        if token.value[:2] != "\\b":
            raise AssertionError(token.value)
        return intf.NUM(token.value[2:], None)
    elif type_ == "COMMENT":
        raise ValueError("unexpected COMMENT")
    elif type_ == "FLOAT":
        a, b = token.value.split(".")
        return intf.NUM(a, b)
    elif type_ == "HEXADECIMAL_INTEGER":
        # TODO: test
        if token.value[:2] != "\\h":
            raise AssertionError(token.value)
        value = int(token.value[2:], 16)
        return intf.NUM(str(value), None)
    elif type_ == "IDENTIFIER":
        return intf.ID(token.value)
    elif type_ == "DECIMAL_INTEGER":
        return intf.NUM(token.value, None)
    elif type_ == "LINECOMMENT":
        raise ValueError("unexpected LINECOMMENT")
    elif type_ == "OCTAL_INTEGER":
        # TODO: test
        if token.value[:2] != "\\o":
            raise AssertionError(token.value)
        value = int(token.value[2:], 8)
        return intf.NUM(str(value), None)
    elif type_ == "PRAGMAS":
        return intf.PUNCT(token.value)
    elif type_ == "RESERVED":
        return intf.KWD(token.value)
    elif type_ == "STRING":
        return intf.STR(token.value)
    else:
        raise ValueError(type_)


def find_beginning_of_line(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    return line_start


def find_column(input, token):
    r"""Return start column of `token`.

    @return: number of column where
        `token` starts, with
        `column \in 1..len(input)`
    @rtype: `int`
    """
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    column = (token.lexpos - line_start) + 1
    n_chars = len(input)
    if column < 1 or column > n_chars:
        raise AssertionError(
            rf"expected `column \in 1..{n_chars} " f"(computed `{column = }`)"
        )
    return column


def _print_lextoken_info(token):
    """Print all the information stored in `token`.

    @type token: `ply.lex.LexToken`.
    """
    print(
        f"type: {token.type}\n"
        f"value: {token.value}\n"
        f"line number: {token.lineno}\n"
        f"offset: {token.lexpos}\n"
        f"type: {token.type}"
    )


def _join_with_newlines(tokens):
    current_line = 1
    strings = list()
    for token in tokens:
        token_line = token.loc.start.line
        diff = token_line - current_line
        if diff < 0:
            raise AssertionError(token_line, current_line)
        # commented due to multi-line comments
        # if diff > 1:
        #     raise AssertionError(
        #         current_line, token_line)
        if token_line > current_line:
            # update current line
            # current_line += 1
            current_line += diff
            if current_line != token_line:
                raise AssertionError(current_line, token_line)
            # output newlines
            newlines = "\n" * diff
            strings.append(newlines)
        strings.append(str(token.form))
        strings.append(" ")
    return "".join(strings)
