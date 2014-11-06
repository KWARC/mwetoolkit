#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# parser_wrappers.py is part of mwetoolkit
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
This module provides wrapper base for parsers.
They provide a more elegant interface to file parsers such as
`libs.genericXMLHandler.GenericXMLHandler`.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import itertools
from xml.etree import ElementTree
from . import util


################################################################################



class StopParsing(Exception):
    """Raised to warn the parser that it should stop parsing the current file.
    Conceptually similar to StopIteration.
    """
    pass


class AbstractParser(object):
    r"""Base class for text parsing objects.

    Subclasses should override `_parse_file` and provide callbacks.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param printer: A printer-like object (see `printers.py`).
    """
    def __init__(self, input_files, printer=None):
        assert isinstance(input_files, list)
        self._files = list(self._open_files(input_files or ["-"]))
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
        return self


    def _open_files(self, paths):
        r"""(Yield readable file objects for all paths.)"""
        for path in paths:
            yield self._open_file(path)

    def _open_file(self, path):
        r"""(Return readable raw file object for given path)"""
        if isinstance(path, file):
            return path
        elif path == "-":
            return sys.stdin
        else:
            return open(path, "r")


    def close(self):
        r"""Close all files opened by this parser."""
        for f in self._files:
            if f != sys.stdin:
                f.close()
        self._files = []

    def postfunction(self, fname):
        r"""Post-processing function that is called
        after parsing each file.
        @param fname A string with the file name.
        """
        pass
        

################################################################################

class XMLParser(AbstractParser):
    r"""Instances of this function parse XML,
    calling `treat_*` for each object that is parsed.
    Run it like this: `XMLParser(xml_fileobjs...).parse()`.
    """
    def treat_meta(self, meta_obj):
        r"""Called to treat a Meta object. Subclasses may override."""
        pass  # By default, we just ignore meta

    def treat_entity(self, entity):
        r"""Called to treat a generic entity. Subclasses may override."""
        util.warn("Ignoring entity")  # XXX we should say what entity (line number...)

    def treat_sentence(self, sentence):
        r"""Called to treat a Sentence object. Subclasses may override."""
        return self.treat_entity(sentence)

    def treat_candidate(self, candidate):
        r"""Called to treat a Candidate object. Subclasses may override."""
        return self.treat_entity(candidate)

    def treat_pattern(self, pattern):
        r"""Called to treat a ParsedPattern object. Subclasses may override."""
        return self.treat_entity(pattern)


    def _parse_file(self, fileobj):
        # Here, fileobj is raw bytes, not unicode, because ElementTree
        # complains if we feed it a pre-decoded stream in python2k
        outer_iterator = ElementTree.iterparse(fileobj, ["start", "end"])

        for event, elem in outer_iterator:
            inner_iterator = itertools.chain(
                    [(event, elem)], outer_iterator)

            if event == "end":
                raise Exception("Unexpected end-tag!")

            elif event == "start":
                if elem.tag == "dict":
                    # Delegate all the work to "dict" handler
                    from .dictXMLHandler import DictXMLHandler
                    self._handle(inner_iterator, DictXMLHandler(
                            treat_meta=self.treat_meta,
                            treat_entry=self.treat_entity))
                elif elem.tag == "corpus":
                    # Delegate all the work to "corpus" handler
                    from .corpusXMLHandler import CorpusXMLHandler
                    self._handle(inner_iterator, CorpusXMLHandler(
                            treat_sentence=self.treat_sentence))
                elif elem.tag == "candidates":
                    # Delegate all the work to "candidates" handler
                    from .candidatesXMLHandler import CandidatesXMLHandler
                    self._handle(inner_iterator, CandidatesXMLHandler(
                            treat_meta=self.treat_meta,
                            treat_candidate=self.treat_candidate))
                elif elem.tag == "patterns":
                    # Delegate all the work to "patterns" handler
                    from .patternlib import iterparse_patterns
                    for pattern in iterparse_patterns(inner_iterator):
                        self.treat_pattern(pattern)
                else:
                    raise Exception("Bad outer tag: " + repr(elem.tag))


    def _handle(self, iterator, handler):
        r"""Call startElement/endElement on handler for all sub-elements."""
        depth = 0
        for event, elem in iterator:
            if event == "start":
                handler.startElement(elem.tag, elem.attrib)
                depth += 1
            elif event == "end":
                handler.endElement(elem.tag)
                depth -= 1
                if depth == 0:
                    return
            elem.clear()


################################################################################

class TxtParser(AbstractParser):
    r"""Instances of this function parse TXT,
    calling `treat_line` on each line.
    Run it like this: `TxtParser(txt_file_objs...).parse()`.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param printer: A printer-like object (see `printers.py`).
    @param encoding: The encoding to use when reading files.
    """
    def __init__(self, input_files, printer, encoding):
        super(TxtParser, self).__init__(input_files, printer)
        self.encoding = encoding

    def treat_line(self, line):
        r"""Called to parse a line of the TXT file.
        Subclasses may override."""
        util.warn("Ignoring entity")  # XXX we should say what entity (line number...)

    def _parse_file(self, fileobj):
        for line in fileobj.readlines():
            self.treat_line(line.strip().decode(self.encoding))


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
