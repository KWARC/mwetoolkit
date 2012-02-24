#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
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
   Simplifies the POS tags of the words from various kinds of formats to simple tags


"""

import sys
import pdb
import xml.sax

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest, verbose

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s OPTIONS <corpus.xml>

OPTIONS may be:

-x OR --text
    Instead of traditional corpus in XML, takes as input a textual list with 
    one sentence per line, words separated by spaces and POS appended to words 
    separated by a special character, defined by option --fs below (default 
    slash "/")
    
-F OR --fs
    Defines a field separator for the word and the POS. Can only be used in 
    conjunction with option --text above. The default field separator is a 
    simple slash "/". CAREFUL: This special character must be escaped in the 
    corpus!

-p OR --palavras
    Convert from Palavras tags instead of Penn Tree Bank tags.

-G or --genia
    Convert from Genia tags instead of Penn Tree Bank tags.

%(common_options)s

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd).
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
text_input = False
field_sep = "/"
simplify = None

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' )

################################################################################

def treat_entity( entity ) :
    """
        For each sentence in the corpus, simplify the POS tags using simple
        heuristics.

        @param sentence A `Sentence` that is being read from the XML file.
    """
    global sentence_counter
    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence number %(n)d" % { "n":sentence_counter } )
    for w in entity :
        w.pos = simplify( w.pos )        
    print entity.to_xml().encode( 'utf-8' )
    sentence_counter += 1

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
            print >> sys.stderr, "WARNING: part of speech " + str( newpos ) + \
                              " not converted."
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
            print >> sys.stderr, "WARNING: part of speech " + str( newpos ) + \
                              " not converted."
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

def treat_text( stream ):
    """
        Treats a text file by simplifying the POS of the lines. Useful for 
        treating a text file containing one sentence per line.
        
        @param stream File or stdin from which the lines (sentences) are read.
    """
    global field_sep
    for line in stream.readlines() :
        sentence = line.strip()
        newsent = ""
        #pdb.set_trace()
        for word in sentence.split( " " ) :
            newword = ""
            partlist = word.split( field_sep )
            for partindex in range( len( partlist ) ) :
                part = partlist[ partindex ]
                if partindex == len( partlist ) - 1 :
                    part = simplify( part )
                newword = newword + part + field_sep
            newword = newword[ : len(newword)-len(field_sep) ]                
            newsent = newsent + newword + " "
        print newsent.strip()

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global text_input
    global field_sep
    global simplify

    simplify = simplify_ptb

    for ( o, a ) in opts:
        if o in ("-x", "--text" ) : 
            text_input = True
        elif o in ("-p", "--palavras" ) : 
            simplify = simplify_palavras
        elif o in ("-G", "--genia"):
            simplify = simplify_genia
        elif o in ("-F", "--fs" ) : 
            field_sep = a               
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################
# MAIN SCRIPT

longopts = ["text", "fs=", "palavras", "genia" ]
arg = read_options( "xF:pg", longopts, treat_options, -1, usage_string )

parser = xml.sax.make_parser()
handler = GenericXMLHandler( treat_meta=treat_meta,
                             treat_entity=treat_entity,
                             gen_xml=True )
parser.setContentHandler( handler )
if len( arg ) == 0 :
    if text_input :
        treat_text( sys.stdin )
    else :
        parser.parse( sys.stdin )
        print handler.footer
else :
    for a in arg :
        input_file = open( a )
        if text_input :
            treat_text( input_file )
        else :
            parser.parse( input_file )
            footer = handler.footer
            handler.gen_xml = False
        input_file.close()
        entity_counter = 0
    if not text_input :    
        print footer
