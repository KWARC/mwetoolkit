#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
# 
# changepos.py is part of mwetoolkit
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
Converts the POS tags of the words from various kinds of formats to
simpler tags.  By default, convert from Penn Treebank tag format.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import xml.sax

from libs.util import read_options, treat_options_simplest, verbose, warn
from libs import filetype



################################################################################
# GLOBALS

usage_string = """Usage:

python {program} OPTIONS <corpus>

The <corpus> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force reading from given file type extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

--to <output-filetype-ext>
    Output extracted candidates in given filetype format.
    (By default, output filetype is the same as the input):
    {descriptions.output[corpus]}

-p OR --palavras
    Convert from Palavras tags instead of Penn Tree Bank tags.

-G or --genia
    Convert from Genia tags instead of Penn Tree Bank tags.

{common_options}
"""

sentence_counter = 0
# This table contains mainly exceptions that need special treatment
ptb_table = { "MD": "V",    # modal verb is a verb
               "IN": "P",    # Preposition in is a preposition
               "TO": "P",    # Preposition to is a preposition
               "RP": "P",
               "EX": "P",
               "CT": "DT", 
               "XT": "DT",
               "CD": "NUM",
               "POS": "PP",
               "FW": "FW",   # Foreign word stays foreign word
               "SYM": "PCT", # Special symbol is a punctuation sign
               "LS": "PCT",  # List symbol is a punctuation sign
               "``": "PCT",  # Quotes are a punctuation sign
               "''": "PCT",  # Quotes are a punctuation sign
               "SENT":"PCT", # Sentence delimiter is a punctuation sign
               "UH":"UH",  } # Interjection stays interjectio
simplify = None

output_filetype_ext = None
input_filetype_ext = None


################################################################################

class FilterHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)

    def handle_sentence(self, sentence, info={}):
        for w in sentence:
            w.pos = simplify(w.pos)
        self.chain.handle_sentence(sentence, info)


################################################################################

palavras_table = { "DET" : "DT",
                   "ADV" : "R",
                   "PRP" : "P",
                   "ADJ" : "A",
                   "PERS" : "PP",
                   "KC" : "CC",
                   "KS" : "CC",
                   "1P>" : "PP",
                   "SPEC" : "PP",
                   "3S>" : "DT",
                   "2S>" : "DT",
                   "1S>" : "DT",
                   "IN" : "P",
                   "EC" : "FW",
                   "PROP" : "N" }

def simplify_palavras( pos ) :
    """
        Receives as input a complex POS tag in the Penn Treebank format (used by 
        treetagger) and return a simplified version of the same tag.
        
        @param pos A string representing the POS tag in PTB format
        
        @return A string representing the simplified POS tag
    """
    # The "split" part is to avoid that multiple POS like NNS|JJ are not 
    # converted. We simply take the first POS, ignoring the second one.
    # This is useful when processing the GENIA corpus

    global palavras_table

    newpos = pos.split("|")[0]    
    if pos == "N" or pos == "V" or pos == "PCT" or pos == "NUM" :
        newpos = pos
    elif "-" in pos or ">" in pos :
        newpos = "UKN"
    else :
        try :
            newpos = palavras_table[ newpos ]
        except Exception :
            warn("part of speech " + str( newpos ) + " not converted.")
    return newpos                                  

################################################################################

def simplify_ptb( pos ) :
    """
        Receives as input a complex POS tag in the Penn Treebank format (used by 
        treetagger) and return a simplified version of the same tag.
        
        @param pos A string representing the POS tag in PTB format
        
        @return A string representing the simplified POS tag
    """
    global ptb_table
    # The "split" part is to avoid that multiple POS like NNS|JJ are not 
    # converted. We simply take the first POS, ignoring the second one.
    # This is useful when processing the GENIA corpus
    newpos = pos.split("|")[0]
    if newpos.startswith( "N" ) or newpos.startswith( "V" ) : # NOUNS / VERBS
        newpos = newpos[ 0 ]
    elif newpos.startswith( "J" ) : # ADJECTIVES
        newpos = "A"
    elif "RB" in newpos : # ADVERBS
        newpos = "R"
    elif "DT" in newpos : # DETERMINERS
        newpos = "DT"
    elif "CC" in newpos : # CONJUNCTIONS
        newpos = "CC"
    elif newpos.startswith( "PRP" ) or newpos.startswith( "PP" ) or newpos.startswith( "WP" ) : # PRONOUNS
        newpos = "PP"
    elif newpos in "\"()':?-/$.," : # ADVERBS
        newpos = "PCT"
    else :
        try :
            newpos = ptb_table[ newpos ]
        except Exception :
            warn("part of speech " + str( newpos ) + " not converted.")
    return newpos    

################################################################################

genia_table = { "NNPS": "N", "NNP": "N", "NNS": "N", "NN": "N", "NPS": "N", 
                "NP": "N", "NN|NNS": "N", "JJ|NN": "N", "VBG|NN": "N", 
                "NN|DT": "N", "NN|CD": "N", "NNS|FW": "N", "JJR": "A", 
                "JJS": "A", "JJ": "A", "JJ|VBG": "A", "JJ|RB": "A",
                "JJ|NNS": "A", "JJ|VBN": "A", "VBG|JJ": "A", "VBD": "V", 
                "VBG": "V", "VBN": "V", "VBP": "V", "VBZ": "V", "VVD": "V", 
                "VVG": "V", "VVN": "V", "VVP": "V", "VVZ": "V", "VHD": "V", 
                "VHG": "V", "VHN": "V", "VHP": "V", "VHZ": "V", "VV": "V", 
                "VB": "V", "VH": "V", "MD": "V", "VBP|VBZ": "V", "VBN|JJ": "V", 
                "VBD|VBN": "V", "RBR": "R", "RBS": "R", "WRB": "R", "RB": "R", 
                "IN": "P", "TO": "P", "RP": "P", "EX": "P", "IN|PRP$": "P", 
                "IN|CC": "P", "PDT": "DT", "WDT": "DT", "DT": "DT", "CT": "DT", 
                "XT": "DT", "PRP$": "PP", "PRP": "PP", "PP$": "PP", "PP": "PP", 
                "WP$": "PP", "WP": "PP", "POS": "PP", "CCS": "CC", "CC": "CC", 
                "FW": "FW", "SYM": "PCT", ".": "PCT", ",": "PCT", ":": "PCT", 
                "CD": "NUM", "\"": "PCT", "(": "PCT", ")": "PCT", "'": "PCT", 
                "?": "PCT", "-": "PCT", "/": "PCT", "LS": "PCT", "``": "PCT", 
                "''": "PCT" }

def simplify_genia(pos):
    return genia_table.get(pos, pos)


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global simplify
    global input_filetype_ext
    global output_filetype_ext

    treat_options_simplest( opts, arg, n_arg, usage_string )

    simplify = simplify_ptb

    for ( o, a ) in opts:
        if o in ("-p", "--palavras"):
            simplify = simplify_palavras
        elif o in ("-G", "--genia"):
            simplify = simplify_genia
        elif o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)
            

################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "palavras", "genia" ]
args = read_options( "xF:pg", longopts, treat_options, -1, usage_string )

printer = FilterHandler(output_filetype_ext)
filetype.parse(args, printer, input_filetype_ext)
