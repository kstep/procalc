# coding: utf-8

import gtk
import hildon

class ModeButton(hildon.GtkButton):

    def set_labels(self, *labels):
        self.__labels = labels
        self.set_label(labels[0])

    def change_mode(self, app, mode):
        try:
            label = self.__labels[mode]
        except IndexError:
            return
        self.set_label(label)

def liststore(*items):
    store = gtk.ListStore(str)
    for i in items:
        store.append((str(i),))
    return store

def selector(*columns):
    select = hildon.TouchSelector()

    for i, column in enumerate(columns):
        if not isinstance(column, gtk.ListStore):
            store = liststore(column)
        else:
            store = column
        select.append_text_column(store, True)
        select.set_active(i, 0)

    return select

def picker(label, onclicked=None, *items):
    if len(items) == 1 and isinstance(items[0], hildon.TouchSelector):
        selector = items[0]
    else:
        selector = hildon.TouchSelector(text=True)
        for i in items:
            selector.append_text(str(i))
        selector.set_active(0, 0)

    button = hildon.PickerButton(gtk.HILDON_SIZE_THUMB_HEIGHT, hildon.BUTTON_ARRANGEMENT_HORIZONTAL)
    button.set_title(label)
    button.set_selector(selector)

    if onclicked:
        button.connect('value-changed', onclicked)

    return button

def transpose_table(table):
    cols = table.get_property('n-columns')
    rows = table.get_property('n-rows')

    children = table.get_children()
    for c in children:
        x1 = table.child_get_property(c, 'left-attach')
        x2 = table.child_get_property(c, 'right-attach')
        y1 = table.child_get_property(c, 'top-attach')
        y2 = table.child_get_property(c, 'bottom-attach')
        table.child_set_property(c, 'left-attach', y1)
        table.child_set_property(c, 'right-attach', y2)
        table.child_set_property(c, 'top-attach', x1)
        table.child_set_property(c, 'bottom-attach', x2)

    table.resize(cols, rows)

def button(label, onclicked=None, button_type='normal', *args):
    button_class = dict(
            normal=hildon.GtkButton,
            mode=ModeButton,
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
        b = button(l, None, 'radio', b)
        b.set_label(l)
        b.set_mode(False)

        menu.add_filter(b)
        buttons.append(b)

    buttons[active].set_active(True)
    if onclicked:
        for b in buttons:
            b.connect('clicked', onclicked)
    return buttons
