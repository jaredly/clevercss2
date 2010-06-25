#!/usr/bin/env python
import operator
import consts
import re

class Value(object):
    methods = []
    def __init__(self, value, raw=True):
        if raw:
            value = self.parse(value)
        self.value = value
    
    def parse(self, value):
        return value
    
    def __repr__(self):
        return str(self)

    def calc(self, op, other):
        return NotImplemented

    __add__ = lambda self, other: self.calc(other, operator.add)
    __sub__ = lambda self, other: self.calc(other, operator.sub)
    __rsub__ = lambda self, other: self.calc(other, operator.sub, True)
    __div__ = lambda self, other: self.calc(other, operator.div)
    __rdiv__ = lambda self, other: self.calc(other, operator.div, True)
    __mul__ = lambda self, other: self.calc(other, operator.mul)

class Number(Value):
    rx = re.compile(r'(-?(?:\d+(?:\.\d+)?|\.\d+))(px|em|%|pt)?')
    def parse(self, value):
        match = self.rx.match(value)
        if not match:
            raise ValueError("invalid number '%s'" % value.encode('string_escape'))
        num,units = match.groups()
        num = float(num)
        if int(num) == num:
            num = int(num)
        return num, units
        
    def __str__(self):
        if self.value[1]:
            return u'%s%s' % self.value
        return str(self.value[0])

    def calc(self, other, op, reverse=False):
        if isinstance(other, Number):
            if reverse:
                newvalue = op(other.value[0], self.value[0])
            else:
                newvalue = op(self.value[0], other.value[0])
            if other.value[1] == self.value[1]:
                return Number((newvalue, self.value[1]), False)
            elif self.value[1] and other.value[1]:
                raise ValueError('cannot do math on numbers of differing units')
            elif self.value[1]:
                return Number((newvalue, self.value[1]), False)
            elif other.value[1]:
                return Number((newvalue, other.value[1]), False)
        return NotImplemented

    methods = ['abs', 'round']
    def abs(self):
        return Number((abs(self.value[0]), self.value[1]), False)

    def round(self, places=0):
        return Number((round(self.value[0], places), self.value[1]), False)

class String(Value):
    def __str__(self):
        return self.value

class Color(Value):
    def parse(self, value):
        if len(value) == 4:
            value = '#' + value[1]*2 + value[2]*2 + value[3]*2
        return int(value[1:3], 16), int(value[3:5], 16), int(value[5:], 16)

    def __str__(self):
        value = '#%02x%02x%02x' % self.value
        return consts.REV_COLORS.get(value) or value

    def calc(self, other, op):
        if isinstance(other, Color):
            return Color(tuple(op(a, b) for a,b in zip(self.value, other.value)), False)
        elif isinstance(other, Number):
            if other.value[1]:
                return NotImplemented
            return Color(tuple(op(a, other.value[0]) for a in self.value), False)
        return NotImplemented

    methods = ['brighten', 'darken']

    def brighten(self, amount=Number('10%')):
        if not isinstance(amount, Number) or amount not in (None, '%'):
            raise ValueError('invalid arg for brighten: %s' % amount)
        num = amount.value[0]
        if amount.value[1] == '%':
            num /= 100.0
        num += 1.0
        hsv = colorsys.rgb_to_hsv(v/255.0 for v in self.value)
        hsv[2] *= num
        return Color(tuple(int(v * 255) for v in colorsys.hsv_to_rgb(hsv)), False)
        
    def darken(self, amount=Number('10%')):
        if not isinstance(amount, Number) or amount not in (None, '%'):
            raise ValueError('invalid arg for brighten: %s' % amount)
        num = amount.value[0] * -1
        if amount.value[1] == '%':
            num /= 100.0
        num += 1.0
        hsv = colorsys.rgb_to_hsv(v/255.0 for v in self.value)
        hsv[2] *= num
        return Color(tuple(int(v * 255) for v in colorsys.hsv_to_rgb(hsv)), False)

# vim: et sw=4 sts=4
