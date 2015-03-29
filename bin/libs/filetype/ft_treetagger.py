#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_treetagger.py is part of mwetoolkit
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
"TreeTagger" filetype, which is a useful input corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import SentenceFactory
from ..base.word import Word
from .. import util


class TreeTaggerInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for TreeTagger format."""
    description = "3-field tab-separated format output by TreeTagger"
    filetype_ext = "TreeTagger"
  
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("|", "${pipe}"), ("#", "${hash}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("\t", "${tab}")]
                    
    entries = ["SURFACE", "POS", "LEMMA"]

    def operations(self):
        return common.FiletypeOperations(
                TreeTaggerChecker, TreeTaggerParser, TreeTaggerPrinter)

class TreeTaggerParser(common.AbstractTxtParser):
    r"""Parse file in TreeTagger TAB-separated format:
    One word per line, each word is in format "surface\tpos\tlemma".
    Optional sentence separators "</s>" may also constitute a word on a line.
    """
    valid_categories = ["corpus"]

    def __init__(self, in_files, encoding='utf-8', sent_split=None):
        super(TreeTaggerParser, self).__init__(in_files, encoding)
        self.sentence_factory = SentenceFactory()
        self.category = "corpus"
        self.words = []
        self.sent_split = sent_split

    def _parse_line(self, line, handler, info={}):
        sentence = None

        if not self.words:
            self.new_partial(self.finish_sentence, handler)

        if line == "</s>":
            self.flush_partial_callback()

        else:
            fields = line.split("\t")
            if len(fields) != 3:
                util.warn("Ignoring line {} (it has {} entries)" \
                        .format(info["linenum"], len(fields)))
                return

            surface, pos, lemma = fields
            word = Word(surface, lemma, pos)
            self.words.append(word)

            if pos == self.sent_split:
                self.flush_partial_callback()

    def finish_sentence(self, handler):
        r"""Finish building sentence and call handler."""
        s = self.sentence_factory.make(self.words)
        handler.handle_sentence(s, {})
        self.words = []

class TreeTaggerChecker(common.AbstractChecker):
    r"""Checks whether input is in TreeTagger format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(1024)
        for line in header.split(b"\n"):
            if line and not line.startswith(
                    bytes(self.filetype_info.comment_prefix)):
                return len(line.split(b"\t")) == len(self.filetype_info.entries)
        return not strict

class TreeTaggerPrinter(common.AbstractPrinter):

    valid_categories = ["corpus"]
    BETWEEN_SENTENCES = "</s>\n"
    
    def __init__(self, category, **kwargs):
        super(TreeTaggerPrinter, self).__init__(category, **kwargs)
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
                    "SURFACE": word.surface,
                    "LEMMA": word.lemma,
                    "POS": word.pos,        
                }
                entry = [data[entry_name] for entry_name in self.filetype_info.entries]
                entries.append(entry)

            line = zip(*entries)  # [[entries A for all], [entries B], ...]
            line = "\t".join(" ".join(entries_n) for entries_n in line)
            self.add_string(line, "\n")



