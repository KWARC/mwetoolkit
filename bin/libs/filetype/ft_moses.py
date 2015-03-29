#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_moses.py is part of mwetoolkit
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
"FactoredMoses" filetype, which is a useful input/output corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from ..base.__common import WILDCARD
from ..base.sentence import SentenceFactory
from ..base.word import Word
from .. import util


################################################################################

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
        self.sentence_factory = SentenceFactory()
        self.category = "corpus"

    def _parse_line(self, line, handler, info={}):
        s = self.sentence_factory.make()
        words = line.split(" ")
        for i, w in enumerate(words):
            token = [self.unescape(x) for x in w.split("|")]
            if len(token) == 4:
                surface, lemma, pos, syn = token
                s.append(Word(surface, lemma, pos, syn))
            else:
                util.warn("Ignoring bad token (line {}, token {})" \
                        .format(info["linenum"], i+1))
        handler.handle_sentence(s, info)


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


