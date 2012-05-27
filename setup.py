#!/usr/bin/env python
from distutils.core import setup
import os

fp = open(os.path.join(os.path.dirname(__file__), "README.rst"))
readme_text = fp.read()
fp.close()

setup(
    name='CleverCSS2',
    author='Jared Forsyth',
    author_email='jared@jaredforsyth.com',
    version='0.2',
    url='http://github.com/jabapyth/clevercss2',
    download_url='http://github.com/jabapyth/clevercss2/tree',
    packages=['clevercss'],
    description='python inspired sass-like css preprocessor',
    long_description=readme_text,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python'
    ],
    requires=['codetalker'],
    scripts=['bin/ccss',],
    test_suite = 'tests.all_tests',
)
