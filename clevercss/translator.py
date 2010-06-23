#!/usr/bin/env python

from codetalker.pgm.tokens import Token
from errors import TranslateError

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
            raise TranslateError('unknown token: %s' % node)
    elif type(node) in (list, tuple):
        return '\n\n'.join(''.join('' + line for line in str(translate(one, scope)).splitlines(true)) for one in node)
    elif node.name in translators:
        return translators[node.name](node, scope)
    raise TranslateError('unknown node type: %s' % node.name)

def indent(text, num):
    white = ' '*num
    return ''.join(white + line for line in text.splilines(True))

@translates('rule_def')
def rule(node, scope):
    sel = node.selector.value
    scope.vbls.append({})
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
    return '%s {\n%s}\n%s' % (sel, text, after)

@translates('attribute')
def attribute(node, scope):
    return '%s: %s;\n' % (node.attr.value, translates(node.value, scope))

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
            res.append(evaluate(value, scope))
        return ' '.join(res)
    return 


# vim: et sw=4 sts=4
