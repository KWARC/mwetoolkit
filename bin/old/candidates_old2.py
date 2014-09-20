#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# candidates.py is part of mwetoolkit
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
    This script extract Multiword Expression candidates from a raw corpus in 
    valid XML (mwetoolkit-corpus.dtd) and generates a candidate list in valid 
    XML (mwetoolkit-candidates.dtd). There are two possible extraction methods: 
    the -p option assumes that you have a patterns file in which you define 
    shallow morphosyntactic patterns (e.g. I want to extract Verb + Preposition
    pairs); the -n option assumes that you do not care about the type of the
    candidates and that you are trying to extract all possible ngrams from the
    corpus. The latter should only be used as a backoff strategy when you do not
    know anything about the corpus or language: do not expect to obtain 
    impressive results with it. Notice that in the -n option, ngrams are not
    extracted across sentence borders, since these would certainly not be
    interesting MWE candidates.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import re
import shelve
import xml.sax
import os
import tempfile

from bin.libs.xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.__common import WILDCARD, \
                                        TEMP_PREFIX, \
                                        TEMP_FOLDER, \
                                        XML_HEADER, \
                                        XML_FOOTER
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.candidate import Candidate
from bin.libs.base.ngram import Ngram
from xmlhandler.classes.word import Word
from util import usage, read_options, treat_options_simplest, verbose
from libs.patternlib import parse_patterns_file, match_pattern, build_generic_pattern
from libs.indexlib import Index



################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s [-n <min>:<max> | -p <patterns.xml>] OPTIONS <corpus>

-p <patterns.xml> OR --patterns <patterns.xml>
    The patterns to extract, valid XML (mwetoolkit-patterns.dtd)

-n <min>:<max> OR --ngram <min>:<max>
    The length of ngrams to extract. For instance, "-n 3:5" extracts ngrams 
    that have at least 3 words and at most 5 words. If you define only <min> or
    only <max>, the default is to consider that both have the same value, i.e. 
    if you call the program with the option "-n 3", you will extract only 
    trigrams while if you call it with the options "-n 3:5" you will extract 
    3-grams, 4-grams and 5-grams. The value of <min> is at least 1, <max> is at
    most 10.
    
OPTIONS may be:

-i OR --index
     Read the corpus from an index instead of an XML file. Default false.
     
-f OR --freq     
    Output the count of the candidate. This counter will merge the candidates if
    more than one pattern matches it, considering it as a single entry. The 
    counts of individual words in the candidate are NOT output by this option,
    you must use counter.py for this. Default false.

-g OR --ignore-pos
     Ignores parts of speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. Default false.

-s OR --surface
    Counts surface forms instead of lemmas. Default false.

    By default, <corpus> must be a valid XML file (mwetoolkit-corpus.dtd). If
the -i option is specified, <corpus> must be the basepath for an index generated
by index.py.

    You must choose either the -p option or the -n option, both are not allowed
