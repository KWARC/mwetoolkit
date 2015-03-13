#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_mosestext.py is part of mwetoolkit
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
"MosesText" filetype, which is a useful output corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common

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

