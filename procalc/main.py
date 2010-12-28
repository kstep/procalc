# coding: utf-8

import gtk
import hildon

from procalc import operations
from procalc.operations import OperationError
from procalc.stack import OpStack, StackError
from procalc.util import button, switch, bin, dec, transpose_table

class ProCalcApp(hildon.Program):

    def __init__(self):
        super(ProCalcApp, self).__init__()

        self.window = hildon.Window()
        self.window.set_title("ProCalc")
        self.window.connect("delete_event", self.quit)
        self.window.connect("key-press-event", self.hit_keyboard)
        self.add_window(self.window)

        keypad = self.create_keypad()
        stack = hildon.TextView()
        input = hildon.Entry(gtk.HILDON_SIZE_AUTO)

        input.set_placeholder('Empty value')
        input.set_properties(hildon_input_mode=gtk.HILDON_GTK_INPUT_MODE_ALPHA|gtk.HILDON_GTK_INPUT_MODE_NUMERIC|gtk.HILDON_GTK_INPUT_MODE_SPECIAL)
        stack.set_placeholder('Stack is empty')
        stack.set_properties(editable=False)

        panner = hildon.PannableArea()
        panner.add_with_viewport(stack)
        panner.set_properties(
                mov_mode=hildon.MOVEMENT_MODE_VERT,
                size_request_policy=hildon.SIZE_REQUEST_MINIMUM,
                width_request=200,
                height_request=110)

        land_box = gtk.HBox()
        land_box.set_spacing(4)
        land_box.pack_start(panner)
        land_box.pack_end(keypad[1])
        land_box.pack_end(keypad[0])

        port_box = gtk.VBox()
        port_box.set_spacing(4)
        port_box.set_properties(no_show_all=True)

        vbox = gtk.VBox()
        vbox.pack_start(input)
        vbox.pack_start(land_box)
        vbox.pack_start(port_box)

        self.w_panner = panner
        self.w_stack = stack
        self.w_input = input
        self.w_keypad = keypad
        self.w_portrait_box = port_box
        self.w_landscape_box = land_box

        self.stack = OpStack(stack.get_buffer(), *(getattr(operations, o) for o in operations.__all__))
        self.opmode = False
        self.show_filter = str

        menu_bar = self.create_menu()
        self.window.set_app_menu(menu_bar)
        self.window.add(vbox)

    def quit(self, *args):
        gtk.main_quit()

    def create_menu(self):
        menu = hildon.AppMenu()
        switch(menu, 2, self.hit_switch_base, 'Bin', 'Oct', 'Dec', 'Hex')
        b = button('Portrait', self.hit_switch_portrait, 'toggle')
        menu.append(b)
        menu.show_all()
        return menu

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
        self.input = self.show_filter(dec(self.input))

    def hit_opkey(self, b):
        op = b.get_label()
        self.stack_push_op()
        self.input = op
        self.opmode = True

    def hit_digit(self, b):
        if self.opmode:
            self.opmode = False
            self.stack_push_op()

        if self.is_mode:
            bases = {'2': '0b', '8': '0', '0': '', 'A': '0x'}
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
            self.input = '-'+text

    def hit_backspace(self, b):
        self.input = self.input[:-1]

    def hit_clear(self, b):
        self.input = ''
        if self.is_func:
            self.stack.clear()
            self.is_func = False

    def hit_push_stack(self, b):
        self.stack_push()

    def hit_pop_stack(self, b):
        self.stack_pop()

    def hit_switch_base(self, b):
        base_name = b.get_label()
        self.show_filter = dict(Bin=bin, Oct=oct, Dec=str, Hex=hex).get(base_name, str)
        if not self.opmode:
            text = self.input
            if text:
                self.input = self.show_filter(dec(text))

    def hit_mode(self, b):
        pass

    def hit_keyboard(self, w, ev):
        def switch_key(attr):
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
                u'g': lambda: self.hit_switch_sign(None),
                u'_': lambda: self.hit_switch_sign(None),

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
                u'm': switch_key('is_mode'),
                u'￣': switch_key('is_func'),
                u'h': lambda: self.hit_push_stack(None),
                u'j': lambda: self.hit_pop_stack(None),
                u'(': lambda: self.hit_push_stack(None),
                u')': lambda: self.hit_pop_stack(None),
                u' ': lambda: self.hit_push_stack(None),
                u'=': lambda: self.hit_execute(None),
                u',': lambda: self.hit_execute(None),
                u'\uff8d': lambda: self.hit_execute(None),
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
            self.input = ''
        except StackError, e:
            self.message(e.message, 2000)
    def stack_pop(self):
        try:
            self.input = self.stack.pop()
        except StackError, e:
            self.message(e.message, 2000)
    def stack_push_op(self):
        try:
            self.stack.push_op(self.input)
            self.input = ''
        except OperationError, e:
            self.message(e.message, 2000)
        except StackError:
            pass
    def stack_pop_op(self):
        try:
            self.input = self.stack.pop_op()
        except (StackError, OperationError), e:
            self.message(e.message, 2000)
        
    def message(self, text, timeout=500):
        banner = hildon.hildon_banner_show_information(self.window, '', text)
        banner.set_timeout(timeout)
        return banner

    def create_keypad(self):
        def create_table(rows, cols, rowsp, colsp):
            box = gtk.Table(rows, cols, homogeneous=True)
            box.set_row_spacings(rowsp)
            box.set_col_spacings(colsp)
            box.set_properties(width_request=cols*75)
            return box

        buttons_box1 = create_table(5, 5, 4, 4)
        buttons_box2 = create_table(5, 3, 4, 4)

        # Decimal digits
        for i in range(0, 9):
            x, y = i % 3, 3 - (i / 3)
            b = button(i+1, self.hit_digit)
            buttons_box1.attach(b, x, x+1, y, y+1)
        b = button(0, self.hit_digit)
        buttons_box1.attach(b, 0, 1, 4, 5)

        # Hex digits
        for i in range(0, 6):
            x, y = i % 2, 3 - (i / 2)
            b = button(chr(i+65), self.hit_digit)
            buttons_box1.attach(b, x+3, x+4, y, y+1)

        # Other digital inputs
        b = button('.', self.hit_digit)
        buttons_box1.attach(b, 1, 2, 4, 5)
        b = button('±', self.hit_switch_sign)
        buttons_box1.attach(b, 2, 3, 4, 5)

        # Basic operations
        for i, c in enumerate(u'↑÷×−+'):
            b = button(str(c), self.hit_opkey)
            buttons_box2.attach(b, 0, 1, i, i+1)

        # Stack operations
        hooks = [self.hit_push_stack, self.hit_pop_stack]
        for i, c in enumerate((u'st↓', u'st↑')):
            b = button(c, hooks[i])
            buttons_box1.attach(b, i+3, i+4, 4, 5)

        # Binary operations
        for i, c in enumerate(('^', '&~', '&', '~', '|')):
            b = button(c, self.hit_opkey)
            buttons_box2.attach(b, 1, 2, i, i+1)

        for i, c in enumerate(('<<', '>>')):
            b = button(c, self.hit_opkey)
            buttons_box2.attach(b, 2, 3, i, i+1)

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
