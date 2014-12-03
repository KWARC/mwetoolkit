#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# ft_xml.py is part of mwetoolkit
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
This module provides classes to manipulate files that are
encoded in mwetoolkit's "XML" filetype.

You should use the methods in package `filetype` instead.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import itertools
from xml.etree import ElementTree

from . import _common as common
from ..base.__common import XML_HEADER, XML_FOOTER


################################################################################


class XMLInfo(common.FiletypeInfo):
    r"""FiletypeInfo subclass for mwetoolkit's XML."""
    description = "An XML in mwetoolkit format (dtd/mwetoolkit-*.dtd)"
    filetype_ext = "XML"

    # TODO use escape_pairs here... how?
    escape_pairs = []

    def operations(self):
        return common.FiletypeOperations(XMLChecker, XMLParser, XMLPrinter)


INFO = XMLInfo()
r"""Singleton instance of XMLInfo."""


class XMLChecker(common.AbstractChecker):
    r"""Checks whether input is in XML format."""
    def matches_header(self, strict):
        header = self.fileobj.peek(20)
        return header.startswith(b"<?xml") or header.startswith(b"<pattern")


class XMLParser(common.AbstractParser):
    r"""Instances of this class parse the mwetoolkit XML format,
    calling the `handler` for each object that is parsed.
    """
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def _parse_file(self, fileobj, handler):
        # Here, fileobj is raw bytes, not unicode, because ElementTree
        # complains if we feed it a pre-decoded stream in python2k
        outer_iterator = ElementTree.iterparse(fileobj, ["start", "end"])

        for event, elem in outer_iterator:
            inner_iterator = itertools.chain(
                    [(event, elem)], outer_iterator)

            if event == "end":
                raise Exception("Unexpected end-tag!")

            elif event == "start":
                info = {"parser": self, "root": elem.tag}

                if elem.tag == "dict":
                    # Delegate all the work to "dict" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .dictXMLHandler import DictXMLHandler
                        self._handle(inner_iterator, DictXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_entry=handler.handle_candidate))
                elif elem.tag == "corpus":
                    # Delegate all the work to "corpus" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .corpusXMLHandler import CorpusXMLHandler
                        self._handle(inner_iterator, CorpusXMLHandler(
                                treat_sentence=handler.handle_sentence))
                elif elem.tag == "candidates":
                    # Delegate all the work to "candidates" handler
                    with common.ParsingContext(fileobj, handler, info):
                        from .candidatesXMLHandler import CandidatesXMLHandler
                        self._handle(inner_iterator, CandidatesXMLHandler(
                                treat_meta=handler.handle_meta,
                                treat_candidate=handler.handle_candidate))
                elif elem.tag == "patterns":
                    with common.ParsingContext(fileobj, handler, info):
                        # Delegate all the work to "patterns" handler
                        from .patternlib import iterparse_patterns
                        for pattern in iterparse_patterns(inner_iterator):
                            handler.handle_pattern(pattern)
                else:
                    raise Exception("Bad outer tag in XML filetype: " + repr(elem.tag))


    def _handle(self, iterator, xmlhandler):
        r"""Call startElement/endElement on handler for all sub-elements."""
        depth = 0
        for event, elem in iterator:
            if event == "start":
                xmlhandler.startElement(elem.tag, elem.attrib)
                depth += 1
            elif event == "end":
                xmlhandler.endElement(elem.tag)
                depth -= 1
                if depth == 0:
                    return
            elem.clear()


class XMLPrinter(common.AbstractPrinter):
    """Instances can be used to print XML objects."""
    valid_roots = ["dict", "corpus", "candidates", "patterns"]

    def before_file(self, fileobj, info={}):
        self.add_string(XML_HEADER % {"root": self._root, "ns": ""}, "\n")

    def after_file(self, fileobj, info={}):
        self.add_string(XML_FOOTER % {"root": self._root} + "\n")

    def handle_comment(self, comment, info={}):
        self.add_string("<!-- ", self.escape(comment), " -->\n")

    def handle_meta(self, meta_obj, info={}):
        self.add_string(meta_obj.to_xml(), "\n")

    def handle_entity(self, entity, info={}):
        self.add_string(entity.to_xml(), "\n")
