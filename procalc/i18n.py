# coding: utf-8
"""
>>> print _(u'''Programmer's calculator, v0.1
... 
... RPN calculator with bit-wise operations
... and infix operators emulation.
... 
... Distributed AS IS under GPLv3 or greater
... without any warranty.
... 
... Author: Konstantin Stepanov, (c) 2010''').encode('utf-8')
Калькулятор для программиста, v0.1
<BLANKLINE>
RPN-калькулятор с побитовыми операциями
и эмуляцией инфиксных операторов.
<BLANKLINE>
Распространяется КАК ЕСТЬ под лицензией GPLv3 или выше
без каких либо гарантий.
<BLANKLINE>
Автор: Константин Степанов, © 2010
"""

from gettext import translation

__all__ = ['_']

try:
    _i18n = translation('procalc')
except IOError:
    _i18n = translation('procalc', './i18n')

_ = _i18n.ugettext
