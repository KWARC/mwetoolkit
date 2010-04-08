#!/usr/bin/python
"""
    This script calculates individual word frequencies for a given candidate 
    list in a given corpus. The corpus may be a valid corpus word index 
    generated by the `index.py` script (-i option) or it may be the World Wide 
    Web through Yahoo's Web Search interface (-y option) or Google's Web Search
    interface (-w option). Notice that this script does not calculate joint 
    ngram frequencies. Joint ngram frequencies are provided by the 
    `candidates.py` script, but you cannot calculate the joint frequency of an 
    ngram in another corpus that is not the corpus in which it was found. This 
    will be implemented in future versions.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import getopt
import shelve
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.classes.__common import WILDCARD, CORPUS_SIZE_KEY, \
                                        INDEX_NAME_KEY
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.yahooFreq import YahooFreq
from xmlhandler.classes.googleFreq import GoogleFreq
from xmlhandler.classes.corpus_size import CorpusSize
from util import usage, read_options, treat_options_simplest
    
################################################################################
# GLOBALS    
    
usage_string = """Usage: 
    
python %(program)s [-y | -i <corpus.index>] OPTIONS <candidates.xml>

-i <corpus.index> OR --index <corpus.index>
    Name of the index file that that was created by "index.py" from a corpus
    file. The <corpus.index> file contains the frequencies of individual words.

-y OR --yahoo
    Search for frequencies in the Web using Yahoo Web Search as approximator for
    Web document frequencies.    
    
-w OR --google
    Search for frequencies in the Web using Google Web Search as approximator 
    for Web document frequencies.   
    
OPTIONS may be:

-g OR --ignore-pos
     Ignores Part-Of-Speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. If you are using -y, this option will be ignored. 
     Default false.
   
    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). 
You must chose either the -y option or the -i otpion, both are not allowed at 
the same time. 
"""    
get_freq_function = None
cache_file = None
freq_name = "?"
ignore_pos = False
web_freq = None
the_corpus_size = -1
     
################################################################################
       
def treat_meta( meta ) :
    """
        Adds a `CorpusSize` meta-information to the header and prints the 
        header. The corpus size is important to allow the calculation of 
        statistical Association Measures by the `feat_association.py` script.
        
        @param meta The `Meta` header that is being read from the XML file.        
    """
    global freq_name, the_corpus_size
    meta.add_corpus_size( CorpusSize( name=freq_name, value=the_corpus_size ) )
    print meta.to_xml()
       
################################################################################
       
def treat_candidate( candidate ) :
    """
        For each candidate, searches for the individual word frequencies of the
        base ngram. The corresponding function, for a corpus index or for yahoo,
        will be called, depending on the -i or -y options. The frequencies are
        added as a child element of the word and then the candidate is printed.
        
        @param candidate The `Candidate` that is being read from the XML file.        
    """
    global get_freq_function, freq_name
    candidate_string = ""
    for word in candidate.base.word_list :
        if word.surface == WILDCARD :
            token = word.lemma
        else :
            token = word.surface
        candidate_string = candidate_string + " " + token
        freq_value = get_freq_function( token, word.pos )
        word.add_frequency( Frequency( freq_name, freq_value ) )
    if freq_name == "yahoo" or freq_name == "google" :
        freq_value = get_freq_function( candidate_string.strip(), word.pos )
        candidate.base.add_frequency( Frequency( freq_name, freq_value ) )
    print candidate.to_xml().encode( 'utf-8' )

################################################################################
       
def get_freq_index( token, pos ) :
    """
        Gets the frequency (number of occurrences) of a token (word) in the
        index file. Calling this function assumes that you called the script
        with the -i option and with a valid index file.
        
        @param token A string corresponding to the surface form or lemma
        of a word.
        
        @param pos A string corresponding to the Part Of Speech of a word.
    """
    global ignore_pos
    cache_entry = cache_file.get( token.encode( 'utf-8' ) , ({}, 0, None ) )
    ( pos_dict, cache_freq, cache_time ) = cache_entry
    if ignore_pos :
        return cache_freq
    else :
        freq_pos = pos_dict.get( pos, 0 )
        return freq_pos
    
################################################################################

def get_freq_web( token, pos ) : 
    """
        Gets the frequency (number of occurrences) of a token (word) in the
        Web through Yahoo's or Google's index. Calling this function assumes 
        that you called the script with the -y or -w option.
        
        @param token A string corresponding to the surface form or lemma
        of a word.
        
        @param pos A string corresponding to the Part Of Speech of a word. This
        parameter is ignored since Web search engines dos no provide linguistic 
        information.
    """
    # POS is ignored
    global web_freq
    return web_freq.search_frequency( token )

################################################################################  

def open_index( index_filename ) :
    """
        Open the index file (a valid index created by the `index.py` script). 
        The index is not loaded into main memory, only opened as a shelve 
        object (something like a very simple embedded DB). Meta-information 
        about the corpus size and name is retrieved.
        
        @param index_filename The string name of the index file.
    """
    global cache_file, freq_name, the_corpus_size
    try :
        cache_file = shelve.open( index_filename )
        freq_name = cache_file[ INDEX_NAME_KEY ]
        the_corpus_size = cache_file[ CORPUS_SIZE_KEY ]              
    except IOError :        
        print >> sys.stderr, "Error opening the index."
        print >> sys.stderr, "Try again with another index filename."
        sys.exit( 2 )
    except KeyError :        
        print >> sys.stderr, "Error opening the index."
        print >> sys.stderr, "Try again with another index filename."
        sys.exit( 2 )        

################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global cache_file, get_freq_function, freq_name, ignore_pos, web_freq, \
           the_corpus_size
    mode = []
    for ( o, a ) in opts:
        if o in ( "-i", "--index" ) : 
            open_index( a )
            get_freq_function = get_freq_index
            mode.append( "index" )              
        elif o in ( "-y", "--yahoo" ) :
            web_freq = YahooFreq()          
            freq_name = "yahoo"
            the_corpus_size = web_freq.corpus_size()         
            get_freq_function = get_freq_web
            mode.append( "yahoo" )   
        elif o in ( "-w", "--google" ) :
            web_freq = GoogleFreq()          
            freq_name = "google"
            the_corpus_size = web_freq.corpus_size()         
            get_freq_function = get_freq_web
            mode.append( "yahoo" )   
        elif o in ("-g", "--ignore-pos"): 
            ignore_pos = True        

    if len(mode) != 1 :
        print >> sys.stderr, "Exactly one option, -y or -i, must be provided"
        usage( usage_string )
        sys.exit( 2 )
                
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################   
# MAIN SCRIPT

longopts = ["yahoo", "google", "index=", "ignore-pos" ]
arg = read_options( "ywi:g", longopts, treat_options, 1, usage_string )  

try :    
    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "mwttoolkit-candidates.dtd">
<candidates>
""" 
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    parser.setContentHandler(CandidatesXMLHandler(treat_meta, treat_candidate)) 
    parser.parse( input_file )
    input_file.close() 
    print "</candidates>"      
     
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(mwttoolkit-candidates.dtd)"
