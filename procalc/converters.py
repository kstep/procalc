# coding: utf-8

import struct

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

def basef(x, base=2):
    '''
    Convert from decimal floating point number to string representation of some base.
    base := 2 | 8 | 16

    >>> basef(10)
    '0b1010'
    >>> basef(0.25)
    '0b0.01'
    >>> basef(10.5)
    '0b1010.1'
    >>> basef(10.0625, 16)
    '0xA.1'
    >>> basef(8.125, 8)
    '0o10.1'
    '''
    prefix = ({2: '0b', 8: '0o', 16: '0x'}).get(base)
    bitn = bits(base - 1)

    def tobin(x):
        s = ''
        while x:
            s = str(x & 1) + s
            x >>= 1
        return s

    v = "".join(tobin(ord(i)).rjust(8, '0') for i in reversed(struct.pack('d', x)))
    sign, exp, mant = int(v[0]), int(v[1:12], 2) - 1023 + 1, '1' + v[12:] 

    sign, intg, frac = '-' if sign else '', '', ''
    if exp < 0:
        frac = ('0' * -exp) + mant
        intg = '0'

    elif exp > 0:
        intg = mant[0:exp]
        frac = mant[exp:]

    if base > 2:
        i, f = '', ''
        while intg:
            d, intg = int(intg[-bitn:], 2), intg[:-bitn]
            d = str(d) if d < 10 else chr(d + 55)
            i = d + i
        while frac:
            d, frac = int(frac[:bitn], 2), frac[bitn:]
            d = str(d) if d < 10 else chr(d + 55)
            f = f + d

    else:
        i, f = intg, frac

    if f:
        f = '.' + f

    return sign + prefix + i + f.rstrip('.0')

hex = lambda x: basef(x, 16)
oct = lambda x: basef(x, 8)
bin = lambda x: basef(x, 2)

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
    x = s.lstrip('-')
    if not x:
        return 0

    base = ({'0x': 16, '0o': 8, '0b': 2}).get(x[0:2], 10)
    bitn = bits(base - 1)

    if base == 10:
        return float(s)
    else:
        i, _, f = x.lstrip('0bxo').partition('.')
        r = int(i or '0', base)
        if f:
            r += sum(float(int(n, base)) / (base << bitn * m) for m, n in enumerate(f))

    return -r if s.startswith('-') else r