at the same time.
"""
patterns = []
ignore_pos = False
surface_instead_lemmas = False
print_cand_freq = False
corpus_from_index = False
longest_pattern = 0
shortest_pattern = sys.maxint
sentence_counter = 0


def copy_word(w):
    return Word(w.surface, w.lemma, w.pos, w.syn, [])

def copy_word_list(ws):
    return map(copy_word, ws)

def copy_ngram(ngram):
    return Ngram(copy_word_list(ngram.word_list), [])


################################################################################
       
def treat_sentence( sentence ) :
    """
        For each sentence in the corpus, generates all the candidates that match
        at least one pattern in the patterns file (-p option) or all the
        ngrams that are in the valid range (-n option). The candidates are
        stored into a temporary file and will be further printed to a XML file.
        The temp file is used to avoid printing twice a repeated candidate and
        to count occurrences of the same candidate.
        
        @param sentence A `Sentence` that is being read from the XML file.    
    """
    global patterns, temp_file, ignore_pos, surface_instead_lemmas, \
           longest_pattern, shortest_pattern, sentence_counter
    if sentence_counter % 100 == 0 :
        verbose( "Processing sentence number %(n)d" % { "n":sentence_counter } )

    words = sentence.word_list

    for pattern in patterns:
        for match in match_pattern(pattern, words):
            match_ngram = Ngram(copy_word_list(match), [])

            if ignore_pos :    
                match_ngram.set_all( pos=WILDCARD )
            internal_key = unicode( match_ngram.to_string() ).encode('utf-8')

            if( surface_instead_lemmas ) :
                match_ngram.set_all( lemma=WILDCARD )
            else :
                match_ngram.set_all( surface=WILDCARD )                    
            key = unicode( match_ngram.to_string() ).encode('utf-8')
            ( surfaces_dict, total_freq ) = temp_file.get( key, ( {}, 0 ) )
            freq_surface = surfaces_dict.get( internal_key, 0 )
            surfaces_dict[ internal_key ] = freq_surface + 1
            temp_file[ key ] = ( surfaces_dict, total_freq + 1 )

    sentence_counter += 1
         
################################################################################

def interpret_ngram( argument ) :
    """
        Parses the argument of the "-n" option. This option is of the form
        "<min>:<max>" and defines the length of n-grams to extract. For 
        instance, "3:5" extracts ngrams that have at least 3 words and at most 5 
        words. If you define only <min> or only <max>, the default is to 
        consider that both have the same value. The value of <min> is at least 
        1, <max> is at most 10. Generates an exception if the syntax is 
        incorrect, generates a None value if the arguments are incoherent 
        (e.g. <max> < <min>)
        
        @param argument String argument of the -n option, has the form 
        "<min>:<max>"
        
        @return A tuple (<min>,<max>) with the two integer limits, or None if
        the argument is incoherent.
    """
    try:
        if ":" in argument :
            [ n_min, n_max ] = argument.split( ":" )
            n_min = int(n_min)
            n_max = int(n_max)
        else :
            n_min = int(argument)
            n_max = int(argument)
        if n_min <= n_max and n_min >= 1 and n_max <= 10:                
            return ( n_min, n_max )
        else :                
            return None
    except IndexError :
        return None
    except TypeError :
        return None
    except ValueError :
        return None
        
################################################################################  

def read_patterns_file( filename ) :
    global patterns

    try:
        patterns = parse_patterns_file(filename)
    except IOError, err:
        print >> sys.stderr, err
        sys.exit( 2 )
        
################################################################################  

def create_patterns_file( ngram_range ) :
    """
        Create an artificial list of MWE patterns in which all the parts of
        the words are wildcards. Such artificial patterns match every ngram
        of size n, which is exactly what we want to do with the option -n. This
        may seem a weird way to extract ngrams, but it allows a single 
        transparent candidate extraction function, treat_sentence.
        
        @param ngram_range String argument of the -n option, has the form 
        "<min>:<max>"        

        FIXMEFIXMEFIXME
    """        
    global patterns, usage_string, shortest_pattern, longest_pattern
    result = interpret_ngram( ngram_range )
    if result :
        ( shortest_pattern, longest_pattern ) = result
        patterns.append(build_generic_pattern(shortest_pattern, longest_pattern))
    else :
        print >> sys.stderr, "The format of the argument must be <min>:<max>"
        print >> sys.stderr, "<min> must be at least 1 and <max> is at most 10"
        usage( usage_string )
        sys.exit( 2 )  

################################################################################  

def print_candidates( temp_file, corpus_name ) :
    """
        Prints a XML file (mwetoolkit-candidates.dtd) from a temporary 
        candidates file generated by the treat_sentence callback function. 
        Repeated candidates are not printed several times: instead, each base 
        form has a joint frequency of the candidate in the corpus. Since the
        new version of the "count.py" script, this initial frequency is only
        printed if you explicitely ask to do it through the -f option.
        
        @param temp_file Temporary file generated during the corpus parsing.
        
        @param corpus_name The name of the corpus from which we generate the
        candidates.
    """
    global print_cand_freq
    try :
        print XML_HEADER % { "root" : "candidates", "ns" : "" }
        print "<meta></meta>"
        id_number = 0        
        for base_string in temp_file.keys() :
            (surface_dict, total_freq) = temp_file[ base_string ]
            cand = Candidate( id_number, [], [], [], [], [] )
            cand.from_string( unicode( base_string, 'utf-8' ) )
            if print_cand_freq :
               freq = Frequency( corpus_name, total_freq )
               cand.add_frequency( freq )
            id_number = id_number + 1                        
            for occur_string in surface_dict.keys() :
                occur_form = Ngram( [], [] )
                occur_form.from_string( occur_string )                 
                freq_value = surface_dict[ occur_string ]
                freq = Frequency( corpus_name, freq_value )
                occur_form.add_frequency( freq )
                cand.add_occur( occur_form )                
            print cand.to_xml().encode( 'utf-8' )
        print XML_FOOTER % { "root" : "candidates" }
    except IOError, err :
        print >> sys.stderr, err
        print >> sys.stderr, "Error reading temporary file."
        print >> sys.stderr, "Please verify __common.py configuration"        
        sys.exit( 2 )

################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global patterns, ignore_pos, surface_instead_lemmas, print_cand_freq, corpus_from_index
    mode = []
    for ( o, a ) in opts:
        if o in ("-p", "--patterns") : 
            read_patterns_file( a )
            mode.append( "patterns" )
        elif o in ( "-n", "--ngram" ) :
            create_patterns_file( a )
            mode.append( "ngram" )
        elif o in ("-g", "--ignore-pos") : 
            ignore_pos = True
        elif o in ("-s", "--surface") : 
            surface_instead_lemmas = True
        elif o in ("-f", "--freq") : 
            print_cand_freq = True
        elif o in ("-i", "--index") :
            corpus_from_index = True

    if len(mode) != 1 :
        print >> sys.stderr, "Exactly one option, -p or -n, must be provided"
        usage( usage_string )
        sys.exit( 2 )
        
    treat_options_simplest( opts, arg, n_arg, usage_string )
################################################################################  
# MAIN SCRIPT

longopts = [ "patterns=", "ngram=", "index", "freq", "ignore-pos", "surface", "verbose" ]
arg = read_options( "p:n:ifgsv", longopts, treat_options, 1, usage_string )

try :    
    try :    
        temp_fh = tempfile.NamedTemporaryFile( prefix=TEMP_PREFIX, 
                                               dir=TEMP_FOLDER )
        temp_name = temp_fh.name
        temp_fh.close()
        temp_file = shelve.open( temp_name, 'n' )
    except IOError, err :
        print >> sys.stderr, err
        print >> sys.stderr, "Error opening temporary file."
        print >> sys.stderr, "Please verify __common.py configuration"
        sys.exit( 2 )


    if corpus_from_index:
        index = Index(arg[0])
        index.load_main()
        for sentence in index.iterate_sentences():
            treat_sentence(sentence)
    else:
        input_file = open( arg[ 0 ] )    
        parser = xml.sax.make_parser()
        parser.setContentHandler( CorpusXMLHandler( treat_sentence ) ) 
        parser.parse( input_file )
        input_file.close()

    corpus_name = re.sub( ".*/", "", re.sub( "\.xml", "", arg[ 0 ] ) )
    print_candidates( temp_file, corpus_name )
    try :
        temp_file.close()
        os.remove( temp_name )
    except IOError, err :
        print >> sys.stderr, err
        print >> sys.stderr, "Error closing temporary file. " + \
              "Please verify __common.py configuration"        
        sys.exit( 2 )            
except IOError, err :  
    print >> sys.stderr, err
    print >> sys.stderr, "Error reading corpus file. Please verify " + \
                         "__common.py configuration"        
    sys.exit( 2 )      
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid corpus file, " + \
#                         "please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-corpus.dtd)"
