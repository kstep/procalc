# coding: utf-8

import __builtin__ as __builtins__

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

def oct(x):
    '''
    >>> oct(123)
    '0o173'
    '''
    r = '0o' + __builtins__.oct(x).lstrip('-0')
    if x < 0:
        r = '-' + r
    return r

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
    '''
    x = s.lstrip('-')
    if not x:
        return 0

    if x.startswith('0x'):
        base = 16
    elif x.startswith('0b'):
        base = 2
    elif x.startswith('0o'):
        base = 8
    else:
        base = 10

    if base == 10:
        r = (float if '.' in x else int)(x)
    else:
        r = int(x.lstrip('0bxo') or '0', base)

    return -r if s.startswith('-') else r

