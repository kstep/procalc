from procalc.i18n import _

function = type(lambda: 1)

class StackError(Exception):
    pass

class OpStack(object):
    def __init__(self, guard=None, *ops):
        self._ops = dict(((o.op_name, o) for o in ops))
        self._guard = guard or (lambda x: x)
        self._stack = list()
        self._opstack = list()

    def as_str(self, filter_=str):
        if self._opstack:
            opstack = '[' + ', '.join(o.op_name for o in self._opstack) + ']\n'
        else:
            opstack = ''

        return opstack + '\n'.join(getattr(i, 'op_name', None) or filter_(i) for i in self._stack)

    def add_op(self, op):
        self._ops[op.op_name] = op

    def add_ops(self, *ops):
        for op in ops:
            self._ops[op.op_name] = op

    def get_op(self, opname):
        try:
            return self._ops[opname]
        except KeyError:
            raise StackError(_(u'Unknown operation %s') % opname)

    def has_op(self, opname):
        return opname in self._ops

    def norm(self, value):
        if value is None or value == '':
            raise StackError(_(u'No empty values allowed on the stack'))
        return self._ops.get(value, None) or self._guard(value)

    def pop(self, index=0):
        """
        Pop value from stack (like get()+drop())
        """
        try:
            text = self._stack.pop(index)
        except IndexError:
            raise StackError(_(u'Stack is empty'))
        return text

    def push(self, data, index=0):
        """
        Push value into stack
        """
        self._stack.insert(index, self.norm(data))

    def get(self, index=0):
        """
        Get value from stack w/o modification
        """
        return self._stack[index]

    def put(self, data, index=0):
        """
        Put value into stack, stack doesn't grow
        """
        self._stack[index] = self.norm(data)

    def drop(self, index):
        """
        Drop value from stack
        """
        self._stack.pop(index)

    def clear(self):
        """
        Clear stack
        """
        self._stack = list()

    __getitem__ = get

    def __setitem__(self, index, data):
        self.put(data, index)

    def push_op(self, opname):
        op = self.norm(opname)

        if not isinstance(op, function):
            self._stack.insert(0, op)

        else:
            while self._opstack and cmp(op.op_prio, self._opstack[0].op_prio) in op.op_asso:
                self._stack.insert(0, self._opstack.pop(0))

            self._opstack.insert(0, op)

    def pop_op(self):
        while self._opstack:
            self._stack.insert(0, self._opstack.pop(0))

        data = self._stack.pop(0)
        while isinstance(data, function):
            data(self)
            data = self._stack.pop(0)

        return data

    def __iter__(self):
        '''
        >>> stack = OpStack()
        >>> for i in reversed(range(0, 4)):
        ...   stack.push(str(i))
        >>> for line, item in stack:
        ...   print (line, item)
        (0, '0')
        (1, '1')
        (2, '2')
        (3, '3')
        '''
        return enumerate(self._stack)

    def __len__(self):
        return len(self._stack)
