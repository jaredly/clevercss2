#!/usr/bin/env python

from codetalker.pgm import Translator, tokens
from errors import TranslateError
from grammar import grammar as ccssgrammar, declare_args
import grammar
import operator
import values
import consts

ccssgrammar.load_rule(declare_args)

CCSS = Translator(ccssgrammar, vbls=[consts.defaults.copy()], rule_stack=[], indent=4)

ast = ccssgrammar.ast_classes

def find_variable(name, scope):
    for vbls in scope.vbls:
        if name in vbls:
            return vbls[name]
    raise TranslateError('Undefined mixin %s' % name)

def handle_body(tree, scope):
    text, after = '', ''
    for node in tree.body:
        if isinstance(node, ast.rule_def):
            after += CCSS.translate(node, scope)
        elif isinstance(node, ast.declare):
            t, a = handle_declare(node, scope)
            text += t
            after += a
        else:
            text += CCSS.translate(node, scope)
    return text, after

@CCSS.translates(ast.start)
def start(node, scope):
    return ''.join(CCSS.translate(st, scope) for st in node.body)

@CCSS.translates(ast.assign)
def assign(node, scope):
    scope.vbls[0][node.left.value] = CCSS.translate(node.value, scope)
    return ''

@CCSS.translates(ast.value)
def value(node, scope):
    return ' '.join(str(CCSS.translate(single, scope)) for single in node.values)

@CCSS.translates(ast.declare)
def declarer(node, scope):
    text, after = handle_declare(node, scope)
    return text + '\n' + after

def handle_declare(node, scope):
    args, tree = find_variable(node.name.value, scope)
    scope.vbls.insert(0, {})
    i = 0
    for i, (arg, val) in enumerate(zip(args[0], node.args)):
        scope.vbls[0][arg] = CCSS.translate(val, scope)

    if i < len(args[0]) - len(args[1]) - 1:
        raise TranslateError('mixin %s requires at least %d argument (%d given)' % (node.name.value,
                                i, len(args[0]) - len(args[1])))

    for num in range(i+1, len(args[0])):
        scope.vbls[0][args[0][num]] = args[1][args[0][num]]

    text, after = handle_body(tree, scope)
    scope.vbls.pop(0)
    return text, after

@CCSS.translates(ast.attribute)
def attribute(node, scope):
    return '%s: %s;\n' % (node.attr.value, CCSS.translate(node.value, scope))

@CCSS.translates(ast.rule_def)
def rule_def(node, scope):
    selector = node.selector.value[:-1].strip()
    if selector.startswith('@'):
        args = declare_arguments(selector, scope)
        scope.vbls[0][selector[1:].split('(')[0]] = args, node
        return ''
    scope.vbls.insert(0, {})
    scope.rule_stack.append(selector)
    selector = get_selector(scope)
    text, after = handle_body(node, scope)
    scope.rule_stack.pop()
    scope.vbls.pop(0)
    if not text.strip():
        rule_text = ''
    else:
        rule_text = '%s {\n%s}\n' % (selector, indent(text, scope.indent))
    return rule_text + after

def get_selector(scope):
    rules = ['']
    for item in scope.rule_stack:
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

def declare_arguments(selector, scope):
    positional, default = [], {}
    if not selector.endswith(')'):
        if not '(' in selector:
            return [], {}
        else:
            raise TranslateError('Invalid syntax for mixin declaration: "%s"' % selector)
    elif not '(' in selector:
        raise TranslateError('Invalid syntax for mixin declaration: "%s"' % selector)
    ## ^ to do this right, list line/column numbers... TODO
    text = '(' + selector.split('(', 1)[1]
    tree = ccssgrammar.process(text, start=declare_args)
    tree = ccssgrammar.to_ast(tree)
    for arg in tree.args:
        if arg.value:
            default[arg.name.value] = CCSS.translate(arg.value, scope)
        positional.append(arg.name.value)
    return positional, default

@CCSS.translates(ast.BinOp)
def BinOp(node, scope):
    result = CCSS.translate(node.left, scope)
    operators = {'*': operator.mul, '/': operator.div, '+': operator.add, '-': operator.sub}
    for op, value in zip(node.ops, node.values):
        try:
            nv = CCSS.translate(value, scope)
            result = operators[op.value](result, nv)
        except TypeError:
            print [result, nv]
            raise
    return result

def indent(text, num):
    white = ' '*num
    return ''.join(white + line for line in text.splitlines(True))

@CCSS.translates(ast.atomic)
def atomic(node, scope):
    value = CCSS.translate(node.literal, scope)
    for post in node.posts:
        if isinstance(post, ast.post_attr): # post.name == 'post_attr':
            value = getattr(value, str(post.name.value))
        elif isinstance(post, ast.post_subs): # post.name == 'post_subs':
            sub = CCSS.translate(post.subscript, scope)
            value = value.__getitem__(sub)
        elif isinstance(post, ast.post_call): # post.name == 'post_call':
            args = []
            for arg in post.args:
                args.append(CCSS.translate(arg, scope))
            value = value(*args)
        else:
            raise TranslateError('invalid postfix operation found: %s' % repr(post))
    return value

@CCSS.translates(grammar.CSSID)
def literal(node, scope):
    for dct in scope.vbls:
        if node.value in dct:
            return dct[node.value]
    if node.value in consts.CSS_VALUES:
        return node.value
    elif node.value in consts.CSS_FUNCTIONS:
        return consts.css_func(node.value)
    elif node.value in consts.COLORS:
        return values.Color(consts.COLORS[node.value])
    raise ValueError('Undefined variable: %s' % node.value)

@CCSS.translates(tokens.STRING)
def string(node, scope):
    return node.value

'''value types....

number (2, 3.5, 50%, 20px)
string (whatever)
function

'''

@CCSS.translates(ast.value)
def value(node, scope):
    res = None
    if len(node.values) > 1:
        res = []
        for value in node.values:
            res.append(str(CCSS.translate(value, scope)))
        return ' '.join(res)
    elif not node.values:
        print node._tree
        raise ValueError('no values')
    return CCSS.translate(node.values[0], scope)

@CCSS.translates(grammar.CSSCOLOR)
def color(node, scope):
    return values.Color(node.value)

@CCSS.translates(grammar.CSSNUMBER)
def number(node, scope):
    return values.Number(node.value)


# vim: et sw=4 sts=4
