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
import array
import pdb

from xmlhandler.corpusXMLHandler import CorpusXMLHandler
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

-g OR --ignore-pos
     Ignores Part-Of-Speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. If you are using -y, this option will be ignored. 
     Default false.
    
-s OR --surface
    Counts surface forms instead of lemmas.

-v OR --verbose
    Print messages that explain what is happening.

    The <corpus.xml> file must be valid XML (mwttoolkit-corpus.dtd). The -i 
<corpus.index> option is mandatory.
"""
vocab_file = {}
corpus_file = array.array( 'L' )
ngrams_file = array.array( 'L' )
corpus_size = 0
sentence_counter = 0
word_id = 0
vocab_ordered = [ None ]
trans_table = None
name = None

################################################################################

def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, 
        
        @param sentence A `Sentence` that is being read from the XML file.
    """
    global vocab_file, corpus_size, sentence_counter, word_id, \
           vocab_ordered, corpus_file, build_entry

    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence %(id)d" % { "id":sentence.s_id } )
      
    for word in sentence.word_list :
        entry = build_entry( word.surface, word.lemma, word.pos )        
        current_id = vocab_file.get( entry, None )
        if current_id is None :
            word_id = word_id + 1
            current_id = word_id
            vocab_file[ entry ] = word_id
            vocab_ordered.append( entry )
        corpus_file.append( current_id )
        corpus_size = corpus_size + 1
        
    corpus_file.append( 0 )
    corpus_size = corpus_size + 1
    sentence_counter = sentence_counter + 1
    
################################################################################

def translate_vocab() :
    """
    """
    global vocab_file, vocab_ordered, trans_table
    
    vocab_ordered.sort()
    
    trans_table = [ 0 ] * len( vocab_ordered )

    for new_id in range( 1, len( vocab_ordered ) ) :
        current_word = vocab_ordered[ new_id ]
        old_id = vocab_file[ current_word ]
        trans_table[ old_id ] = new_id
        vocab_file[ current_word ] = new_id        

################################################################################

def translate_corpus() :
    """
    """
    global trans_table, corpus_file, corpus_size
    for word_index in range( corpus_size ) :    
        corpus_file[ word_index ] = trans_table[ corpus_file[ word_index ] ]
        
################################################################################

def compare_indices( pos1, pos2 ) :
    """
        returns 1 if ngram(pos1) >lex ngram(pos2), -1 for ngram(pos1) <lex
        ngram(pos2) and 0 for matching ngrams
    """
    global corpus_file
    pos1_cursor = pos1
    wordp1 = corpus_file[ pos1_cursor ]
    pos2_cursor = pos2 
    wordp2 = corpus_file[ pos2_cursor ]          

    while wordp1 == wordp2 and wordp1 != 0:
        # both are zero, we can stop because they are considered identical
        pos1_cursor += 1   
        wordp1 = corpus_file[ pos1_cursor ]        
        pos2_cursor += 1   
        wordp2 = corpus_file[ pos2_cursor ]             
    return int( wordp1 - wordp2 )
    
################################################################################    

def create_suffix_array() :
    """
    """
    global corpus_file, ngrams_file
    i_start = 0
    while corpus_file[ i_start ] == 0 :
        i_start = i_start + 1
    ngrams_file.append( i_start )
    i_start = i_start + 1
    sentence_counter = 0
    for i in range( i_start, len( corpus_file ) ) :
        if corpus_file[ i ] != 0 :            
            ngrams_file.append( i )                        
    verbose( "Sorting suffix array. This might take some time..." )
    ngrams_file = array.array( 'L', sorted( ngrams_file, cmp=compare_indices ) )

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global vocab_file, corpus_file, ngrams_file, name, build_entry
    surface_flag = False
    pos_flag = False
    for ( o, a ) in opts:
        if o in ("-i", "--index") :
            try :
                name = a
            except IOError :        
                print >> sys.stderr, "Error opening the index."
                print >> sys.stderr, "Try again with another index filename."
                sys.exit( 2 )
        elif o in ("-s", "--surface" ) :
            surface_flag = True
        elif o in ("-g", "--ignore-pos"): 
            pos_flag = True              
            
    if surface_flag and pos_flag :
        build_entry = lambda s, l, p: (s + SEPARATOR + WILDCARD).encode('utf-8')
    elif surface_flag :
        build_entry = lambda s, l, p: (s + SEPARATOR + p).encode('utf-8')
    elif pos_flag :
        build_entry = lambda s, l, p: (l + SEPARATOR + WILDCARD).encode('utf-8')
    else :      
        build_entry = lambda s, l, p: (l + SEPARATOR + p).encode('utf-8')
            
    if name is None:     
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
    input_file.close()

    verbose( "Sorting vocab in lexicographical order" )
    translate_vocab()
    verbose( "Translating corpus to new vocab IDs" )    
    translate_corpus()
    verbose( "Creating suffix array for the corpus ngrams" )
    create_suffix_array() 

    vocab_fd = shelve.open( name + ".vocab" )
    vocab_fd.clear()   
    vocab_fd[ CORPUS_SIZE_KEY ] = corpus_size - sentence_counter    
    vocab_fd.update( vocab_file )
    vocab_fd.close()
    
    fd = open( name + ".corpus", "w" )
    corpus_file.tofile( fd )
    fd.close()   
    
    fd = open( name + ".ngrams", "w" )
    ngrams_file.tofile( fd )
    fd.close()     
      
    verbose( "Index created for \"%(c)s\". Please do not erase the index files " % \
             { "c" : corpus_name } )
              
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," +\
#                         " please validate it against the DTD " + \
#                         "(mwttoolkit-candidates.dtd)"
