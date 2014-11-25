#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# filetype.py is part of mwetoolkit
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
This module provides classes and methods for filetype detection,
parsing and printing.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import collections
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


class FiletypeOperations(collections.namedtuple("FiletypeOperations",
        "checker_class parser_class printer_class")):
    r"""A named triple (checker_class, parser_class, printer_class):
    -- checker_class: A subclass of AbstractChecker.
    -- parser_class: Either None or a subclass of AbstractParser.
    -- printer_class: Either None or a subclass of AbstractPrinter.
    """
    pass


class InputHandler(object):
    r"""Handler interface whose methods are called by the parser."""
    def before_file(self, fileobj, info={}):
        r"""Called before parsing file contents."""
        pass  # By default, do nothing

    def after_file(self, fileobj, info={}):
        r"""Called after parsing file contents."""
        pass  # By default, do nothing

    def handle_by_kind(self, kind, obj, info={}):
        r"""Alternative to calling `self.handle_{kind}` methods.
        Useful as a catch-all when delegating from another InputHandler."""
        return getattr(self, "handle_"+kind)(obj, info=info)

    def handle_meta(self, meta_obj, info={}):
        r"""Called to treat a Meta object."""
        pass  # By default, we just silently ignore Meta instances

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

    def handle_entity(self, entity, info={}):
        r"""Called to treat a generic entity (sentence/candidate/pattern)."""
        kind = info.get("kind", "entity")
        util.warn("Ignoring " + kind)


class DelegatorInputHandler(InputHandler):
    r"""InputHandler that delegates all methods to `self.delegate`."""
    delegate = None

    def before_file(self, fileobj, info={}):
        return self.delegate.before_file(fileobj, info)

    def after_file(self, fileobj, info={}):
        return self.delegate.after_file(fileobj, info)

    def handle_entity(self, entity, info={}):
        return self.delegate.handle_by_kind(info["kind"], entity, info)


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


def printer_class(filetype_ext):
    r"""Return a subclass of AbstractPrinter for given filetype extension.
    If you want a printer class that automatically handles all root types,
    create an instance of AutomaticPrinterHandler instead.
    """
    try:
        ret = HINT_TO_INFO[filetype_ext].operations().printer_class
    except KeyError:
        raise Exception("Unknown file extension: " + unicode(filetype_ext))
    if ret is None:
        raise Exception("Printer not implemented for: " + unicode(filetype_ext))
    return ret


class AutomaticPrinterHandler(DelegatorInputHandler):
    r"""InputHandler that creates an appropriate printer
    (based on either `self.forced_filetype_ext` or info["parser"])
    and delegates to it."""
    def __init__(self, forced_filetype_ext=None):
        self.forced_filetype_ext = forced_filetype_ext

    def before_file(self, fileobj, info={}):
        ext = self.forced_filetype_ext \
                or info["parser"].filetype_info.filetype_ext
        self.delegate = printer_class(ext)(info["root"])
        self.delegate.before_file(fileobj, info)



################################################################################


