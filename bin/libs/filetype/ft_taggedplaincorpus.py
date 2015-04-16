#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_taggedplaincorpus.py is part of mwetoolkit
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
"TaggedPlainCorpus" filetype, which is a useful output corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import collections
import re

from . import _common as common
from ..base.candidate import CandidateFactory
from ..base.sentence import SentenceFactory
from ..base.mweoccur import MWEOccurrence
from ..base.word import Word
from .. import util


class TPCInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for TaggedPlainCorpus format."""
    description = "One sentence per line with <mwepart>tags</mwepart>"
    filetype_ext = "TaggedPlainCorpus"
  
    comment_prefix = "#"
    escape_pairs = [("$", "${dollar}"), ("#", "${hash}"),
                    ("<", "${lt}"), (">", "${gt}"), (" ", "${space}"),
                    ("\n", "${newline}")]

    def operations(self):
        return common.FiletypeOperations(TPCChecker, TPCParser, TPCPrinter)


class TPCChecker(common.AbstractChecker):
    r"""Checks whether input is in TaggedPlainCorpus format."""
    def matches_header(self, strict):
        return not strict or "<mwepart" in self.fileobj.peek(1024)


class TPCParser(common.AbstractTxtParser):
    r"""Instances of this class parse the TaggedPlainCorpus format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["corpus"]
    RE_ENTRY = re.compile(
            "(?P<word>[^<> ])" \
            "|(?P<complex><mwepart +id=\"(?P<ids>[0-9,])*\">" \
                    "(?P<c_word>[^<> ])</ *mwepart *>)")

    def __init__(self, encoding='utf-8'):
        super(TPCParser, self).__init__(encoding)
        self.candidate_factory = CandidateFactory()
        self.sentence_factory = SentenceFactory()
        self.category = "corpus"

    def _parse_line(self, line, info={}):
        sentence = self.sentence_factory.make()
        num2cand = collections.defaultdict(list)
        num2indexes = collections.defaultdict(list)

        for match in self.RE_ENTRY.finditer(line):
            word, complex, ids, c_word = match.groups()
            if word:
                sentence.append(Word(word))
            else:
                sentence.append(Word(c_word))
                for id in ids.split(","):
                    num2cand[int(id)].append(sentence[-1])
                    num2indexes[int(id)].append(len(sentence)-1)

        for num, words in num2cand.iteritems():
            c = self.candidate_factory.make(words, id_number=num)
            mweo = MWEOccurrence(sentence, c, num2indexes[num])
            sentence.mweoccurs.append(mweo)

        self.handler.handle_sentence(sentence, info)


class TPCPrinter(common.AbstractPrinter):
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
                              + "\">" + surface_list[mwetag_i] + "</mwepart>"
        line = " ".join(surface_list)
        self.add_string(line, "\n")
