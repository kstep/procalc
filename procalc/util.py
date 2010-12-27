# coding: utf-8

import gtk
import hildon

def bin(x):
    r = ''
    while x:
        r = str(x & 1) + r
        x = x >> 1
    return '0b' + (r or '0')

def dec(s):
    minus = s.startswith('-')
    s = s.lstrip('-')
    if not s:
        return 0

    if s.startswith('0'):
        if s.startswith('0x'):
            base = 16
        elif s.startswith('0b'):
            base = 2
        else:
            base = 8
        r = int(s.lstrip('0bx'), base)
    else:
        r = (float if '.' in s else int)(s)

    return -r if minus else r

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
