#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
#
# conll2xml.py is part of mwetoolkit
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
This script transforms the CONLL file format to the XML corpus format of
required by the mwetoolkit scripts. The script is language independent
as it does not transform the information. Only UTF-8 text is accepted.

For more information, call the script with no parameter and read the
usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
from libs.util import read_options, treat_options_simplest, verbose, strip_xml
from libs.base.sentence import Sentence
from libs.base.word import Word
from libs.base.__common import *

from libs.printers import XMLPrinter
from libs.parser_wrappers import TxtParser
from libs.util import warn_once
     

################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <files.xml>

OPTIONS:
%(common_options)s

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""    


################################################################################

class ConllParser(TxtParser):
    """Parser that reads an input file and converts it into mwetoolkit
    corpus XML format, printing the XML file to stdout.

    @param in_files The input files, in CONLL format: one word per line,
    with each word represented by the following 10 entries.

    Per-word entries:
    0. ID      -- word index in sentence (starting at 1).
    1. FORM    -- equivalent to `surface` in XML.
    2. LEMMA   -- equivalent to `lemma` in XML.
    3. CPOSTAG -- equivalent to `pos` in XML.
    4. POSTAG  -- simplified version of `pos` in XML.
                  (XXX currently ignored).
    5. FEATS   -- (XXX currently ignored).
    6. HEAD    -- equivalent to second part of `syn` in XML
                  (that is, the parent of this word)
    7. DEPREL  -- equivalent to the first part of `syn` in XML
                  (that is, the relation between this word and HEAD).
    8. PHEAD   -- (XXX currently ignored).
    9. PDEPREL -- (XXX currently ignored).
    """
    ENTRIES = ["ID", "FORM", "LEMMA", "CPOSTAG", "POSTAG",
            "FEATS", "HEAD", "DEPREL", "PHREAD", "PDEPREL"]

    def __init__(self, in_files, printer, encoding='utf-8'):
        super(ConllParser,self).__init__(in_files, printer, encoding)
        self.name2index = {name:index for (index, name) \
                in enumerate(self.ENTRIES)}
        self.s_id = 0

    def treat_line(self, line):
        data = line.strip().split()
        if len(data) <= 1: return
        data = [(WILDCARD if d == "_" else d) for d in data]

        def get(attribute):
            try:
                return data[self.name2index[attribute]]
            except KeyError:
                return WILDCARD

        # TODO handle cases where len(data) < len(ENTRIES)
        if get("ID") == "1":
            self.printer.flush().add(Sentence([], self.s_id))
            self.s_id += 1

        surface, lemma = get("FORM"), get("LEMMA")
        pos, syn = get("CPOSTAG"), get("DEPREL")

        if get("POSTAG") != get("CPOSTAG"):
            self.maybe_warn(get("POSTAG"), "POSTAG != CPOSTAG")
        self.maybe_warn(get("FEATS"), "found FEATS")
        self.maybe_warn(get("PHEAD"), "found PHEAD")
        self.maybe_warn(get("PDEPREL"), "found PDEPREL")

        if get("HEAD") != WILDCARD:
            syn = syn + ":" + unicode(get("HEAD"))
        objectWord = Word(surface, lemma, pos, syn)
        self.printer.last().append(objectWord)


    def maybe_warn(self, entry, entry_name):
        if entry != WILDCARD:
            warn_once("WARNING: unable to handle CONLL " \
                    "entry: {}.".format(entry_name))


################################################################################     
       
def treat_options( opts, arg, n_arg, usage_string ) :
    """
    Callback function that handles the command line options of this script.
    
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    @param usage_string Instructions that appear if you run the program with
    the wrong parameters or options.
    """
    treat_options_simplest(opts, arg, n_arg, usage_string)
    
    for o, a in opts:
        sys.exit(1)


################################################################################     
# MAIN SCRIPT

longopts = []
args = read_options("", longopts, treat_options, -1, usage_string)
ConllParser(args, printer=XMLPrinter("corpus")).parse()
