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
from .base.candidate import Candidate
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
    filetype_ext string.
    """
    return SmartParser(input_files, filetype_hint).parse(handler)



################################################################################


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
            if hasattr(f, "close"):
                if f != sys.stdin:  # XXX 2014-11-07 broken by Python2kFileWrapper
                    f.close()
        self._files = []


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


class AbstractTxtParser(AbstractParser):
    r"""Base class for plaintext-file parsing objects.
    (For example, CONLL parsers, Moses parsers...)

    Subclasses should override `_parse_line`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    @param encoding: The encoding to use when reading files.
    """
    def __init__(self, input_files, encoding):
        super(AbstractTxtParser, self).__init__(input_files)
        self.encoding = encoding
        self.encoding_errors = "replace"
        self.root = "<unknown-root>"

    def _parse_file(self, fileobj, handler):
        if self.root == "<unknown-root>":
            raise Exception("Subclass should have set `self.root`")
        info = {"parser": self, "root": self.root}
        with ParsingContext(fileobj, handler, info):
            for i, line in enumerate(fileobj):
                self._parse_line(
                        line[:-1].decode(self.encoding, self.encoding_errors),
                        handler, {"fileobj": fileobj, "linenum": i+1})

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


class FiletypeInfo(object):
    r"""Instances of this class represent a filetype.
    Subclasses must define `filetype_ext` and override
    the methods `make_parser` and `matches`.

    Attributes:
    -- filetype_ext: the extension for this filetype.
    Also used as a filetype hint.
    """
    def __init__(self, ext):
        self.filetype_ext = ext

    def make_parser(self, fileobjs):
        r"""Return a parser for given file objects."""
        raise NotImplementedError

    def matches_header(self, fileobj, strict):
        r"""Return whether the header of `fileobj`
        could be interpreted as an instance of this filetype.

        If `strict` is True, perform stricter checks and
        only return True if the header is *known* to be in
        the format of this filetype (usually, one should use
        strict=True when detecting filetypes and strict=False
        when checking for bad matches."""
        raise NotImplementedError

    def matches_filetype(self, filetype_hint):
        r"""Return whether the binary contents
        of `header` matches this filetype."""
        return self.filetype_ext == filetype_hint

    def check(self, fileobj):
        r"""Check if `fileobj` belongs to this filetype
        and raise an exception if it does not."""
        if not self.matches_header(fileobj, strict=False):
            raise Exception("Bad {} input".format(self.filetype_ext))



################################################################################


class XMLInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for mwetoolkit's XML."""
    def __init__(self):
        super(XMLInfo, self).__init__("XML")

    def make_parser(self, fileobjs):
        return XMLParser(fileobjs)

    def matches_header(self, fileobj, strict):
        header = fileobj.peek(20)
        return header.startswith(b"<?xml") or header.startswith(b"<pattern")


class XMLParser(AbstractParser):
    r"""Instances of this class parse the mwetoolkit XML format,
    calling the `handler` for each object that is parsed.
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
                    raise Exception("Bad outer tag in XML filetype: " + repr(elem.tag))


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



class WaCInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for ukWaC format."""
    def __init__(self):
        super(WaCInfo, self).__init__("WaC")

    def make_parser(self, fileobjs):
        return WaCParser(fileobjs)

    def matches_header(self, fileobj, strict):
        return fileobj.peek(20).startswith(b"CURRENT URL")


class WaCParser(AbstractTxtParser):
    r"""Instances of this class parse the ukWaC format,
    calling the `handler` for each object that is parsed.
    """
    def __init__(self, in_files, encoding='utf-8'):
        super(WaCParser,self).__init__(in_files, encoding)
        self.root = "corpus"
        self.line_terminators = ".!?"
        self.s_id = 1

    def _parse_line(self, line, handler, info={}):
        if not line.startswith("CURRENT URL"):
            import re
            eols = self.line_terminators
            for m in re.finditer("([^"+eols+"]+ .(?! [a-z])|[^"+eols+"]+$) *", line):
                words = [Word(surface) for surface in m.group(1).split(" ")]
                handler.handle_sentence(Sentence(words, self.s_id))
                self.s_id += 1



class PlainCandidatesInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for PlainCandidates format."""
    def __init__(self):
        super(PlainCandidatesInfo, self).__init__("WaC")

    def make_parser(self, fileobjs):
        return PlainCandidatesParser(fileobjs)

    def matches_header(self, fileobj, strict):
        header = fileobj.peek(1024)
        return " " not in header and "_" in header


class PlainCandidatesParser(AbstractTxtParser):
    r"""Instances of this class parse the PlainCandidates format,
    calling the `handler` for each object that is parsed.
    """
    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCandidatesParser, self).__init__(in_files, encoding)
        self.root = "candidates"

    def _parse_line(self, line, handler, info={}):
        words = [Word(lemma) for lemma in line.split("_")]
        c = Candidate(info["linenum"], words)
        handler.handle_candidate(c)



class MosesInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for Moses."""
    def __init__(self):
        super(MosesInfo, self).__init__("Moses")

    def make_parser(self, fileobjs):
        return MosesParser(fileobjs)

    def matches_header(self, fileobj, strict):
        return False  # XXX add code


class MosesParser(AbstractTxtParser):
    r"""Instances of this class parse the Moses format,
    calling the `handler` for each object that is parsed.
    """
    def __init__(self, in_files, encoding='utf-8'):
        super(MosesParser,self).__init__(in_files, encoding)
        self.root = "corpus"

    def _parse_line(self, line, handler, info={}):
        s = Sentence([], info["linenum"])
        words = line.split(" ")
        for w in words:
            try:
                surface, lemma, pos, syntax = w.split("|")
                s.append(Word(surface, lemma, pos, syntax))
            except Exception as e:
                util.warn("Ignored token " + w)
                util.warn(unicode(type(e)))
        handler.handle_sentence(s)



class ConllInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for CONLL."""
    def __init__(self):
        super(ConllInfo, self).__init__("CONLL")

    def make_parser(self, fileobjs):
        return ConllParser(fileobjs)

    def matches_header(self, fileobj, strict):
        header = fileobj.peek(1024)
        return len(header.split(b"\n", 1)[0].split()) \
                == len(ConllParser.ENTRIES)


class ConllParser(AbstractTxtParser):
    r"""Instances of this class parse the CONLL format,
    calling the `handler` for each object that is parsed.

    Each line should have these entries:
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

    def __init__(self, in_files, encoding='utf-8'):
        super(ConllParser,self).__init__(in_files, encoding)
        self.name2index = {name:i for (i, name) in enumerate(self.ENTRIES)}
        self.root = "corpus"
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        data = line.strip().split()
        if len(data) <= 1: return
        data = [(WILDCARD if d == "_" else d) for d in data]

        if len(data) < len(self.ENTRIES):
            util.warn("Ignoring line {} (only {} entries)" \
                    .format(info["linenum"], len(data)))
            return

        def get(attribute):
            try:
                return data[self.name2index[attribute]]
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
        self.partial_obj.append(objectWord)


    def maybe_warn(self, entry, entry_name):
        if entry != WILDCARD:
            util.warn_once("WARNING: unable to handle CONLL " \
                    "entry: {}.".format(entry_name))



class BinaryIndexInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for BinaryIndex files."""
    def __init__(self):
        super(BinaryIndexInfo, self).__init__("BinaryIndex")

    def make_parser(self, fileobjs):
        return BinaryIndexParser(fileobjs)

    def check(self, fileobj):
        if fileobj == sys.stdin:
            raise Exception("Cannot read BinaryIndex file from stdin!")
        if not fileobj.name.endswith(".info"):
            raise Exception("BinaryIndex file should have extension .info!")
        super(BinaryIndexInfo, self).check(fileobj)

    def matches_header(self, fileobj, strict):
        return fileobj.peek(20).startswith(b"corpus_size int")


class BinaryIndexParser(AbstractParser):
    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "root": "corpus"}
        with ParsingContext(fileobj, handler, info):
            from .indexlib import Index
            assert fileobj.name.endswith(".info")
            index = Index(fileobj.name[:-len(".info")])
            index.load_main()
            for sentence in index.iterate_sentences():
                handler.handle_sentence(sentence)


class SmartParser(AbstractParser):
    r"""Class that detects the file format
    and delegates the work to the correct parser."""
    def __init__(self, input_files, filetype_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.filetype_hint = filetype_hint
        self.filetype_infos = [XMLInfo(), ConllInfo(),
                WaCInfo(), BinaryIndexInfo(),
                MosesInfo(), PlainCandidatesInfo()]

    def parse(self, handler):
        with handler:
            for f in self._files:
                fti = self._detect_filetype(f, self.filetype_hint)
                fti.check(f)
                p = fti.make_parser([f])
                # Delegate the whole work to parser `p`.
                p.parse(handler)
        return handler


    def _detect_filetype(self, fileobj, filetype_hint):
        r"""Return a FiletypeInfo instance for given fileobj."""
        for fti in self.filetype_infos:
            if fti.matches_filetype(filetype_hint):
                return fti

        for fti in self.filetype_infos:
            if fti.matches_header(fileobj, strict=True):
                return fti

        raise Exception("Unknown file format")



################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
