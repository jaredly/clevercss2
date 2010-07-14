#!/usr/bin/env python
'''
This is the grammar for CleverCSS. There's no pseudo-code here -- it's all
human readable, pythonic, syntax definition. How is it done? `CodeTalker
<http://github.com/jabapyth/codetalker>`_ has just been reloaded, and is
really awesome ;) 
'''

from codetalker.pgm import Grammar
from codetalker.pgm.special import star, plus, _or, commas
from codetalker.pgm.tokens import STRING, ID, NUMBER, EOF, NEWLINE, WHITE, CCOMMENT, ReToken, INDENT, DEDENT, StringToken

class SYMBOL(StringToken):
    items = list('.()=:')

import re
class CSSNUMBER(ReToken):
    rx = re.compile(r'-?(?:\d+(?:\.\d+)?|\.\d+)(px|em|%|pt)?')

class CSSSELECTOR(ReToken):
    ## the more specific rx was **much** slower...
    rx = re.compile(r'[^\n]+:(?=\n)') #r'(?:[ \t]+|[.:#]?[\w-]+|[>,+&])+:(?=\n|$)')

class CSSID(ReToken):
    rx = re.compile(r'-?[a-zA-Z_][a-zA-Z0-9_-]*')

class CSSCOLOR(ReToken):
    rx = re.compile(r'#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})')

class SYMBOL(StringToken):
    items = tuple('+-*/@(),=:.')

def start(rule):
    rule | (star(_or(statement, NEWLINE)))
    rule.astAttrs = {'body': statement}

def statement(rule):
    rule | assign | declare | rule_def
    rule.pass_single = True

def assign(rule):
    rule | (CSSID, '=', value, _or(NEWLINE, EOF))
    rule.astAttrs = {'left': {'type':CSSID, 'single':True}, 'value': {'type':value, 'single':True}}

def attribute(rule):
    rule | (CSSID, ':', value, _or(NEWLINE, EOF))
    rule.astAttrs = {'attr': {'type':CSSID, 'single':True}, 'value': {'type':value, 'single':True}}

def value(rule):
    rule | plus(expression)
    rule.astAttrs = {'values': expression}

def declare(rule):
    rule | ('@', CSSID, '(', [commas(expression)], ')', _or(NEWLINE, EOF))
    rule.astAttrs = {'name': {'type':CSSID, 'single':True}, 'args': expression}

def rule_def(rule):
    rule | (CSSSELECTOR, plus(NEWLINE), INDENT, plus(_or(statement, attribute, NEWLINE)), _or(DEDENT, EOF))
    rule.astAttrs = {'selector': {'type':CSSSELECTOR, 'single':True}, 'body': [statement, attribute]}

def binop(name, ops, next):
    def meta(rule):
        rule | (next, star(_or(*ops), next))
        rule.astAttrs = {'left': {'type':next, 'single':True}, 'ops': SYMBOL, 'values': {'type':next, 'start':1}}
    meta.astName = 'BinOp'
    return meta

def atomic(rule):
    rule | (literal, star(_or(post_attr, post_subs, post_call)))
    rule.astAttrs = {'literal':{'type':literal, 'single':True}, 'posts':(post_attr, post_subs, post_call)}

def mul_ex(rule):
    rule | (atomic, star(_or(*'*/'), atomic))
    rule.astAttrs = {'left': {'type':atomic, 'single':True}, 'ops': SYMBOL, 'values': {'type':atomic, 'start':1}}
mul_ex.astName = 'BinOp'

def expression(rule):
    rule | (mul_ex, star(_or(*'-+'), mul_ex))
    rule.astAttrs = {'left': {'type':mul_ex, 'single':True}, 'ops': SYMBOL, 'values': {'type':mul_ex, 'start':1}}
expression.astName = 'BinOp'

def literal(rule):
    rule | paren | STRING | CSSID | CSSNUMBER | CSSCOLOR
    rule.pass_single = True

def paren(rule):
    rule | ('(', expression, ')')
    rule.pass_single = True

def post_attr(rule):
    rule | ('.', CSSID)
    rule.astAttrs = {'name': {'type':CSSID, 'single':True}}

def post_subs(rule):
    rule | ('[', expression, ']')
    rule.astAttrs = {'subscript': {'type':expression, 'single':True}}

def post_call(rule):
    rule | ('(', [commas(expression)], ')')
    rule.astAttrs = {'args': expression}

def declare_args(rule):
    rule | ('(', [commas(arg)], ')')
    rule.astAttrs = {'args': arg}

def arg(rule):
    rule | (CSSID, ['=', expression])
    rule.astAttrs = {'name':{'type':CSSID, 'single':True},
                     'value':{'type':expression, 'optional':True, 'single':True}}

grammar = Grammar(start=start, indent=True, tokens=[CSSSELECTOR, STRING, CSSID, CSSNUMBER, CSSCOLOR, CCOMMENT, SYMBOL, NEWLINE, WHITE], ignore=[WHITE, CCOMMENT], ast_tokens=[CSSID, CSSCOLOR, STRING, CSSNUMBER])

# vim: et sw=4 sts=4