class AbstractParser(object):
    r"""Base class for file parsing objects.

    Subclasses should override `_parse_file`,
    calling the appropriate `handler` methods.

    Constructor Arguments:
    @param input_files: A list of target file paths.
    """
    filetype_info = None
    valid_roots = []

    def __init__(self, input_files):
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
        assert isinstance(paths, list)
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
                line = line.rstrip()
                self._parse_line(
                        line.decode(self.encoding, self.encoding_errors),
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
    
    def __exit__(self, t, v, tb):
        if v is None or isinstance(v, StopParsing):
            self.handler.after_file(self.fileobj, self.info)


class FiletypeInfo(object):
    r"""Instances of this class represent a filetype.
    Subclasses must define the attribute `filetype_ext`
    and override the method `info`.
    """
    @property
    def description(self):
        """A small string describing this filetype."""
        raise NotImplementedError

    @property
    def filetype_ext(self):
        """A string with the extension for this filetype.
        Also used as a filetype hint."""
        raise NotImplementedError

    def matches_filetype(self, filetype_hint):
        r"""Return whether the binary contents
        of `header` matches this filetype."""
        return self.filetype_ext == filetype_hint

    def operations(self):
        r"""Return an instance of FiletypeOperations."""
        raise NotImplementedError


class AbstractChecker(object):
    r"""Instances of this class can be used to peek at a file object
    and test whether its header matches a given filetype.
    
    Constructor Arguments:
    @param fileobj: The file object to be peeked.

    Attributes:
    @param filetype_info: Instance of FiletypeInfo
    that corresponds to the underlying filetype.
    """
    filetype_info = None

    def __init__(self, fileobj):
        self.fileobj = fileobj

    def matches_header(self, strict):
        r"""Return whether the header of `self.fileobj`
        could be interpreted as an instance of this filetype.

        If `strict` is True, perform stricter checks and
        only return True if the header is *known* to be in
        the format of this filetype (usually, one should use
        strict=True when detecting filetypes and strict=False
        when checking for bad matches."""
        raise NotImplementedError

    def check(self):
        r"""Check if `self.fileobj` belongs to this filetype
        and raise an exception if it does not."""
        if not self.matches_header(strict=False):
            raise Exception("Bad \"{}\" input".format(
                self.filetype_info.filetype_ext))



class AbstractPrinter(InputHandler):
    r"""Base implementation of a printer-style class.

    Constructor Arguments:
    @param root The type of the output file. This value
    must be in the subclass's `valid_roots`.
    @param output An IO-like object, such as sys.stdout
    or an instance of StringIO.
    @param flush_on_add If True, calls `self.flush()` automatically
    inside `self.add_string()`, before actually adding the element(s).
    """
    filetype_info = None
    valid_roots = []

    def __init__(self, root, output=None, flush_on_add=True):
        if root not in self.valid_roots:
            raise Exception("Bad printer: {}(root=\"{}\")"
                    .format(type(self).__name__, root))
        self._root = root
        self._output = output or sys.stdout
        self._flush_on_add = flush_on_add
        self._waiting_objects = []
        self._scope = 0

    def after_file(self, fileobj, info={}):
        r"""Finish processing and flush `fileobj`."""
        self.flush()

    def add_string(self, *objects):
        r"""Queue strings to be printed."""
        if self._flush_on_add:
            self.flush()
        for obj in objects:
            obj = obj.encode('utf-8')
            self._waiting_objects.append(obj)
        return self  # enable call chaining

    def last(self):
        r"""Return last (non-flushed) added object."""
        return self._waiting_objects[-1]

    def flush(self):
        r"""Eagerly print the current contents."""
        for obj in self._waiting_objects:
            self._write(obj)
        del self._waiting_objects[:]
        return self  # enable call chaining

    def _write(self, bytestring, end=""):
        r"""(Print bytestring in self._output)"""
        assert isinstance(bytestring, bytes)
        self._output.write(bytestring)



################################################################################


class XMLInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for mwetoolkit's XML."""
    description = "An XML in mwetoolkit format (dtd/mwetoolkit-*.dtd)"
    filetype_ext = "XML"

    def operations(self):
        return FiletypeOperations(XMLChecker, XMLParser, XMLPrinter)

class XMLChecker(AbstractChecker):
    r"""Checks whether input is in XML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(20)
        return header.startswith(b"<?xml") or header.startswith(b"<pattern")


class XMLParser(AbstractParser):
    r"""Instances of this class parse the mwetoolkit XML format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

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


class XMLPrinter(AbstractPrinter):
    """Instances can be used to print XML objects."""
    from .base.__common import XML_HEADER, XML_FOOTER
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def before_file(self, fileobj, info={}):
        self.add_string(self.XML_HEADER % {"root": self._root, "ns": ""} + "\n")
        super(XMLPrinter, self).before_file(fileobj, info)

    def after_file(self, fileobj, info={}):
        self.add_string(self.XML_FOOTER % {"root": self._root} + "\n")
        super(XMLPrinter, self).after_file(fileobj, info)

    def handle_entity(self, entity, info={}):
        self.add_string(entity.to_xml(), "\n")


##############################


class MosesTextInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for MosesText format."""
    description = "Moses textual format, with one sentence per line and <mwe> tags"
    filetype_ext = "MosesText"

    def operations(self):
        return FiletypeOperations(MosesTextChecker, None, MosesTextPrinter)


class MosesTextChecker(AbstractChecker):
    r"""Checks whether input is in MosesText format."""
    def matches_header(self, strict):
        return not strict


class MosesTextPrinter(AbstractPrinter):
    """Instances can be used to print HTML format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        self.add_string(sentence.to_surface(), "\n")


##############################


class WaCInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for ukWaC format."""
    description = "ukWac non-parsed format"
    filetype_ext = "WaC"

    def operations(self):
        return FiletypeOperations(WaCChecker, WaCParser, None)

class WaCChecker(AbstractChecker):
    r"""Checks whether input is in WaC format."""
    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"CURRENT URL")


class WaCParser(AbstractTxtParser):
    r"""Instances of this class parse the ukWaC format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(WaCParser,self).__init__(in_files, encoding)
        self.root = "corpus"
        self.line_terminators = ".!?"
        self.s_id = 1

    def _parse_line(self, line, handler, info={}):
        if not line.startswith("CURRENT URL"):
            import re
            eols = self.line_terminators
            for m in re.finditer(r"([^.!?]+ .|[^.!?]+$)", line):
                words = [Word(surface) for surface in m.group(1).split(" ")]
                handler.handle_sentence(Sentence(words, self.s_id))
                self.s_id += 1


##############################


class HTMLInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for HTML format."""
    description = "[[TODO REWRITE]] Pretty html"
    filetype_ext = "HTML"

    def operations(self):
        return FiletypeOperations(HTMLChecker, None, HTMLPrinter)


class HTMLChecker(AbstractChecker):
    r"""Checks whether input is in HTML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        return b"<html>" in header


class HTMLPrinter(AbstractPrinter):
    """Instances can be used to print HTML format."""
    valid_roots = ["corpus"]

    def before_file(self, fileobj, info={}):
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
        s = fileobj.name
        import datetime
        self.add_string(html_header % { "timestamp": datetime.datetime.now(),
              "corpusname": s[max(0,s.rfind("/")):], "filename": s})
        super(HTMLPrinter, self).before_file(fileobj, info)


    def after_file(self, fileobj, info={}):
        self.add_string("</body>\n</html>")
        super(HTMLPrinter, self).after_file(fileobj, info)


    def handle_sentence(self, sentence, info={}):
        self.add_string(sentence.to_html(), "\n")


##############################


class PlainCorpusInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for PlainCorpus format."""
    description = "One sentence per line, with multi_word_expressions"
    filetype_ext = "PlainCorpus"
    def operations(self):
        return FiletypeOperations(PlainCorpusChecker, PlainCorpusParser, PlainCorpusPrinter)


class PlainCorpusChecker(AbstractChecker):
    r"""Checks whether input is in PlainCorpus format."""
    def matches_header(self, strict):
        return not strict


class PlainCorpusParser(AbstractTxtParser):
    r"""Instances of this class parse the PlainCorpus format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCorpusParser, self).__init__(in_files, encoding)
        self.root = "corpus"

    def _parse_line(self, line, handler, info={}):
        sentence = Sentence([], info["linenum"])
        mwes = line.split(" ")  # each entry is an SWE/MWE
        for mwe in mwes:
            words = [Word(lemma) for lemma in mwe.split("_")]
            sentence.word_list.extend(words)
            if len(words) != 1:
                from .base.mweoccur import MWEOccurrence
                c = Candidate(info["linenum"], words)
                indexes = list(xrange(len(sentence)-len(words), len(sentence)))
                mweo = MWEOccurrence(sentence, c, indexes)
                sentence.mweoccurs.append(mweo)
        handler.handle_sentence(sentence)


