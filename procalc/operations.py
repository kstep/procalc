# coding: utf-8

__all__ = ['op_noop', 'op_oper', 'op_add', 'op_sub', 'op_mul', 'op_div', 'op_mod', 'op_pow', 'op_or', 'op_xor', 'op_and', 'op_andnot', 'op_not', 'op_shl', 'op_shr']

from procalc.util import dec

class OperationError(ValueError):
    pass

def operation(name, prio, *types):
    def decorator(func):
        def wrapper(stack):
            try:
                args = (t(stack.pop_op()) for t in types)
                result = func(*args)
            except ValueError, e:
                raise OperationError("Arguments type mismatch for %s(%s)" % (name, ", ".join(map(lambda t: t.__name__, types))))

            if result is None:
                pass
            elif isinstance(result, tuple):
                for r in result:
                    stack.push(r)
            else:
                stack.push(result)
        wrapper.op_name = name
        wrapper.op_prio = prio
        return wrapper
    return decorator

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

@operation('%', 2, dec, dec)
def op_mod(a, b):
    return a % b

@operation('↑', 3, dec, dec)
def op_pow(a, b):
    return a ** b

@operation('^', 2, dec, dec)
def op_xor(a, b):
    return a ^ b

@operation('|', 2, dec, dec)
def op_or(a, b):
    return a | b

@operation('&', 2, dec, dec)
def op_and(a, b):
    return a & b

@operation('~', 4, dec)
def op_not(a):
    return ~a

@operation('&~', 2, dec, dec)
def op_andnot(a, b):
    return a & ~b

@operation('>>', 2, dec, dec)
def op_shr(a, b):
    return a >> b

@operation('<<', 2, dec, dec)
def op_shl(a, b):
    return a << b

