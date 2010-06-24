#!/usr/bin/env python

import magictest
from magictest import MagicTest as TestCase

import clevercss
from clevercss.grammar import grammar
from codetalker.pgm.grammar import Text, ParseError
from codetalker.pgm.errors import *

class Tokenize(TestCase):
    def tokens(self):
        text = Text('hello = world')
        tokens = grammar.get_tokens(text)
        self.assertEqual(len(tokens.tokens), 6)
        self.assertEqual(tokens.tokens[2].charno, 7)
        self.assertEqual(tokens.tokens[-2].value, 'world')

    def token_lines(self):
        text = Text('hello\nworld = 6')
        tokens = grammar.get_tokens(text)
        self.assertEqual(len(tokens.tokens), 8)
        self.assertEqual(tokens.tokens[-2].lineno, 2)


class Parse(TestCase):
    def parse(self):
        text = 'hello=orld\n\nother=bar\n'
        tree = check_parse(text)

    def rule_def(self):
        text = 'div:\n  a = b\n  @import(d)'
        tree = check_parse(text)

    def selectors(self):
        text = '#some:\n stuff = 3\n\n#other .stuff:\n k = ok'
        tree = check_parse(text)

    def hyphen(self):
        text = '.a-b-c:\n and = other'
        tree = check_parse(text)

    def color(self):
        check_parse('five = #555\n\na = #666666')
        try:
            check_parse('one = #1111')
            raise Exception('supposed to fail on #1111')
        except:
            pass

    def attr(self):
        check_parse('one:\n two: 4\n three = 7')
        check_parse('one:\n -moz-something: 17')
        check_fail('two: 4')
        check_fail('one:\n -moz -space: 5')

    def neg_number(self):
        check_parse('one = -10')
        check_parse('one = -10px')
        check_parse('one = 10%')
        check_parse('one = -10em')
        check_parse('one = -10%')

    def url(self):
        check_parse('one = url("hello.png")')

def make_pass(grammar, text):
    def meta(self):
        try:
            return grammar.process(text)
        except ParseError:
            return grammar.process(text, debug=True)
    return meta

def make_fail(grammar, text):
    def meta(self):
        try:
            tree = grammar.process(text)
            self.fail('Expected "%s" to fail' % text.encode('string_escape'))
        except ParseError:
            pass
    return meta

strings = [(
    '',
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

for i, good in enumerate(strings[0]):
    setattr(Parse, '%d_good' % i, make_pass(grammar, good))
for i, bad in enumerate(strings[1]):
    setattr(Parse, '%d_bad' % i, make_fail(grammar, good))

class Convert(TestCase):
    pass

cases = (('body:\n top: 5', 'body {\n  top: 5;\n}\n', 'basic'),
        ('body:\n top: 2+4', 'body {\n  top: 6;\n}\n', 'add'),
        ('body:\n top: (5+4 - 1) /2', 'body {\n  top: 4;\n}\n', 'math'),
        ('one = 2\nbody:\n top: one', 'body {\n  top: 2;\n}\n', 'vbl'),
        ('one = 2\nbody:\n top: one+3', 'body {\n  top: 5;\n}\n', 'vbl2'))

def make_convert(ccss, css):
    def meta(self):
        self.assertEqual(clevercss.convert(ccss), css)
    return meta

for i, (ccss, css, name) in enumerate(cases):
    setattr(Convert, 'convert_%d_%s' % (i, name), make_convert(ccss, css))

def check_parse(text):
    try:
        return grammar.process(text)
    except:
        return grammar.process(text, debug=True)

def check_fail(text):
    try:
        grammar.process(text)
    except:
        pass
    else:
        grammar.process(text, debug=True)
        raise Exception('was supposed to fail on \'%s\'' % text.encode('string_escape'))
 
all_tests = magictest.suite(__name__)

# vim: et sw=4 sts=4
