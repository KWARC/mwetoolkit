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
import re
import sys

from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import Sentence
from ..base.word import Word
from .. import util

from . import _common as common


################################################################################


# Leak very common stuff into this namespace
from ._common import StopParsing, InputHandler, \
        ChainedInputHandler, AutomaticPrinterHandler, \
        Directive


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



################################################################################

from xml.etree import ElementTree


class XMLInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for mwetoolkit's XML."""
    description = "An XML in mwetoolkit format (dtd/mwetoolkit-*.dtd)"
    filetype_ext = "XML"

    # TODO use escape_pairs here... how?
    escape_pairs = []

    def operations(self):
        return common.FiletypeOperations(XMLChecker, XMLParser, XMLPrinter)


class XMLChecker(common.AbstractChecker):
    r"""Checks whether input is in XML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(20)
        return header.startswith(b"<?xml") or header.startswith(b"<pattern")


class XMLParser(common.AbstractParser):
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
                    with common.ParsingContext(fileobj, handler, info):
                        from .dictXMLHandler import DictXMLHandler
                        self._handle(inner_iterator, DictXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_entry=handler.handle_entity))
                elif elem.tag == "corpus":
                    # Delegate all the work to "corpus" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .corpusXMLHandler import CorpusXMLHandler
                        self._handle(inner_iterator, CorpusXMLHandler(
                                treat_sentence=handler.handle_sentence))
                elif elem.tag == "candidates":
                    # Delegate all the work to "candidates" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .candidatesXMLHandler import CandidatesXMLHandler
                        self._handle(inner_iterator, CandidatesXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_candidate=handler.handle_candidate))
                elif elem.tag == "patterns":
                    with common.ParsingContext(fileobj, handler, info):
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


class XMLPrinter(common.AbstractPrinter):
    """Instances can be used to print XML objects."""
    from ..base.__common import XML_HEADER, XML_FOOTER
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def before_file(self, fileobj, info={}):
        self.add_string(self.XML_HEADER % {"root": self._root, "ns": ""}, "\n")

    def after_file(self, fileobj, info={}):
        self.add_string(self.XML_FOOTER % {"root": self._root} + "\n")

    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_meta(self, meta_obj, info={}):
        self.add_string(meta_obj.to_xml(), "\n")

    def handle_entity(self, entity, info={}):
        self.add_string(entity.to_xml(), "\n")



##############################


class MosesTextInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for MosesText format."""
    description = "Moses textual format, with one sentence per line and <mwe> tags"
    filetype_ext = "MosesText"
  
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("|", "${pipe}"), ("#", "${hash}"),
                    (" ", "${space}"), ("\t", "${tab}")]

    def operations(self):
        return common.FiletypeOperations(MosesTextChecker, None, MosesPrinter)


class MosesTextChecker(common.AbstractChecker):
    r"""Checks whether input is in MosesText format."""
    def matches_header(self, strict):
        return not strict


class MosesTextPrinter(common.AbstractPrinter):
    """Instances can be used to print HTML format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        """Print a simple readable string where the surface forms of the 
        current sentence are concatenated and separated by a single space.
            
        @return A string with the surface form of the sentence,
        space-separated.
        """
        surface_list = [self.escape(w.surface) for w in sentence.word_list]
        mwetags_list = [[] for i in range(len(surface_list))]
        for mweoccur in sentence.mweoccurs:
            for i in mweoccur.indexes:
                mwetags_list[i].append( mweoccur.candidate.id_number)
        for (mwetag_i, mwetag) in enumerate(mwetags_list):
            if mwetag:
                mwetag = (unicode(index) for index in mwetag)
                surface_list[mwetag_i] = "<mwepart id=\"" + ",".join(mwetag) \
                              + "\" >" + surface_list[mwetag_i] + "</mwepart>"
        line = " ".join(surface_list)
        self.add_string(line, "\n")


##############################

class HTMLInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for HTML format."""
    description = "Pretty HTML for in-browser visualization"
    filetype_ext = "HTML"

    # TODO use python-based HTML escape
    escape_pairs = []

    def operations(self):
        return common.FiletypeOperations(HTMLChecker, None, HTMLPrinter)


class HTMLChecker(common.AbstractChecker):
    r"""Checks whether input is in HTML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        return b"<html>" in header


class HTMLPrinter(common.AbstractPrinter):
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


    def after_file(self, fileobj, info={}):
        self.add_string("</body>\n</html>")


    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_sentence(self, sentence, info={}):
        self.add_string(sentence.to_html(), "\n")


##############################

class PlainCorpusInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for PlainCorpus format."""
    description = "One sentence per line, with multi_word_expressions"
    filetype_ext = "PlainCorpus"
 
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), (" ", "${space}"), ("\t", "${tab}"),
            ("_", "${underscore}"), ("#", "${hash}")]

    def operations(self):
        return common.FiletypeOperations(PlainCorpusChecker,
                PlainCorpusParser, PlainCorpusPrinter)


