from unittest import TestCase, main

import unittest

'''
import color_convert
import ccss_to_css
import minify
import spritemap_test
'''
import parsing
import tokenize_
import one_liners

# mods = [color_convert, ccss_to_css, minify, spritemap_test]
mods = [parsing, tokenize_, one_liners]
def all_tests():
    return unittest.TestSuite(getattr(mod, 'all_tests')() for mod in mods)

