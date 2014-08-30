#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
#
# printer.py is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
This module provides `Printer` classes.
These classes can be used to print all kinds of
objects in different output formats.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
from .xmlhandler.classes.sentence import Sentence
from .xmlhandler.classes.__common import XML_HEADER, XML_FOOTER


################################################################################


class AbstractPrinter(object):
    r"""Base implementation of a printer-style class.
    Instances support reentrant `with` constructs.

    Subclasses should override `stringify`, and optionally
    also `header` and `footer`.
    
    Constructor Arguments:
    @param output An IO-like object, such as sys.stdout
    or an instance of StringIO.
    """
    def __init__(self, output=None):
        self._output = output or sys.stdout
        self._waiting_objects = []
        self._scope = 0

    def stringify(self, obj):
        r"""Convert `obj` into a string to be flushed."""
        raise NotImplementedError

    def header(self):
        r"""String to print before everything else."""
        return ""

    def footer(self):
        r"""String to print after everything else."""
        return ""


    def add(self, *objects):
        r"""Queue objects to be printed."""
        self._waiting_objects.extend(objects)
        return self  # enable call chaining

    def last(self):
        r"""Return last (non-flushed) added object."""
        return self._waiting_objects[-1]

    def flush(self):
        r"""Eagerly print the current contents."""
        for obj in self._waiting_objects:
            self._write(self.stringify(obj))
        del self._waiting_objects[:]
        return self  # enable call chaining

    def _write(self, string, end=""):
        r"""(Print string in self._output)"""
        string = string.encode('utf-8')
        self._output.write(string)

    def __enter__(self):
        r"""(Called when entering `with` statement)"""
        if self._scope == 0:
            self.add(self.header())
        self._scope += 1
        return self

    def __exit__(self, t, v, tb):
        r"""(Called when exiting `with` statement)"""
        self._scope -= 1
        if self._scope == 0:
            if t is None:
                self.add(self.footer()).flush()
        return False



#################################################
class SimplePrinter(AbstractPrinter) :
    """Instances can be used to print plain-text data.

    Example:
    >>> from sentence import *
    >>> from word import *
    >>> s1 = Sentence((Word(w) for w in "Sample sentence .".split()), 1)
    >>> s2 = Sentence((Word(w) for w in "Another sentence !".split()), 2)
    >>> s3 = "A plain-text sentence."
    >>> with XMLPrinter(root=None) as p:  # doctest: +ELLIPSIS
    ...     p.add(s1, s2)
    <__main__.TextPrinter object at ...>
    Sample sentence .
    Another sentence !
    A plain-text sentence.
    """
    def stringify(self, obj):
        return unicode(obj) + "\n"


#################################################
class XMLPrinter(AbstractPrinter):
    """Instances can be used to print XML objects.
    
    Example:
    >>> from sentence import *
    >>> from word import *
    >>> s1 = Sentence((Word(w) for w in "Sample sentence .".split()), 1)
    >>> s2 = Sentence((Word(w) for w in "Another sentence !".split()), 2)
    >>> s3 = "A plain-text sentence."
    >>> with XMLPrinter(root=None) as p:  # doctest: +ELLIPSIS
    ...     p.add(s1, s2)
    <__main__.XMLPrinter object at ...>
    <s s_id="1"><w surface="Sample" /> <w surface="sentence" /> <w surface="." /> </s>
    <s s_id="2"><w surface="Another" /> <w surface="sentence" /> <w surface="!" /> </s>
    A plain-text sentence.

    Constructor Arguments:
    @param root Name of the root for the XML output.
    May be None to skip printing header/footers.
    @param output An IO-like object, such as sys.stdout
    or an instance of StringIO.
    """
    def __init__(self, root, output=None) :
        super(XMLPrinter,self).__init__(output=output)
        self.root = root

    def header(self):
        if not self.root: return ""
        return XML_HEADER % {"root": self.root, "ns": ""} + "\n"

    def footer(self):
        if not self.root: return ""
        return XML_FOOTER % {"root": self.root} + "\n"

    def stringify(self, obj):
        try:
            return obj.to_xml() + "\n"
        except AttributeError:
            return unicode(obj)


#################################################
class SurfacePrinter(AbstractPrinter):
    """Instances can be used to print XML surface forms.

    Example:
    >>> from sentence import *
    >>> from word import *
    >>> s1 = Sentence((Word(w) for w in "Sample sentence .".split()), 1)
    >>> s2 = Sentence((Word(w) for w in "Another sentence !".split()), 2)
    >>> s3 = "A plain-text sentence."
    >>> with XMLPrinter(root=None) as p:  # doctest: +ELLIPSIS
    ...     p.add(s1, s2)
    <__main__.TextPrinter object at ...>
    Sample sentence .
    Another sentence !
    A plain-text sentence.
    """
    def stringify(self, obj):
        try:
            return obj.to_surface() + "\n"
        except AttributeError:
            return unicode(obj)


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