class PlainCorpusChecker(common.AbstractChecker):
    r"""Checks whether input is in PlainCorpus format."""
    def matches_header(self, strict):
        return not strict


class PlainCorpusParser(common.AbstractTxtParser):
    r"""Instances of this class parse the PlainCorpus format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCorpusParser, self).__init__(in_files, encoding)
        self.root = "corpus"

    def _parse_line(self, line, handler, info={}):
        sentence = Sentence([], info["linenum"])
        mwes = line.split()  # each entry is an SWE/MWE
        for mwe in mwes:
            words = [Word(self.unescape(lemma)) for lemma in mwe.split("_")]
            sentence.word_list.extend(words)
            if len(words) != 1:
                from ..base.mweoccur import MWEOccurrence
                c = Candidate(info["linenum"], words)
                indexes = list(xrange(len(sentence)-len(words), len(sentence)))
                mweo = MWEOccurrence(sentence, c, indexes)
                sentence.mweoccurs.append(mweo)
        handler.handle_sentence(sentence)


class PlainCorpusPrinter(common.AbstractPrinter):
    """Instances can be used to print PlainCorpus format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        """Handle sentence as a PlainCorpus line, consisting of
        space-separated Word surfaces. MWEs are separated by "_"s.
        """
        surface_list = [self.escape(w.lemma_or_surface() or "<?>") \
                for w in sentence.word_list]

        from collections import defaultdict
        mwe_parts = defaultdict(set)  # index -> set(mwe)
        for mweoccur in sentence.mweoccurs:
            for i in mweoccur.indexes:
                mwe_parts[i].add(mweoccur)

        for i in xrange(len(surface_list)-1):
            if mwe_parts[i] & mwe_parts[i+1]:
                surface_list[i] += "_"
            else:
                surface_list[i] += " "
        line = "".join(surface_list)
        self.add_string(line, "\n")


##############################


class PlainCandidatesInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for PlainCandidates format."""
    description = "One multi_word_candidate per line"
    filetype_ext = "PlainCandidates"

    comment_prefix = "#"
    escape_pairs = PlainCorpusInfo.escape_pairs

    def operations(self):
        return common.FiletypeOperations(PlainCandidatesChecker,
                PlainCandidatesParser, PlainCandidatesPrinter)


class PlainCandidatesChecker(common.AbstractChecker):
    r"""Checks whether input is in PlainCandidates format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        return b" " not in header and b"_" in header


class PlainCandidatesParser(common.AbstractTxtParser):
    r"""Instances of this class parse the PlainCandidates format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["candidates"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCandidatesParser, self).__init__(in_files, encoding)
        self.root = "candidates"

    def _parse_line(self, line, handler, info={}):
        words = [Word(self.unescape(lemma)) for lemma in line.split("_")]
        c = Candidate(info["linenum"], words)
        handler.handle_candidate(c)


class PlainCandidatesPrinter(common.AbstractPrinter):
    """Instances can be used to print PlainCandidates format."""
    valid_roots = ["candidates"]

    def handle_candidate(self, candidate, info={}):
        self.add_string("_".join(self.escape(w.lemma_or_surface()) \
                for w in candidate.word_list), "\n")


##############################

class MosesInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for Moses."""
    description = "Moses factored format (word=f1|f2|f3|f4|f5)"
    filetype_ext = "FactoredMoses"

    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("|", "${pipe}"), ("#", "${hash}"),
                    (" ", "${space}"), ("\t", "${tab}")]

    def operations(self):
        return common.FiletypeOperations(MosesChecker,
                MosesParser, MosesPrinter)


class MosesChecker(common.AbstractChecker):
    r"""Checks whether input is in FactoredMoses format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(512)
        first_words = header.split(b" ", 5)[:-1]
        return all(w.count(b"|") == 3 for w in first_words) \
                and (not strict or len(first_words) >= 3)


class MosesParser(common.AbstractTxtParser):
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
                surface, lemma, pos, syntax = \
                        (self.unescape(x) for x in w.split("|"))
                s.append(Word(surface, lemma, pos, syntax))
            except Exception as e:
                util.warn("Ignored token " + repr(w))
                util.warn(unicode(type(e)))
        handler.handle_sentence(s)


class MosesPrinter(common.AbstractPrinter):
    """Instances can be used to print Moses factored format."""
    valid_roots = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        """Prints a simple Moses-factored string where words are separated by 
        a single space and each word part (surface, lemma, POS, syntax) is 
        separated from the next using a vertical bar "|".
        
        @return A string with the Moses factored form of the sentence
        """
        moses_list = [self.word_to_moses(w) for w in sentence.word_list]
        tagged_list = sentence.add_mwe_tags(moses_list)
        line = " ".join(tagged_list)
        self.add_string(line, "\n")

    def word_to_moses(self, word) :
        """Converts word to a string representation where word parts are
        separated from each other by "|" character, as in Moses' factored
        translation format.
            
        @return A string with Moses factored representation of a word.
        """
        args = (word.surface, word.lemma, word.pos, word.syn)
        return "|".join(self.escape(w) if w != WILDCARD else "" for w in args)



##############################


class ConllInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for CONLL."""
    description = "CONLL tab-separated 10-entries-per-word"
    filetype_ext = "CONLL"

    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("_", "${underscore}"),
            (" ", "${space}"), ("\t", "${tab}"), ("#", "${hash}")]

    def operations(self):
        return common.FiletypeOperations(ConllChecker, ConllParser, None)


