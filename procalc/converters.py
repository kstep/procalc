# coding: utf-8
from __future__ import division

import math
import struct
import __builtin__ as core
import re

def strdig(d):
    return str(d) if d < 10 else chr(d + 55)

def noop(n):
    return n

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


        self._renum = re.compile('^' + snumber + '$')
        self._recnum = re.compile('^' + cnumber + '$')
        self._reinum = re.compile('^' + inumber + '$')

        self.set_precision(-1, -1)
        self.set_mode(0)
        self.set_base(10)

    def set_precision(self, integ, fract):
        integ, fract = int(integ), int(fract)
        self._precision = (integ, fract)
        self._adjust_pipe = (
                noop if integ < 1 else lambda n: n.lstrip('0').rjust(integ, '0'),
                noop if fract < 1 else lambda n: n.rstrip('0').ljust(fract, '0')
                )

    def set_mode(self, mode):
        '''
        0 - normal,
        1 - raw,
        2 - binary exp,
        3 - base exp.
        '''
        self._exponent_pipe = [
                lambda n: (n, 0),
                lambda n: (raw(n), 0),
                self.split_exponent,
                math.frexp
                ][int(mode)]

    def set_base(self, base):
        self._prefix = {2: '0b', 8: '0o', 10: '', 16: '0x'}.get(base)
        self._convert_pipe = {
                2: lambda n: bin(n).lstrip('0b').rstrip('L'),
                8: lambda n: oct(n).lstrip('0').rstrip('L'),
                10: lambda n: str(n).rstrip('L'),
                16: lambda n: hex(n).lstrip('0x').rstrip('L').upper()
                }.get(int(base))
        self._base = base
        self._bits = nbits(base - 1)

    def parse(self, s):
        '''
        Parts:
        sign, base, integer, fraction, exponent
        '''
        if isinstance(s, (int, long, float, complex)):
            return s

        def compose(sign, base, integer, fraction, exponent):
            base = {'0x': 16, '0o': 8, '0b': 2}.get(base, 10)
            if base == 10:
                for c in 'ABCDEF':
                    if c in s:
                        base = 16
                        break

            if base == 10:
                if fraction or exponent:
                    n = (sign or '') + (integer or '0') + '.' + (fraction or '0') + 'e' + (exponent or '0')
                    return float(n)
                else:
                    return int((sign or '') + (integer or '0'))

            sign = sign == '-' and -1 or 1

            integer = int(integer or '0', base)
            if fraction:
                integer += sum(int(a, base) / base ** (i + 1) for i, a in enumerate(fraction))

            if exponent:
                integer *= base ** int(exponent, base)

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
        if isinstance(x, complex):
            return self.format(x.real) + ('-' if x.imag < 0 else '') + self.format(x.imag) + 'j'

        number, exponent = self._exponent_pipe(x)
        if exponent:
            exponent = 'e' + self._convert_pipe(exponent)
        else:
            exponent = ''

        if isinstance(number, (int, long)):
            return self.format_integer(number) + exponent

        elif isinstance(number, float):
            return self.format_float(number) + exponent

        else:
            raise ValueError('Expected int, long, float or complex, got %s' % type(x).__name__)

    def format_integer(self, x):
        return (x < 0 and '-' or '') + self._prefix + (self._adjust_pipe[0](self._convert_pipe(abs(x))) or '0')

    def format_float(self, x):
        fraction, integer = math.modf(x)
        if self._base == 10:
            fraction = str(fraction)[2:]

        else:
            align = self._base == 8 and 54 or 52
            fraction = int(abs(fraction) * 2 ** align)
            fraction = self._convert_pipe(fraction).rjust(align // self._bits, '0').rstrip('0')

        fraction = self._adjust_pipe[1](fraction) or '0'
        return self.format_integer(int(integer)) + '.' + fraction

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

    def split_exponent(self, x):
        power = int(math.ceil(math.log(x, self._base))) - self._precision[0]
        return x / self._base ** power, power


def nbits(n):
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
        r = str(i & 1) + r
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

