#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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
    This script adds five new features for each candidate in the list and for
    each corpus with a known size. These features correspond to Association
    Measures (AMs) based on the frequency of the ngram compared to the frequency
    of the individual words. The AMs are:
        mle: Maximum Likelihood Estimator
        pmi: Pointwise Mutual Information
        t: Student's t test score
        dice: Dice's coeficient
        ll: Log-likelihood (bigrams only)
    Each AM feature is suffixed by the name of the corpus from which it was
    calculated.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import math

from libs.base.feature import Feature
from libs.base.meta_feat import MetaFeat
from libs.util import read_options, treat_options_simplest, \
                 verbose, warn, error
from libs import filetype




################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python {program} OPTIONS <candidates>

The <candidates> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force reading from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--to <output-filetype-ext>
    Write output in given filetype extension.
    (By default, keeps original input format):
    {descriptions.output[candidates]}

-m <meas> OR --measures <meas>
    The name of the measures that will be calculated. If this option is not
    defined, the script calculates all available measures. Measure names should
    be separated by colon ":" and should be in the list of supported measures
    below:

    mle -- Maximum Likelihood Estimator
    pmi -- Pointwise Mutual Information
    t -- Student's t test score
    dice -- Dice's coeficient
    ll -- Log-likelihood (bigrams only)

-o <name> OR --original <name>
    The name of the frequency source from which the candidates were extracted
    originally. This is only necessary if you are using backoff to combine the
    counts. In this case, you MUST define the original count source and it must
    be a valid name described through a <corpussize> element in the meta header.

-u OR --unnorm-mle
    Does not normalize Maximum Likelihood Estimator. This means that instead of
    the raw frequency divided by the size of the corpus, MLE will correspond to
    the simple raw frequency of the n-gram. Both, normalized and unnormalized
    MLE are rank-equivalent.

{common_options}
"""
input_filetype_ext = None
output_filetype_ext = None

supported_measures = [ "mle", "t", "pmi", "dice", "ll" ]
corpussize_dict = {}
measures = supported_measures
# TODO: Parametrable combine function
heuristic_combine = lambda l : sum( l ) / len( l ) # Arithmetic mean
not_normalize_mle=False
warn_ll_bigram_only = True

     
################################################################################     

class FeatureAdderPrinter(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)

    def handle_meta(self, meta, info={}):
        """Adds new meta-features corresponding to the AM features that we add to
        each candidate. The meta-features define the type of the features, which
        is a real number for each of the 4 AMs in each corpus.
        
        @param meta The `Meta` header that is being read from the XML file.       
        """
        global corpussize_dict
        global measures
        for corpus_size in meta.corpus_sizes :
            corpussize_dict[ corpus_size.name ] = float(corpus_size.value)
        for corpus_size in meta.corpus_sizes :
            for meas in measures :
                meta.add_meta_feat(MetaFeat( meas+ "_" +corpus_size.name, "real" ))
        self.chain.handle_meta(meta, info)


    def handle_candidate(self, candidate, info={}):
        """For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates four features that correspond to the Association
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
        """
        global corpussize_dict, main_freq

        joint_freq = {}
        singleword_freq = {}
        backed_off = False
        # Convert all these integers to floats...
        for freq in candidate.freqs :
            joint_freq[ freq.name ] = ( float(abs( freq.value ) ) )
            singleword_freq[ freq.name ] = []
            if freq.value < 0 :
                backed_off = True
        for word in candidate :
            for freq in word.freqs :
                singleword_freq[ freq.name ].append( abs( float(freq.value) ) )
                # Little trick: negative counts indicate backed-off counts
                if freq.value < 0 :
                    backed_off = True
        
        for freq in candidate.freqs :
            corpus_name = freq.name
            if not backed_off and corpus_name == "backoff" :
                N = corpussize_dict[ main_freq ]
            else :
                N = corpussize_dict[ corpus_name ]
            try :
                feats = calculate_ams( joint_freq[ corpus_name ],
                        singleword_freq[ corpus_name ],
                        N, corpus_name )
                for feat in feats :
                    candidate.add_feat( feat )
            except Exception :
                error( "This should never be printed. The end of the world is here")

        self.chain.handle_candidate(candidate, info)


################################################################################     

def contingency_tables( bigram_freqs, unigram_freqs, N, corpus_name ):
    """
        Given an ngram (generic n) w_1 ... w_n, the input is a couple of lists
        containing integer frequencies, the output is a couple of lists with
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
    n = len( unigram_freqs )
    if len( bigram_freqs ) != n - 1 :
        warn( "Invalid unigram/bigram frequencies passed to "
              "calculate_negations function")
        return None
    # 1) Verify that all the frequencies are valid
    for i in range( len( bigram_freqs ) ) :
        if bigram_freqs[ i ] > unigram_freqs[ i ] or \
           bigram_freqs[ i ] > unigram_freqs[ i + 1 ] :
            warn( corpus_name + " unigrams must occur at least as much as bigram.")
        if bigram_freqs[ i ] > unigram_freqs[ i ] :
            warn("Automatic correction: " + \
                                 str( unigram_freqs[ i ] ) + " -> " + \
                                 str( bigram_freqs[ i ] ))
            unigram_freqs[ i ] = bigram_freqs[ i ]
        if bigram_freqs[ i ] > unigram_freqs[ i + 1 ] :            
            warn("Automatic correction: " + \
                                 str( unigram_freqs[ i + 1 ] ) + " -> " + \
                                 str( bigram_freqs[ i ] ))
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
        e[ 0 ][ 1 ] = expect( [ cw1, N - n + 1 - cw2 ], N )
        o[ 1 ][ 0 ] = cw2 - cw1w2
        e[ 1 ][ 0 ] = expect( [ N - n + 1 - cw1, cw2 ], N )
        # BEWARE! THERE WAS A HUGE ERROR HERE, CORRECTED ON APRIL 18, 2012
        # ALL LOG-LIKELIHOOD VALUES CALCULATED BY THE TOOLKIT WERE WRONG!
        # PLEASE RE-RUN IF YOU USED THE OLD VERSION!
        o[ 1 ][ 1 ] = N - len( unigram_freqs )  + 1 - cw1 - cw2 + cw1w2 
        e[ 1 ][ 1 ] = expect( [ N - n + 1 - cw1, N - n + 1 - cw2 ], N )
        observed.append( o )
        expected.append( e )
    return (observed, expected)

