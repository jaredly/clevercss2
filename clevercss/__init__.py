#!/usr/bin/env python

from grammar import grammar
from translator import translate
import consts

from ctranslator import CCSS

VERSION = '0.5'

def convert(source, variables={}, indent=2, fname=None, minified=False):
    """Convert CleverCSS text into normal CSS."""
    return CCSS.from_string(source, indent=indent, fname=fname, minified=minified, variables={})

# vim: et sw=4 sts=4
