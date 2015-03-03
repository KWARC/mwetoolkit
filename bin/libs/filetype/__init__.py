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
        ChainedInputHandler, Directive


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
    handler = FirstInputHandler(handler)
    SmartParser(input_files, filetype_hint).parse(handler)


def parse_entities(input_files, filetype_hint=None):
    r"""For each input file, detect its file format and parse it,
    returning a list of all parsed entities.
    
    @param input_files: a list of file objects
    whose contents should be parsed.
    @param filetype_hint: either None or a valid
    filetype_ext string.
    """
    handler = EntityCollectorHandler()
    parse(input_files, handler, filetype_hint)
    return handler.entities


def printer_class(filetype_ext):
    r"""Return a subclass of AbstractPrinter for given filetype extension.
    If you want a printer class that automatically handles all categories,
    create an instance of AutomaticPrinterHandler instead.
    """
    try:
        ret = HINT_TO_INFO[filetype_ext].operations().printer_class
    except KeyError:
        util.error("Unknown file extension: " + unicode(filetype_ext))
    if ret is None:
        util.error("Printer not implemented for: " + unicode(filetype_ext))
    return ret


################################################################################


class EntityCollectorHandler(InputHandler):
    r"""InputHandler that collects all entities
    in `self.entities`. Will fail with an out-of-memory
    error if used on huge inputs."""
    def __init__(self):
        self.entities = []

    def _fallback_entity(self, entity, info={}):
        self.entities.append(entity)

    def handle_comment(self, comment, info={}):
        pass  # Just ignore them


class FirstInputHandler(ChainedInputHandler):
    r"""First instance of InputHandler in a chain.
    This InputHandler does some general processing before
    passing the arguments over to the actual handlers.
    
    Tasks that are performed here:
    -- print_progress: warning the user about what
    has already been processed.
    -- handle_meta_if_absent: guarantee that `handle_meta`
    has been called when handling entities.
    """
    def __init__(self, chain):
        self.chain = chain
        self.kind = None
        self.count = 0
        self._meta_handled = False

    def _fallback_entity(self, entity, info={}):
        entity_kind = info["kind"]
        if self.kind is None:
            self.kind = entity_kind
        if self.kind != entity_kind:
            self.kind = "entity"
        self.count += 1

        self.print_progress(info)
        self.chain.handle(entity, info)
        
    def handle_candidate(self, candidate, info={}):
        self.handle_meta_if_absent()
        self.chain.handle_candidate(candidate,info)
    
    def handle_meta(self, meta, info={}):
        self._meta_handled = True
        self.chain.handle_meta(meta,info)

    def handle_meta_if_absent(self):
        if not self._meta_handled:
            from ..base.meta import Meta
            self.handle_meta(Meta([], [], []), info={})

    def print_progress(self, info):
        if self.count % 100 == 0:
            percent = float("NAN")
            if "progress" in info:
                a, b = info["progress"]
                if b != 0 :
                    percent = 100 * (a/b)                    
            util.verbose("~~> Processing {kind} number {n} ({percent:2.0f}%)"
                    .format(kind=self.kind, n=self.count, percent=percent))


class AutomaticPrinterHandler(ChainedInputHandler):
    r"""Utility subclass of ChainedInputHandler that automatically
    creates an appropriate printer by calling `make_printer` with
    information from the first input file.
    """
    def __init__(self, forced_filetype_ext):
        self.forced_filetype_ext = forced_filetype_ext

    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, self.forced_filetype_ext)
        self.chain.before_file(fileobj, info)



################################################################################


class MosesTextInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for MosesText format."""
    description = "Moses textual format, with one sentence per line and <mwe> tags"
    filetype_ext = "MosesText"
  
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("|", "${pipe}"), ("#", "${hash}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("\t", "${tab}"), ("\n", "${newline}")]

    def operations(self):
        return common.FiletypeOperations(MosesTextChecker, None, MosesTextPrinter)


class MosesTextChecker(common.AbstractChecker):
    r"""Checks whether input is in MosesText format."""
    def matches_header(self, strict):
        return not strict


class MosesTextPrinter(common.AbstractPrinter):
    """Instances can be used to print HTML format."""
    valid_categories = ["corpus"]

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
    valid_categories = ["corpus"]

    def before_file(self, fileobj, info={}):
        html_header="""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>MWETOOLKIT annotated corpus: {corpusname}</title>
    <!--<link rel="stylesheet" href="mwetk-corpus.css" type="text/css" media="screen"/>-->
    <style>
    h1{{margin:0}}
    p.notice{{font-family:Arial;font-size:10pt;margin:0}}
    hr{{margin:10px 0}}
    p.sent{{margin:2px 100px 2px 0;line-height:145%%;padding:4px 2px}}
    p.sent:hover{{background-color:#FFC}}
    p.sent span.sid{{border:1px solid #000;border-radius:2px;padding:1px 5px}}
    p.sent:hover span.sid{{background:#F22;color:#FFF}}
    p.sent:hover a.word{{border-color:#03A}}
    span.mwepart a.word{{border:2px solid #000}}
    span.mwe1 a.word{{background-color:#F66}}
    span.mwe2 a.word{{background-color:#9C0}}
    span.mwe3 a.word{{background-color:#69F}}
    span.mwe4 a.word{{background-color:#F90}}
    a.word{{position:relative;border:1px solid #CCF;border-radius:2px;padding:1px 2px;margin:auto 0;font-family:Verdana sans-serif;text-decoration:none;color:#000}}
    a.word:hover{{background-color:#03A;border-color:#000;color:#FFF}}
    a.word span.surface{{font-weight:700}}
    a.word span.wid{{font-size:70%%;position:relative;top:.3em;font-style:italic;padding-left:3px}}
    a.word span.lps{{color:#000;padding:2px 5px;top:1em;z-index:1;height:auto;opacity:0;position:absolute;visibility:hidden;background-color:#AAA;border:1px solid #000;border-radius:2px;box-shadow:#000 2px 2px 6px}}
    a.word:hover span.lps{{opacity:.95;visibility:visible}}
    a.word span.lps span.lemma{{font-style:italic;display:block}}
    a.word span.lps span.pos{{font-weight:700;display:block}}
    a.word span.lps span.syn{{font-weight:400;display:block;font-family:Arial}}
    </style>
</head>
<body>
<h1>Corpus: {corpusname}</h1>
<p class="notice">Generated automatically by the <a href="http://mwetoolkit.sf.net/" target="_blank">mwetoolkit</a> </p>
<p class="notice"> Timestamp: {timestamp}</p>
<p class="notice">Source: <tt>{filename}</tt></p>
<hr/>"""
        s = fileobj.name
        import os, datetime
        # XXX escape these parameters
        self.add_string(html_header.format(
                timestamp=datetime.datetime.now(),
                corpusname=s[s.rfind("/")+1:],
                filename=os.path.abspath(s)))


    def after_file(self, fileobj, info={}):
        self.add_string("</body>\n</html>")
        self.flush()

    def escape(self, text):
        return text  # XXX use a python native html escaper

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
            ("_", "${underscore}"), ("#", "${hash}"), ("\n", "${newline}")]

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
    valid_categories = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCorpusParser, self).__init__(in_files, encoding)
        self.sentence_count = 0
        self.category = "corpus"

    def _parse_line(self, line, handler, info={}):
        self.sentence_count += 1
        sentence = Sentence([], self.sentence_count)
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
    valid_categories = ["corpus"]

    def handle_sentence(self, sentence, info={}):
        """Handle sentence as a PlainCorpus line, consisting of
        space-separated Word surfaces. MWEs are separated by "_"s.
        """
        surface_list = [self.escape(w.surface
                if w.surface != WILDCARD else "<?>") \
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
        if not strict: return True
        header = self.fileobj.peek(1024)
        return b" " not in header and b"_" in header


class PlainCandidatesParser(common.AbstractTxtParser):
    r"""Instances of this class parse the PlainCandidates format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["candidates"]    

    def __init__(self, in_files, encoding='utf-8'):
        super(PlainCandidatesParser, self).__init__(in_files, encoding)
        self.candidate_count = 0
        self.category = "candidates"

    def _parse_line(self, line, handler, info={}):
        words = [Word(self.unescape(lemma)) for lemma in line.split("_")]
        self.candidate_count += 1
        c = Candidate(self.candidate_count, words)
        handler.handle_candidate(c)


class PlainCandidatesPrinter(common.AbstractPrinter):
    """Instances can be used to print PlainCandidates format."""
    valid_categories = ["candidates"]

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
                    (" ", "${space}"), ("\t", "${tab}"), ("\n", "${newline}")]

    def operations(self):
        return common.FiletypeOperations(MosesChecker,
                MosesParser, MosesPrinter)


class MosesChecker(common.AbstractChecker):
    r"""Checks whether input is in FactoredMoses format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(512)
        for line in header.split(b"\n"):
            if not line.startswith(bytes(self.filetype_info.comment_prefix)):
                return all(w.count(b"|") == 3 for w in line.split(b" ") if w)
        return not strict


class MosesParser(common.AbstractTxtParser):
    r"""Instances of this class parse the FactoredMoses format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(MosesParser,self).__init__(in_files, encoding)
        self.sentence_count = 0
        self.category = "corpus"

    def _parse_line(self, line, handler, info={}):
        self.sentence_count += 1
        s = Sentence([], self.sentence_count)
        words = line.split(" ")
        for i, w in enumerate(words):
            token = [self.unescape(x) for x in w.split("|")]
            if len(token) == 4:
                surface, lemma, pos, syn = token
                s.append(Word(surface, lemma, pos, syn))
            else:
                util.warn("Ignoring bad token (line {}, token {})" \
                        .format(info["linenum"], i+1))
        handler.handle_sentence(s)


class MosesPrinter(common.AbstractPrinter):
    """Instances can be used to print Moses factored format."""
    valid_categories = ["corpus"]

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
            (" ", "${space}"), ("#", "${hash}"),
            ("\t", "${tab}"), ("\n", "${newline}")]

    entries = ["ID", "FORM", "LEMMA", "CPOSTAG", "POSTAG",
            "FEATS", "HEAD", "DEPREL", "PHREAD", "PDEPREL"]

    def operations(self):
        return common.FiletypeOperations(ConllChecker, ConllParser,
                ConllPrinter)


class ConllChecker(common.AbstractChecker):
    r"""Checks whether input is in CONLL format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        for line in header.split(b"\n"):
            if line and not line.startswith(
                    bytes(self.filetype_info.comment_prefix)):
                return len(line.split(b"\t")) == len(self.filetype_info.entries)
        return not strict


def getitem(a_list, index, default=None):
    r"""Obvious implementation for a function
    that should already exist."""
    try:
        return a_list[index]
    except IndexError:
        return default


class ConllParser(common.AbstractTxtParser):
    r"""Instances of this class parse the CONLL-X format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(ConllParser,self).__init__(in_files, encoding)
        self.name2index = {name:i for (i, name) in
                enumerate(self.filetype_info.entries)}
        self.category = "corpus"
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        data = line.split("\t")
        if len(data) <= 1: return
        data = [d.split(" ") for d in data]  # split MWEs
        indexes = []
        for mwe_i in xrange(len(data[0])):
            word_data = [getitem(d, mwe_i, "_") for d in data]
            self._word_data = [(WILDCARD if d == "_" else d) for d in word_data]
            self._id = self.get("ID", None) or ("1" \
                    if self.partial_obj is None
                    else len(self.partial_obj.word_list))
            indexes.append(int(self._id) - 1)
            if len(self._word_data) < len(self.filetype_info.entries):
                util.warn("Ignoring line {} (only {} entries)" \
                        .format(info["linenum"], len(self._word_data)))
            else:
                word = self._parse_word(handler, info)
                self.partial_obj.append(word)

        if len(data[0]) != 1:
            from ..base.mweoccur import MWEOccurrence
            mwe_words = []  # XXX do we use surface or lemma?
            c = Candidate(info["linenum"], mwe_words)
            mweo = MWEOccurrence(self.partial_obj, c, indexes)
            self.partial_obj.mweoccurs.append(mweo)

    def get(self, attribute, default=WILDCARD):
        r"""Return CONLL data with given attribute
        (ID, FORM, LEMMA...) name."""
        try:
            return self.unescape(self._word_data[
                    self.name2index[attribute]])
        except KeyError:
            return default

    def _parse_word(self, handler, info={}):
        if len(self._word_data) > len(self.filetype_info.entries):
            util.warn("Ignoring extra entries in line {}" \
                    .format(info["linenum"]))

        if self._id == "1":
            self.new_partial(handler.handle_sentence,
                    Sentence([], self.s_id), info=info)
            self.s_id += 1

        surface, lemma = self.get("FORM"), self.get("LEMMA")
        pos, syn = self.get("CPOSTAG"), self.get("DEPREL")

        if self.get("POSTAG") != self.get("CPOSTAG"):
            self.maybe_warn(self.get("POSTAG"), "POSTAG != CPOSTAG")
        self.maybe_warn(self.get("FEATS"), "found FEATS")
        self.maybe_warn(self.get("PHEAD"), "found PHEAD")
        self.maybe_warn(self.get("PDEPREL"), "found PDEPREL")

        if self.get("HEAD") != WILDCARD:
            syn = syn + ":" + unicode(self.get("HEAD"))
        return Word(surface, lemma, pos, syn)


    def maybe_warn(self, entry, entry_name):
        if entry != WILDCARD:
            util.warn_once("WARNING: unable to handle {} entry: {}." \
                    .format(self.filetype_info.filetype_ext, entry_name))


class ConllPrinter(common.AbstractPrinter):
    BETWEEN_SENTENCES = "\n"
    valid_categories = ["corpus"]
    def __init__(self, category, **kwargs):
        super(ConllPrinter, self).__init__(category, **kwargs)
        self.count_sentences = 0


    def handle_sentence(self, sentence, info={}):
        if self.count_sentences != 0:
            self.add_string(self.BETWEEN_SENTENCES)
        self.count_sentences += 1

        for indexes in sentence.xwe_indexes():
            entries = []  # [[entries for word 1], [entries for 2], ...]
            for i in indexes:
                word = sentence[i]
                data = {
                    "ID": unicode(i + 1),
                    "FORM": word.surface,
                    "LEMMA": word.lemma,
                    "CPOSTAG": word.pos,
                    "POSTAG": word.pos,
                    "DEPREL": word.syn.split(":")[0],
                    "HEAD": word.syn.split(":")[1] if ":" in word.syn else "_",
                }
                entry = [self.handle_wildcard(data.get(entry_name, "_")) \
                        for entry_name in self.filetype_info.entries]
                entries.append(entry)

            line = zip(*entries)  # [[entries A for all], [entries B], ...]
            line = "\t".join(" ".join(entries_n) for entries_n in line)
            self.add_string(line, "\n")


    def handle_wildcard(self, argument):
        r"""Transform WILDCARD into CONLL "_"."""
        if argument == WILDCARD:
            return "_"
        return argument




##############################


class PWaCInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for pWaC format."""
    description = "Wac parsed format"
    filetype_ext = "pWaC"

    entries = ["FORM", "LEMMA", "CPOSTAG", "ID", "HEAD", "DEPREL"]

    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("_", "${underscore}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("#", "${hash}"), ("\t", "${tab}"), ("\n", "${newline}")]

    def operations(self):
        return common.FiletypeOperations(PWaCChecker, PWaCParser, PWaCPrinter)


class PWaCChecker(common.AbstractChecker):
    r"""Checks whether input is in pWaC format."""
    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"<text id")


class PWaCParser(ConllParser):
    r"""Instances of this class parse the pWaC format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["corpus"]

    def __init__(self, in_files, encoding='utf-8'):
        super(PWaCParser, self).__init__(in_files, encoding)

    def _parse_line(self, line, handler, info={}):
        if line == "":
            pass  # Ignore empty lines
        elif line[0] == "<" and line[-1] == ">":
            # We just ignore <text id>, <s> and </s>
            # `new_partial` will be called when seeing ID "1"
            pass
        else:
            super(PWaCParser, self)._parse_line(line, handler, info)


class PWaCPrinter(ConllPrinter):
    BETWEEN_SENTENCES = ""
    def before_file(self, fileobj, info={}):
        self.add_string('<text id="mwetoolkit">\n')

    def after_file(self, fileobj, info={}):
        self.add_string('</text>\n')

    def handle_sentence(self, sentence, info={}):
        self.add_string('<s>\n')
        super(PWaCPrinter, self).handle_sentence(sentence, info)
        self.add_string('</s>\n')


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
            util.error("Cannot read BinaryIndex file from stdin!")
        if not self.fileobj.name.endswith(".info"):
            util.error("BinaryIndex file should have extension .info!")
        super(BinaryIndexChecker, self).check()

    def matches_header(self, strict):
        return self.fileobj.peek(20).startswith(b"corpus_size int")


class BinaryIndexParser(common.AbstractParser):
    valid_categories = ["corpus"]

    def _parse_file(self, fileobj, handler):
        info = {"parser": self, "category": "corpus"}
        with common.ParsingContext(fileobj, handler, info):
            from .indexlib import Index
            assert fileobj.name.endswith(".info")
            index = Index(fileobj.name[:-len(".info")])
            index.load_main()
            for sentence in index.iterate_sentences():
                handler.handle_sentence(sentence)


###############################################################################


from . import ft_arff
from . import ft_xml
from . import ft_csv

# Instantiate FiletypeInfo singletons
INFOS = [ft_arff.INFO, ft_xml.INFO, ft_csv.INFO, ConllInfo(), PWaCInfo(),
        PlainCorpusInfo(), BinaryIndexInfo(),
        MosesInfo(), PlainCandidatesInfo(), HTMLInfo(), MosesTextInfo()]

# Map filetype_hint -> filetype_info
HINT_TO_INFO = {}
# Map input_category -> list of filetype_infos
INPUT_INFOS = {}
# Map output_category -> list of filetype_infos
OUTPUT_INFOS = {}


for fti in INFOS:
    checker, parser, printer = fti.operations()
    HINT_TO_INFO[fti.filetype_ext] = fti
    if checker is not None:
        checker.filetype_info = fti
    if parser is not None:
        parser.filetype_info = fti
        INPUT_INFOS.setdefault("ALL", []).append(fti)
        for category in parser.valid_categories:
            INPUT_INFOS.setdefault(category, []).append(fti)
    if printer is not None:
        printer.filetype_info = fti
        OUTPUT_INFOS.setdefault("ALL", []).append(fti)
        for category in printer.valid_categories:
            OUTPUT_INFOS.setdefault(category, []).append(fti)



class SmartParser(common.AbstractParser):
    r"""Class that detects input file formats
    and chains the work to the correct parser.
    """
    def __init__(self, input_files, filetype_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.filetype_hint = filetype_hint

    def parse(self, handler):    
        for sub_filelist in self.filelist.sublists():
            fti = self._detect_filetype(sub_filelist.only(), self.filetype_hint)
            checker_class, parser_class, _ = fti.operations()
            checker_class(sub_filelist.only()).check()
            p = parser_class(sub_filelist)
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
                    util.error("Parser not implemented for: " \
                            + unicode(fti.filetype_ext))
                return fti

        util.error("Unknown file format for: " + fileobj.name)



################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
