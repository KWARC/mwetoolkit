#!/usr/bin/python
"""
   
"""

import sys
import xml.sax

import install
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from util import usage, read_options, treat_options_simplest

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <corpus.xml>

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd).
"""

################################################################################
       
def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, lowercases its words in a dummy stupid
        way.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    for w in sentence.word_list :
        w.surface = w.surface.lower()
    print sentence.to_xml()
    
################################################################################  
# MAIN SCRIPT


arg = read_options( "", [], treat_options_simplest, 1 )

try :    
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    print "<!DOCTYPE corpus SYSTEM \"mwttoolkit-corpus.dtd\">"
    print "<corpus>"
    input_file = open( arg[ 0 ] )    
    parser = xml.sax.make_parser()
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
    parser.parse( input_file )
    input_file.close() 
    print "</corpus>"    
except IOError, err :  
    print err
    print "Error reading corpus file. Please verify __common.py configuration"        
    sys.exit( 2 )      
except Exception, err :
    print err
    print "You probably provided an invalid corpus file, please " + \
          "validate it against the DTD (mwttoolkit-corpus.dtd)"
