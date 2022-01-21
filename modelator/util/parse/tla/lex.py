"""Lexer for TLA+, using Python Lex-Yacc (PLY)."""
# Copyright 2016-2020 by California Institute of Technology
# Copyright (c) 2008-2013  INRIA and Microsoft Corporation
# All rights reserved. Licensed under 3-clause BSD.
#
# This module is based on the file:
#
# https://github.com/tlaplus/tlapm/blob/master/src/alexer.mll
#
import logging
import pprint
import re

import ply.lex

from tla import _location
from tla import tokens as intf


logger = logging.getLogger(__name__)


RESERVED = {
    'ACTION',
    'ASSUME',
    'ASSUMPTION',
    'AXIOM',
    'BOOLEAN',  # operator
    'BY',
    'CASE',
    'CHOOSE',
    'CONSTANT',
    'CONSTANTS',
    'COROLLARY',
    'DEF',
    'DEFINE',
    'DEFS',
    # 'DOMAIN',  # prefix operator
    'ELSE',
    # 'ENABLED',  # prefix operator
    'EXCEPT',
    'EXTENDS',
    'FALSE',  # operator
    'HAVE',
    'HIDE',
    'IF',
    'IN',
    'INSTANCE',
    'LAMBDA',
    'LEMMA',
    'LET',
    'LOCAL',
    'MODULE',
    'NEW',
    'OBVIOUS',
    'OMITTED',
    'ONLY',
    'OTHER',
    'PICK',
    'PROOF',
    'PROPOSITION',
    'PROVE',
    'QED',
    'RECURSIVE',
    # 'SF_',  # separate lexer rule
    'STATE',
    'STRING',  # operator
    # 'SUBSET',  # prefix operator
    'SUFFICES',
    'TAKE',
    'TEMPORAL',
    'THEN',
    'THEOREM',
    'TRUE',  # operator
    # 'UNCHANGED',  # prefix operator
    # 'UNION',  # prefix operator
    'USE',
    'VARIABLE',
    'VARIABLES',
    # 'WF_',  # separate lexer rule
    'WITH',
    'WITNESS'}
PREFIX_OPERATORS = {
    'DOMAIN',
    'ENABLED',
    'SUBSET',
    'UNCHANGED',
    'UNION',
    }
letter   = '[a-zA-Z]'
numeral  = '[0-9]'
# namechar = letter | numeral | _
namechar = '[a-zA-Z0-9_]'.format(
    letter=letter, numeral=numeral)
name = '({namechar})*{letter}({namechar})*'.format(
    namechar=namechar, letter=letter)


