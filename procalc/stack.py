function = type(lambda: 1)

class StackError(Exception):
    pass

class OpStack(object):
    def __init__(self, guard=None, *ops):
        self._ops = dict(((o.op_name, o) for o in ops))
        self._guard = guard or (lambda x: x)
        self._stack = list()

    def as_str(self, filter_=str):
        return '\n'.join(getattr(i, 'op_name', None) or filter_(i) for i in self._stack)

    def add_op(self, op):
        self._ops[op.op_name] = op

    def add_ops(self, *ops):
        for op in ops:
            self._ops[op.op_name] = op

    def get_op(self, opname):
        try:
            return self._ops[opname]
        except KeyError:
            raise StackError('Unknown operation %s' % opname)

    def has_op(self, opname):
        return opname in self._ops

    def norm(self, value):
        if value is None or value == '':
            raise StackError('No empty values allowed on the stack')
        return self._ops.get(value, None) or self._guard(value)

    def pop(self, index=0):
        """
        Pop value from stack (like get()+drop())
        """
        try:
            text = self._stack.pop(index)
        except IndexError:
            raise StackError('Stack is empty')
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

    def _get_push_operand_index(self):
        idx, pri = 0, 0
        for i, item in self:
            opri = getattr(item, 'op_prio', 100)
            if opri > pri:
                pri = opri
            else:
                return i - 1 if pri == 100 else i
            idx = i
        return idx

    def _get_push_operator_index(self, op):
        idx, pri = 0, op.op_prio
        for i, item in self:
            if getattr(item, 'op_prio', 100) >= pri:
                return i
            idx = i
        return idx

    def push_op(self, opname):
        op = self._ops.get(opname, None)

        if op is None:
            idx = self._get_push_operand_index()

        else:
            idx = self._get_push_operator_index(op)

        self.push(opname, idx)

    def pop_op(self):
        data = self.pop()
        if isinstance(data, function):
            data(self)
            data = self.pop()
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
        >>> 
        '''
        return enumerate(self._stack)

