#!/usr/bin/env python
'''
This is the grammar for CleverCSS. There's no pseudo-code here -- it's all
human readable, pythonic, syntax definition. How is it done? `CodeTalker
<http://github.com/jabapyth/codetalker>`_ has just been reloaded, and is
really awesome ;) 
'''

from codetalker.pgm import Grammar
from codetalker.pgm.special import star, plus, _or
from codetalker.pgm.tokens import STRING, ID, NUMBER, EOF, NEWLINE, WHITE, SYMBOL, CCOMMENT, ReToken, INDENT, DEDENT, StringToken

import re
class CSSNUMBER(ReToken):
    rx = re.compile(r'-?(?:\d+(?:\.\d+)?|\.\d+)(px|em|%|pt)?')

class CSSSELECTOR(ReToken):
    ## the more specific rx was **much** slower...
    rx = re.compile(r'[^\n]+:(?=\n)') #r'(?:[ \t]+|[.:#]?[\w-]+|[>,+&])+:(?=\n|$)')

class CSSID(ReToken):
    rx = re.compile(r'-?[a-zA-Z_][a-zA-Z0-9_-]*')

class CSSCOLOR(ReToken):
    rx = re.compile(r'#(?:[\da-fA-F]{3}|[\da-fA-F]{6})')

class SYMBOL(StringToken):
    items = tuple('+-*/@(),=:.')

def start(rule):
    rule | (star(_or(statement, NEWLINE)))

def statement(rule):
    rule | assign | declare | rule_def

def assign(rule):
    rule | (CSSID, '=', value, _or(NEWLINE, EOF))
    rule.astAttrs = {'left': 'CSSID', 'value': 'value'}

def attribute(rule):
    rule | (CSSID, ':', value, _or(NEWLINE, EOF))
    rule.astAttrs = {'attr': 'CSSID', 'value': 'value'}

def value(rule):
    rule | plus(add_ex)
    rule.astAttrs = {'values': 'BinOp[]'}

#def cssid(rule):
    #rule.no_ignore = True
    #rule | (_or(('-', ID), (ID)), star('-', ID))
    #rule.astAttrs = {'parts': 'ID,SYMBOL'}

def declare(rule):
    rule | ('@', CSSID, '(', [commas(add_ex)], ')', _or(NEWLINE, EOF))
    rule.astAttrs = {'name': 'CSSID', 'args': 'BinOp[]'}

def rule_def(rule):
    rule | (CSSSELECTOR, plus(NEWLINE), INDENT, plus(_or(statement, attribute, NEWLINE)), _or(DEDENT, EOF))
    rule.astAttrs = {'selector': 'CSSSELECTOR', 'body': 'statement,attribute'}

def binop(name, ops, next):
    def meta(rule):
        rule | (next, star(_or(*ops), next))
        next_name = getattr(next, 'astName', next.__name__)
        rule.astAttrs = {'left': next_name, 'ops': 'SYMBOL[]', 'values': '%s[1:]' % next_name}
    meta.astName = 'BinOp'
    return meta

def atomic(rule):
    rule | (literal, star(_or(post_attr, post_subs, post_call)))
    rule.astAttrs = {'literal':'literal', 'posts':'post_attr, post_subs, post_call'}

def literal(rule):
    rule | paren | STRING | CSSID | CSSNUMBER | CSSCOLOR
    rule.astAll = True

def paren(rule):
    rule | ('(', add_ex, ')')

def post_attr(rule):
    rule | ('.', CSSID)
    rule.astAttrs = {'name': 'CSSID'}

def post_subs(rule):
    rule | ('[', add_ex, ']')
    rule.astAttrs = {'subscript': 'BinOp'}

def post_call(rule):
    rule | ('(', [commas(add_ex)], ')')
    rule.astAttrs = {'args': 'BinOp[]'}

def post(rule):
    rule | ('.', CSSID) | ('[', add_ex, ']') | ('(', [commas(add_ex)], ')')
    rule.astAll = True

def commas(item):
    return (item, star(',', item), [','])

mul_ex = binop('mul_ex', '*/', atomic)
add_ex = binop('add_ex', '+-', mul_ex)
add_ex.astHelp = 'value (or expression)'

grammar = Grammar(start=start, indent=True, tokens=[CSSSELECTOR, STRING, CSSID, CSSNUMBER, CSSCOLOR, CCOMMENT, SYMBOL, NEWLINE, WHITE], ignore=[WHITE, CCOMMENT])

# vim: et sw=4 sts=4
