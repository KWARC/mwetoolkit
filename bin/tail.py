#!/usr/bin/python
"""
    Prints the first N sentences of a corpus. Works like the "head" command in
    the unix platform, only it takes a corpus in xml format as input.
"""

import sys
import xml.sax

import install
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from util import usage, read_options, treat_options_simplest

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS <corpus.xml>

    OPTIONS may be:    
    
-n OR --number
    Number of sentences that you want to print out. Default value is 10.

-v OR --verbose
    Print messages that explain what is happening.

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd).
"""
limit = 10
sentence_counter = 0
sentence_buffer = [ None ] * limit

################################################################################
       
def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, prints it if the limit is still not 
        achieved.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    global sentence_counter, sentence_buffer, limit
    sentence_buffer[ sentence_counter % limit ] = sentence
    sentence_counter += 1
    
################################################################################    

def print_sentences() :
    """
    """
    global sentence_buffer, sentence_counter
    for i in range( limit ) :
        index = ( sentence_counter + i ) % limit
        if sentence_buffer[ index ] != None :
            print sentence_buffer[ index ].to_xml().encode( 'utf-8' )
        else :
            break
        
    
################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global limit,  sentence_buffer
    for ( o, a ) in opts:
        if o in ("-n", "--number") :
            try :
                limit = int( a )
                sentence_buffer = [ None ] * limit
                print sentence_buffer
                if limit < 0 :
                    raise ValueError
            except ValueError :
                print >> sys.stderr, "ERROR: You must provide a positive " + \
                                     "integer value as argument of -n option."
                usage( usage_string )
                sys.exit( 2 )
                             
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################    
# MAIN SCRIPT

longopts = [ "verbose", "number=" ]
arg = read_options( "vn:", longopts, treat_options, -1, usage_string )

try :    
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    print "<!DOCTYPE corpus SYSTEM \"dtd/mwttoolkit-corpus.dtd\">"
    print "<corpus>"
    parser = xml.sax.make_parser()
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
    if len( arg ) == 0 :        
        parser.parse( sys.stdin )
    else :
        for a in arg : 
            input_file = open( a )            
            parser.parse( input_file )
            input_file.close() 
    print_sentences() 
    print "</corpus>"
    
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid corpus file," +\
#                         " please validate it against the DTD " + \
#                         "(mwttoolkit-corpus.dtd)"