class Lexer(object):
    '''Lexer for the TLA+ specification language.'''

    states = (
        ('multilinecomment', 'exclusive'),
        ('string', 'exclusive'),
    )

    reserved = {k: k for k in RESERVED}
    delimiters = [
        'DASH_LINE',
        'EQ_LINE',
        'PUNCTUATION',
        'PUNCTUATION_DOT',
        'STEP_NUMBER',
        'STEP_NUMBER_PLUS',
        'STEP_NUMBER_STAR']
    # remember to check precedence
    operators = [
        'ALWAYS',
        'FAIRNESS',
        'INFIX_OPERATOR',
        'INFIX_OPERATOR_LEADSTO',
        'NAME',
        'PAREN_OPERATOR',
        'PREFIX_OPERATOR',
        'POSTFIX_OPERATOR']
    misc = [
        'BINARY_INTEGER',
        'COMMENT',
        'FLOAT',
        'HEXADECIMAL_INTEGER',
        'IDENTIFIER',
        'INTEGER',
        'LINECOMMENT',
        'OCTAL_INTEGER',
        'PRAGMAS',
        'RESERVED',
        ]

    whitesp  = ' '
    tab = '\t'
    newline  = r'\r|\n|\r\n'

    def __init__(self, debug=False):
        self.tokens = (
            self.delimiters + self.operators +
            self.misc + list(self.reserved))
        self.build(debug=debug)

    def build(
            self,
            debug=False,
            debuglog=None,
            **kwargs):
        """Create a lexer.

        @param kwargs: Same arguments as C{ply.lex.lex}:

          - except for C{module} (fixed to C{self})
          - C{debuglog} defaults to the module's logger.
        """
        if debug and debuglog is None:
            debuglog = logger
        self.lexer = ply.lex.lex(
            module=self,
            debug=debug,
            debuglog=debuglog,
            **kwargs)

    # State "token" of the `tlapm` lexer

    # (* pragmas *)
    #   | ("(*{"|"}*)" as prag)
    #       { [ PUNCT prag ] }
    def t_PRAGMAS(self, t):
        r'\(\*\{|\}\*\)'
        return t

    # (* comments *)
    #   | "\\*"
    #       { linecom lexbuf }
    def t_LINECOMMENT(self, t):
        r'\\\*.*'
        return None

    #   | "(*"
    #       { comment 1 lexbuf }
    # def t_COMMENT(self, t):
    #     r'\(\*(.|\n)*?\*\)'
    #     t.lineno += t.value.count('\n')
    def t_COMMENT(self, t):
        r'\(\*'
        t.lexer.comment_level = 1
        t.lexer.begin('multilinecomment')

    def t_multilinecomment_left_paren(self, t):
        r'\(\*'
        t.lexer.comment_level += 1

    def t_multilinecomment_right_paren(self, t):
        r'\*\)'
        t.lexer.comment_level -= 1
        # if matching the outer left parenthesis,
        # then return to INITIAL-state lexing
        if t.lexer.comment_level == 0:
            t.lexer.begin('INITIAL')

    def t_multilinecomment_newline(self, t):
        r'\n'
        t.lexer.lineno += 1

    def t_multilinecomment_other(self, t):
        r'[^\n(\*]+'
        return None

    def t_multilinecomment_lparen(self, t):
        r'\('
        return None

    def t_multilinecomment_star(self, t):
        r'\*'
        return None

    def t_multilinecomment_error(self, t):
        raise ValueError(
            'Illegal character "{s}"'.format(
                s=t.value[0]))

    t_multilinecomment_ignore = ''

    # (* exceptions *)
    # | ("[]" as op)
    #   { [ OP op ] }
    def t_ALWAYS(self, t):
        r'\[\]'
        return t

    # | ("(+)"|"(-)"|"(/)"|"(\\X)"|"(.)" as op)
    #   { [ OP op ] }
    def t_PAREN_OPERATOR(self, t):
        r'\(\+\)|\(-\)|\(/\)|\(\\X\)|\(\.\)'
        return t

    # (* strict punctuation *)
    # | "----" '-'*
    #   { [ PUNCT "----" ] }
    def t_DASH_LINE(self, t):
        r'----(-)*'
        return t

    # | "====" '='*
    #   { [ PUNCT "====" ] }
    def t_EQ_LINE(self, t):
        r'====(=)*'
        return t

    # | "<*>" ('.'* as dots)
    #   { [ ST ( `Star, "", String.length dots) ] }
    def t_STEP_NUMBER_STAR(self, t):
        r'<\*>(\.)*'
        return t

    # | "<+>" ('.'* as dots)
    #   { [ ST ( `Plus, "", String.length dots) ] }
    def t_STEP_NUMBER_PLUS(self, t):
        r'<\+>(\.)*'
        return t

    # | '<' (numeral+ as num) '>' (namechar* as lab)
    #       ('.'* as dots)
    #   { [ ST (`Num (int_of_string num),
    #       lab, String.length dots) ] }
    step_number = r'<{numeral}+>{namechar}*\.*'.format(
        numeral=numeral, namechar=namechar)

    @ply.lex.TOKEN(step_number)
    def t_STEP_NUMBER(self, t):
        return t

    # | (","|"."|"_"|"("|")"|"["|"]"|"{"|"}"
    #   |"<<"|">>"|"]_"|">>_"|"=="|"!"
    # |"@"|":"|"::"|";"|"->"|"<-"|"|->"|"\\A"
    #   |"\\AA"|"\\E"|"\\EE"|'_' as p)
    #   { [ PUNCT p ] }
    punctuation = (
        # '.' has been moved below to the method
        # `PUNCTUATION_DOT`
        r',|\(|\)|\[|\]_|\]|\{|\}|<<|>>_|>>|==|!'
        r'|\@|::|:|;|->|<-|\|->|\\AA|\\A|\\EE|\\E')
        # See also '_' in NAME
        # TODO: change \\A \\A \\E \\EE to prefix operators
        # in the grammar ?

    @ply.lex.TOKEN(punctuation)
    def t_PUNCTUATION(self, t):
        return t

    # (* numbers *)
    # | (numeral+ as ch) '.' (numeral+ as man)
    #   { [ NUM (ch, man) ] }
    float = '{numeral}+\.{numeral}+'.format(
        numeral=numeral)

    @ply.lex.TOKEN(float)
    def t_FLOAT(self, t):
        return t

    # | (numeral+ as i)
    #   { [ NUM (i, "") ] }
    integer = '{numeral}+'.format(numeral=numeral)

    @ply.lex.TOKEN(integer)
    def t_INTEGER(self, t):
        return t

    # | ("\\b" ['0' '1']+ as b)
    #   { Bytes.set (Bytes.of_string b) 0 '0' ;
    #     [ NUM (string_of_int (int_of_string b), "") ] }
    def t_BINARY_INTEGER(self, t):
        r'(\\b|\\B)[0-1]+'
        return t

    # | ("\\o" ['0'-'7']+ as o)
    #   { Bytes.set (Bytes.of_string o) 0 '0' ;
    #     [ NUM (string_of_int (int_of_string o), "") ] }
    def t_OCTAL_INTEGER(self, t):
        r'(\\o|\\O)[0-7]+'
        return t

    # | ("\\h" (numeral | ['a'-'f' 'A'-'F'])+ as h)
    #   { Bytes.set (Bytes.of_string h) 0 '0' ;
    #     Bytes.set (Bytes.of_string h) 1 'x' ;
    #     [ NUM (string_of_int (int_of_string h), "") ] }
    hexadecimal = '(\\h,\\H)({numeral}|[a-fA-F])+'

    @ply.lex.TOKEN(hexadecimal)
    def HEXADECIMAL_INTEGER(self, t):
        return t

    # def t_STRING(self, t):
    #     r'"[^"\']*"'
    #     return t

    def t_STRING(self, t):
        r'"'
        t.lexer.string_start = t.lexpos
        t.lexer.begin('string')

    def t_string_escaped_quotes(self, t):
        r'\\"|\\t|\\n|\\f|\\r|\\'

    def t_string_newline(self, t):
        r'\n'
        raise ValueError('Newline within string.')

    def t_string_other_characters(self, t):
        r'[^"\\]+'

    def t_string_closing(self, t):
        r'"'
        start = t.lexer.string_start
        end = t.lexpos + len(t.value)
        t.value = t.lexer.lexdata[start:end]
        t.lexer.begin('INITIAL')
        t.type = 'STRING'
        t.lexpos = start
        return t

    def t_string_error(self, t):
        raise ValueError(
            'Illegal character "{s}"'.format(
                s=t.value[0]))

    t_string_ignore = ''

    # (* prefix operators *)
    #   | ("\\neg"|"\\lnot"|"~"|"-."|"<>"|"UNION"|"SUBSET"
    #     |"ENABLED"|"UNCHANGED"|"DOMAIN" as op)
    #       { [ OP op ] }
    prefix_operator = (
        r'\\neg|\\lnot|~|-\.|<>')
    # See also PREFIX_OPERATORS

    #   (* postfix operators *)
    #   | ("'"|"^+"|"^*"|"^#" as op)
    #       { [ OP op ] }
    postfix_operator = r'\'|\^\+"|\^\*|\^\#'

    infix_operator = (
        r'>=|\\geq|<=>|<=|=<|\\leq|\#|/='
        r'|\\oplus|\\ominus|\\otimes|\\oslash'
        r'|\\odot|\\cap|\\intersect'
        r'|\\cup|\\union|\\equiv|\\o|\\circ|\\X|\\times'
        r'|=>|-\+->|/\\|\\land'
        r'|\\/|\\lor|/=|-\||::=|:=|<|=|=\||>|\\approx'
        r'|\\asymp|\\cong|\\doteq|\\gg|\\notin'
        r'|\\ll|\\preceq|\\prec'
        r'|\\propto|\\sim|\\simeq'
        r'|\\sqsubseteq|\\sqsubset|\\sqsupseteq'
        r'|\\sqsupset|\\subseteq|\\subset'
        r'|\\succeq|\\succ|\\supseteq|\\supset'
        r'|\|-|\|=|\\cdot|\@\@|:>|<:|\\in|\\'
        r'|\.\.\.|\.\.|!!|\#\#|\$\$|\$|\?\?|\\sqcap'
        r'|\\sqcup|\\uplus|\\wr|\+\+|\+|%%|%|\|\|'
        r'|\||--|-|&&|&|\*\*|\*|/|//|\\bigcirc|\\bullet'
        r'|\\div|\\star|\^\^|\^')

    def t_INFIX_OPERATOR_LEADSTO(self, t):
        r'~>'
        t.type = 'INFIX_OPERATOR'
        return t

    @ply.lex.TOKEN(prefix_operator)
    def t_PREFIX_OPERATOR(self, t):
        return t

    @ply.lex.TOKEN(postfix_operator)
    def t_POSTFIX_OPERATOR(self, t):
        return t

    @ply.lex.TOKEN(infix_operator)
    def t_INFIX_OPERATOR(self, t):
        return t

    # ensure that '..' appears before '.'
    def t_PUNCTUATION_DOT(self, t):
        r'\.'
        t.type = 'PUNCTUATION'
        return t


    def t_FAIRNESS(self, t):
        r'SF_|WF_'
        return t

    def t_NAME(self, t):
        r'[a-zA-Z_0-9]*[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in RESERVED:
            t.type = 'RESERVED'
        elif t.value in PREFIX_OPERATORS:
            t.type = 'PREFIX_OPERATOR'
        elif t.value == '_':
            t.type = 'PUNCTUATION'
        else:
            t.type = 'IDENTIFIER'
        return t

    # t_ignore is reserved by lex to provide
    # much more efficient internal handling by lex
    #
    # A string containing ignored characters (spaces)
    t_ignore = r' '  # whitesp

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    def t_tab(self, t):
        r'\t'
        raise ValueError('TAB characters are unsupported.')

    def t_error(self, t):
        logger.error(
            'Illegal character "{s}"'.format(s=t.value[0]))
        t.lexer.skip(1)


