
from procalc.operations import op_oper

class StackError(Exception):
    pass

class OpStack(object):
    def __init__(self, buffer_, *ops):
        if not buffer_:
            from gtk import TextBuffer
            buffer_ = TextBuffer()

        self._buffer = buffer_
        self._ops = dict(((o.op_name, o) for o in ops))

    def get_line_iters(self, index):
        start = self._buffer.get_iter_at_line(index)
        end = self._buffer.get_iter_at_line(index + 1)
        return start, end

    @property
    def buffer(self):
        return self._buffer

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
        start, end = self.get_line_iters(index)
        text = self._buffer.get_text(start, end)
        if not text:
            raise StackError('Stack is empty')
        self._buffer.delete(start, end)
        return text.strip()

    def push(self, data, index=0):
        """
        Push value into stack
        """
        data = str(data)
        if not data:
            raise StackError('No empty values allowed on the stack')
        iter = self._buffer.get_iter_at_line(index)
        self._buffer.insert(iter, data + '\n')

    def get(self, index=0):
        """
        Get value from stack w/o modification
        """
        text = self._buffer.get_text(*self.get_line_iters(index))
        return text.strip()

    def put(self, data, index=0):
        """
        Put value into stack, stack doesn't grow
        """
        data = str(data)
        if not data:
            raise StackError('No empty values allowed on the stack')
        start, end = self.get_line_iters(index)
        self._buffer.delete(start, end)
        self._buffer.insert(start, data + '\n')

    def drop(self, index):
        """
        Drop value from stack
        >>> import gtk
        >>> buf = gtk.TextBuffer()
        >>> it = buf.get_start_iter()
        >>> buf.insert(it, "random line 1\\nrandom line 2\\n")
        >>> stack = OpStack(buf)
        >>> stack.drop(0)
        >>> buf.get_text(buf.get_iter_at_line(0), buf.get_iter_at_line(1))
        'random line 2\\n'
        """
        self._buffer.delete(*self.get_line_iters(index))

    def clear(self):
        """
        Clear stack
        """
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
        >>> import gtk
        >>> buf = gtk.TextBuffer()
        >>> it = buf.get_start_iter()
        >>> for i in range(0, 4):
        ...   buf.insert(it, str(i) + '\\n')
        >>> stack = OpStack(buf)
        >>> for line, item in stack:
        ...   print (line, item)
        ... 
        (0, '0')
        (1, '1')
        (2, '2')
        (3, '3')
        >>> 
        '''
        start = self._buffer.get_start_iter()
        end = self._buffer.get_start_iter()
        while end.forward_to_line_end():
            item = self._buffer.get_text(start, end).strip()
            if not item:
                break
            yield start.get_line(), item
            start.forward_line()

