#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# moses2xml.py is part of mwetoolkit
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
    This script transforms the Moses factored format to the XML format of
    a corpus, as required by the mwetoolkit scripts. The script is language
    independent as it does not transform the information. Only UTF-8 text is 
    accepted.
    
    For more information, call the script with -h parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.util import read_options, treat_options_simplest, warn
from libs.base.sentence import Sentence
from libs.base.word import Word
from libs.base.__common import XML_HEADER, XML_FOOTER
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <files.moses>

OPTIONS may be:

%(common_options)s

    The <files.moses> file(s) must be valid Moses-formatted files.
"""          
s_id = 0
################################################################################

def transform_format( in_file ) :
    """
        Reads a Moses file and converts it into mwetoolkit corpus XML format, 
        printing the XML file to stdout.
        
        @param in_file The file in Moses format, one sentence per line, words
        separated by spaces, each word is in format "surface|lemma|pos|syntax". 
    """
    global s_id
    for line in in_file.readlines() :
        s_id = s_id + 1   
        s = Sentence( [], s_id )     
        words = line.strip().split(" ")
        for w in words :
            try :
                surface, lemma, pos, syntax = w.split("|")
                s.append( Word( surface, lemma, pos, syntax ) )
            except Exception as e:
                warn( str(type(e) ) )
                warn( "Ignored token " + w )
        print(s.to_xml())
    

################################################################################     
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, -1, usage_string )

print(XML_HEADER % { "root": "corpus", "ns": "" })
if len( arg ) == 0 :
    transform_format( sys.stdin )        
else :
    for a in arg :
        input_file = open( a )
        transform_format( input_file )
        input_file.close()                
print(XML_FOOTER % { "root": "corpus" })
