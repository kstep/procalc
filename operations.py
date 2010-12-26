

__all__ = ['op_noop', 'op_add', 'op_sub', 'op_mul', 'op_div', 'op_mod', 'op_pow']

def operation(name, prio, argnum):
    def decorator(func):
        def wrapper(stack):
            args = [stack.pop_op() for a in range(0, argnum)]
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

@operation('', 0, 0)
def op_noop():
    pass

@operation('+', 1, 2)
def op_add(a, b):
    return a + b

@operation('-', 1, 2)
def op_sub(a, b):
    return a - b

@operation('*', 2, 2)
def op_mul(a, b):
    return a * b

@operation('/', 2, 2)
def op_div(a, b):
    return a / b

@operation('%', 2, 2)
def op_mod(a, b):
    return a % b

@operation('', 3, 2)
def op_pow(a, b):
    return a ** b

