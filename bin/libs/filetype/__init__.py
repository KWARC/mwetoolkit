#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2015 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# filetype.py is part of mwetoolkit
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
This module provides classes and methods for filetype detection,
parsing and printing.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import io
import collections
import re
import sys

from ..base.__common import WILDCARD
from ..base.candidate import Candidate
from ..base.sentence import Sentence
from ..base.word import Word
from .. import util

from . import _common as common

################################################################################

# Leak very common stuff into this namespace
from ._common import StopParsing, InputHandler, \
        ChainedInputHandler, Directive

#############################


def parse(input_files, handler, filetype_hint=None):
    r"""For each input file, detect its file format,
    parse it and call the appropriate handler methods.
    
    You MUST call either this or `parse_with`.
    Don't EVER call `parser.parse` directly.

    @param input_files: a list of file objects
    whose contents should be parsed.
    @param handler: an InputHandler.
    @param filetype_hint: either None or a valid
    filetype_ext string.
    """
    parse_with(SmartParser(input_files, filetype_hint), handler)


def parse_with(parser, handler):
    r"""For each input file, detect its file format,
    parse it and call the appropriate handler methods.
    
    You MUST call this function when parsing a file.
    Don't EVER call `parser.parse` directly, or you will
    suffer HARSH CONSEQUENCES. You have been warned.
    
    @param parser: an instance of AbstractParser.
    @param handler: an instance of InputHandler.
    """
    try:
        handler = FirstInputHandler(handler)
        parser.parse(handler)
        handler.finish()
    except IOError as e:
        import errno
        if e.errno != errno.EPIPE:
            raise  # (EPIPE is just a closed stdout, so we ignore it)


#############################


def parse_entities(input_files, filetype_hint=None):
    r"""For each input file, detect its file format and parse it,
    returning a list of all parsed entities.
    
    @param input_files: a list of file objects
    whose contents should be parsed.
    @param filetype_hint: either None or a valid
    filetype_ext string.
    """
    handler = EntityCollectorHandler()
    parse(input_files, handler, filetype_hint)
    return handler.entities

#############################


def printer_class(filetype_ext):
    r"""Return a subclass of AbstractPrinter for given filetype extension.
    If you want a printer class that automatically handles all categories,
    create an instance of AutomaticPrinterHandler instead.
    """
    try:
        ret = HINT_TO_INFO[filetype_ext].operations().printer_class
    except KeyError:
        util.error("Unknown file extension: " + unicode(filetype_ext))
    if ret is None:
        util.error("Printer not implemented for: " + unicode(filetype_ext))
    return ret


################################################################################


class EntityCollectorHandler(InputHandler):
    r"""InputHandler that collects all entities
    in `self.entities`. Will fail with an out-of-memory
    error if used on huge inputs."""
    def __init__(self):
        self.entities = []

    def _fallback_entity(self, entity, info={}):
        self.entities.append(entity)

    def handle_comment(self, comment, info={}):
        pass  # Just ignore them

################################################################################


class FirstInputHandler(ChainedInputHandler):
    r"""First instance of InputHandler in a chain.
    This InputHandler does some general processing before
    passing the arguments over to the actual handlers.
    
    Tasks that are performed here:
    -- print_progress: warning the user about what
    has already been processed.
    -- handle_meta_if_absent: guarantee that `handle_meta`
    has been called when handling entities.
    """
    def __init__(self, chain):
        self.chain = chain
        self.kind = None
        self.count = 0
        self._meta_handled = False

    def _fallback_entity(self, entity, info={}):
        entity_kind = info["kind"]
        if self.kind is None:
            self.kind = entity_kind
        if self.kind != entity_kind:
            self.kind = "entity"
        self.count += 1

        self.print_progress(info)
        self.chain.handle(entity, info)
        
    def handle_candidate(self, candidate, info={}):
        self.handle_meta_if_absent()
        self.chain.handle_candidate(candidate,info)
    
    def handle_meta(self, meta, info={}):
        self._meta_handled = True
        self.chain.handle_meta(meta,info)

    def handle_meta_if_absent(self):
        if not self._meta_handled:
            from ..base.meta import Meta
            self.handle_meta(Meta([], [], []), info={})

    def print_progress(self, info):
        if self.count % 100 == 0:
            percent = float("NAN")
            if "progress" in info:
                a, b = info["progress"]
                if b != 0 :
                    percent = 100 * (a/b)                    
            util.verbose("~~> Processing {kind} number {n} ({percent:2.0f}%)"
                    .format(kind=self.kind, n=self.count, percent=percent))

