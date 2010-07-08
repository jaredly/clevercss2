#!/usr/bin/env python

import magictest
from magictest import MagicTest as TestCase
from clevercss.grammar import grammar

class Parse(TestCase):
    pass

strings = [(
    # assignment + expressions
    'a = b',
    '\na = b + c',
    'a = b+c/3.0 - 12',
    'a = 12px',
    'a= 12px + 1/4%',
    'a = a b',
    # @declares
    '@import("abc.css")',
    '@dothis()',
    '@other(1, 3, 4+5, 45/manhatten)',
),()]

def make_pass(text):
    def meta(self):
        result = grammar.process(text)
        self.assertEquals(str(result), text)
        # self.assertEquals(''.join(str(tk) for tk in result), text)
    return meta

for st in strings[0]:
    setattr(Parse, st, make_pass(st))

all_tests = test_suite = magictest.suite(__name__)

# vim: et sw=4 sts=4
