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
from util import read_options, treat_options_simplest, verbose, strip_xml
from xmlhandler.classes.printer import Printer
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word
from xmlhandler.classes.__common import *
     

################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <files.xml>

OPTIONS:
%(common_options)s

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""    


################################################################################

def transform_format(printer, in_file):
    """Reads an input file and converts it into mwetoolkit corpus XML format, 
    printing the XML file to stdout.

    @param in_file The file, in CONLL format: one word per line,
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
    s_id = 0
    for line in in_file.readlines():
        data = line.strip().split()
        if len(data) <= 1: continue

        if data[0] == "1":
            printer.flush().add(Sentence([], s_id))
            s_id += 1

        data = [(WILDCARD if d == "_" else d) for d in data]
        surface, lemma, pos, syn = data[1], data[2], data[3], data[7]

        if data[4] != data[3]:
            maybe_warn(data[4], "POSTAG != CPOSTAG")
        maybe_warn(data[5], "FEATS")
        maybe_warn(data[8], "PHEAD")
        maybe_warn(data[9], "PDEPREL")

        if data[6] != WILDCARD:
            syn = syn + ":" + str(data[6])
        objectWord = Word(surface, lemma, pos, syn)
        printer.last().append_word(objectWord)


warned = set()
def maybe_warn(entry, entry_name):
    global warned
    if entry != WILDCARD and entry_name not in warned:
        print("WARNING: unable to handle CONLL entry: {}." \
                .format(entry_name), file=sys.stderr)
        warned.add(entry_name)


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

with Printer("corpus") as p:
    if len(args) == 0 :
        transform_format(p, sys.stdin)
    else:
        for fname in args:
            with open(fname) as f:
                transform_format(p, f)