class PlainCorpusPrinter(AbstractPrinter):
    """Instances can be used to print PlainCorpus format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        self.add_string(sentence.to_plaincorpus(), "\n")


##############################


class PlainCandidatesInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for PlainCandidates format."""
    description = "One multi_word_candidate per line"
    filetype_ext = "PlainCandidates"

    def operations(self):
        return FiletypeOperations(PlainCandidatesChecker, PlainCandidatesParser, PlainCandidatesPrinter)


class PlainCandidatesChecker(AbstractChecker):
    r"""Checks whether input is in PlainCandidates format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        return b" " not in header and b"_" in header


class PlainCandidatesParser(AbstractTxtParser):
    r"""Instances of this class parse the PlainCandidates format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["candidates"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCandidatesParser, self).__init__(in_files, encoding)
        self.root = "candidates"

    def _parse_line(self, line, handler, info={}):
        words = [Word(lemma) for lemma in line.split("_")]
        c = Candidate(info["linenum"], words)
        handler.handle_candidate(c)


class PlainCandidatesPrinter(AbstractPrinter):
    """Instances can be used to print PlainCandidates format."""
    valid_roots = ["candidates"]

    def handle_candidate(self, candidate, info={}):
        self.add_string("_".join(w.lemma_or_surface() \
                for w in candidate.word_list), "\n")


##############################


class MosesInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for Moses."""
    description = "Moses factored format (word=f1|f2|f3|f4|f5)"
    filetype_ext = "FactoredMoses"

    def operations(self):
        return FiletypeOperations(MosesChecker, MosesParser, MosesPrinter)


class MosesChecker(AbstractChecker):
    r"""Checks whether input is in FactoredMoses format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(512)
        first_words = header.split(b" ", 5)[:-1]
        return all(w.count(b"|") == 3 for w in first_words) \
                and (not strict or len(first_words) >= 3)


