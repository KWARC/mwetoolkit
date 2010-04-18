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

def calculate_ams( f, m_list, N, corpus_name ) :
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
    f_sum = 0
    n = len( m_list )
    f_null = 1 / math.pow( N, n - 1 )
    for m_i in m_list :
        f_null *= m_i
        f_sum += m_i
    
    mle = f / N  
    if f_null != 0.0 and f != 0:
        pmi = math.log( f / f_null, 2 ) + (n - 1) * math.log( N, 2 )
    else :
        pmi = 0.0
    if f != 0.0 :
        t = ( f - f_null ) / math.sqrt( f )
    else :
        t = 0.0
    if f_sum != 0.0 :
        dice = ( n * f ) / f_sum
    else :
        dice = 0.0

    feats = []
    feats.append( Feature( "mle_" + corpus_name, mle ) )
    feats.append( Feature( "pmi_" + corpus_name, pmi ) )
    feats.append( Feature( "t_" + corpus_name, t ) )
    feats.append( Feature( "dice_" + corpus_name, dice ) )    
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
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-candidates.dtd)"
