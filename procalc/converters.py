# coding: utf-8

def bin(x):
    r = ''
    a = abs(x)
    while a:
        r = str(a & 1) + r
        a = a >> 1
    r = '0b' + (r or '0')
    if x < 0:
        r = '-' + r
    return r

def dec(s):
    x = s.lstrip('-')
    if not x:
        return 0

    if x.startswith('0'):
        if x.startswith('0x'):
            base = 16
        elif x.startswith('0b'):
            base = 2
        else:
            base = 8
        r = int(x.lstrip('0bx') or '0', base)
    else:
        r = (float if '.' in x else int)(x)

    return -r if s.startswith('-') else r

