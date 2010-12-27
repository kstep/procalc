#!/usr/bin/python
# coding: utf-8

import gtk
import hildon

import operations
from operations import OperationError
from stack import OpStack, StackError

def button(label, onclicked=None, button_type='normal', *args):
    button_class = dict(
            normal=hildon.GtkButton,
            toggle=hildon.GtkToggleButton,
            radio=hildon.GtkRadioButton,
            check=hildon.CheckButton).get(button_type, hildon.GtkButton)
    button = button_class(gtk.HILDON_SIZE_FINGER_HEIGHT, *args)
    button.set_label(str(label))
    if onclicked:
        button.connect('clicked', onclicked)
    return button

def switch(menu, active=0, onclicked=None, *labels):
    b = None
    buttons = list()
    for l in labels:
        b = button(l, onclicked, 'radio', b)
        b.set_label(l)
        b.set_mode(False)

        menu.add_filter(b)
        buttons.append(b)

    buttons[active].set_active(True)
    return buttons

class MyApp(hildon.Program):

    def __init__(self):
        super(MyApp, self).__init__()

        self.window = hildon.Window()
        self.window.set_title("Programmer's Calculator")
        self.window.connect("delete_event", self.quit)
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
        panner.set_properties(mov_mode=hildon.MOVEMENT_MODE_VERT,
                size_request_policy=hildon.SIZE_REQUEST_MINIMUM, width_request=300)

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
        text = self.w_input.get_text()
        if text:
            self.stack.push_op(text)
        try:
            result = self.stack.pop_op()
        except (StackError, OperationError), e:
            self.message(e.message, 2000)
            return

        self.w_input.set_text(str(result))
        self.w_input.set_position(-1)

    def hit_opkey(self, b):
        op = b.get_label()
        text = self.w_input.get_text()
        if text:
            self.stack.push_op(text)
        self.w_input.set_text(op)
        self.w_input.set_position(-1)
        self.opmode = True

    def hit_digit(self, b):
        if self.opmode:
            self.opmode = False
            text = self.w_input.get_text()
            if text:
                self.stack.push_op(text)
                self.w_input.set_text('')

        self.w_input.insert_text(b.get_label(), -1)
        self.w_input.set_position(-1)

    def hit_switch_sign(self, b):
        if self.opmode:
            return
        text = self.w_input.get_text()
        if text.startswith('-'):
            self.w_input.set_text(text.lstrip('-'))
        else:
            self.w_input.set_text('-'+text)
        self.w_input.set_position(-1)

    def hit_backspace(self, b):
        text = self.w_input.get_text()
        self.w_input.set_text(text[:-1])
        self.w_input.set_position(-1)

    def hit_clear(self, b):
        self.w_input.set_text('')

    def hit_push_stack(self, b):
        text = self.w_input.get_text()
        self.w_input.set_text('')
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

        self.w_input.set_text(text)
        self.w_input.set_position(-1)

    def hit_switch_base(self, b):
        self.message('Base is %s now' % b.get_label())

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
            b = button(c, self.hit_opkey)
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

        b = button('Fill', None, 'toggle')
        buttons_box.attach(b, 7, 8, 2, 3)

        # Execute
        b = button('=', self.hit_execute)
        buttons_box.attach(b, 7, 8, 3, 5)

        # Special mode keys
        b = button('Mode', None, 'toggle')
        buttons_box.attach(b, 3, 4, 0, 1)
        b = button('Fn', None, 'toggle')
        buttons_box.attach(b, 4, 5, 0, 1)

        # Edit keys
        b = button('C', self.hit_clear)
        buttons_box.attach(b, 0, 1, 0, 1)
        b = button(u'←', self.hit_backspace)
        buttons_box.attach(b, 1, 3, 0, 1)

        return buttons_box

    def run(self):
        self.window.show_all()
        gtk.main()


if __name__ == '__main__':
    app = MyApp()
    app.run()

