#!/usr/bin/python
"""
    This script creates an index file for a given corpus. 

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import shelve
import bisect
import re
import xml.sax
import pdb

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.corpus import Corpus
from xmlhandler.classes.suffix_array import SuffixArray
from xmlhandler.classes.__common import INDEX_NAME_KEY, \
                                        CORPUS_SIZE_KEY, \
                                        WILDCARD, SEPARATOR
from util import usage, read_options, treat_options_simplest, set_verbose, \
                 verbose

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS -i <index> <corpus.xml>

-i <index> OR --index <index>
    Name of the output index files <index>.vocab, <index>.corpus and 
    <index>.ngrams    
    
OPTIONS may be:    
    
-s OR --surface
    Counts surface forms instead of lemmas.

-v OR --verbose
    Print messages that explain what is happening.

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd). The -i 
<corpus.index> option is mandatory.
"""
vocab_file = None
corpus_file = None
ngrams_file = None
surface = False
corpus_size = 0
sentence_counter = 0
word_id = 0
vocab_ordered = [ None ]
trans_table = None
ignore_pos = False

################################################################################

def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, counts the words in the sentence and
        adds them to the cache file that contains the index. The cache file is
        an instance of shelve, so the corpus vocabulary may be arbitrarily 
        large.
        
        @param sentence A `Sentence` that is being read from the XML file.
    """
    global surface, vocab_file, corpus_size, sentence_counter, word_id, \
           vocab_ordered, corpus_file, ignore_pos

    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence %(id)d" % { "id":sentence.s_id } )
      
    for word in sentence.word_list :
        if ignore_pos :
            pos = WILDCARD
        else :
            pos = word.pos
        if surface :
            form = word.surface
        else :
            form = word.lemma
        entry = ( form + SEPARATOR + pos ).encode( 'utf-8' )
        current_id = vocab_file.get( entry, None )
        if current_id is None :
            word_id = word_id + 1
            current_id = word_id
            vocab_file[ entry ] = word_id            
            bisect.insort_left( vocab_ordered, entry )
        corpus_file.append( current_id )
        corpus_size = corpus_size + 1
        
    corpus_file.append( 0 )
    
    sentence_counter = sentence_counter + 1
    
################################################################################

def translate_vocab() :
    global vocab_file, vocab_ordered, trans_table
    trans_table = [ 0 ] * len( vocab_ordered )

    for new_id in range( 1, len( vocab_ordered ) ) :
        current_word = vocab_ordered[ new_id ]
        old_id = vocab_file[ current_word ]
        trans_table[ old_id ] = new_id
        vocab_file[ current_word ] = new_id        

################################################################################

def translate_corpus() :
    global trans_table, corpus_file
    for word_index in range( len( corpus_file ) ) :
        try :
            corpus_file[ word_index ] = trans_table[ corpus_file[ word_index ] ]
        except Exception:
            pdb.set_trace()

################################################################################

def create_suffix_array() :
    global corpus_file, vocab_file, ngrams_file
    i_start = 0
    while corpus_file[ i_start ] == 0 :
        i_start = i_start + 1
    ngrams_file.append( i_start )
    i_start = i_start + 1
    sentence_counter = 0
    for i in range( i_start, len( corpus_file ) ) :
        if corpus_file[ i ] != 0 :
            i_low = 0
            i_up = len( ngrams_file )
            i_mid = ( i_up + i_low ) / 2
            #pdb.set_trace()
            while i_up - i_low > 1 :
                if corpus_file.compare_indices( ngrams_file[i_mid], i ) > 0 :
                    i_up = i_mid
                else :
                    i_low = i_mid
                i_mid = ( i_up + i_low ) / 2                
            # decide before or after
            if corpus_file.compare_indices( ngrams_file[i_low], i ) > 0 :
                ngrams_file.insert( i_low, i )                
            else : 
                ngrams_file.insert( i_up, i )
        else :
            sentence_counter += 1
            if sentence_counter % 100 == 0 :
                verbose( "Processing sentence %(id)d" % { "id":sentence_counter } )  

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global vocab_file, surface, corpus_file, ngrams_file, ignore_pos
    for ( o, a ) in opts:
        if o in ("-i", "--index") :
            try :
                #cache_file = shelve.open( cache_file_name, writeback=True )
                vocab_file = shelve.open( a + ".vocab" )
                vocab_file.clear()
                corpus_file = Corpus( a + ".corpus" )   
                corpus_file.clear()             
                ngrams_file = SuffixArray( vocab_file, corpus_file, a + ".ngrams" )
                ngrams_file.clear()
            except IOError :        
                print >> sys.stderr, "Error opening the index."
                print >> sys.stderr, "Try again with another index filename."
                sys.exit( 2 )
        elif o in ("-s", "--surface" ) :
            surface = True
        elif o in ("-v", "--verbose") :
            set_verbose( True )
            verbose( "Verbose mode on" )
        elif o in ("-g", "--ignore-pos"): 
            ignore_pos = True                 
            
    if vocab_file is None:     
        print >> sys.stderr, "ERROR: You must provide a filename for the index."
        print >> sys.stderr, "Option -i is mandatory."
        usage( usage_string )
        sys.exit( 2 )   
                             
    treat_options_simplest( opts, arg, n_arg, usage_string )    

################################################################################
# MAIN SCRIPT

longopts = ["index=", "surface", "verbose", "ignore-pos"]
arg = read_options( "i:svg", longopts, treat_options, 1, usage_string )
    
try :    
    verbose( "Reading corpus file..." )
    input_file = open( arg[ 0 ] )
    corpus_name = re.sub( "\.xml", "", arg[ 0 ] )
    parser = xml.sax.make_parser()    
    parser.setContentHandler( CorpusXMLHandler( treat_sentence ) )   
    parser.parse( input_file )  
    #pdb.set_trace()
    vocab_file[ CORPUS_SIZE_KEY ] = corpus_size
    input_file.close()

    verbose( "Sorting vocab in lexicographical order" )
    translate_vocab()
    verbose( "Translating corpus to new vocab IDs" )    
    translate_corpus()
    verbose( "Creating suffix array for the corpus ngrams" )
    create_suffix_array() 

    vocab_file.close()
    del corpus_file # force flush
    del ngrams_file # force flush
      
    verbose( "Index created for \"%(c)s\". Please do not erase the index files " % \
             { "c" : corpus_name } )
              
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," +\
#                         " please validate it against the DTD " + \
#                         "(mwttoolkit-candidates.dtd)"
