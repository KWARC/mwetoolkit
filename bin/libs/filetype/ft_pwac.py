#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_pwac.py is part of mwetoolkit
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
"pWaC" filetype, which is a useful input/output corpus textual format.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from .ft_conll import ConllParser, ConllPrinter
from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import Sentence
from ..base.word import Word
from .. import util

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
        # Check is always strict because tag <text id is mandatory
        return self.fileobj.peek(20).startswith(b"<text id")


class PWaCParser(ConllParser):
    r"""Instances of this class parse the pWaC format,
    calling the `handler` for each object that is parsed.
    """
    valid_categories = ["corpus"]

    def __init__(self, encoding='utf-8'):
        super(PWaCParser, self).__init__(encoding)

    def _parse_line(self, line, info={}):
        if line == "":
            pass  # Ignore empty lines
        elif line[0] == "<" and line[-1] == ">":
            # We just ignore <text id>, <s> and </s>
            # `new_partial` will be called when seeing ID "1"
            pass
        else:
            super(PWaCParser, self)._parse_line(line, info)


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

