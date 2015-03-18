#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# content_words.py is part of mwetoolkit
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
    This script filters the input and leaves only content words using the 
    tagset of pUKWaC.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import re

from libs.util import read_options, treat_options_simplest, error
from libs.base.sentence import Sentence
from libs.base.__common import WILDCARD
from libs import filetype


     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <input-file>

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps output in same format as input):
    {descriptions.output[ALL]}

--append-pos-tag <mode>
    Append POS-tags to output. The <mode> is one of the following:
    * "coarse": only append the first letter of POS tag
    * "fine": append the whole POS tag, regardless of its level of detail
    
--clean-special
    Remove words whose lemma contains special characters, keeping
    only those that respect the regexp [a-zA-Z]+(-_ [a-zA-Z]+)*

{common_options}
"""

input_filetype_ext = None
output_filetype_ext = None
clean_special = False
append_pos_tag = None


################################################################################

class ConverterHandler(filetype.ChainedInputHandler):

    def __init__(self, append_pos_tag=None, clean_special=False):
        super(filetype.ChainedInputHandler, self)
        self.append_pos_tag = append_pos_tag
        self.clean_special = clean_special
        
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)

    def handle_sentence(self, sentence, info={}):
        new_indexes = []
        for inds in sentence.xwe_indexes():
            if len(inds) != 1:
                new_indexes.extend(inds)
            else:
                if self.is_good(sentence[inds[0]]):
                    new_indexes.extend(inds)
        sentence = sentence.sub_sentence(new_indexes)
        sentence.word_list = [self.change(w) for w in sentence]
        self.chain.handle_sentence(sentence, info)

    NOSPECIAL = "[a-zA-Z]+(-_ [a-zA-Z]+)*"

    PLACEHOLD = set(["CD", "NP", "NPS"])

    GOOD = PLACEHOLD | set([
            "NN", "NNS",
            "JJ", "JJR", "JJS",
            "VV", "VVD", "VVG", "VVN", "VVP", "VVZ",
            "RB", "RBR", "RBS", "RP"])

    def is_good(self, word):
        r"""Return whether `word` matches one of the POS-tags.
            ------------------------------------------------
            NN      noun, singular or mass           table
            NNS     noun plural                      tables
            JJ      adjective                        green
            JJR     adjective, comparative           greener
            JJS     adjective, superlative           greenest
            VV      verb, base form                  take
            VVD     verb, past tense                 took
            VVG     verb, gerund/present participle  taking
            VVN     verb, past participle            taken
            VVP     verb, sing. present, non-3d      take
            VVZ     verb, 3rd person sing. present   takes
            RB      adverb                           however, usually, naturally, here, good
            RBR     adverb, comparative              better
            RBS     adverb, superlative              best
            RP      particle                         give up
            ------------------------------------------------
        """
        return word.pos in self.GOOD and \
                (not self.clean_special or re.match(self.NOSPECIAL, word.lemma))


    def change(self, word):
        r"""Convert lemma/surfaces to placeholder.
            ---------------------------------------
            CD     numbers                  42
            NP     proper noun, singular    John
            NPS    proper noun, plural      Vikings
            ---------------------------------------
        """
        if word.pos in self.PLACEHOLD:
            word.lemma = word.surface = "${placehold_" + word.pos + "}"
        if word.pos != WILDCARD:
            pos_to_append = ""
            if self.append_pos_tag == "coarse":
                pos_to_append = "/" + word.pos[0]
            elif self.append_pos_tag == "fine":
                pos_to_append = "/" + word.pos
            word.lemma = word.surface = \
                    word.lemma_or_surface() + pos_to_append
        return word


def treat_options(opts, arg, n_arg, usage_string):
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global input_filetype_ext
    global output_filetype_ext
    global append_pos_tag
    global clean_special

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o == ("--from"):
            input_filetype_ext = a
        elif o == ("--to"):
            output_filetype_ext = a
        elif o == "--append-pos-tag":
        	if a in ("coarse","fine"):
	            append_pos_tag = a
	        else:
	        	error("Expected \"coarse\" or \"fine\", found " + a)
        elif o == "--clean-special":
        	clean_special = True
        else:
            raise Exception("Bad arg: " + o)


################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "append-pos-tag=", "clean-special"]
args = read_options("", longopts, treat_options, -1, usage_string)
handler = ConverterHandler(append_pos_tag, clean_special)
filetype.parse(args, handler, input_filetype_ext)
