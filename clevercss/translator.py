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
        return '\n'.join(''.join('' + line for line in str(translate(one, scope)).splitlines(True)) for one in node).strip() + '\n'
    elif node.name in translators:
        return translators[node.name](node, scope)
    raise TranslateError('unknown node type: %s' % node.name)

def indent(text, num):
    white = ' '*num
    return ''.join(white + line for line in text.splitlines(True))

def define_mixin(sel, node, scope):
    sel = sel.strip()
    if '(' in sel[1:]:
        name, args = sel[1:-1].split('(', 1)
        # TODO: have all the args processed by yon grammar
        args = args.split(',')
        pos = []
        defaults = {}
        dflag = False
        for arg in args:
            arg = arg.strip()
            if '=' in arg:
                dflag = True
                n, v = arg.strip().split('=')
                pos.append(n)
                dnode = grammar.grammar.process(v, grammar.add_ex)
                dnode = grammar.grammar.toAst(dnode)
                defaults[n] = translate(dnode, scope)
            elif dflag:
                raise TranslateError('positional argument after default argument: %s' % (repr(node)))
            else:
                pos.append(arg)
    else:
        pos = []
        defaults = {}
        name = sel[1:]
    # print 'mixingin', name, pos, defaults
    scope.vbls[-1][name] = (pos, defaults, node)
    return ''

def handle_body(node, scope):
    text = ''
    after = ''
    for item in node.body:
        if type(item) == list:
            if item[0].name == 'assign':
                translate(item[0], scope)
            elif item[0].name == 'declare':
                t, a = declare(item[0], scope)
                text += t
                after += a
            elif item[0].name == 'rule_def':
                after += translate(item[0], scope)
            else:
                raise TranslateError('unexpected sub rule %s %s' % (item[0].name, repr(item[0])))
        else:
            text += translate(item, scope)
    return text, after

@translates('rule_def')
def rule(node, scope):
    sel = node.selector.value[:-1].strip()
    if sel.startswith('@'):
        return define_mixin(sel, node, scope)
    scope.vbls.append({})
    scope.rules.append(sel)
    text, after = handle_body(node, scope)
    scope.vbls.pop(-1)
    selector = get_selector(scope)
    scope.rules.pop(-1)
    if not text.strip():
        rule_text = ''
    else:
        rule_text = '%s {\n%s}\n' % (selector, indent(text, scope.indent))
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

@translates('declare')
def declares(node, scope):
    t, a = declare(node, scope)
    return t + '\n' + a

def declare(node, scope):
    for vbls in reversed(scope.vbls):
        if node.which.value in vbls:
            pos, dfl, dnode = vbls[node.which.value]
            break
    else:
        raise TranslateError('Undefined mixin called: %s' % repr(node.which))
    scope.vbls.append({})
    args = node.args
    i = 0
    for i, (arg, val) in enumerate(zip(pos, args)):
        scope.vbls[-1][arg] = translate(val, scope)
    if i < len(args) - len(dfl) - 1:
        raise TranslateError('Not enough arguments for mixin %s; at least %d re required (%d given)' % (node.which.value, i, len(pos) - len(dfl)))
    for a in range(i+1, len(pos)):
        scope.vbls[-2][pos[a]] = dfl[pos[a]]
    text, after = handle_body(dnode, scope)
    scope.vbls.pop(-1)
    return text, after

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
    elif node.value in consts.COLORS:
        return values.Color(consts.COLORS[node.value])
    raise ValueError('Undefined variable: %s' % node.value)

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
    # print 'first result %r ::::: from %r' % (result, node.left)
    operators = {'*': operator.mul, '/': operator.div, '+': operator.add, '-': operator.sub}
    for op, value in zip(node.ops, node.values):
        try:
            nv = translate(value, scope)
            result = operators[op.value](result, nv)
        except TypeError:
            print [result, nv]
            raise
    return result

@translates('assign')
def assign(node, scope):
    scope.vbls[-1][node.left.value] = translate(node.value, scope)
    return ''

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
