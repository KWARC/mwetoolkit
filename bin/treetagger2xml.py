#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# treetagger2xml.py is part of mwetoolkit
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
    This script transforms the output format of TreeTagger to the XML format of
    a corpus, as required by the mwetoolkit scripts. The script is language
    independent as it does not transform the information. You can chose either
    to use sentence splitting of the treetagger (default) or to keep the 
    original sentence splitting. In the latter case, you should add a sentence
    delimiter </s> at the end of each sentence before tagging the text. Only
    UTF-8 text is accepted.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import pdb

from util import read_options, treat_options_simplest, verbose
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <files.xml>

OPTIONS may be:

-o OR --original-split
	Keep the original sentence splitting of the input file. If this option is
	activated, you should add a sentence delimiter "</s>" at the end of each
	sentence before feeding the text into treetagger. This tag will be ignored
	by the tagger and then used to retrieve the original sentence splitting. 
	This otpion is particularly useful when dealing with parellel corpora in 
	which the sentence alignment cannot be messed up by the tagger.

-v OR --verbose
    Print messages that explain what is happening.

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""    
original_split = False

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
    global original_split
    for ( o, a ) in opts:
        if o in ( "-o", "--original-split" ) : 
            original_split = True
                
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################     

def escape( line ) :
	"""
		Replaces the escaped characters " & < > ` by the corresponding XML 
		entities.
		
		@param line The string containing characters that may be escaped
		
		@return The same string with the special XML characters replaced by the
		corresponding entitites
	"""
	result = line
	result = result.replace( "&", "&amp;" )
	result = result.replace( "\"", "&quot;" )
	result = result.replace( "<", "&lt;" )
	result = result.replace( ">", "&gt;" )
	result = result.replace( "'", "&apos;" )
	return result
	
################################################################################

def transform_format( in_file ) :
	"""
		Reads an input file and converts it into mwetoolkit corpus XML format, 
		printing the XML file to stdout.
		
		@param in_file The file in TreeTagger TAB-separated format, one word per
		line, each word is in format "surface\tpos\tlemma". Optional sentence
		separators "</s>" may also constitute a word on a line.
	"""
	global original_split
	#print original_split
	s_id = 0
	new_sent = True
	words = []
	for line in in_file.readlines() :
		line = line.strip()
		if new_sent and line != "</s>" :
			print "<s s_id=\"" + str( s_id ) + "\">",
			s_id = s_id + 1
			new_sent = False
			#pdb.set_trace()
		if line == "</s>" and original_split and words :
			print "</s>"
			new_sent = True
			words = []
		elif line != "</s>" :
			line = escape( line )
			(surface, pos, lemma) = line.split("\t")
			print "<w surface=\"" + surface + "\" pos=\"" + pos + "\" lemma=\"" + lemma + "\"/>",
			words.append( surface )
			if pos == "SENT" and not original_split and words :
				print "</s>"
				new_sent = True
				words = []	

################################################################################     
# MAIN SCRIPT

longopts = ["verbose", "original-split"]
arg = read_options( "vo", longopts, treat_options, -1, usage_string )
try :    
    print XML_HEADER % { "root": "corpus", "ns": "" }
    if len( arg ) == 0 :
        transform_format( sys.stdin )        
    else :
        for a in arg :
            input_file = open( a )
            transform_format( input_file )
            input_file.close()                
    print XML_FOOTER % { "root": "corpus" }
except IOError, err :
    print >> sys.stderr, err
