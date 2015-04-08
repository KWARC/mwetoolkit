#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_binaryindex.py is part of mwetoolkit
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
This module provides classes to manipulate binary index files. It is actually
a wrapper that uses indexlib.

You should use the methods in package `filetype` instead.
"""



from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from . import _common as common
from . import util
import sys

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
        if self.fileobj.name == "<stdin>":
            util.error("Cannot read BinaryIndex file from stdin!")
        if not self.fileobj.name.endswith(".info"):
            util.error("BinaryIndex file should have extension .info!")
        super(BinaryIndexChecker, self).check()

    def matches_header(self, strict):
        # Check is always strict because the absence of header means file is wrong
        return self.fileobj.peek(20).startswith(b"corpus_size int")


class BinaryIndexParser(common.AbstractParser):
    valid_categories = ["corpus"]

    def _parse_file(self, fileobj):
        info = {"parser": self, "category": "corpus"}
        with common.ParsingContext(fileobj, self.handler, info):
            from .indexlib import Index
            assert fileobj.name.endswith(".info")
            index = Index(fileobj.name[:-len(".info")])
            index.load_main()
            for sentence, progress in index.iterate_sentences_and_progress():
                info["progress"] = progress
                self.handler.handle_sentence(sentence, info)
