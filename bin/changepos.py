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
   Simplifies the POS tags of the words from Penn Treebank format to simple tags
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

-v OR --verbose
    Print friendly messages that explain what is happening.

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd).
"""
sentence_counter = 0
# This table contains mainly exceptions that need special treatment
conv_table = { "MD": "V",    # modal verb is a verb
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
palavras = False

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

def simplify( pos ) :
    """
        Receives as input a complex POS tag and returns a simplified version.
        
        @param pos A string representing the POS tag in some format
        
        @return A string representing the simplified POS tag
    """
    global palavras
    if palavras :
        return simplify_palavras( pos )
    else :
        return simplify_ptb( pos )   

################################################################################

def simplify_palavras( pos ) :
    """
        Receives as input a complex POS tag in the Penn Treebank format (used by 
        treetagger) and return a simplified version of the same tag.
        
        @param pos A string representing the POS tag in PTB format
        
        @return A string representing the simplified POS tag
    """
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
    # The "split" part is to avoid that multiple POS like NNS|JJ are not 
    # converted. We simply take the first POS, ignoring the second one.
    # This is useful when processing the GENIA corpus
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
    global conv_table
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
            newpos = conv_table[ newpos ]
        except Exception :
            print >> sys.stderr, "WARNING: part of speech " + str( newpos ) + \
                              " not converted."
    return newpos    

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
    global palavras
    for ( o, a ) in opts:
        if o in ("-x", "--text" ) : 
            text_input = True
        elif o in ("-p", "--palavras" ) : 
            palavras = True
        elif o in ("-F", "--fs" ) : 
            field_sep = a               
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################
# MAIN SCRIPT

longopts = ["verbose", "text", "fs=", "palavras" ]
arg = read_options( "vxF:p", longopts, treat_options, -1, usage_string )
try :
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
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"

