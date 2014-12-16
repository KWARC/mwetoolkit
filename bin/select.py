#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# select.py is part of mwetoolkit
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
This script selects specific information from a corpus and
discards the rest.
    
For more information, call the script with no parameter and read the
usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

from libs.base.__common import WILDCARD
from libs.util import read_options, treat_options_simplest
from libs import filetype

     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <corpus>

The <corpus> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force reading from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--to <output-filetype-ext>
    Write output in given filetype extension.
    (By default, keeps original input format):
    {descriptions.output[corpus]}

--keep-empty-words
    Keep words without lemma/surface in output.

--word-lemmas
    Keep word lemmas (or surface if no lemma is available).

--word-lemmas-matching <regex>
    Keep only lemmas matching given regex (default: keep none).

--word-surfaces-matching <regex>
    Keep only surface forms matching given regex (default: keep none).

--word-pos-matching <regex>
    Keep only POS-tags matching given regex (default: keep none).

--word-syn-matching <regex>
    Keep only syntax information matching given regex (default: keep none).

{common_options}
"""

input_filetype_ext = None
output_filetype_ext = None

keep_empty_words = False
take_lemma = False
regex_word_lemma = "(?!)"
regex_word_surface = "(?!)"
regex_word_pos = "(?!)"
regex_word_syn = "(?!)"


################################################################################


class SelectorPrinterHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)

    def handle_sentence(self, sentence, info={}):
        for word in sentence.word_list:
            if not re.search(regex_word_surface, word.surface):
                word.surface = WILDCARD
            if take_lemma or word.surface == WILDCARD:
                word.surface = word.lemma

            if not re.search(regex_word_lemma, word.lemma):
                word.lemma = WILDCARD

            if not re.search(regex_word_pos, word.pos):
                word.pos = WILDCARD
            if not re.search(regex_word_syn, word.syn):
                word.syn = WILDCARD

        sentence.word_list = [word for word in sentence.word_list
                if not (word.lemma == word.surface == WILDCARD)]
        self.chain.handle_sentence(sentence, info)


def treat_options(opts, arg, n_arg, usage_string):
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global input_filetype_ext
    global output_filetype_ext
    global regex_word_lemma
    global regex_word_surface
    global regex_word_pos
    global regex_word_syn
    global take_lemma

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o in ("--from"):
            input_filetype_ext = a
        elif o in ("--to"):
            output_filetype_ext = a
        elif o == "--keep-empty-words":
            keep_empty_words = True
        elif o == "--word-lemmas":
            take_lemma = True
        elif o == "--word-lemmas-matching":
            regex_word_lemma = a
        elif o == "--word-surfaces-matching":
            regex_word_surface = a
        elif o == "--word-pos-matching":
            regex_word_pos = a
        elif o == "--word-syn-matching":
            regex_word_syn = a
        else:
            raise Exception("Bad arg")



################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "keep-empty-words", "word-lemmas",
        "word-lemmas-matching=", "word-surfaces-matching=",
        "word-pos-matching=", "word-syn-matching="]
args = read_options("", longopts, treat_options, -1, usage_string)
printer = SelectorPrinterHandler()
filetype.parse(args, printer, input_filetype_ext)