################################################################################


class AutomaticPrinterHandler(ChainedInputHandler):
    r"""Utility subclass of ChainedInputHandler that automatically
    creates an appropriate printer by calling `make_printer` with
    information from the first input file.
    """
    def __init__(self, forced_filetype_ext):
        self.forced_filetype_ext = forced_filetype_ext

    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, self.forced_filetype_ext)
        self.chain.before_file(fileobj, info)



################################################################################


from . import ft_arff
from . import ft_xml
from . import ft_csv
from . import ft_moses
from . import ft_conll
from . import ft_pwac
from . import ft_binaryindex
from . import ft_plaincorpus
from . import ft_plaincandidates
from . import ft_html
from . import ft_mosestext
from . import ft_treetagger

# Instantiate FiletypeInfo singletons
INFOS = [ft_arff.INFO, ft_xml.INFO, ft_csv.INFO, ft_conll.ConllInfo(), 
         ft_pwac.PWaCInfo(), ft_plaincorpus.PlainCorpusInfo(), 
         ft_binaryindex.BinaryIndexInfo(), ft_moses.MosesInfo(), 
         ft_plaincandidates.PlainCandidatesInfo(), ft_html.HTMLInfo(), 
         ft_mosestext.MosesTextInfo(), ft_treetagger.TreeTaggerInfo()]

# Map filetype_hint -> filetype_info
HINT_TO_INFO = {}
# Map input_category -> list of filetype_infos
INPUT_INFOS = {}
# Map output_category -> list of filetype_infos
OUTPUT_INFOS = {}


for fti in INFOS:
    checker, parser, printer = fti.operations()
    HINT_TO_INFO[fti.filetype_ext] = fti
    if checker is not None:
        checker.filetype_info = fti
    if parser is not None:
        parser.filetype_info = fti
        INPUT_INFOS.setdefault("ALL", []).append(fti)
        for category in parser.valid_categories:
            INPUT_INFOS.setdefault(category, []).append(fti)
    if printer is not None:
        printer.filetype_info = fti
        OUTPUT_INFOS.setdefault("ALL", []).append(fti)
        for category in printer.valid_categories:
            OUTPUT_INFOS.setdefault(category, []).append(fti)

################################################################################


class SmartParser(common.AbstractParser):
    r"""Class that detects input file formats
    and chains the work to the correct parser.
    """
    def __init__(self, input_files, filetype_hint=None):
        super(SmartParser, self).__init__(input_files)
        self.filetype_hint = filetype_hint

    def parse(self, handler):
        for sub_filelist in self.filelist.sublists():
            fti = self._detect_filetype(sub_filelist.only(), self.filetype_hint)
            checker_class, parser_class, _ = fti.operations()
            checker_class(sub_filelist.only()).check()
            p = parser_class(sub_filelist)
            # Delegate the whole work to parser `p`.
            p.parse(handler)
        handler.flush()
        return handler


    def _detect_filetype(self, fileobj, filetype_hint=None):
        r"""Return a FiletypeInfo instance for given fileobj."""
        if filetype_hint in HINT_TO_INFO:
            return HINT_TO_INFO[filetype_hint]

        header = fileobj.peek(1024)
        for m in common.Directive.RE_PATTERN.finditer(header):
            if m.group(1) == "filetype":
                return HINT_TO_INFO[common.Directive(*m.groups()).value]

        for fti in INFOS:
            checker_class = fti.operations().checker_class
            if checker_class(fileobj).matches_header(strict=True):
                parser_class = fti.operations().parser_class
                if parser_class is None:
                    util.error("Parser not implemented for: " \
                            + unicode(fti.filetype_ext))
                return fti

        util.error("Unknown file format for: " + fileobj.name)

################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()  
