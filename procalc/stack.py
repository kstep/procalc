
from procalc.operations import op_noop, op_oper

class StackError(Exception):
    pass

class OpStack(object):
    def __init__(self, buffer, *ops):
        self.buffer = buffer
        self.ops = dict(((o.op_name, o) for o in ops))

    def pop(self, index=0):
        """
        Pop value from stack (like get()+drop())
        """
        start = self.buffer.get_iter_at_line(index)
        end = self.buffer.get_iter_at_line(index + 1)
        text = self.buffer.get_text(start, end)
        if not text:
            raise StackError('Stack is empty')
        self.buffer.delete(start, end)
        return text.strip()

    def push(self, data, index=0):
        """
        Push value into stack
        """
        data = str(data)
        if not data:
            raise StackError('No empty values allowed on the stack')
        iter = self.buffer.get_iter_at_line(index)
        self.buffer.insert(iter, data + '\n')

    def get(self, index=0):
        """
        Get value from stack w/o modification
        """
        start = self.buffer.get_iter_at_line(index)
        end = self.buffer.get_iter_at_line(index + 1)
        text = self.buffer.get_text(start, end)
        return text.strip()

    def put(self, data, index=0):
        """
        Put value into stack, stack doesn't grow
        """
        data = str(data)
        if not data:
            raise StackError('No empty values allowed on the stack')
        start = self.buffer.get_iter_at_line(index)
        end = self.buffer.get_iter_at_line(index + 1)
        self.buffer.delete(start, end)
        self.buffer.insert(start, data + '\n')

    def drop(self, index):
        """
        Drop value from stack
        """
        start = self.buffer.get_iter_at_line(index)
        end = self.buffer.get_iter_at_line(index + 1)
        self.buffer.delete(start, end)

    def clear(self):
        """
        Clear stack
        """
        self.buffer.set_text('')

    __getitem__ = get

    def __setitem__(self, index, data):
        self.put(data, index)

    def push_op(self, op):
        fop = self.ops.get(op, op_noop)
        pri = fop.op_prio

        idx = 0
        while True:
            item = self.get(idx)
            if not item:
                break

            iop = self.ops.get(item, op_oper)
            if fop is op_noop:
                if iop.op_prio <= pri:
                    break
                pri = iop.op_prio

            elif iop.op_prio >= pri:
                break

            idx += 1

        if pri == op_oper.op_prio:
            idx -= 1

        self.push(op, idx)

    def pop_op(self):
        data = self.pop()
        op = self.ops.get(data, None)
        if op:
            op(self)
            data = self.pop()
        return data

