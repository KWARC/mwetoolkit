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
This module provides the `Printer` class. This class can be used to print
XML objects such as Sentence and Word.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
from .sentence import Sentence
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER

################################################################################

class Printer(object) :
    """A `Printer` is an object that prints XML objects.
    
    Example:
    >>> from sentence import *
    >>> from word import *
    >>> s1 = Sentence((Word(w) for w in "Sample sentence .".split()), 1)
    >>> s2 = Sentence((Word(w) for w in "Another sentence !".split()), 2)
    >>> with Printer(root=None) as p:  # doctest: +ELLIPSIS
    ...     p.add(s1, s2)
    <__main__.Printer object at ...>
    <s s_id="1"><w surface="Sample" /> <w surface="sentence" /> <w surface="." /> </s>
    <s s_id="2"><w surface="Another" /> <w surface="sentence" /> <w surface="!" /> </s>
    """
    
    def __init__(self, root, output=None) :
        """Instantiates a new Printer for `output`.
        @param root Name of the root for the XML output.
        May be None to skip printing header/footers.
        @param output An IO-like object, such as sys.stdout
        or an instance of StringIO.
        """
        self.root = root
        self.output = output or sys.stdout
        self.xml_objects = []
        if self.root:
            print(XML_HEADER % {"root": root, "ns": ""})

    def add(self, *xml_objects):
        r"""Queue object(s) to be printed."""
        self.xml_objects.extend(xml_objects)
        return self  # enable chaining

    def last(self):
        r"""Return last object added."""
        return self.xml_objects[-1]

    def flush(self):
        r"""Eagerly print the current contents."""
        for obj in self.xml_objects:
            print(obj.to_xml(), file=self.output)
        del self.xml_objects[:]
        return self  # enable chaining

    def __enter__(self):
        return self

    def __exit__(self, *e):
        self.flush()
        if self.root:
            print(XML_FOOTER % {"root": self.root})


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
