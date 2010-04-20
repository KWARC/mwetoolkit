#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# feat_association.py is part of mwetoolkit
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
    This script adds four new features for each candidate in the list and for
    each corpus with a known size. These features correspond to Association
    Measures (AMs) based on the frequency of the ngram compared to the frequency
    of the individual words. The AMs are:
        mle: Maximum Likelihood Estimator
        pmi: Pointwise Mutual Information
        t: Student's t test score
        dice: Dice's coeficient
        ll: Log-likelihood (bigrams only)
    Each AM feature is subscribed by the name of the corpus from which it was
    calculated.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import math
import pdb

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.classes.feature import Feature
from xmlhandler.classes.meta_feat import MetaFeat
from util import usage, read_options, treat_options_simplest, \
                 verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""
supported_measures = [ "mle", "t", "pmi", "dice", "ll" ]
corpussize_dict = {}
measures = supported_measures
# TODO: Parametrable combine function
heuristic_combine = lambda l : sum( l ) / len( l ) # Arithmetic mean
     
################################################################################     
       
def treat_meta( meta ) :
    """
        Adds new meta-features corresponding to the AM features that we add to
        each candidate. The meta-features define the type of the features, which
        is a real number for each of the 4 AMs in each corpus.
        
        @param meta The `Meta` header that is being read from the XML file.       
    """
    global corpussize_dict, measures
    for corpus_size in meta.corpus_sizes :
        corpussize_dict[ corpus_size.name ] = float(corpus_size.value)
    for corpus_size in meta.corpus_sizes :
        for meas in measures :
            meta.add_meta_feat(MetaFeat( meas+ "_" +corpus_size.name, "real" ))
    print meta.to_xml().encode( 'utf-8' )
       
################################################################################     
       
