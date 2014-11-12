#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# printers.py is part of mwetoolkit
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
This module provides `Printer` base.
These base can be used to print all kinds of
objects in different output formats.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import datetime

from .base.__common import XML_HEADER, XML_FOOTER
from .parser_wrappers import StopParsing

################################################################################


class AbstractPrinter(object):
    r"""Base implementation of a printer-style class.
    Instances support reentrant `with` constructs, which
    should be used when `root` is not None.

    Subclasses should override `stringify`, and optionally
    also `header` and `footer`.
    
    Constructor Arguments:
    @param root The type of the output file. This value
    must be one of [None, "corpus", "candidates", "patterns"].
    @param output An IO-like object, such as sys.stdout
    or an instance of StringIO.
    @param flush_on_add If True, calls `self.flush()` automatically
    inside `self.add()`, before actually adding the element(s).
    """
    def __init__(self, root, output=None, flush_on_add=True):
        assert root in [None, "corpus", "candidates", "patterns"], root
        self._root = root
        self._output = output or sys.stdout
        self._flush_on_add = flush_on_add
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
        if self._flush_on_add:
            self.flush()
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
        try:
            self._output.write(string)
        except IOError:
            sys.exit(-1)

    def __enter__(self):
        r"""(Called when entering `with` statement)"""
        if self._scope == 0:
            self._write(self.header())
        self._scope += 1
        return self

    def __exit__(self, t, v, tb):
        r"""(Called when exiting `with` statement)"""
        self._scope -= 1
        if self._scope == 0:
            if v is None or isinstance(v, StopParsing):
                self.flush()
                self._write(self.footer())
        return False



#################################################
class SimplePrinter(AbstractPrinter) :
    """Instances can be used to print plain-text data.

    Example:
    >>> from libs.base.sentence import Sentence
    >>> from libs.base.word import Word
    >>> s1 = Sentence((Word(w) for w in "Sample sentence .".split()), 1)
    >>> s2 = Sentence((Word(w) for w in "Another sentence !".split()), 2)
    >>> s3 = "A plain-text sentence."
    >>> with SimplePrinter(root=None) as p:  # doctest: +ELLIPSIS
    ...     p.add(s1, s2)
    <__main__.SimplePrinter object at ...>
    Sample sentence .
    Another sentence !
    A plain-text sentence.

    Constructor Arguments:
    Same as `AbstractPrinter`.
    Parameter `root` is ignored.
    """
    def stringify(self, obj):
        return unicode(obj) + "\n"


#################################################
class XMLPrinter(AbstractPrinter):
    """Instances can be used to print XML objects.
    
    Example:
    >>> from libs.base.sentence import Sentence
    >>> from libs.base.word import Word
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
    @param root: Name of the root for the XML output. This value
    must be one of [None, "corpus", "candidates", "patterns"].
    When it is None, skip printing header/footers.
    @param output: An IO-like object, such as sys.stdout
    or an instance of StringIO.
    """
    def header(self):
        if not self._root: return ""
        return XML_HEADER % {"root": self._root, "ns": ""} + "\n"

    def footer(self):
        if not self._root: return ""
        return XML_FOOTER % {"root": self._root} + "\n"

    def stringify(self, obj):
        try:
            return obj.to_xml() + "\n"
        except AttributeError:
            return unicode(obj)


#################################################
class SurfacePrinter(AbstractPrinter):
    """Instances can be used to print XML surface forms.
    Similar to `SimplePrinter`.
    """
    def stringify(self, obj):
        try:
            return obj.to_surface() + "\n"
        except AttributeError:
            return unicode(obj)
            
#################################################
class MosesPrinter(AbstractPrinter):
    """Instances can be used to print Moses factored format.
    Similar to `SimplePrinter`.
    """
    def stringify(self, obj):
        try:
            return obj.to_moses() + "\n"
        except AttributeError:
            return unicode(obj)

#################################################
class HTMLPrinter(AbstractPrinter):
    """Instances can be used to print HTML format.
    """
    def __init__(self, source):
        super(HTMLPrinter, self).__init__(None)
        self.source = source

    def header(self):
        html_header="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>MWETOOLKIT annotated corpus: %(corpusname)s</title>
    <!--<link rel="stylesheet" href="mwetk-corpus.css" type="text/css" media="screen"/>-->
    <style>
    h1{margin:0}
    p.notice{font-family:Arial;font-size:10pt;margin:0}
    hr{margin:10px 0}
    p.sent{margin:2px 100px 2px 0;line-height:145%%;padding:4px 2px}
    p.sent:hover{background-color:#FFC}
    p.sent span.sid{border:1px solid #000;border-radius:2px;padding:1px 5px}
    p.sent:hover span.sid{background:#F22;color:#FFF}
    p.sent:hover a.word{border-color:#03A}
    span.mwepart a.word{border:2px solid #000}
    span.mwe1 a.word{background-color:#F66}
    span.mwe2 a.word{background-color:#9C0}
    span.mwe3 a.word{background-color:#69F}
    span.mwe4 a.word{background-color:#F90}
    a.word{position:relative;border:1px solid #CCF;border-radius:2px;padding:1px 2px;margin:auto 0;font-family:Verdana sans-serif;text-decoration:none;color:#000}
    a.word:hover{background-color:#03A;border-color:#000;color:#FFF}
    a.word span.surface{font-weight:700}
    a.word span.wid{font-size:70%%;position:relative;top:.3em;font-style:italic;padding-left:3px}
    a.word span.lps{color:#000;padding:2px 5px;top:1em;z-index:1;height:auto;opacity:0;position:absolute;visibility:hidden;background-color:#AAA;border:1px solid #000;border-radius:2px;box-shadow:#000 2px 2px 6px}
    a.word:hover span.lps{opacity:.95;visibility:visible}
    a.word span.lps span.lemma{font-style:italic;display:block}
    a.word span.lps span.pos{font-weight:700;display:block}
    a.word span.lps span.syn{font-weight:400;display:block;font-family:Arial}
    </style>
</head>
<body>
<h1>Corpus: %(corpusname)s</h1>
<p class="notice">Generated automatically by the <a href="http://mwetoolkit.sf.net/" target="_blank">mwetoolkit</a> </p>
<p class="notice"> Timestamp: %(timestamp)s</p>
<p class="notice">Source: <tt>%(filename)s</tt></p>
<hr/>"""
        s = self.source
        return html_header % { "timestamp": datetime.datetime.now(),
                              "corpusname": s[max(0,s.rfind("/")):],
                              "filename": s}

    def footer(self):
        return  "</body>\n</html>"


    def stringify(self, obj):
        try:
            return obj.to_html() + "\n"
        except AttributeError:
            return unicode(obj)


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
