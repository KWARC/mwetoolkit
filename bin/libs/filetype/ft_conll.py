#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_conll.py is part of mwetoolkit
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
This module provides classes to manipulate files that are encoded in the
"CONLL" filetype, which is a useful input/output corpus textual format.

You should use the methods in package `filetype` instead.
"""


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import Sentence
from ..base.word import Word
from .. import util

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
        self.ignoring_cur_sent = False
        self.id_index = self.name2index["ID"]
        self.category = "corpus"
        self.s_id = 0

    def _parse_line(self, line, handler, info={}):
        data = line.split("\t")
        if len(data) <= 1: return
        data = [d.split(" ") for d in data]  # split MWEs
        indexes = []
        for mwe_i, wid in enumerate(data[self.id_index]):
            word_data = [getitem(d, mwe_i, "_") for d in data]
            self._word_data = [(WILDCARD if d == "_" else d) for d in word_data]

            if len(self._word_data) != len(self.filetype_info.entries):
                util.warn("Expected {n_expected} entries, got {n_gotten}" \
                        " (at line {linenum})", linenum=info["linenum"],
                        n_expected=len(self.filetype_info.entries),
                        n_gotten=len(self._word_data))
                self.ignoring_cur_sent = True
            else:
                try:
                    wid = int(wid)
                except ValueError:
                    util.warn("Bad word ID at field {field_idx}: {wid!r} (at line {linenum})",
                            field_idx=self.id_index, wid=wid, linenum=info["linenum"])
                    self.ignoring_cur_sent = True
                else:
                    if wid == 1:
                        self.new_partial(handler.handle_sentence,
                                Sentence([], self.s_id), info=info)
                        self.ignoring_cur_sent = False
                        self.s_id += 1

                    if not self.ignoring_cur_sent:
                        indexes.append(wid - 1)
                        word = self._parse_word(handler, info)
                        self.partial_obj.append(word)

        if len(data[self.id_index]) != 1:
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



