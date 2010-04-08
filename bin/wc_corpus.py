#!/usr/bin/python
"""
    This script simply gives some stats about a corpus file, such as number
    of words, etc. Output is written on stderr.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import xml.sax

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from util import read_options, treat_options_simplest, set_verbose, verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd). 
"""          
word_counter = 0
sentence_counter = 0
 
################################################################################     
       
def treat_sentence( sentence ) :
    """
        For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates four features that correspond to the Association
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global word_counter, sentence_counter
    
    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence %(id)d" % { "id":sentence.s_id } )            

    for word in sentence.word_list :
        word_counter += 1
    sentence_counter += 1

################################################################################     
# MAIN SCRIPT

arg = read_options( "v", ["verbose"], treat_options_simplest, 1, usage_string )

try :    
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler(CorpusXMLHandler( \
                             treat_sentence=treat_sentence)) 
    parser.parse( input_file )
    input_file.close() 
    print >> sys.stderr, str( word_counter ) + " words in " + arg[ 0 ]
    print >> sys.stderr, str( sentence_counter ) + " sentences in " + arg[ 0 ]    
    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid corpus file, " + \
                         "please validate it against the DTD " + \
                         "(mwttoolkit-corpus.dtd)"
