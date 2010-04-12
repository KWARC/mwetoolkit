#!/usr/bin/python
"""
    This script creates an index file for a given corpus. The index file an
    inverted word index that says how many occurrences of each word were found
    in the corpus AND in which sentences these words occur. If not explicitely 
    declared, the default is to count lemmas instead of word occurrences.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import shelve
import time
import re
import xml.sax

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.__common import INDEX_NAME_KEY, \
                                        CORPUS_SIZE_KEY, \
                                        WILDCARD
from util import usage, read_options, treat_options_simplest, set_verbose, \
                 verbose

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS -i <corpus.index> <corpus.xml>

-i <corpus.index> OR --index <corpus.index>
    Name of the index file that is going to be created or updated. Please pay 
    attention to index uptade: different corpora should never be mixed in the 
    same index file.
    
OPTIONS may be:    
    
-s OR --surface
    Counts surface forms instead of lemmas.

-v OR --verbose
    Print messages that explain what is happening.

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd). The -i 
<corpus.index> option is mandatory.
"""
cache_file = None
surface = False
now = time.time()
cache_file_name = None
corpus_size = 0
sentence_counter = 0

################################################################################

def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, counts the words in the sentence and
        adds them to the cache file that contains the index. The cache file is
        an instance of shelve, so the corpus vocabulary may be arbitrarily 
        large.
        
        @param sentence A `Sentence` that is being read from the XML file.
    """
    global surface, cache_file, now, corpus_size, sentence_counter
    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence %(id)d" % { "id":sentence.s_id } )  
    for word in sentence.word_list :
        corpus_size = corpus_size + 1
        pos = word.pos
        if surface :
            form = word.surface
        else :
            form = word.lemma
        pos_dict = cache_file.get( form.encode( 'utf-8' ) , {} )
        #if cache_time != now : # Overwrite old cache values
        #    ( pos_dict, cache_time ) = ( {}, now )
        freq_pos = pos_dict.get( pos, 0 )
        sent_set = pos_dict.get( 0, set([]) )
        sent_set.add( sentence.s_id )
        pos_dict[ pos ] = freq_pos + 1
        pos_dict[ 0 ] = sent_set
        #cache_file[ form.encode( 'utf-8' ) ] = ( pos_dict, now )
        cache_file[ form.encode( 'utf-8' ) ] = pos_dict
    sentence_counter = sentence_counter + 1
    
################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global cache_file, surface, cache_file_name
    for ( o, a ) in opts:
        if o in ("-i", "--index") :
            try :
                cache_file_name = a
                #cache_file = shelve.open( cache_file_name, writeback=True )
                cache_file = {}
            except IOError :        
                print >> sys.stderr, "Error opening the index."
                print >> sys.stderr, "Try again with another index filename."
                sys.exit( 2 )
        elif o in ("-s", "--surface" ) :
            surface = True
        elif o in ("-v", "--verbose") :
            set_verbose( True )
            verbose( "Verbose mode on" )
            
    if cache_file is None:     
        print >> sys.stderr, "ERROR: You must provide a filename for the index."
        print >> sys.stderr, "Option -i is mandatory."
        usage( usage_string )
        sys.exit( 2 )   
                             
    treat_options_simplest( opts, arg, n_arg, usage_string )    

################################################################################
# MAIN SCRIPT

longopts = ["index=", "surface", "verbose"]
arg = read_options( "i:sv", longopts, treat_options, 1, usage_string )
    
try :
    
    
    verbose( "Reading corpus file..." )
    input_file = open( arg[ 0 ] )
    corpus_name = re.sub( "\.xml", "", arg[ 0 ] )
    parser = xml.sax.make_parser()    
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) )   
    parser.parse( input_file )  
    cache_file[ INDEX_NAME_KEY ] = corpus_name
    cache_file[ CORPUS_SIZE_KEY ] = corpus_size
    input_file.close()  

    verbose( "Index created. Dumping it to file. This may take some time..." ) 
    cache_file_pers = shelve.open( cache_file_name )
    for k in cache_file.keys() :
        cache_file_pers[ k ] = cache_file[ k ]
    cache_file_pers.close()  
    
    verbose( "Index created for \"%(c)s\" and stored in \"%(i)s\"" % \
             { "c" : corpus_name, "i" : cache_file_name } )
          
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," +\
#                         " please validate it against the DTD " + \
#                         "(mwttoolkit-candidates.dtd)"
