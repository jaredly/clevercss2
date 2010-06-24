#!/usr/bin/env python

from codetalker.pgm.tokens import Token
from codetalker.pgm import tokens
from errors import TranslateError
import operator
import grammar
import values
import consts

translators = {}
def translates(name):
    def meta(func):
        translators[name] = func
        return func
    return meta

def translate(node, scope):
    if isinstance(node, Token):
        if node.__class__ in translators:
            return translators[node.__class__](node, scope)
        else:
            raise TranslateError('Unknown token: %s' % repr(node))
    elif type(node) in (list, tuple):
        return '\n'.join(''.join('' + line for line in str(translate(one, scope)).splitlines(True)) for one in node)
    elif node.name in translators:
        return translators[node.name](node, scope)
    raise TranslateError('unknown node type: %s' % node.name)

def indent(text, num):
    white = ' '*num
    return ''.join(white + line for line in text.splitlines(True))

@translates('rule_def')
def rule(node, scope):
    sel = node.selector.value[:-1].strip()
    scope.vbls.append({})
    scope.rules.append(sel)
    text = ''
    after = ''
    for item in node.body:
        if type(item) == list:
            if item[0].name == 'assign':
                translate(item[0], scope)
            elif item[0].name == 'declare':
                raise TranslateError('declaratives not yet supported...')
            elif item[0].name == 'rule_def':
                after += translate(item[0], scope)
            else:
                raise TranslateError('unexpected sub rule')
        else:
            text += translate(item, scope)
    scope.vbls.pop(-1)
    selector = get_selector(scope)
    scope.rules.pop(-1)
    if not text:
        rule_text = ''
    else:
        rule_text = '%s {\n%s}\n' % (selector, indent(text, 2))
    return rule_text + after

def get_selector(scope):
    rules = ['']
    for item in scope.rules:
        new = []
        for parent in rules:
            for child in item.split(','):
                child = child.strip()
                if '&' in child:
                    new.append(child.replace('&', parent).strip())
                else:
                    new.append((parent + ' ' + child).strip())
        rules = new
    return ', '.join(rules)
        

@translates('attribute')
def attribute(node, scope):
    return '%s: %s;\n' % (node.attr.value, translate(node.value, scope))

@translates('atomic')
def atomic(node, scope):
    value = translate(node.literal, scope)
    #if getattr(value, '__name__', None) == 'meta':
        #print 'meta -- css_func', [value, node.literal, node.posts]
    for post in node.posts:
        if post.name == 'post_attr':
            value = getattr(value, str(post.name.value))
        elif post.name == 'post_subs':
            sub = translate(post.subscript, scope)
            value = value.__getitem__(sub)
        elif post.name == 'post_call':
            args = []
            for arg in post.args:
                args.append(translate(arg, scope))
            value = value(*args)
        else:
            raise TranslateError('invalid postfix operation found: %s' % repr(post))
    return value

@translates('literal')
def literal(node, scope):
    return translate(node.items[0], scope)

@translates(grammar.CSSID)
def literal(node, scope):
    for dct in reversed(scope.vbls):
        if node.value in dct:
            return dct[node.value]
    if node.value in consts.CSS_VALUES:
        return node.value
    elif node.value in consts.CSS_FUNCTIONS:
        return consts.css_func(node.value)
    raise ValueError('undefined variable: %s' % node.value)

@translates(tokens.STRING)
def string(node, scope):
    return node.value

'''value types....

number (2, 3.5, 50%, 20px)
string (whatever)
function

'''

@translates('value')
def value(node, scope):
    res = None
    if len(node.values) > 1:
        res = []
        for value in node.values:
            res.append(str(translate(value, scope)))
        return ' '.join(res)
    elif not node.values:
        print node._tree
        raise ValueError('no values')
    return translate(node.values[0], scope)

@translates('BinOp')
def BinOp(node, scope):
    result = translate(node.left, scope)
    operators = {'*': operator.mul, '/': operator.div, '+': operator.add, '-': operator.sub}
    for op, value in zip(node.ops, node.values):
        try:
            nv = translate(value, scope)
            result = operators[op.value](result, nv)
        except TypeError:
            print [result, nv]
            raise
    return result

@translates(grammar.CSSCOLOR)
def color(node, scope):
    return values.Color(node.value)

@translates(grammar.CSSNUMBER)
def number(node, scope):
    return values.Number(node.value)

@translates('paren')
def paren(node, scope):
    return translate(node.value, scope)

# vim: et sw=4 sts=4