class MosesParser(AbstractTxtParser):
    r"""Instances of this class parse the FactoredMoses format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["corpus"]

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
                util.warn("Ignored token " + repr(w))
                util.warn(unicode(type(e)))
        handler.handle_sentence(s)


class MosesPrinter(AbstractPrinter):
    """Instances can be used to print Moses factored format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, obj):
        self.add_string(obj.to_moses(), "\n")


##############################


class ConllInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for CONLL."""
    description = "CONLL tab-separated 10-entries-per-word"
    filetype_ext = "CONLL"

    def operations(self):
        return FiletypeOperations(ConllChecker, ConllParser, None)


class ConllChecker(AbstractChecker):
    r"""Checks whether input is in CONLL format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        return len(header.split(b"\n", 1)[0].split()) \
                == len(ConllParser.entries)


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
    valid_roots = ["corpus"]
    entries = ["ID", "FORM", "LEMMA", "CPOSTAG", "POSTAG",
            "FEATS", "HEAD", "DEPREL", "PHREAD", "PDEPREL"]

    def __init__(self, in_files, encoding='utf-8'):
        super(ConllParser,self).__init__(in_files, encoding)
        self.name2index = {name:i for (i, name) in enumerate(self.entries)}
        self.root = "corpus"
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        data = line.split()
        if len(data) <= 1: return
        data = [(WILDCARD if d == "_" else d) for d in data]

        if len(data) < len(self.entries):
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


##############################


class BinaryIndexInfo(FiletypeInfo):
    r"""FiletypeInfo subclass for BinaryIndex files."""
    description = "The `.info` file for binary index created by index.py"
    filetype_ext = "BinaryIndex"

    def operations(self):
        # TODO import indexlib...  BinaryIndexPrinter
        return FiletypeOperations(BinaryIndexChecker, BinaryIndexParser, None)


class BinaryIndexChecker(AbstractChecker):
    r"""Checks whether input is in BinaryIndex format."""
    def check(self):
        if self.fileobj == sys.stdin:
            raise Exception("Cannot read BinaryIndex file from stdin!")
        if not self.fileobj.name.endswith(".info"):
            raise Exception("BinaryIndex file should have extension .info!")
        super(BinaryIndexChecker, self).check()

    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"corpus_size int")


class BinaryIndexParser(AbstractParser):
    valid_roots = ["corpus"]

    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "root": "corpus"}
        with ParsingContext(fileobj, handler, info):
            from .indexlib import Index
            assert fileobj.name.endswith(".info")
            index = Index(fileobj.name[:-len(".info")])
            index.load_main()
            for sentence in index.iterate_sentences():
                handler.handle_sentence(sentence)


##############################


# Instantiate FiletypeInfo singletons
INFOS = [XMLInfo(), ConllInfo(),
        PlainCorpusInfo(), WaCInfo(), BinaryIndexInfo(),
        MosesInfo(), PlainCandidatesInfo(), HTMLInfo(), MosesTextInfo()]

# Map filetype_hint -> filetype_info
HINT_TO_INFO = {}
# Map input_root -> list of filetype_infos
INPUT_INFOS = {}
# Map output_root -> list of filetype_infos
OUTPUT_INFOS = {}


for fti in INFOS:
    checker, parser, printer = fti.operations()
    HINT_TO_INFO[fti.filetype_ext] = fti
    checker.filetype_info = fti
    if parser is not None:
        parser.filetype_info = fti
        INPUT_INFOS.setdefault("ALL", []).append(fti)
        for root in parser.valid_roots:
            INPUT_INFOS.setdefault(root, []).append(fti)
    if printer is not None:
        printer.filetype_info = fti
        OUTPUT_INFOS.setdefault("ALL", []).append(fti)
        for root in printer.valid_roots:
            OUTPUT_INFOS.setdefault(root, []).append(fti)



class SmartParser(AbstractParser):
    r"""Class that detects the file format
    and delegates the work to the correct parser."""
    def __init__(self, input_files, filetype_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.filetype_hint = filetype_hint

    def parse(self, handler):
        for f in self._files:
            fti = self._detect_filetype(f, self.filetype_hint)
            checker_class, parser_class, _ = fti.operations()
            checker_class(f).check()
            p = parser_class([f])
            # Delegate the whole work to parser `p`.
            p.parse(handler)
        return handler


    def _detect_filetype(self, fileobj, filetype_hint=None):
        r"""Return a FiletypeInfo instance for given fileobj."""
        if filetype_hint in HINT_TO_INFO:
            return HINT_TO_INFO[filetype_hint]

        for fti in INFOS:
            checker_class = fti.operations().checker_class
            if checker_class(fileobj).matches_header(strict=True):
                return fti

        raise Exception("Unknown file format for " + fileobj.name)



################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
