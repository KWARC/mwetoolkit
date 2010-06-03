#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# combine_freqs.py is part of mwetoolkit
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
    This script TODO: ADD DESCRIPTION
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import math
import pdb

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from xmlhandler.classes.feature import Feature
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.corpus_size import CorpusSize
from util import usage, read_options, treat_options_simplest, \
                 verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <main_freq> <candidates.xml>

<main_freq> is the name of the main frequency source, used in back-off
combination to guess when it is necessary to back-off and when we use the
original main_freq frequency. Should be a valid name of a frequency with a meta
header for the corpus size.

OPTIONS may be:

-c OR --combination
    TODO: describe

-v OR --verbose
    Print messages that explain what is happening.

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""
supported_combination = [ "uniform", "inverse", "backoff" ]
corpussize_dict = {}
combination = supported_combination
# TODO: Parametrable combine function
# heuristic_combine = lambda l : sum( l ) / len( l ) # Arithmetic mean
backed_off = False

################################################################################

def backoff_threshold( corpus_size ):
    """
    """
    return math.log( float( corpus_size ) / 100000.0, 2 )

################################################################################

def web_freqs( freqs ) :
    """
        Given a list of strings, returns a sub-list containing only those
        strings that correspond to the names of Web-based counts. This is
        totally hard-coded because there's no information in the freq element
        that tells whether the count comes from a corpus or from the Web (this
        should be easy to modify in the DTD and in the count script, though)
    """
    result = {}
    for (name, freq) in freqs.items() :
        if "yahoo" in name.lower() or "google" in name.lower() :
            result[ name ] = freq
    return result

################################################################################

def combine( method, freqs ):
    """
    """
    global corpussize_dict, backed_off, main_freq
    # Weight of each corpus is its size
    if method =="uniform" :
        return float( sum( freqs.values() ) ) / len( freqs.values() )
    # Corpora have all the same weight, frequencies are 0..1
    elif method == "inverse" :
        result = 0.0
        total_size = float( sum( corpussize_dict.values() ) )
        for ( name, freq ) in freqs.items() :
            weight = ( ( total_size - corpussize_dict[ name ] ) / total_size )
            result += weight * freq
        return result
    elif method == "backoff" :
        for (name, freq ) in freqs.items() :
            if name == main_freq :
                if freq < backoff_threshold( corpussize_dict[ name ] ) :
                    backed_off = True
                    w_freqs = web_freqs( freqs )
                    # The minus is to signal that we backed off. It will be
                    # ignored since abs value is taken to calculate association
                    # measures. However, it is important that the association
                    # measures script knows that this is a back-off, since the
                    # value of N is different for "backed off" and "did not back
                    # off".
                    return - ( sum(w_freqs.values()) / len(w_freqs.values() ) )
                else :
                    backed_off = False
                    return freq


################################################################################     
       
def treat_meta( meta ) :
    """
        Adds new meta-features corresponding to the AM features that we add to
        each candidate. The meta-features define the type of the features, which
        is a real number for each of the 4 AMs in each corpus.
        
        @param meta The `Meta` header that is being read from the XML file.       
    """
    global corpussize_dict, combination
    for corpus_size in meta.corpus_sizes :
        corpussize_dict[ corpus_size.name ] = float(corpus_size.value)
    for comb in combination :        
        if comb == "backoff" :
            meta.add_corpus_size( CorpusSize( comb, int( combine( "uniform", web_freqs( corpussize_dict ) ) ) ) )
        else :
            meta.add_corpus_size( CorpusSize( comb, int( combine( comb, corpussize_dict ) ) ) )
    print meta.to_xml().encode( 'utf-8' )
       
################################################################################     
       
def treat_candidate( candidate ) :
    """
        
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global corpussize_dict, combination, backed_off, main_freq
    joint_freq = {}    
    # Convert all these integers to floats...
    for freq in candidate.freqs :
        joint_freq[ freq.name ] = float(freq.value)

    for comb in combination :
        candidate.add_frequency(Frequency(comb,int(combine(comb,joint_freq))))

    for word in candidate :
        singleword_freq = {}
        for freq in word.freqs :
            singleword_freq[ freq.name ] = float( freq.value )
        for comb in combination :
            # Force backing off individual words if the whole n-gram was backed
            # off.
            if comb == "backoff" and backed_off :
                singleword_freq[ main_freq ] = 0.0 # Forces to backoff
            word.add_frequency(Frequency(comb,int(combine(comb,singleword_freq))))
    
    print candidate.to_xml().encode( 'utf-8' )

################################################################################

def interpret_combinations( combination_string ) :
    """
    """
    global supported_combination
    combination_list = combination_string.split( ":" )
    result = []
    for comb_name in combination_list :
        if comb_name in supported_combination :
            result.append( comb_name )
        else :
            raise ValueError, "ERROR: combination is not supported: " + \
                              str(comb_name)
    return result

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global combination, supported_combination
    for ( o, a ) in opts:
        if o in ( "-m", "--measures" ) :
            try :
                combination = []
                combination = interpret_combination( a )
            except ValueError, message :
                print >> sys.stderr, message
                print >> sys.stderr, "ERROR: argument must be list separated"+ \
                                     "by \":\" and containing the names: "+\
                                     str( supported_combination )
                usage( usage_string )
                sys.exit( 2 )
    treat_options_simplest( opts, arg, n_arg, usage_string )
################################################################################
# MAIN SCRIPT

longopts = ["verbose", "combination="]
arg = read_options( "vc:", longopts, treat_options, 2, usage_string )

try :    
    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "dtd/mwetoolkit-candidates.dtd">
<candidates>
"""
    main_freq = arg[ 0 ]
    input_file = open( arg[ 1 ] )
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
