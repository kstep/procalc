# coding: utf-8
from __future__ import division

import math
import struct
import __builtin__ as core
import re

def strdig(d):
    return str(d) if d < 10 else chr(d + 55)

class IntComplex(complex):
    def __init__(self, real, imag):
        self.real = int(real)
        self.imag = int(imag)

    def __str__(self):
        return "(%d%+dj)" % (self.real, self.imag)

class Converter(object):

    def __init__(self):
        sign = r'([+-])'
        number = r'(0x|0o|0b)?([0-9A-F]+)?(?:\.([0-9A-F]+))?(?:e([+-]?[0-9A-F]+))?'
        snumber = sign + '?' + number
        inumber = snumber + 'j'
        cnumber = snumber + sign + number + 'j'


        self._renum = re.compile(snumber)
        self._recnum = re.compile(cnumber)
        self._reinum = re.compile(inumber)

        self.set_precision(-1, -1)
        self.set_raw_mode(False)
        self.set_base(10)

    def set_precision(self, integer, fraction):
        self._precision = (int(integer), int(fraction))

    def set_raw_mode(self, value):
        self._raw_mode = bool(value)

    def set_base(self, base):
        self._prefix = {2: '0b', 8: '0o', 10: '', 16: '0x'}.get(base)
        self._converter = {2: bin, 8: oct, 10: str, 16: hex}.get(base)
        self._base = base

    def parse(self, s):
        '''
        Parts:
        sign, base, integer, fraction, exponent
        '''
        if isinstance(s, (int, long, float, complex)):
            return s

        def compose(sign, base, integer, fraction, exponent):
            if not base:
                return (float if fraction or exponent else int)(s)

            base = {'0x': 16, '0o': 8, '0b': 2}.get(base, 10)
            sign = sign == '-' and -1 or 1

            integer = int(integer or '0', base)
            if fraction:
                integer += sum(int(a, base) / base ** i for i, a in enumerate(fraction))

            if exponent:
                integer *= base ** exponent

            return sign * integer

        if s.endswith('j'):  # complex
            parsed = self._recnum.match(s)
            if parsed:
                parts = parsed.groups()
                real = compose(*parts[0:5])
                imag = compose(*parts[5:10])
            else:
                parsed = self._reinum.match(s)
                real = 0
                imag = compose(*parsed.groups())
            return complex(real, imag)

        else:  # real
            parsed = self._renum.match(s)
            return compose(*parsed.groups())

    def format(self, x):
        if x < 0:
            prefix = '-' + self._prefix
        else:
            prefix = self._prefix

        if self._raw_mode:
            x = self.raw(x)

        def format_integer(n):
            number = self._converter(abs(n)).lstrip('0bxo') or '0'
            if self._precision[0] > -1:
                number = number.rjust(self._precision[0], '0')
            return prefix + number

        def format_fraction(n):
            number = self._format_fraction(n)
            if self._precision[1] > -1:
                number = number.ljust(self._precision[1] + 1, '0')
            return number

        if isinstance(x, (int, long)):
            return format_integer(x)

        elif isinstance(x, float):
            fraction, integer = math.modf(x)
            return format_integer(int(integer)) + format_fraction(abs(fraction))

        elif isinstance(x, complex):
            real = self.format(x.real)
            if x.imag == 0:
                return real

            imag = self.format(x.imag)
            if x.imag > 0:
                imag = '+' + imag

            return real + imag

    def _format_fraction(self, x):
        result = ''
        prec = self._precision[1]
        if prec < 0:
            prec = 1000
        base = self._base

        while x and len(result) < prec:
            x, d = math.modf(x * base)
            result += strdig(int(d))

        if result:
            result = '.' + result
        return result

    def repack(self, x, f, t):
        return struct.unpack(t, struct.pack(f, x))[0]

    def raw(self, x):
        if isinstance(x, float):
            f, t = 'd', 'Q'

        elif isinstance(x, (int, long)):
            if x > 0:
                return x
            f, t = 'q', 'Q'

        elif isinstance(x, complex):
            return IntComplex(self.raw(x.real), self.raw(x.imag))

        return self.repack(x, f, t)


def bits(n):
    '''
    Get number of bits in integer number.

    >>> bits(10)
    4
    '''
    c = 0
    while n:
        c += 1
        n >>= 1
    return c

def bin(i):
    r = ''
    while i:
        r += str(i & 1)
        i >>= 1
    r = '0b' + (r or '0')
    if i < 0:
        r = '-' + r
    return r

def fint(x):
    '''
    >>> fint(10.0)
    4621819117588971520L
    '''
    if isinstance(x, float):
        return struct.unpack('Q', struct.pack('d', x))[0]
    else:
        return int(x)

def intf(x):
    '''
    >>> intf(4621819117588971520L)
    10.0
    '''
    if isinstance(x, (int, long)):
        return struct.unpack('d', struct.pack('Q', x))[0]
    else:
        return x

def sint(x):
    if x < 0:
        return int(x)
    return struct.unpack('q', struct.pack('Q', int(x)))[0]

def uint(x):
    return struct.unpack('Q', struct.pack('q', int(x)))[0]