class ConllParser(common.AbstractTxtParser):
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
        data = line.split("\t")
        if len(data) <= 1: return
        data = [(WILDCARD if d == "_" else d) for d in data]

        if len(data) < len(self.entries):
            util.warn("Ignoring line {} (only {} entries)" \
                    .format(info["linenum"], len(data)))
            return

        if len(data) > len(self.entries):
            util.warn("Ignoring extra entries in line {}" \
                    .format(info["linenum"]))

        def get(attribute):
            try:
                return self.unescape(data[self.name2index[attribute]])
            except KeyError:
                return WILDCARD

        if get("ID") == "1":
            self.new_partial(handler.handle_sentence,
                    Sentence([], self.s_id), info={})
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


class ConllChecker(common.AbstractChecker):
    r"""Checks whether input is in CONLL format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        for line in header.split(b"\n"):
            if line and not line.startswith(self.filetype_info.comment_prefix):
                return len(line.split("\t")) == len(ConllParser.entries)
        return strict


##############################


class PWaCInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for pWaC format."""
    description = "Wac parsed format"
    filetype_ext = "pWaC"

    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("_", "${underscore}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("\t", "${tab}"), ("#", "${hash}")]

    def operations(self):
        return common.FiletypeOperations(PWaCChecker, PWaCParser, None)


class PWaCChecker(common.AbstractChecker):
    r"""Checks whether input is in pWaC format."""
    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"<text id")


class PWaCParser(ConllParser):
    r"""Instances of this class parse the pWaC format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["corpus"]
    entries = ["FORM", "LEMMA", "CPOSTAG", "?", "?", "?"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PWaCParser, self).__init__(in_files, encoding)

    def _parse_line(self, line, handler, info={}):
        if line[0] == "<" and line[-1] == ">":
            if line == "<s>":
                self.new_partial(handler.handle_sentence,
                        Sentence([], self.s_id), info={})
                self.s_id += 1
        else:
            super(PWaCParser, self)._parse_line(line, handler, info)


##############################


class BinaryIndexInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for BinaryIndex files."""
    description = "The `.info` file for binary index created by index.py"
    filetype_ext = "BinaryIndex"

    def operations(self):
        # TODO import indexlib...  BinaryIndexPrinter
        return common.FiletypeOperations(BinaryIndexChecker, BinaryIndexParser, None)


class BinaryIndexChecker(common.AbstractChecker):
    r"""Checks whether input is in BinaryIndex format."""
    def check(self):
        if self.fileobj == sys.stdin:
            raise Exception("Cannot read BinaryIndex file from stdin!")
        if not self.fileobj.name.endswith(".info"):
            raise Exception("BinaryIndex file should have extension .info!")
        super(BinaryIndexChecker, self).check()

    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"corpus_size int")


class BinaryIndexParser(common.AbstractParser):
    valid_roots = ["corpus"]

    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "root": "corpus"}
        with common.ParsingContext(fileobj, handler, info):
            from .indexlib import Index
            assert fileobj.name.endswith(".info")
            index = Index(fileobj.name[:-len(".info")])
            index.load_main()
            for sentence in index.iterate_sentences():
                handler.handle_sentence(sentence)


###############################################################################


from . import arff

# Instantiate FiletypeInfo singletons
INFOS = [arff.INFO, XMLInfo(), ConllInfo(), PWaCInfo(),
        PlainCorpusInfo(), BinaryIndexInfo(),
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



class SmartParser(common.AbstractParser):
    r"""Class that detects input file formats
    and chains the work to the correct parser.
    """
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
        handler.flush()
        return handler


    def _detect_filetype(self, fileobj, filetype_hint=None):
        r"""Return a FiletypeInfo instance for given fileobj."""
        if filetype_hint in HINT_TO_INFO:
            return HINT_TO_INFO[filetype_hint]

        header = fileobj.peek(1024)
        for m in common.Directive.RE_PATTERN.finditer(header):
            if m.group(1) == "filetype":
                return HINT_TO_INFO[common.Directive(*m.groups()).value]

        for fti in INFOS:
            checker_class = fti.operations().checker_class
            if checker_class(fileobj).matches_header(strict=True):
                parser_class = fti.operations().parser_class
                if parser_class is None:
                    raise Exception("Parser not implemented for: " \
                            + unicode(fti.filetype_ext))
                return fti

        raise Exception("Unknown file format for: " + fileobj.name)



################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
