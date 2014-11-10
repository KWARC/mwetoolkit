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

import io
import itertools
import sys

from xml.etree import ElementTree
from . import util


################################################################################


class StopParsing(Exception):
    """Raised to warn the parser that it should stop parsing the current file.
    Conceptually similar to StopIteration.
    """
    pass


class InputHandler(object):
    r"""Handler interface whose methods are called by the parser.
    Parsers will also call __enter__/__exit__ at the start/end
    of the parsing.

    Attributes:
    -- `printer`: A printer-like object (see `printers.py`).
    May be None if no printer object should be used.
    """
    printer = None

    def __enter__(self):
        if self.printer:
            self.printer.__enter__()
    
    def __exit__(self, t, v, tb):
        if self.printer:
            self.printer.__exit__(t, v, tb)

    def before_file(self, fileobj, info={}):
        r"""Called before parsing file contents."""
        pass  # By default, do nothing

    def after_file(self, fileobj, info={}):
        r"""Called after parsing file contents."""
        pass  # By default, do nothing

    def handle_meta(self, meta_obj, info={}):
        r"""Called to treat a Meta object."""
        pass  # By default, we just ignore meta

    def handle_entity(self, entity, info={}):
        r"""Called to treat a generic entity."""
        kind = info.get("kind", "entity")
        util.warn("Ignoring " + kind)

    def handle_sentence(self, sentence, info={}):
        r"""Called to treat a Sentence object."""
        info["kind"] = "sentence"
        return self.handle_entity(sentence, info)

    def handle_candidate(self, candidate, info={}):
        r"""Called to treat a Candidate object."""
        info["kind"] = "candidate"
        return self.handle_entity(candidate, info)

    def handle_pattern(self, pattern, info={}):
        r"""Called to treat a ParsedPattern object."""
        info["kind"] = "pattern"
        return self.handle_entity(pattern, info)



def parse(input_files, handler, file_format_hint=None):
    r"""For each input file, detect its file format,
    parse it and call the appropriate handler methods.
    
    Most of the time, this method should be preferred over
    explicitly creating a Parser object."""
    return SmartParser(input_files, file_format_hint).parse(handler)



################################################################################


class Python2kFileWrapper(object):
    r"""Wrapper to make Python2k stdin/stdout
    behave as in Python3k.  When wrapping io.BytesIO,
    this will also fix Python Issue 1539381."""
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getattr__(self, name):
        r"""Behave like the underlying file."""
        return getattr(self._wrapped, name)

    def readable(self):
        r"""(Override required by `sys.stdin`)."""
        try:
            return self._wrapped.readable()
        except AttributeError:
            return True  # Very deeply though-out code...

    def readinto(self, b):
        r"""(Override required by `io.StringIO`)."""
        try:
            return self._wrapped.readinto(b)
        except AttributeError:
            b[:] = self._wrapped.read(len(b))


class AbstractParser(object):
    r"""Base class for file parsing objects.

    Subclasses should override `_check_file` and `_parse_file`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    """
    def __init__(self, input_files):
        assert isinstance(input_files, list)
        self._files = list(self._open_files(input_files or ["-"]))


    def parse(self, handler):
        r"""Parse all files with this parser.

        @param handler: An instance of InputHandler.
        Callback methods will be called on `handler`.
        """
        with handler:
            for f in self._files:
                try:
                    self._parse_file(f, handler)
                except StopParsing:  # Reading only part of file
                    pass  # Just interrupt parsing
        self.close()
        return handler


    def _parse_file(self, fileobj, handler):
        r"""(Called to parse file `fileobj`)"""
        raise NotImplementedError

    def _open_files(self, paths):
        r"""(Yield readable file objects for all paths.)"""
        for path in paths:
            yield self._open_file(path)

    def _open_file(self, path):
        r"""(Return buffered file object for given path)"""
        if isinstance(path, io.BufferedReader):
            return path
        if path == "-":
            path = sys.stdin
        if isinstance(path, basestring):
            path = open(path, "rb")
        f = Python2kFileWrapper(path)
        return io.BufferedReader(f)


    def close(self):
        r"""Close all files opened by this parser."""
        for f in self._files:
            if f != sys.stdin:  # XXX 2014-11-07 broken by Python2kFileWrapper
                f.close()
        self._files = []