def treat_candidate( candidate ) :
    """
        For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates four features that correspond to the Association
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global corpussize_dict
    joint_freq = {}
    singleword_freq = {}
    # Convert all these integers to floats...
    for freq in candidate.freqs :
        joint_freq[ freq.name ] = float(freq.value)
        singleword_freq[ freq.name ] = []
    for word in candidate :
        for freq in word.freqs :
            singleword_freq[ freq.name ].append( float(freq.value) )
    
    for corpus_name in joint_freq.keys() :
        feats = calculate_ams( joint_freq[ corpus_name ], \
                singleword_freq[ corpus_name ], \
                corpussize_dict[ corpus_name ],
                corpus_name )
        for feat in feats :
            candidate.add_feat( feat )
    print candidate.to_xml().encode( 'utf-8' )

################################################################################     

def contingency_tables( bigram_freqs, unigram_freqs, N, corpus_name ):
    """
        Given an ngram (generic n) w_1 ... w_n, the input is a couple of lists
        containing integer frequencies, the output is a couble of lists with
        contingency tables. The first list contains bigram frequencies
        [ f(w_1 w_2), f(w_2 w_3), ..., f(w_n-1 w_n) ]. The second list contains
        unigram frequencies [ f(w_1), f(w_2), ..., f(w_n) ]. While the first
        list contains n-1 elements, the second list contains n elements. The
        result is a couple of lists with contingency tables, the first
        corresponds to the observed frequencies, the second to expected
        frequencies. The contingency tables are 2D lists that contain the 4
        possible outcomes for the occurrence of a bigram, i.e. c(w1 w2),
        c(w1 ~w2), c(~w1 w2) and c(~w1 ~w2), where "~w" means "any word but w".
        Observed contingency tables are exact calculations based on simple
        set operations (intersection, difference). The expected frequencies are
        calculated using maximum likelihood for independent events (e.g. the
        occurrence of w1 does not change the probability of the occurrence of w2
        or of ~w2 imediately after w1, also noted P(w2|w1)=P(w2)).

        @param bigram_freqs List of integers representing bigram frequencies.
        Notice that no bigram can occur more than the words that is contains.
        Any inconsistency will be automatically corrected and output as a
        warning. This list should contain n-1 elements.

        @param unigram_freqs List of integers representing unigram (word)
        frequencies. This list should have n elements.

        @param corpus_name The name of the corpus from which frequencies were
        drawn. This is only used in verbose mode to provide friendly output
        messages.

        @return a couple (observed, expected), where observed and expected are
        lists, both of size n-1, and each cell of each list contains a 2x2 table
        with observed and expected contingency tables for the bigrams given as
        input.
    """
    observed = []
    expected = []
    if len(bigram_freqs) != (len(unigram_freqs)-1) :
        print >> sys.stderr, "WARNING: Invalid unigram/bigram frequencies " +\
                             "passed to calculate_negations function"
        return None
    # 1) Verify that all the frequencies are valid
    for i in range( len( bigram_freqs ) ) :
        if bigram_freqs[ i ] > unigram_freqs[ i ] or \
           bigram_freqs[ i ] > unigram_freqs[ i + 1 ] :
            print >> sys.stderr, "WARNING: " + corpus_name + " unigrams " +\
                                 "must occur at least as much as bigram."
        if bigram_freqs[ i ] > unigram_freqs[ i ] :
            print >> sys.stderr, "Automatic correction: " + \
                                 str( unigram_freqs[ i ] ) + " -> " + \
                                 str( bigram_freqs[ i ] )
            unigram_freqs[ i ] = bigram_freqs[ i ]
        if bigram_freqs[ i ] > unigram_freqs[ i + 1 ] :            
            print >> sys.stderr, "Automatic correction: " + \
                                 str( unigram_freqs[ i + 1 ] ) + " -> " + \
                                 str( bigram_freqs[ i ] )
            unigram_freqs[ i + 1 ] = bigram_freqs[ i ]
    # 2) Calculate negative freqs 
    for i in range( len( bigram_freqs ) ) :        
        o = [ 2 * [ -1 ], 2 * [ -1 ] ]
        e = [ 2 * [ -1 ], 2 * [ -1 ] ]
        cw1 = unigram_freqs[ i ]
        cw2 = unigram_freqs[ i + 1 ]
        cw1w2 = bigram_freqs[ i ]
        o[ 0 ][ 0 ] = cw1w2
        e[ 0 ][ 0 ] = expect( [ cw1, cw2 ], N )
        o[ 0 ][ 1 ] = cw1 - cw1w2
        e[ 0 ][ 1 ] = expect( [ cw1, N - cw2 ], N )
        o[ 1 ][ 0 ] = cw2 - cw1w2
        e[ 1 ][ 0 ] = expect( [ N - cw1, cw2 ], N )
        o[ 1 ][ 1 ] = N - len( unigram_freqs )  + 1 - cw1w2 #exact nb of bigrams
        e[ 1 ][ 1 ] = expect( [ N - cw2, N - cw2 ], N )
        observed.append( o )
        expected.append( e )
    return (observed, expected)

################################################################################

def expect( m_list, N ):
    """
    """
    result = 1.0
    for i in range(len(m_list)) :
        result *= m_list[ i ] / N
    return result * ( N - len(m_list) + 1 )

################################################################################

def calculate_ams( o, m_list, N, corpus_name ) :
    """
        Given a joint frequency of the ngram, a list of individual frequencies,
        a corpus size and a corpus name, generates a list of `Features`, each
        containing the value of an Association Measure.
        
        @param f The float value corresponding to the number of occurrences of 
        the ngram.
        
        @param m_list A list of float values corresponding to the number of 
        occurrences of each of the words composing the ngram. The list should
        NEVER be empty, otherwise the result is undefined.
        
        @param N The float value corresponding to the number of tokens in the
        corpus, i.e. its total size. The size of the corpus should NEVER be 
        zero, otherwise the result is undefined.
        
        @param corpus_name A string that uniquely identifies the corpus from
        which the counts were drawn.        
    """
    # N is never null!!!
    # m_list is never empty!!!
    global measures, heuristic_combine
    feats = []
    f_sum = 0
    n = len( m_list )
    e = expect( m_list, N )
    if "mle" in measures :
        feats.append( Feature( "mle_" + corpus_name, o / N ) )
    if "pmi" in measures :
        if e != 0 and o != 0:
            pmi = math.log( o / e, 2 )
        else :
            pmi = 0.0
        feats.append( Feature( "pmi_" + corpus_name, pmi ) )
    if "t" in measures :
        if o != 0.0 :
            t = ( o - e ) / math.sqrt( o )
        else :
            t = 0.0
        feats.append( Feature( "t_" + corpus_name, t ) )
    if "dice" in measures :
        if sum( m_list ) != 0.0 :
            dice = ( n * o ) / sum( m_list )
        else :
            dice = 0.0
        feats.append( Feature( "dice_" + corpus_name, dice ) )
    if "ll" in measures :
        #pdb.set_trace()
        if len( m_list ) == 2 :
            # Contingency tables observed, expected
            ( ct_os, ct_es ) = contingency_tables( [o], m_list, N, corpus_name )
            ll_list  = [] # Calculation is suitable for generic ngrams
            for (ct_o, ct_e) in map( None, ct_os, ct_es ) :
                ll = 0.0
                for i in range( 2 ) :
                    for j in range( 2 ) :
                        if ct_o[i][j] != 0.0 :
                            
                            ll += ct_o[i][j] * ( math.log( ct_o[i][j], 2 ) -\
                                                 math.log( ct_e[i][j], 2 ) )

                ll_list .append( ll )
            ll_final = heuristic_combine( ll_list )
        else :
            print >> sys.err, "WARNING: log-likelihood is only implemented "+\
                              "for 2-grams. Defaults to 0.0 for n>2"
            ll_final = 0.0
        feats.append( Feature( "ll_" + corpus_name, ll_final ) )
    return feats

################################################################################

def interpret_measures( measures_string ) :
    """
    """
    global supported_measures
    measures_list = measures_string.split( ":" )
    result = []
    for meas_name in measures_list :
        if meas_name in supported_measures :
            result.append( meas_name )
        else :
            raise ValueError, "ERROR: measure is not supported: "+str(meas_name)
    return result

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global measures, supported_measures
    for ( o, a ) in opts:
        if o in ( "-m", "--measures" ) :
            try :
                measures = []
                measures = interpret_measures( a )
            except ValueError, message :
                print >> sys.stderr, message
                print >> sys.stderr, "ERROR: argument must be list separated"+ \
                                     "by \":\" and containing the names: "+\
                                     str( supported_measures )
                usage( usage_string )
                sys.exit( 2 )
    treat_options_simplest( opts, arg, n_arg, usage_string )
################################################################################
# MAIN SCRIPT

longopts = ["verbose", "measures="]
arg = read_options( "vm:", longopts, treat_options, 1, usage_string )

try :    
    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "dtd/mwetoolkit-candidates.dtd">
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
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid candidates file," + \
#                         " please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-candidates.dtd)"
