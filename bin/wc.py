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

from xmlhandler.dictXMLHandler import DictXMLHandler
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import read_options, treat_options_simplest, set_verbose, verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <corpus.xml> file must be valid XML (mwetoolkit-corpus.dtd). 
"""    
char_counter = 0
word_counter = 0
ngram_counter = 0
 
################################################################################     
       
def treat_ngram( ngram ) :
    """
        For each candidate/sentence, counts the number of occurrences, the 
        number of words and the number of characters (except spaces and XML).
        
        @param candidate The `Ngram` that is being read from the XML file.    
    """
    global char_counter, word_counter, ngram_counter
    
    if ngram_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":ngram_counter } )            

    for word in sentence.word_list :
        word_counter += 1
        char_counter += len( word )
    ngram_counter += 1

################################################################################     
# MAIN SCRIPT

arg = read_options( "v", ["verbose"], treat_options_simplest, 1, usage_string )

try :    
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    
    corpusHandler = CorpusXMLHandler( treat_sentence=treat_ngram )
    candidatesHandler = CandidatesXMLHandler( treat_sentence=treat_ngram )
    
    
    parser.setContentHandler( corpusHandler ) 
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
                         "(mwetoolkit-corpus.dtd)"
