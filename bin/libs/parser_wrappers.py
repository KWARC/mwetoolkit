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
from .base.__common import WILDCARD
from .base.sentence import Sentence
from .base.word import Word
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



def parse(input_files, handler, filetype_hint=None):
    r"""For each input file, detect its file format,
    parse it and call the appropriate handler methods.
    
    Most of the time, this method should be preferred over
    explicitly creating a Parser object.
    
    @param input_files: a list of file objects
    whose contents should be parsed.
    @param handler: an InputHandler.
    @param filetype_hint: either None or a valid
    filetype hint string.
    """
    return SmartParser(input_files, filetype_hint).parse(handler)



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

    Subclasses should override `_parse_file`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    """
    def __init__(self, input_files):
        assert isinstance(input_files, list)
        self._files = list(self._open_files(input_files or ["-"]))
        self.partial_obj = None
        self.partial_fun = None

    def _flush_partial_callback(self):
        r"""Finally perform the callback `self.partial_fun(self.partial_obj)`."""
        if self.partial_obj:
            self.partial_fun(self.partial_obj)
        self.partial_obj = self.partial_fun = None

    def new_partial(self, new_partial_obj, partial_fun):
        r"""Add future callback `partial_fun(self.partial_obj)`."""
        self._flush_partial_callback()
        self.partial_obj = new_partial_obj
        self.partial_fun = partial_fun


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
                self._flush_partial_callback()
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


class AbstractTxtParser(AbstractParser):
    r"""Base class for plaintext-file parsing objects.
    (For example, CSV parsers, Moses parsers, CONLL parsers...)

    Subclasses should override `_parse_line`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param encoding: The encoding to use when reading files.
    """
    def __init__(self, input_files, encoding):
        super(AbstractTxtParser, self).__init__(input_files)
        self.encoding = encoding
        self.root = "<unknown-root>"

    def _parse_file(self, fileobj, handler):
        if self.root == "<unknown-root>":
            raise Exception("Subclass should have set `self.root`")
        info = {"parser": self, "root": self.root}
        with ParsingContext(fileobj, handler, info):
            for i, line in enumerate(fileobj):
                self._parse_line(
                        line.strip().decode(self.encoding), handler,
                        {"fileobj": fileobj, "linenum": i})

    def _parse_line(self, line, handler, info={}):
        r"""Called to parse a line of the TXT file.
        Subclasses may override."""
        raise NotImplementedError


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


################################################################################


class XMLParser(AbstractParser):
    r"""Instances of this class parse XML,
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


class ConllParser(AbstractTxtParser):
    """Parser that reads an input file and converts it into mwetoolkit
    corpus XML format, printing the XML file to stdout.

    @param in_files The input files, in CONLL format: one word per line,
    with each word represented by the following 10 entries.

    Per-word entries:
    0. ID      -- word index in sentence (starting at 1).
    1. FORM    -- equivalent to `surface` in XML.
    2. LEMMA   -- equivalent to `lemma` in XML.
    3. CPOSTAG -- equivalent to `pos` in XML.
    4. POSTAG  -- simplified version of `pos` in XML.
                  (XXX currently ignored).
    5. FEATS   -- (XXX currently ignored).
    6. HEAD    -- equivalent to second part of `syn` in XML
                  (that is, the parent of this word)
    7. DEPREL  -- equivalent to the first part of `syn` in XML
                  (that is, the relation between this word and HEAD).
    8. PHEAD   -- (XXX currently ignored).
    9. PDEPREL -- (XXX currently ignored).
    """
    ENTRIES = ["ID", "FORM", "LEMMA", "CPOSTAG", "POSTAG",
            "FEATS", "HEAD", "DEPREL", "PHREAD", "PDEPREL"]
    NAME_TO_INDEX = {name:i for (i, name) in enumerate(ENTRIES)}

    def __init__(self, in_files, encoding='utf-8'):
        super(ConllParser,self).__init__(in_files, encoding)
        self.root = "corpus"
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        data = line.strip().split()
        if len(data) <= 1: return
        data = [(WILDCARD if d == "_" else d) for d in data]

        if len(data) < len(self.ENTRIES):
            util.warn("Ignoring line {} ({} entries)" \
                    .format(info["linenum"], len(data)))
            return

        def get(attribute):
            try:
                return data[self.NAME_TO_INDEX[attribute]]
            except KeyError:
                return WILDCARD

        if get("ID") == "1":
            self.new_partial(Sentence([], self.s_id),
                    handler.handle_sentence)
            self.s_id += 1

        surface, lemma = get("FORM"), get("LEMMA")
        pos, syn = get("CPOSTAG"), get("DEPREL")

        if get("POSTAG") != get("CPOSTAG"):
            self.maybe_warn(get("POSTAG"), "POSTAG != CPOSTAG")
        self.maybe_warn(get("FEATS"), "found FEATS")
        self.maybe_warn(get("PHEAD"), "found PHEAD")
        self.maybe_warn(get("PDEPREL"), "found PDEPREL")

        if get("HEAD") != WILDCARD:
            syn = syn + ":" + unicode(get("HEAD"))
        objectWord = Word(surface, lemma, pos, syn)
        self.partial_obj.word_list.append(objectWord)


    def maybe_warn(self, entry, entry_name):
        if entry != WILDCARD:
            util.warn_once("WARNING: unable to handle CONLL " \
                    "entry: {}.".format(entry_name))


class SmartParser(AbstractParser):
    r"""Class that detects the file format
    and delegates the work to the correct parser."""
    def __init__(self, input_files, filetype_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.filetype_hint = filetype_hint
        self.parsers = [
                (XMLParser,   "XML",   self.matches_xml),
                (ConllParser, "CONLL", self.matches_conll),
                #(MosesParser, "Moses", self.matches_moses),
                #(CSVParser,   "CSV",   self.matches_csv),
        ]

    def parse(self, handler):
        with handler:
            for f in self._files:
                p = self._parser_for(f, self.filetype_hint)([f])
                # Delegate the whole work to `p`.
                p.parse(handler)
        return handler


    def _parser_for(self, fileobj, filetype_hint):
        r"""Find parser class for given fileobj."""
        for (p_class, ext, matches) in self.parsers:
            if ext == filetype_hint:
                return p_class

        header = fileobj.peek(1024)
        for (p_class, ext, matches) in self.parsers:
            if matches(header):
                return p_class

        raise Exception("Unknown file format")


    def matches_xml(self, header):
        r"""Return True if binary `header` is in mwetoolkit's XML."""
        return header.startswith(b"<")

    def matches_conll(self, header):
        r"""Return True if binary `header` is in CONLL."""
        return len(header.split(b"\n", 1)[0].split()) \
                == len(ConllParser.ENTRIES)

    def matches_moses(self, header):
        r"""Return True if binary `header` is in Moses."""
        return False  # XXX add code

    def matches_csv(self, header):
        r"""Return True if binary `header` is in CSV."""
        return False  # XXX add code



################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
