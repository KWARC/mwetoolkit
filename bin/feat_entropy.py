#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# feat_entropy.py is part of mwetoolkit
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
    This script adds entropy fetures based on a number of variations. It may
    only be called with candidate files containing <vars> elements. The way
    entropy is calculated can be changed through the command line options.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import pdb
import math

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.classes.feature import Feature
from xmlhandler.classes.meta_feat import MetaFeat
from util import read_options, treat_options_simplest, verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (mwetoolkit-candidates.dtd).
"""     
all_patterns = {}
     
################################################################################
       
def treat_meta( meta ) :
    """
        Adds two new meta-features corresponding to the features that we add to
        each candidate. The meta-features define the type of the features, which
        is an enumeration of all possible POS patterns for the POS pattern and
        an integer number for the size n of the candidate.
        
        @param meta The `Meta` header that is being read from the XML file.        
    """
    global all_patterns
    pattern_feat_values = "{"
    for corpus_size in meta.corpus_sizes :
        meta.add_meta_feat( MetaFeat( "entropy_" + corpus_size.name, "real" ) )        
    print meta.to_xml()

################################################################################

def entropy( probabilities ) :
    """
        Given a list of probabilities, calculates the entropy as -sum(p*log(p))
    """
    ent = 0
    #pdb.set_trace()
    for p in probabilities :
        if p != 0 :
            ent = ent - p * math.log( p )
    return ent

################################################################################

def probs_from_varfreqs( varfreqs ) :
    """
       Gives the a list of probabilities as the relative frequency of each
       variation, i.e. generates a percent list from an absolute count list.
    """
    probabilities = []
    sum_vf = 0.0
    for vf in varfreqs :
        sum_vf = sum_vf + vf
    if sum_vf != 0 :
        for vf in varfreqs :
            probabilities.append( vf / sum_vf )
    return probabilities

################################################################################

def probs_weighted( varfreqs, weights ) :
    """
        Gives the list of probabilities but considers a weight in the
        calculation, which is going to be divided by each probability 
        frequency. Each frequency must have a weight, i.e. the inputs must
        have the same number of elements.
    """
    probabilities = []
    sum_vf = 0.0
    for vfi in range(len(varfreqs)) :
        if weights[ vfi ] == 0 :
            pdb.set_trace()
        sum_vf = sum_vf + ( varfreqs[ vfi ] / float( weights[ vfi ] ) )
    if sum_vf != 0 :       
        for vfi in range(len(varfreqs)) :
            probabilities.append( ( varfreqs[ vfi ] / float( weights[ vfi ] ) ) / sum_vf )
    return probabilities
       
################################################################################

def treat_candidate( candidate ) :
    """
        For each candidate, generates two new features that correspond to the
        POS pattern and to the number of words in the candidate. Then, prints
        the new candidate with the two extra features.
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    pattern = candidate.get_pos_pattern()
    #pdb.set_trace()
    freq_table = {}
    weight_table = {}
    #pdb.set_trace()
    f_det = candidate[ 1 ].get_freq_value( "bnc" ) + candidate[ 2 ].get_freq_value( "bnc" )
    for variation in candidate.vars :
    	for freq in variation.freqs :
            f_list = freq_table.get( freq.name, [] )
            w_list = weight_table.get( freq.name, [] )
            f_list.append( freq.value )
            w_list.append( int(variation[ 0 ].get_freq_value("bnc")) * f_det * int(variation[2].get_freq_value("bnc")) )
            freq_table[ freq.name ] = f_list
            weight_table[ freq.name ] = w_list
    for source in freq_table.keys() :
        ent = entropy( probs_from_varfreqs( freq_table[ source ] ) )
        ent_w = entropy( probs_weighted( freq_table[ source ], weight_table[ source ] ) )
	candidate.add_feat( Feature( "entropy_" + source, str( ent ) ) )
	candidate.add_feat( Feature( "entropy_w_" + source, str( ent_w ) ) )
    print candidate.to_xml().encode( 'utf-8' )

################################################################################
# MAIN SCRIPT
longopts = [ "verbose" ]
arg = read_options( "v", longopts, treat_options_simplest, 1, usage_string )

try :    
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    handler = CandidatesXMLHandler( treat_meta=treat_meta,
                                    treat_candidate=treat_candidate,
                                    gen_xml=True)
    parser.setContentHandler( handler )
    parser.parse( input_file )
    input_file.close()    
    print handler.footer
     
except IOError, err :
    print >> sys.stderr, err