class XMLParser(AbstractParser):
    r"""Instances of this function parse XML,
    calling `handle_*` for each object that is parsed.
    Run it like this: `XMLParser(xml_fileobjs...).parse()`.
    """
    def _parse_file(self, fileobj, handler):
        # Here, fileobj is raw bytes, not unicode, because ElementTree
        # complains if we feed it a pre-decoded stream in python2k
        outer_iterator = ElementTree.iterparse(fileobj, ["start", "end"])

        for event, elem in outer_iterator:
            inner_iterator = itertools.chain(
                    [(event, elem)], outer_iterator)

            if event == "end":
                raise Exception("Unexpected end-tag!")

            elif event == "start":
                info = {"parser": self, "root": elem.tag}

                if elem.tag == "dict":
                    # Delegate all the work to "dict" handler
                    with ParsingContext(fileobj, handler, info):
                        from .dictXMLHandler import DictXMLHandler
                        self._handle(inner_iterator, DictXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_entry=handler.handle_entity))
                elif elem.tag == "corpus":
                    # Delegate all the work to "corpus" handler
                    with ParsingContext(fileobj, handler, info):
                        from .corpusXMLHandler import CorpusXMLHandler
                        self._handle(inner_iterator, CorpusXMLHandler(
                                treat_sentence=handler.handle_sentence))
                elif elem.tag == "candidates":
                    # Delegate all the work to "candidates" handler
                    with ParsingContext(fileobj, handler, info):
                        from .candidatesXMLHandler import CandidatesXMLHandler
                        self._handle(inner_iterator, CandidatesXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_candidate=handler.handle_candidate))
                elif elem.tag == "patterns":
                    with ParsingContext(fileobj, handler, info):
                        # Delegate all the work to "patterns" handler
                        from .patternlib import iterparse_patterns
                        for pattern in iterparse_patterns(inner_iterator):
                            handler.handle_pattern(pattern)
                else:
                    raise Exception("Bad outer tag: " + repr(elem.tag))


    def _handle(self, iterator, xmlhandler):
        r"""Call startElement/endElement on handler for all sub-elements."""
        depth = 0
        for event, elem in iterator:
            if event == "start":
                xmlhandler.startElement(elem.tag, elem.attrib)
                depth += 1
            elif event == "end":
                xmlhandler.endElement(elem.tag)
                depth -= 1
                if depth == 0:
                    return
            elem.clear()


class TxtParser(AbstractParser):
    r"""Instances of this function parse TXT,
    calling `handle_line` on each line.
    Run it like this: `TxtParser(txt_file_objs...).parse()`.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param encoding: The encoding to use when reading files.
    """
    def __init__(self, input_files, encoding):
        super(TxtParser, self).__init__(input_files)
        self.encoding = encoding
        self.root = "<unknown>"

    def handle_line(self, line, info={}):
        r"""Called to parse a line of the TXT file.
        Subclasses may override."""
        util.warn("Ignoring entity")  # XXX we should say what entity (line number...)

    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "root": self.root}
        with ParsingContext(fileobj, handler, info):
            for i, line in enumerate(fileobj.readlines()):
                handler.handle_line(
                        line.strip().decode(self.encoding),
                        {"linenum": i})


class ParsingContext(object):
    r"""(Call `handler.{before,after}_file`.)"""
    def __init__(self, fileobj, handler, info):
        self.fileobj, self.handler, self.info = fileobj, handler, info

    def __enter__(self):
        self.handler.before_file(self.fileobj, self.info)
        return self.handler.__enter__()
    
    def __exit__(self, t, v, tb):
        if v is None:
            self.handler.after_file(self.fileobj, self.info)
        return self.handler.__exit__(t, v, tb)


class SmartParser(AbstractParser):
    r"""Class that detects the file format
    and delegates the work to the correct parser."""
    def __init__(self, input_files, file_format_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.file_format_hint = file_format_hint

    def parse(self, handler):
        with handler:
            for f in self._files:
                p = self._parser_for(f)
                # Delegate the whole work to `p`.
                p.parse(handler)
        return handler

    def _parser_for(self, fileobj, file_format_hint=None):
        r"""Find parser for given fileobj."""
        if self.file_format_hint == "xml":
            return XMLParser([fileobj])
        if self.file_format_hint == "txt":
            return TxtParser([fileobj])
        if self.file_format_hint == "moses":
            return MosesParser([fileobj])
        if self.file_format_hint == "conll":
            return ConllParser([fileobj])
        header = fileobj.peek()
        if header[0] == "<":
            return XMLParser([fileobj])
        raise Exception("Unknown file format")


################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
