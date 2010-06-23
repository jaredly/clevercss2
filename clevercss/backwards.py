#!/usr/bin/env python

import cssutils
import logging
cssutils.log.setLevel(logging.FATAL)

def parseCSS(text):
    parser = cssutils.CSSParser()
    css = parser.parseString(text)
    rules = {}
    for rule in css.cssRules:
        commas = rule.selectorText.split(',')
        for comma in commas:
            parts = comma.split()
            c = rules
            for i, part in enumerate(parts):
                if part in '>+':
                    parts[i+1] = '&' + part + parts[i+1]
                    continue
                c = c.setdefault(part, {})
            c.setdefault(':rules:', []).append(rule)
    return rules

def rulesToCCSS(selector, rules):
    text = selector + ':\n  '
    if rules.get(':rules:'):
        text += '\n\n  '.join('\n  '.join(line.strip().rstrip(';') for line in rule.style.cssText.splitlines()) for rule in rules.get(':rules:', [])) + '\n'
    for other in rules:
        if other == ':rules:':
            continue
        text += '\n  ' + rulesToCCSS(other, rules[other]).replace('\n', '\n  ')
    return text

def cleverfy(fname):
    rules = parseCSS(open(fname).read())
    text = ''
    for rule in rules:
        text += rulesToCCSS(rule, rules[rule]) + '\n\n'
    return text

# vim: et sw=4 sts=4
