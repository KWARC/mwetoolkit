#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_plaincorpus.py is part of mwetoolkit
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
"PlainCorpus" filetype, which is a useful input/output corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from ..base.__common import WILDCARD
from ..base.candidate import CandidateFactory
from ..base.sentence import SentenceFactory
from ..base.word import Word
from .. import util


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
        self.candidate_factory = CandidateFactory()
        self.sentence_factory = SentenceFactory()
        self.category = "corpus"

    def _parse_line(self, line, handler, info={}):
        sentence = self.sentence_factory.make()
        mwes = line.split()  # each entry is an SWE/MWE
        for mwe in mwes:
            words = [Word(self.unescape(lemma)) for lemma in mwe.split("_")]
            sentence.word_list.extend(words)
            if len(words) != 1:
                from ..base.mweoccur import MWEOccurrence
                c = self.candidate_factory.make_uniq(words)
                indexes = list(xrange(len(sentence)-len(words), len(sentence)))
                mweo = MWEOccurrence(sentence, c, indexes)
                sentence.mweoccurs.append(mweo)
        handler.handle_sentence(sentence, info)


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


