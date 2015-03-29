#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_plaincandidates.py is part of mwetoolkit
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
"PlainCandidates" filetype, that is, a list of _-separated words in raw text.

You should use the methods in package `filetype` instead.
"""


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from .ft_plaincorpus import PlainCorpusInfo
from ..base.__common import WILDCARD
from ..base.candidate import CandidateFactory
from ..base.word import Word
from .. import util

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
        self.candidate_factory = CandidateFactory()
        self.category = "candidates"

    def _parse_line(self, line, handler, info={}):
        words = [Word(self.unescape(lemma)) for lemma in line.split("_")]
        c = self.candidate_factory.make_uniq(words)
        handler.handle_candidate(c, info)


class PlainCandidatesPrinter(common.AbstractPrinter):
    """Instances can be used to print PlainCandidates format."""
    valid_categories = ["candidates"]

    def handle_candidate(self, candidate, info={}):
        self.add_string("_".join(self.escape(w.lemma_or_surface()) \
                for w in candidate.word_list), "\n")

