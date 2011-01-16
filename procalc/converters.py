# coding: utf-8
from __future__ import division

import math
import struct
import re

# Base functions

def strd(d):
    return str(d) if d < 10 else chr(d + 55)

def noop(n):
    return n

def bin(x):
    r = ''
    n = abs(int(x))
    while n:
        r = str(n & 1) + r
        n >>= 1
    if x < 0:
        return '-' + r
    return r

def repack(x, f, t):
    return struct.unpack(t, struct.pack(f, x))[0]

def raw(x):
    if isinstance(x, float):
        f, t = 'd', 'Q'

    elif isinstance(x, (int, long)):
        if x > 0:
            return x
        f, t = 'q', 'Q'

    return repack(x, f, t)

def fbconv(x, base, prec=100):
    r = ''
    while x and len(r) < prec:
        x, a = math.modf(x * base)
        r += strd(int(a))
    return r

def bfrexp(x, base, lng=0):
    power = int(math.log(abs(x), base)) - lng + 1
    return x / base ** power, power

# Formatter generators

format_char = {16: ('X', '0x', None), 10: ('d', '', None), 8: ('o', '0o', None), 2: ('s', '0b', bin)}

def format_func1(lng, dec, base):
    char, pfx, func = format_char.get(base)
    format = '%%s%s%%0%d%s' % (pfx, abs(lng), char)
    if func:
        return lambda a, b, c: (format % ('-' if a < 0 else '', func(abs(a)))).replace(' ', '0')
    else:
        return lambda a, b, c: (format % ('-' if a < 0 else '', abs(a))).replace(' ', '0')

def format_func2(lng, dec, base):
    char, pfx, func = format_char.get(base)
    format = '%%s%s%%0%d%s.%%-0%ds' % (pfx, abs(lng), char, abs(dec))
    if func:
        return lambda a, b, c: (format % ('-' if a < 0 else '', func(abs(a)), fbconv(b, base))).replace(' ', '0')
    else:
        return lambda a, b, c: (format % ('-' if a < 0 else '', abs(a), fbconv(b, base))).replace(' ', '0')

def format_func3(lng, dec, base):
    char, pfx, func = format_char.get(base)
    format = '%%s%s%%0%d%s.%%-0%dse%%%s' % (pfx, abs(lng), char, abs(dec), char)
    if func:
        return lambda a, b, c: (format % ('-' if a < 0 else '', func(abs(a)), fbconv(b, base), func(c))).replace(' ', '0')
    else:
        return lambda a, b, c: (format % ('-' if a < 0 else '', abs(a), fbconv(b, base), c)).replace(' ', '0')

# Splitters

def splitn1(x, lng, dec, base):
    return x, 0, 0

def splitraw(x, lng, dec, base):
    return raw(x), 0, 0

def splitn3(x, lng, dec, base):
    num, exp = bfrexp(x, base, lng)
    frac, intg = math.modf(num)
    return intg, abs(frac), exp

def splitn2(x, lng, dec, base):
    frac, intg = math.modf(x)
    return intg, abs(frac), 0

def fround(x, dec, base):
    p = base ** dec
    return round(x * p) / p

mode_func = [
        [(splitn1, format_func1), (splitn2, format_func2)],
        [(splitraw, format_func1), (splitraw, format_func1)],
        [(splitn3, format_func3), (splitn3, format_func3)],
        ]

def rounded(dec):
    def decorator(func):
        if dec < 0:
            return func

        if func is splitn1 or func is splitraw:
            return func

        def wrapper(x, lng, dec, base):
            a, b, c = func(x, lng, dec, base)
            if b: b = fround(b, dec, base)
            return a, b, c
        return wrapper
    return decorator

def format_func(mode, lng, dec, base):
    _int, _float  = mode_func[mode]

    split_int = rounded(dec)(_int[0])
    format_int = _int[1](lng, dec, base)
    int_func = lambda x: format_int(*split_int(x, lng, dec, base))

    split_float = rounded(dec)(_float[0])
    format_float = _float[1](lng, dec, base)
    float_func = lambda x: format_float(*split_float(x, lng, dec, base))

    complex_func = lambda x: '%s%s%sj' % (float_func(x.real), '' if x.imag < 0 else '+', float_func(x.imag))

    formatters = {
            int: int_func,
            long: int_func,
            float: float_func,
            complex: complex_func,
            }
    return lambda x: formatters.get(type(x))(x)

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

        self._mode = 0
        self._length = -1
        self._decimals = -1
        self._base = 10
        self._autobase = False
        self._formatter = format_func(0, -1, -1, 10)

    def mode(self):
        return self._mode

    def set_mode(self, mode):
        self._mode = int(mode)
        self._generate_formatter()

    mode = property(mode, set_mode)

    def precision(self):
        return (self._length, self._decimals)

    def set_precision(self, prec):
        self._length = int(prec[0])
        self._decimals = int(prec[1])
        self._generate_formatter()

    precision = property(precision, set_precision)

    def base(self):
        return -1 if self._autobase else self._base

    def realbase(self):
        return self._base

    def set_base(self, base):
        base = int(base)
        self._autobase = base < 0
        if not self._autobase:
            self._base = base
        self._generate_formatter()

    base = property(base, set_base)

    def _generate_formatter(self):
        self._formatter = format_func(self._mode, self._length, self._decimals, self._base)

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

            if self._autobase:
                self._base = base
                self._generate_formatter()

            if base == 10:
                b = base ** int(exponent or '0', base)
                if fraction:
                    n = (sign or '') + (integer or '0') + '.' + (fraction or '0')
                    return float(n) * b
                else:
                    return int((sign or '') + (integer or '0')) * b

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
        return self._formatter(x)

