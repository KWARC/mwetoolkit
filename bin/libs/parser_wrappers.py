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
This module provides wrapper classes for parsers.
They provide a more elegant interface to file parsers such as
`xmlhandler.genericXMLHandler.GenericXMLHandler`.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import xml.sax


################################################################################


def open_files_r(paths):
    r"""(Yield readable file objects for all paths)"""
    for path in paths:
        if isinstance(path, file):
            yield path
        elif path == "-":
            yield sys.stdin
        else:
            yield open(path, "r")


class StopParsing(Exception):
    """Raised to warn the parser that it should stop parsing the current file.
    Conceptually similar to StopIteration.
    """
    pass


class AbstractParser(object):
    r"""Base class for text parsing objects.

    Subclasses should override `_parse_file` and provide callbacks.

    Constructor Arguments:
    @param in_files A list of target file paths.
    @param printer A printer-like object (see `printers.py`).
    """
    def __init__(self, in_files, printer=None):
        assert isinstance(in_files, list)
        self._files = list(open_files_r(in_files or ["-"]))
        self.printer = printer
        if self.printer is None:
            from . import printers
            self.printer = printers.SimplePrinter(root=None)

    def _parse_file(self, fileobj):
        r"""(Called to parse file `fileobj`)"""
        raise NotImplementedError

    def parse(self):
        r"""Parse all files with this parser."""
        with self.printer:
            for f in self._files:
                try:
                    self._parse_file(f)
                except StopParsing:  # Read only part of file
                    pass  # Just interrupt parsing
                self.postfunction(f.name)
        self.close()

    def close(self):
        r"""Close all files opened by this parser."""
        for f in self._files:
            if f != sys.stdin:
                f.close()
        self._files = []

    def _parse_file(self, f):
        r"""Internal function. (Parses file with this parser)."""
        raise NotImplementedError

    def postfunction(self, fname):
        r"""Post-processing function that is called
        after parsing each file.
        @param fname A string with the file name.
        """
        pass
        
################################################################################

class XMLParser(AbstractParser):
    r"""Instances of this function parse XML,
    calling `treat_sentence` for each Sentence object read.
    Run it like this: `XMLParser(xml_file_objs...).parse()`.
    """
    def _parse_file(self, fileobj):
        from xmlhandler.genericXMLHandler import GenericXMLHandler
        self.parser = xml.sax.make_parser()
        # Ignores the DTD declaration. This will not validate the document!
        self.parser.setFeature(xml.sax.handler.feature_external_ges, False)
        handler = GenericXMLHandler(treat_entity=self.treat_sentence)
        self.parser.setContentHandler(handler)
        self.parser.parse(fileobj)

    def treat_sentence(self, entity):
        r"""Called to parse an Entity object. Subclasses may override."""
        pass

################################################################################

class TxtParser(AbstractParser):
    r"""Instances of this function parse TXT,
    calling `treat_line` on each line.
    Run it like this: `TxtParser(txt_file_objs...).parse()`.
    """
    def _parse_file(self, fileobj):
        for line in fileobj.readlines():
            self.treat_line(line.strip())

    def treat_line(self, sentence):
        r"""Called to parse a line of the TXT file.
        Subclasses may override."""
        pass


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
