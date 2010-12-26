#!/usr/bin/python
# coding: utf-8

import gtk
import hildon

def button(label):
    button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
    button.set_label(str(label))
    return button

class MyApp(hildon.Program):

    def __init__(self):
        super(MyApp, self).__init__()

        self.window = hildon.Window()
        self.window.connect("delete_event", self.quit)
        self.add_window(self.window)

        #menu_bar = self.create_menu()
        #label = gtk.Label('Hello, world!')

        keypad = self.create_keypad()
        stack = hildon.TextView()
        input = hildon.Entry(gtk.HILDON_SIZE_AUTO)

        input.set_properties(hildon_input_mode=gtk.HILDON_GTK_INPUT_MODE_ALPHA|gtk.HILDON_GTK_INPUT_MODE_NUMERIC|gtk.HILDON_GTK_INPUT_MODE_SPECIAL)
        stack.set_properties(width_request=300, editable=False)

        hbox = gtk.HBox()
        hbox.pack_start(stack)
        hbox.pack_end(keypad)

        vbox = gtk.VBox()
        vbox.pack_start(input)
        vbox.pack_end(hbox)

        #self.window.set_app_menu(menu_bar)
        #self.window.add(label)
        self.window.add(vbox)

    def quit(self, *args):
        gtk.main_quit()

    def create_menu(self):
        pass

    def create_keypad(self):
        buttons_box = gtk.Table(5, 8, homogeneous=True)
        buttons_box.set_row_spacings(4)

        # Decimal digits
        for i in range(0, 9):
            x, y = i % 3, 3 - (i / 3)
            b = button(i+1)
            buttons_box.attach(b, x, x+1, y, y+1)
        b = button(0)
        buttons_box.attach(b, 0, 1, 4, 5)

        # Hex digits
        for i in range(0, 6):
            x, y = i % 2, 3 - (i / 2)
            b = button(chr(i+65))
            buttons_box.attach(b, x+3, x+4, y, y+1)

        # Other digital inputs
        for i, c in enumerate(u',±'):
            b = button(c)
            buttons_box.attach(b, i+1, i+2, 4, 5)

        # Basic operations
        for i, c in enumerate(u'↑÷×−+'):
            b = button(c)
            buttons_box.attach(b, 5, 6, i, i+1)


        # Stack operations
        for i, c in enumerate((u'st↓', u'st↑')):
            b = button(c)
            buttons_box.attach(b, i+3, i+4, 4, 5)

        # Binary operations
        for i, c in enumerate(('xor', 'and\nnot', 'and', 'not', 'or')):
            b = button(c)
            buttons_box.attach(b, 6, 7, i, i+1)

        for i, c in enumerate(('<<', '>>')):
            b = button(c)
            buttons_box.attach(b, 7, 8, i, i+1)

        b = button('Fill')
        buttons_box.attach(b, 7, 8, 2, 3)

        # Execute
        b = button('=')
        buttons_box.attach(b, 7, 8, 3, 5)

        # Special mode keys
        b = button('Mode')
        buttons_box.attach(b, 3, 4, 0, 1)
        b = button('Fn')
        buttons_box.attach(b, 4, 5, 0, 1)

        # Edit keys
        b = button('C')
        buttons_box.attach(b, 0, 1, 0, 1)
        b = button(u'←')
        buttons_box.attach(b, 1, 3, 0, 1)

        return buttons_box

    def run(self):
        self.window.show_all()
        gtk.main()


if __name__ == '__main__':
    app = MyApp()
    app.run()