def lex(data):
    data = _omit_preamble(data)
    return _lex(data)


def _lex(data):
    lexer = Lexer()
    lexer.lexer.input(data)
    output = list()
    for token in lexer.lexer:
        # print(token)
        output.append(token)
    return output


def _omit_preamble(data):
    regex = r'----(-)*\s*MODULE'
    match = re.search(regex, data)
    n = match.start()
    return data[n:]


# This mapping is a separate step because `ply.lex`
# checks the type of token returned by each token rule.
def _map_to_token_(token):
    type_ = token.type
    # delimiters
    if type_ == 'DASH_LINE':
        return intf.PUNCT('----')
    elif type_ == 'EQ_LINE':
        return intf.PUNCT('====')
    elif type_ == 'PUNCTUATION':
        return intf.PUNCT(token.value)
    elif type_ == 'STEP_NUMBER':
        step_level = re.findall('<([0-9]+)>', token.value)[0]
        match = re.search(r'(\.)+', token.value)
        if match is None:
            n = 0
        else:
            n = len(match.group())
            assert n >= 1, match.group()
        step_name_regex = '<[0-9]+>([a-zA-Z0-9_]*)'
        step_name = re.findall(step_name_regex, token.value)[0]
        return intf.ST(intf.StepNum(step_level), step_name, n)
    elif type_ == 'STEP_NUMBER_PLUS':
        assert token.value[:3] == '<+>', token.value
        n = len(token.value[3:])
        return intf.ST(intf.StepPlus(), None, n)
    elif type_ == 'STEP_NUMBER_STAR':
        assert token.value[:3] == '<*>', token.value
        n = len(token.value[3:])
        return intf.ST(intf.StepStar(), None, n)
    # operators
    elif type_ == 'ALWAYS':
        return intf.OP(token.value)
    elif type_ == 'FAIRNESS':
        # TODO: change grammar to OP here ?
        return intf.PUNCT(token.value)
    elif type_ == 'INFIX_OPERATOR':
        return intf.OP(token.value)
    elif type_ == 'NAME':
        raise ValueError(
            'expected IDENTIFIER or RESERVED '
            'or PREFIX_OPERATOR or PUNCTUATION')
    elif type_ == 'PAREN_OPERATOR':
        return intf.OP(token.value)
    elif type_ == 'PREFIX_OPERATOR':
        return intf.OP(token.value)
    elif type_ == 'POSTFIX_OPERATOR':
        return intf.OP(token.value)
    # misc
    elif type_ == 'BINARY_INTEGER':
        # TODO: test
        assert token.value[:2] == '\\b', token.value
        return intf.NUM(token.value[2:], None)
    elif type_ == 'COMMENT':
        raise ValueError('unexpected COMMENT')
    elif type_ == 'FLOAT':
        a, b = token.value.split('.')
        return intf.NUM(a, b)
    elif type_ == 'HEXADECIMAL_INTEGER':
        # TODO: test
        assert token.value[:2] == '\\h', token.value
        value = int(token.value[2:], 16)
        return intf.NUM(str(value), None)
    elif type_ == 'IDENTIFIER':
        return intf.ID(token.value)
    elif type_ == 'INTEGER':
        return intf.NUM(token.value, None)
    elif type_ == 'LINECOMMENT':
        raise ValueError('unexpected LINECOMMENT')
    elif type_ == 'OCTAL_INTEGER':
        # TODO: test
        assert token.value[:2] == '\\o', token.value
        value = int(token.value[2:], 8)
        return intf.NUM(str(value), None)
    elif type_ == 'PRAGMAS':
        return intf.PUNCT(token.value)
    elif type_ == 'RESERVED':
        return intf.KWD(token.value)
    elif type_ == 'STRING':
        return intf.STR(token.value)
    else:
        raise ValueError(type_)


