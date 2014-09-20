#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# simplifytags.py is part of mwetoolkit
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
   Simplifies the POS tags of the words from PDB format (used e.g. in Genia) to
   a simple version containing only N, A, R, V, etc...
"""

import sys
import xml.sax

from bin.libs.xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest


################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <files.xml>

-v OR --verbose
    Print messages that explain what is happening.
    
    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
conv_table = { "NNPS": "N", "NNP": "N", "NNS": "N", "NN": "N", "NPS": "N", 
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
entity_counter = 0               

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
    global conv_table
    for w in entity :
        w.pos = conv_table.get(  w.pos, w.pos )
    print entity.to_xml().encode( 'utf-8' )
    
################################################################################  
# MAIN SCRIPT

longopts = [ "verbose" ]
arg = read_options( "v", longopts, treat_options_simplest, 1, usage_string )

parser = xml.sax.make_parser()
handler = GenericXMLHandler( treat_meta=treat_meta,
                             treat_entity=treat_entity,
                             gen_xml=True )
parser.setContentHandler( handler )
if len( arg ) == 0 :
    parser.parse( sys.stdin )
    print handler.footer
else :
    for a in arg :
        input_file = open( a )
        parser.parse( input_file )
        footer = handler.footer
        handler.gen_xml = False
        input_file.close()
        entity_counter = 0
    print footer
