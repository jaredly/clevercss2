#!/usr/bin/env python

from grammar import grammar
from translator import translate
import consts

from ctranslator import CCSS

VERSION = '0.5'

class Scope:
    pass

def convert(source, variables={}, indent=2, fname=None, minified=False):
    """Convert CleverCSS text into normal CSS."""
    # tree = grammar.process(source)
    # ast = grammar.to_ast(tree)
    # context = Scope()
    # context.vbls = [consts.defaults, variables.copy()]
    # context.indent = indent
    # context.rules = []
    # text = translate(ast, context)
    return CCSS.from_string(source, indent=indent, fname=fname, minified=minified, variables={})
    # return text

# vim: et sw=4 sts=4
