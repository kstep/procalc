# coding: utf-8
from __future__ import division

import math
import struct
import __builtin__ as core

def strdig(d):
    return str(d) if d < 10 else chr(d + 55)

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

def basef(frac, base, prec=10):
    result = ''
    while frac and len(result) < prec:
        frac, d = math.modf(frac * base)
        result += strdig(int(d))

    if result:
        result = '.' + result
    return result

def bin(x):
    r = ''
    f, i = math.modf(abs(x))
    i = int(i)
    while i:
        r += str(i & 1)
        i >>= 1
    r = '0b' + (r or '0')
    if i < 0:
        r = '-' + r
    return r + basef(f, 2)

def oct(x):
    f, i = math.modf(abs(x))
    r = '0o' + core.oct(int(i)).lstrip('0')
    if r == '0o':
        r += '0'
    if x < 0:
        r = '-' + r
    return r + basef(f, 8)

def hex(x):
    f, i = math.modf(x)
    return core.hex(int(i)).upper().replace('0X', '0x') + basef(abs(f), 16)

def dec(s):
    '''
    Convert from string number representation of some base to decimal floating point.
    >>> dec("0xAA"), dec("0o100"), dec("0b101")
    (170, 64, 5)
    >>> dec("0b123")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 2: '123'
    >>> dec("0o108")
    Traceback (most recent call last):
        ...
    ValueError: invalid literal for int() with base 8: '108'
    >>> dec(hex(123)), dec(oct(123)), dec(bin(123))
    (123, 123, 123)
    >>> dec('0b1.01')
    1.25
    '''
    if isinstance(s, (long, int, float)):
        return s

    x = s.lstrip('-')
    if not x:
        return 0

    base = ({'0x': 16, '0o': 8, '0b': 2}).get(x[0:2], 10)
    bitn = bits(base - 1)

    if base == 10:
        for c in 'ABCDEF':
            if c in s:
                base = 16
                break

    if base == 10:
        return (float if '.' in s or 'e' in s else int)(s)
    else:
        x = x.lstrip('0bxo')
        i, _, e = x.partition('e')
        i, _, f = i.partition('.')
        r = int(i or '0', base)
        if f:
            r += sum(int(n, base) / (base << bitn * m) for m, n in enumerate(f))
        if e:
            r = float(r * base ** int(e))

    return -r if s.startswith('-') else r

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

def raw(x):
    if isinstance(x, float):
        f, t = 'd', 'Q'
    else:
        x = int(x)
        if x > 0:
            return x
        f, t = 'q', 'Q'
    return struct.unpack(t, struct.pack(f, x))[0]

