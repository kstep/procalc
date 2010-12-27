# coding: utf-8

import gtk
import hildon

def bin(x):
    r = ''
    a = abs(x)
    while a:
        r = str(a & 1) + r
        a = a >> 1
    r = '0b' + (r or '0')
    if x < 0:
        r = '-' + r
    return r

def dec(s):
    x = s.lstrip('-')
    if not x:
        return 0

    if x.startswith('0'):
        if x.startswith('0x'):
            base = 16
        elif x.startswith('0b'):
            base = 2
        else:
            base = 8
        r = int(x.lstrip('0bx') or '0', base)
    else:
        r = (float if '.' in x else int)(x)

    return -r if s.startswith('-') else r

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
