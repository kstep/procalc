# coding: utf-8

__all__ = ['op_noop', 'op_add', 'op_sub', 'op_mul', 'op_div', 'op_mod', 'op_pow']

def operation(name, prio, *types):
    def decorator(func):
        def wrapper(stack):
            args = (t(stack.pop_op()) for t in types)
            result = func(*args)
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

@operation('+', 1, int, int)
def op_add(a, b):
    return a + b

@operation('−', 1, int, int)
def op_sub(a, b):
    return a - b

@operation('×', 2, int, int)
def op_mul(a, b):
    return a * b

@operation('÷', 2, int, int)
def op_div(a, b):
    return a / b

@operation('%', 2, int, int)
def op_mod(a, b):
    return a % b

@operation('↑', 3, int, int)
def op_pow(a, b):
    return a ** b

