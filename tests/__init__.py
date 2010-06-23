from unittest import TestCase, main

import unittest

'''
import color_convert
import ccss_to_css
import minify
import spritemap_test
'''
import parsing

# mods = [color_convert, ccss_to_css, minify, spritemap_test]
mods = [parsing]
def all_tests():
    return unittest.TestSuite(getattr(mod, 'all_tests')() for mod in mods)