################################################################################

def expect( m_list, N ):
    """
        Returns the expected joint frequency of the n-gram by multiplying the
        individual frequencies of each word divided by N, and then scaling it
        back to N. That is, given c(w_1), c(w_2), ..., c(w_n) counts of words
        w_1 to w_n, and the size of the corpus N, we calculate the expected
        count E(w_1, ..., w_n) as:
        
                             w_1   w_2         w_n         w_1 x w_2 x ... x w_n
        E(w_1, ..., w_n) = ( --- x --- x ... x --- ) x N = ---------------------
                              N     N           N                 N^(n-1)
                              
        Actually, N is adjusted to correspond to the number of n-grams and not
        of tokens in the corpus, i.e. N - n + 1 instead of N. For large values 
        of N, this is neglectable.
        
        @param m_list List of the individual word counts. The list has n float
        elements, the same size of the n-gram.
        
        @param N Number of total tokens in the frequency source.
        
        @return A single float value that corresponds to E(w_1, ..., w_n) as
        calculated in the formula above.
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
        
        @param o The float value corresponding to the number of occurrences of 
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
    global measures, heuristic_combine, not_normalize_mle, warn_ll_bigram_only
    feats = []
    f_sum = 0
    n = len( m_list )
    e = expect( m_list, N )
    if "mle" in measures :
        if not_normalize_mle :
            mle = int( o )
        else :
            mle = o / N
        feats.append( Feature( "mle_" + corpus_name, mle ) )
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
                            
                            ll += ct_o[i][j] * ( math.log( ct_o[i][j], 10 ) -
                                                 math.log( ct_e[i][j], 10 ) )
                ll *= 2
                ll_list .append( ll )
            ll_final = heuristic_combine( ll_list )
        else :
            if warn_ll_bigram_only:
                warn_ll_bigram_only = False
                warn("log-likelihood is only implemented for 2grams. "
                     "Defaults to 0.0 for n>2")
            ll_final = 0.0
        feats.append( Feature( "ll_" + corpus_name, ll_final ) )
    return feats

################################################################################

def interpret_measures( measures_string ) :
    """
        Parses the names of the AMs from the command line. It verifies that the
        names of the AMs are valid names of available measures that can be
        calculated by the script.
        
        @param measures_string A string containing the names of the AMs the user
        wants to calculate separated by ":" colon.
        
        @return A list os strings containing the names of the AMs we need to 
        calculate.
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
    global measures
    global supported_measures
    global main_freq
    global not_normalize_mle
    global input_filetype_ext
    global output_filetype_ext
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
        
    for ( o, a ) in opts:
        if o in ( "-m", "--measures" ) :
            try :
                measures = interpret_measures( a )
            except ValueError as message :
                error( str(message) + "\nargument must be list separated by "
                                      "\":\" and containing the names: " +
                       str( supported_measures ))
        elif o in ( "-o", "--original" ) :
            main_freq = a
        elif o in ( "-u", "--unnorm-mle" ) :
            not_normalize_mle = True
        elif o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)


################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "measures=", "original=", "unnorm-mle"]
args = read_options( "m:o:u", longopts, treat_options, -1, usage_string )

printer = FeatureAdderPrinter()
filetype.parse(args, printer, input_filetype_ext)
