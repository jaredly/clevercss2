#!/usr/bin/env python

from grammar import grammar
from translator import translate
import consts

VERSION = '0.5'

class Scope:
    pass

def convert(source, variables={}, indent=2, fname=None, minified=False):
    """Convert CleverCSS text into normal CSS."""
    tree = grammar.process(source)
    ast = grammar.toAst(tree)
    context = Scope()
    context.vbls = [consts.defaults, variables.copy()]
    context.indent = indent
    context.rules = []
    text = translate(ast, context)
    return text

# vim: et sw=4 sts=4