def _map_to_token(
        data, token,
        module_name='dummy_file'):
    # `data` is needed to find the beginning of line
    token_ = _map_to_token_(token)
    # print(token.__dict__)
    # _print_lextoken_info(token)
    # print('\n')
    line_number = token.lineno
    bol = find_beginning_of_line(data, token)
    start_column_offset = token.lexpos
    start_loc = _location.locus_of_position(
        module_name, line_number, bol, start_column_offset)
    assert '\n' not in token.value, (token.type, token.value)
    stop_column_offset = token.lexpos + len(token.value)
    stop_loc = _location.locus_of_position(
        module_name, line_number, bol, stop_column_offset)
    assert data[start_column_offset:
        stop_column_offset] == token.value, (
        data[start_column_offset:stop_column_offset],
        token.value)
    loc = start_loc.merge(stop_loc)
    assert len(token.value) == loc.stop.column - loc.start.column
    return intf.Token(token_, None, loc)


def find_beginning_of_line(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return line_start


def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


def _print_lextoken_info(token):
    """Print all the information stored in `token`.

    @type token: `ply.lex.LexToken`."""
    print('type: ', token.type)
    print('value: ', token.value)
    print('line number: ', token.lineno)
    print('offset: ', token.lexpos)


def _join_with_newlines(tokens):
    current_line = 1
    strings = list()
    for token in tokens:
        token_line = token.loc.start.line
        diff = token_line - current_line
        assert diff >= 0, (
            token_line, current_line)
        # commented due to multi-line comments
        # assert diff <= 1, (
        #     current_line, token_line)
        if token_line > current_line:
            # update current line
            # current_line += 1
            current_line += diff
            assert current_line == token_line, (
                current_line, token_line)
            # output newlines
            newlines = '\n' * diff
            strings.append(newlines)
        strings.append(str(token.form))
        strings.append(' ')
    return ''.join(strings)


MODULE_FOO = '''
comments
---- MODULE Foo ----
VARIABLE x

\* a one-line comment
\* a nested \* one-line comment

(* This is a multi-line comment. *)
(* This is a multi-line
comment. * (
*)
(* A nested
(* multi-line *)
comment. *)
a == 1.0
b == a + 2

A == x' = x + 1

P == SF_x(A)

THEOREM Thm ==
    ASSUME x = 1
    PROVE x + 1 = 2
PROOF
<1>1. x = 1
    OBVIOUS
<1>2. x + 1 = 1 + 1
    BY <1>1
<1>3. 1 + 1 = 2
    OBVIOUS
<1> QED
    BY <1>2, <1>3
====================
'''


def tokenize(data, omit_preamble=True):
    """Return `list` of `Token` instances."""
    if omit_preamble:
        data = _omit_preamble(data)
    lextokens = _lex(data)
    if (len(lextokens) >= 2 and
            lextokens[1].value == 'MODULE'):
        module_name = lextokens[2].value
    else:
        module_name = 'unknown module'
    tokens = [
        _map_to_token(
            data, token,
            module_name=module_name)
        for token in lextokens]
    return tokens


def _test_lexer():
    """Test lexing and conversions between tokens."""
    data = MODULE_FOO
    data = _omit_preamble(data)
    lextokens = _lex(data)
    # Token_ instances
    tokens_ = [
        _map_to_token_(token)
        for token in lextokens]
    pprint.pprint(tokens_)
    for token_ in tokens_:
        print(token_)
        print(str(token_))
    str_of_tokens_ = [
        str(token_) for token_ in tokens_]
    pprint.pprint(str_of_tokens_)
    # Token instances
    tokens = [
        _map_to_token(data, token)
        for token in lextokens]
    pprint.pprint(tokens)
    # join raw strings
    print(''.join(str_of_tokens_))
    # join with newlines in between
    s = _join_with_newlines(tokens)
    print(s)
    # check location information
    for token in tokens:
        print(token.loc)


if __name__ == '__main__':
    _test_lexer()
