# coding: utf-8

import __builtin__ as __builtins__
import sys

def bfrac(x, p=5, b=2):
    '''
    >>> bfrac(0.25)
    '.01'
    >>> bfrac(0.5)
    '.1'
    >>> bfrac(0.625)
    '.101'
    >>> bfrac(0.75)
    '.11'
    >>> bfrac(0.125)
    '.001'
    >>> bfrac(0.0625, b=16)
    '.1'
    '''
    x -= int(x)
    r = ''
    while x > 0 and len(r) < p:
        x *= b
        i = int(x)
        r += chr(55 + i) if i > 9 else str(i)
        x -= i
    return '.' + r if r else ''

def with_floating_version(base):
    def decorator(func):
        def wrapper(x, p=5):
            return func(int(x)) + bfrac(x, p, base)
        wrapper.__doc__ = func.__doc__
        wrapper.__name__ = func.__name__ + 'f'
        setattr(sys.modules[__name__], wrapper.__name__, wrapper)
        return func
    return decorator

@with_floating_version(2)
def bin(x):
    '''
    >>> bin(123)
    '0b1111011'
    '''
    r = ''
    a = abs(x)
    while a:
        r = str(a & 1) + r
        a = a >> 1
    r = '0b' + (r or '0')
    if x < 0:
        r = '-' + r
    return r

@with_floating_version(8)
def oct(x):
    '''
    >>> oct(123)
    '0o173'
    '''
    r = '0o' + __builtins__.oct(x).lstrip('-0')
    if x < 0:
        r = '-' + r
    return r

@with_floating_version(16)
def hex(x):
    '''
    >>> hex(123)
    '0x7B'
    '''
    r = __builtins__.hex(x).upper().replace('0X', '0x')
    return r

def dec(s):
    '''
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
    x = s.lstrip('-')
    if not x:
        return 0

    base = ({'0x': 16, '0o': 8, '0b': 2}).get(x[0:2], 10)

    if base == 10:
        return (float if '.' in s else int)(s)
    else:
        i, _, f = x.lstrip('0bxo').partition('.')
        r = int(i or '0', base)
        if f:
            r += sum(float(int(n, base)) / base ** (m + 1) for m, n in enumerate(f))

    return -r if s.startswith('-') else r

