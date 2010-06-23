#!/usr/bin/env python

from grammar import grammar
from translator import translate

VERSION = '0.5'

def convert(source, context=None, fname=None, minified=False):
    """Convert CleverCSS text into normal CSS."""
    tree = grammar.process(source)
    ast = grammar.toAst(tree)
    text = translate(ast, context)
    return text

# vim: et sw=4 sts=4
