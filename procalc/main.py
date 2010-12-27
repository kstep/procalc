# coding: utf-8

import gtk
import hildon

from procalc import operations
from procalc.operations import OperationError
from procalc.stack import OpStack, StackError
from procalc.util import button, switch, bin, dec

class ProCalcApp(hildon.Program):

    def __init__(self):
        super(ProCalcApp, self).__init__()

        self.window = hildon.Window()
        self.window.set_title("ProCalc")
        self.window.connect("delete_event", self.quit)
        self.add_window(self.window)

        keypad = self.create_keypad()
        stack = hildon.TextView()
        input = hildon.Entry(gtk.HILDON_SIZE_AUTO)

        input.set_placeholder('Empty value')
        input.set_properties(hildon_input_mode=gtk.HILDON_GTK_INPUT_MODE_HEXA|gtk.HILDON_GTK_INPUT_MODE_NUMERIC|gtk.HILDON_GTK_INPUT_MODE_SPECIAL)
        stack.set_placeholder('Stack is empty')
        stack.set_properties(editable=False)

        panner = hildon.PannableArea()
        panner.add_with_viewport(stack)
        panner.set_properties(mov_mode=hildon.MOVEMENT_MODE_VERT,
                size_request_policy=hildon.SIZE_REQUEST_MINIMUM, width_request=200)

        hbox = gtk.HBox()
        hbox.pack_start(panner)
        hbox.pack_end(keypad)

        vbox = gtk.VBox()
        vbox.pack_start(input)
        vbox.pack_end(hbox)

        self.w_stack = stack
        self.w_input = input
        self.w_keypad = keypad
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
        menu.show_all()
        return menu

    def hit_execute(self, b):
        text = self.input
        if text:
            self.stack.push_op(text)
        try:
            result = self.stack.pop_op()
        except (StackError, OperationError), e:
            self.message(e.message, 2000)
            return

        self.input = self.show_filter(dec(result))

    def hit_opkey(self, b):
        op = b.get_label()
        text = self.input
        if text:
            self.stack.push_op(text)
        self.input = op
        self.opmode = True

    def hit_digit(self, b):
        if self.opmode:
            self.opmode = False
            text = self.input
            if text:
                self.stack.push_op(text)
                self.input = ''

        if self.is_mode:
            bases = {'2': '0b', '8': '0', '0': '', 'A': '0x'}
            base = bases.get(b.get_label(), None)
            if base:
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
        text = self.input
        self.input = ''
        try:
            self.stack.push(text)
        except StackError, e:
            self.message(e.message)

    def hit_pop_stack(self, b):
        try:
            text = self.stack.pop()
        except StackError, e:
            self.message(e.message)
            return

        self.input = text

    def hit_switch_base(self, b):
        base_name = b.get_label()
        self.show_filter = dict(Bin=bin, Oct=oct, Dec=str, Hex=hex).get(base_name, str)
        if not self.opmode:
            text = self.input
            if text:
                self.input = self.show_filter(dec(text))

    def hit_mode(self, b):
        pass

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

    def message(self, text, timeout=500):
        banner = hildon.hildon_banner_show_information(self.window, '', text)
        banner.set_timeout(timeout)
        return banner

    def create_keypad(self):
        buttons_box = gtk.Table(5, 8, homogeneous=True)
        buttons_box.set_row_spacings(4)
        buttons_box.set_col_spacings(4)

        # Decimal digits
        for i in range(0, 9):
            x, y = i % 3, 3 - (i / 3)
            b = button(i+1, self.hit_digit)
            buttons_box.attach(b, x, x+1, y, y+1)
        b = button(0, self.hit_digit)
        buttons_box.attach(b, 0, 1, 4, 5)

        # Hex digits
        for i in range(0, 6):
            x, y = i % 2, 3 - (i / 2)
            b = button(chr(i+65), self.hit_digit)
            buttons_box.attach(b, x+3, x+4, y, y+1)

        # Other digital inputs
        b = button('.', self.hit_digit)
        buttons_box.attach(b, 1, 2, 4, 5)
        b = button('±', self.hit_switch_sign)
        buttons_box.attach(b, 2, 3, 4, 5)

        # Basic operations
        for i, c in enumerate(u'↑÷×−+'):
            b = button(str(c), self.hit_opkey)
            buttons_box.attach(b, 5, 6, i, i+1)

        # Stack operations
        hooks = [self.hit_push_stack, self.hit_pop_stack]
        for i, c in enumerate((u'st↓', u'st↑')):
            b = button(c, hooks[i])
            buttons_box.attach(b, i+3, i+4, 4, 5)

        # Binary operations
        for i, c in enumerate(('^', '&~', '&', '~', '|')):
            b = button(c, self.hit_opkey)
            buttons_box.attach(b, 6, 7, i, i+1)

        for i, c in enumerate(('<<', '>>')):
            b = button(c, self.hit_opkey)
            buttons_box.attach(b, 7, 8, i, i+1)

        # Execute
        b = button('=', self.hit_execute)
        buttons_box.attach(b, 7, 8, 3, 5)

        # Special mode keys
        b = button('Mod', self.hit_mode, 'toggle')
        self.w_mode = b
        buttons_box.attach(b, 3, 4, 0, 1)

        b = button('Fn', None, 'toggle')
        self.w_func = b
        buttons_box.attach(b, 4, 5, 0, 1)

        b = button('×Bⁿ')
        buttons_box.attach(b, 7, 8, 2, 3)

        # Edit keys
        b = button('C', self.hit_clear)
        buttons_box.attach(b, 0, 1, 0, 1)
        b = button(u'←', self.hit_backspace)
        buttons_box.attach(b, 1, 3, 0, 1)

        return buttons_box

    def run(self):
        self.window.show_all()
        gtk.main()
