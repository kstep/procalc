# coding: utf-8

import gtk
import hildon

from procalc import operations
from procalc.operations import OperationError
from procalc.stack import OpStack, StackError
from procalc.helpers import button, switch, picker, selector, liststore, transpose_table
from procalc.converters import bin, oct, dec, hex

class ProCalcApp(hildon.Program):

    def init_window(self):
        self.window = hildon.Window()
        self.window.set_title("ProCalc")
        self.window.connect("delete_event", self.quit)
        self.window.connect("key-press-event", self.hit_keyboard)
        self.add_window(self.window)

    def init_controls(self):
        keypad = self.create_keypad()
        stack = hildon.TextView()
        input = hildon.Entry(gtk.HILDON_SIZE_AUTO)

        input.set_placeholder('Empty value')
        input.set_properties(
                hildon_input_mode=gtk.HILDON_GTK_INPUT_MODE_ALPHA
                | gtk.HILDON_GTK_INPUT_MODE_NUMERIC
                | gtk.HILDON_GTK_INPUT_MODE_SPECIAL)
        stack.set_placeholder('Stack is empty')
        stack.set_properties(editable=False)

        self.w_stack = stack
        self.w_buffer = stack.get_buffer()
        self.w_input = input
        self.w_keypad = keypad

    def init_layout(self):
        panner = hildon.PannableArea()
        panner.add_with_viewport(self.w_stack)
        panner.set_properties(
                mov_mode=hildon.MOVEMENT_MODE_VERT,
                size_request_policy=hildon.SIZE_REQUEST_MINIMUM,
                width_request=200,
                height_request=110)

        land_box = gtk.HBox()
        land_box.set_spacing(4)
        land_box.pack_start(panner)
        land_box.pack_end(self.w_keypad[1])
        land_box.pack_end(self.w_keypad[0])

        port_box = gtk.VBox()
        port_box.set_spacing(4)
        port_box.set_properties(no_show_all=True)

        vbox = gtk.VBox()
        vbox.pack_start(self.w_input)
        vbox.pack_start(land_box)
        vbox.pack_start(port_box)

        self.w_panner = panner
        self.w_portrait_box = port_box
        self.w_landscape_box = land_box

        self.window.add(vbox)

    def init_menu(self):
        menu_bar = self.create_menu()
        self.window.set_app_menu(menu_bar)

    def init_stack(self):
        ops = (getattr(operations, o) for o in operations.__all__)
        self.stack = OpStack(dec, *ops)

    def init_state(self):
        self.opmode = False
        self.filter = str
        self._ninput = None
        self._sinput = ''

    def __init__(self):
        super(ProCalcApp, self).__init__()

        # 0. set state attributes
        self.init_state()

        # 1. init stack
        self.init_stack()

        # 2. create window
        self.init_window()

        # 3. init main controls
        self.init_controls()

        # 4. place controls into layout
        self.init_layout()

        # 5. init main menu
        self.init_menu()

    def quit(self, *args):
        gtk.main_quit()

    def create_menu(self):
        menu = hildon.AppMenu()
        switch(menu, 2, self.hit_switch_base, 'Bin', 'Oct', 'Dec', 'Hex')

        # TODO
        # Integer - bit-wise operations on floats are as on ints,
        # tend to work in integers, except one of operands is float,
        # division always converts to float,
        # Float - bit-wise operations on floats are as on bit arrays,
        # all numbers tend to be converted to floats,
        # Raw - like float, but show inner binary representation
        # of floats in non-decimal modes, doesn't make sense for
        # integers as integers are always in "raw" format.
        menu.append(picker('Format', None, 'Integer', 'Float', 'Raw'))

        # TODO
        # First number is minimal integer part length to pad to with
        # zeroes (-1 means no leading zero for numbers less than 1),
        # second number is number of digits left after decimal
        # point (0 means always work with integers, -1 - no rounding
        # is applied).
        nums = liststore(*range(-1, 11))
        menu.append(picker('Precision', None, selector(nums, nums)))

        menu.append(button('Portrait', self.hit_switch_portrait, 'toggle'))
        menu.append(button('About', self.show_about_info))
        menu.show_all()
        return menu

    def show_about_info(self, b):
        self.note("""
Programmer's calculator, v0.1

RPN calculator with bit-wise operations
and infix operators emulation.

Distributed AS IS under GPLv3 or greater
without any warranty.

Author: Konstantin Stepanov, © 2010
                """)

    def hit_switch_portrait(self, b):
        flags = 0
        if b.get_active():
            flags = hildon.PORTRAIT_MODE_SUPPORT | \
                    hildon.PORTRAIT_MODE_REQUEST
            new_parent = self.w_portrait_box
            old_parent = self.w_landscape_box
        else:
            old_parent = self.w_portrait_box
            new_parent = self.w_landscape_box

        hildon.hildon_gtk_window_set_portrait_flags(self.window, flags)

        self.w_panner.reparent(new_parent)
        self.w_keypad[0].reparent(new_parent)
        self.w_keypad[1].reparent(new_parent)
        transpose_table(self.w_keypad[1])

        old_parent.hide()
        new_parent.show()

    def hit_execute(self, b):
        self.stack_push_op()
        self.stack_pop_op()

    def hit_opkey(self, b):
        op = b.get_label()
        if self.is_func:
            op = ({
                '÷': 'μ',
                '↑': 'σ',
                '×': 'Π',
                '+': 'Σ',
                }).get(op, op)
        self.stack_push_op()
        self.input = op
        self.opmode = True

    def hit_digit(self, b):
        if self.opmode:
            self.opmode = False
            self.stack_push_op()

        if self.is_mode:
            bases = {'2': '0b', '8': '0o', '0': '', 'A': '0x'}
            base = bases.get(b.get_label(), None)
            if base is not None:
                text = self.input
                minus = text.startswith('-')
                text = base + text.lstrip('-0bx')
                if minus:
                    text = '-' + text
                self.input = text
                self.is_mode = False
            else:
                self.message('Press 2, 8, 0 or A to select base', 2000)
        else:
            self.add_input(b.get_label())

    def hit_switch_sign(self, b):
        if self.opmode:
            return
        text = self.input
        if text.startswith('-'):
            self.input = text.lstrip('-')
        else:
            self.input = '-' + text

    def hit_backspace(self, b):
        self.input = self.input[:-1]

    def hit_clear(self, b):
        self.ninput = None
        if self.is_func:
            self.stack.clear()
            self.w_buffer.set_text('')
            self.is_func = False

    def hit_push_stack(self, b):
        self.stack_push()

    def hit_pop_stack(self, b):
        self.stack_pop()

    def hit_switch_base(self, b):
        base_name = b.get_label()
        self.filter = dict(Bin=bin, Oct=oct, Dec=str, Hex=hex).get(base_name, str)
        if not self.opmode:
            try:
                self.ninput = self.ninput
                self.w_buffer.set_text(self.stack.as_str(self.filter))
            except ValueError, e:
                self.message(e.message.capitalize(), 2000)

    def hit_mode(self, b):
        pass

    def hit_keyboard(self, w, ev):
        def mod_key(attr):
            def w():
                setattr(self, attr, not getattr(self, attr))
            return w

        def ins_key(ch):
            def w():
                if self.opmode:
                    self.stack_push_op()
                    self.opmode = False
                self.ins_input(ch)
            return w

        def op_key(ch):
            def w():
                self.stack_push_op()
                self.opmode = True
                self.add_input(ch)
            return w

        def act_key(meth):
            def w():
                getattr(self, meth)(None)
            return w

        char = unichr(ev.keyval)
        keymap = {
                u'q': ins_key(u'1'),
                u'w': ins_key(u'2'),
                u'e': ins_key(u'3'),
                u'r': ins_key(u'4'),
                u't': ins_key(u'5'),
                u'y': ins_key(u'6'),
                u'u': ins_key(u'7'),
                u'i': ins_key(u'8'),
                u'o': ins_key(u'9'),
                u'p': ins_key(u'0'),
                u'g': act_key('hit_switch_sign'),
                u'_': act_key('hit_switch_sign'),

                u'+': op_key(u'+'),
                u's': op_key(u'+'),
                u'-': op_key(u'−'),
                u'f': op_key(u'−'),
                u'*': op_key(u'×'),
                u'a': op_key(u'×'),
                u'/': op_key(u'÷'),
                u'v': op_key(u'÷'),
                u'\\': op_key(u'↑'),
                u'b': op_key(u'↑'),
                u'&': op_key(u'&'), # and
                u'k': op_key(u'&'), # and
                u'|': op_key(u'|'), # or
                u'z': op_key(u'|'), # or
                u'#': op_key(u'^'), # xor
                u'd': op_key(u'^'), # xor
                u'!': op_key(u'~'), # not
                u'l': op_key(u'~'), # not
                u'$': op_key(u'&~'), # and not
                u'x': op_key(u'&~'), # and not
                u'm': mod_key('is_mode'),
                u'￣': mod_key('is_func'),
                u'h': act_key('hit_push_stack'),
                u'j': act_key('hit_pop_stack'),
                u'(': act_key('hit_push_stack'),
                u')': act_key('hit_pop_stack'),
                u' ': act_key('hit_push_stack'),
                u'=': act_key('hit_execute'),
                u',': act_key('hit_execute'),
                u'\uff8d': act_key('hit_execute'),
                u'c': act_key('hit_clear'),
                }
        #print char
        try:
            action = keymap[char]
        except KeyError:
            return False

        action()
        return True

    def is_mode(self):
        return self.w_mode.get_active()

    def set_mode(self, value):
        return self.w_mode.set_active(value)

    is_mode = property(is_mode, set_mode)

    def is_func(self):
        return self.w_func.get_active()

    def set_func(self, value):
        return self.w_func.set_active(value)

    is_func = property(is_func, set_func)

    def input(self):
        return self.w_input.get_text()

    def set_input(self, value):
        self.w_input.set_text(str(value))
        self.w_input.set_position(-1)

    input = property(input, set_input)

    def stack_denorm(self, value):
        '''
        Turn normalized value from stack into string representation
        according to format settings.
        '''
        if value is None:
            return ''
        return getattr(value, 'op_name', None) or self.filter(value)

    def ninput(self):
        '''
        Get normalized value from user input.
        If user changes input value, update normalized value as well.
        '''
        if self._sinput != self.input:
            self._sinput = self.input
            self._ninput = self.stack.norm(self._sinput)
        return self._ninput

    def set_ninput(self, value):
        '''
        Set normalized value. This action updates user entry as well.
        '''
        self._sinput = self.input = self.stack_denorm(value)
        self._ninput = value

    ninput = property(ninput, set_ninput)

    def add_input(self, value):
        self.w_input.insert_text(value, -1)
        self.w_input.set_position(-1)

    def ins_input(self, value, pos=None):
        if pos is None:
            pos = self.w_input.get_position()
        self.w_input.insert_text(value, pos)
        self.w_input.set_position(pos + len(value))

    def stack_push(self):
        try:
            self.stack.push(self.input)
            self.w_buffer.set_text(self.stack.as_str(self.filter))
            if not self.is_func:
                self.ninput = None

        except StackError, e:
            self.message(e.message, 2000)

    def stack_pop(self):
        try:
            data = self.stack.pop()
            self.w_buffer.set_text(self.stack.as_str(self.filter))

            input = self.input
            if self.is_func and input:
                self.stack.push(input)

            self.ninput = data

        except StackError, e:
            self.message(e.message, 2000)

    def stack_push_op(self):
        try:
            self.stack.push_op(self.input)
            self.w_buffer.set_text(self.stack.as_str(self.filter))
            self.ninput = None

        except OperationError, e:
            self.message(e.message, 2000)

        except StackError:
            pass

    def stack_pop_op(self):
        try:
            self.ninput = self.stack.pop_op()
            self.w_buffer.set_text(self.stack.as_str(self.filter))

        except (StackError, OperationError), e:
            self.message(e.message, 2000)

    def message(self, text, timeout=500):
        banner = hildon.hildon_banner_show_information(self.window, '', text)
        banner.set_timeout(timeout)
        return banner

    def note(self, text):
        banner = hildon.hildon_note_new_information(self.window, text)
        banner.connect('response', lambda s, ev: s.destroy())
        banner.show()
        return banner

    def create_keypad(self):
        def create_table(rows, cols, rowsp, colsp):
            box = gtk.Table(rows, cols, homogeneous=True)
            box.set_row_spacings(rowsp)
            box.set_col_spacings(colsp)
            box.set_properties(width_request=cols * 75)
            return box

        buttons_box1 = create_table(5, 5, 4, 4)
        buttons_box2 = create_table(5, 3, 4, 4)

        # Decimal digits
        for i in range(0, 9):
            x, y = i % 3, 3 - (i / 3)
            b = button(i + 1, self.hit_digit)
            buttons_box1.attach(b, x, x + 1, y, y + 1)
        b = button(0, self.hit_digit)
        buttons_box1.attach(b, 0, 1, 4, 5)

        # Hex digits
        for i in range(0, 6):
            x, y = i % 2, 3 - (i / 2)
            b = button(chr(i + 65), self.hit_digit)
            buttons_box1.attach(b, x + 3, x + 4, y, y + 1)

        # Other digital inputs
        b = button('.', self.hit_digit)
        buttons_box1.attach(b, 1, 2, 4, 5)
        b = button('±', self.hit_switch_sign)
        buttons_box1.attach(b, 2, 3, 4, 5)

        # Basic operations
        for i, c in enumerate(u'↑÷×−+'):
            b = button(str(c), self.hit_opkey)
            buttons_box2.attach(b, 0, 1, i, i + 1)

        # Stack operations
        hooks = [self.hit_push_stack, self.hit_pop_stack]
        for i, c in enumerate((u'st↓', u'st↑')):
            b = button(c, hooks[i])
            buttons_box1.attach(b, i + 3, i + 4, 4, 5)

        # Binary operations
        for i, c in enumerate(('^', '&~', '&', '~', '|')):
            b = button(c, self.hit_opkey)
            buttons_box2.attach(b, 1, 2, i, i + 1)

        for i, c in enumerate(('<<', '>>')):
            b = button(c, self.hit_opkey)
            buttons_box2.attach(b, 2, 3, i, i + 1)

        # Execute
        b = button('=', self.hit_execute)
        buttons_box2.attach(b, 2, 3, 3, 5)

        # Special mode keys
        b = button('Mod', self.hit_mode, 'toggle')
        self.w_mode = b
        buttons_box1.attach(b, 3, 4, 0, 1)

        b = button('Fn', None, 'toggle')
        self.w_func = b
        buttons_box1.attach(b, 4, 5, 0, 1)

        b = button('×Bⁿ')
        buttons_box2.attach(b, 2, 3, 2, 3)

        # Edit keys
        b = button('C', self.hit_clear)
        buttons_box1.attach(b, 0, 1, 0, 1)
        b = button(u'←', self.hit_backspace)
        buttons_box1.attach(b, 1, 3, 0, 1)

        return buttons_box1, buttons_box2

    def run(self):
        self.window.show_all()
        gtk.main()
