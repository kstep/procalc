# coding: utf-8
from __future__ import division

import math
from procalc.converters import dec, fint

__all__ = [
            'op_noop', 'op_oper',  # service
            'op_add', 'op_sub', 'op_mul', 'op_div','op_mod', 'op_pow',  # standard
            'op_or', 'op_xor', 'op_and', 'op_andnot', 'op_not', 'op_shl', 'op_shr',  # bitwise
            'op_sum', 'op_prod', 'op_mean', 'op_stdev'  # statistics
            ]

class OperationError(ValueError):
    pass

def operation(name, prio, *types):
    def decorator(func):
        rtypes = tuple(reversed(types))
        def wrapper(stack):
            try:
                args = [t(stack.pop_op()) for t in rtypes]
                args.reverse()
            except ValueError:
                raise OperationError("Arguments type mismatch for %s(%s)" % (name, ", ".join(map(lambda t: t.__name__, types))))

            result = func(*args)
            if result is None:
                pass
            elif isinstance(result, tuple):
                for r in reversed(result):
                    stack.push(r)
            else:
                stack.push(result)
        wrapper.op_name = name
        wrapper.op_prio = prio
        return wrapper
    return decorator

def operation_for_all(name, prio, type_):
    def decorator(func):
        def wrapper(stack):
            try:
                args = [type_(item) for item in stack]
                args.reverse()
            except ValueError:
                raise OperationError("Argument type mismatch for %s(%s, ...)" % (name, type_.__name__))

            result = func(*args)
            if result is None:
                pass
            elif isinstance(result, tuple):
                for r in reversed(result):
                    stack.push(r)
            else:
                stack.push(result)
        wrapper.op_name = name
        wrapper.op_prio = prio
        return wrapper
    return decorator

@operation_for_all('Σ', -2, dec)
def op_sum(*args):
    return sum(args)

@operation_for_all('Π', -1, dec)
def op_prod(*args):
    return reduce(lambda x, y: x * y, args, 1)

@operation_for_all('μ', -3, dec)
def op_mean(*args):
    return sum(args) / len(args)

@operation_for_all('σ', -3, dec)
def op_stdev(*args):
    mean = sum(args) / len(args)
    disp = sum((x - mean) ** 2 for x in args) / len(args)
    return math.sqrt(disp)

@operation('', 0)
def op_noop():
    pass

@operation('', 100)
def op_oper():
    pass

@operation('+', 1, dec, dec)
def op_add(a, b):
    return a + b

@operation('−', 1, dec, dec)
def op_sub(a, b):
    return a - b

@operation('×', 2, dec, dec)
def op_mul(a, b):
    return a * b

@operation('÷', 2, dec, dec)
def op_div(a, b):
    return a / b

@operation('%', 2, int, int)
def op_mod(a, b):
    return a % b

@operation('↑', 3, dec, dec)
def op_pow(a, b):
    return a ** b

@operation('^', 2, fint, fint)
def op_xor(a, b):
    return a ^ b

@operation('|', 2, fint, fint)
def op_or(a, b):
    return a | b

@operation('&', 2, fint, fint)
def op_and(a, b):
    return a & b

@operation('~', 4, fint)
def op_not(a):
    return ~a

@operation('&~', 2, fint, fint)
def op_andnot(a, b):
    return a & ~b

@operation('>>', 2, fint, fint)
def op_shr(a, b):
    return a >> b if b >= 0 else a << -b

@operation('<<', 2, fint, fint)
def op_shl(a, b):
    return a << b if b >= 0 else a >> -b

