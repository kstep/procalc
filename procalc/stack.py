
from procalc.operations import op_oper

class StackError(Exception):
    pass

class OpStack(object):
    def __init__(self, buffer_, *ops):
        if not buffer_:
            from gtk import TextBuffer
            buffer_ = TextBuffer()

        self._buffer = buffer_
        buffer_.set_text('')
        self._ops = dict(((o.op_name, o) for o in ops))
        self._stack = list()

    def get_line_iters(self, index):
        start = self._buffer.get_iter_at_line(index)
        end = self._buffer.get_iter_at_line(index + 1)
        return start, end

    @property
    def buffer(self):
        return self._buffer

    def reflect(self):
        self._buffer.set_text('\n'.join(str(i) for i in self._stack))

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

    def pop(self, index=0):
        """
        Pop value from stack (like get()+drop())
        """
        try:
            text = self._stack.pop(index)
        except IndexError:
            raise StackError('Stack is empty')
        self.reflect()
        return text

    def push(self, data, index=0):
        """
        Push value into stack
        """
        if data is None or data == '':
            raise StackError('No empty values allowed on the stack')
        self._stack.insert(index, data)
        self.reflect()

    def get(self, index=0):
        """
        Get value from stack w/o modification
        """
        return self._stack[index]

    def put(self, data, index=0):
        """
        Put value into stack, stack doesn't grow
        """
        if data is None or data == '':
            raise StackError('No empty values allowed on the stack')
        self._stack[index] = data
        self.reflect()

    def drop(self, index):
        """
        Drop value from stack
        """
        self._stack.pop(index)
        self.reflect()

    def clear(self):
        """
        Clear stack
        """
        self._stack = list()
        self._buffer.set_text('')

    __getitem__ = get

    def __setitem__(self, index, data):
        self.put(data, index)

    def _get_push_operand_index(self):
        idx, pri = 0, 0
        for i, item in self:
            op = self._ops.get(item, op_oper)
            if op.op_prio > pri:
                pri = op.op_prio
            else:
                return i - 1 if pri == op_oper.op_prio else i
            idx = i
        return idx

    def _get_push_operator_index(self, op):
        idx, pri = 0, op.op_prio
        for i, item in self:
            if self._ops.get(item, op_oper).op_prio >= pri:
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
        op = self._ops.get(data, None)
        if op:
            op(self)
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
