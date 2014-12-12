#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
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
    This script combines several frequency sources. For instance, if each n-gram
    was counted in three different frequency sources (corpora or web), it is 
    possible to combine them in a single frequency with a given combination
    heuristic. Three combination heuristics are implemented: uniform, inverse 
    and backoff.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import math

from libs.base.frequency import Frequency
from libs.base.corpus_size import CorpusSize
from libs.util import usage, read_options, treat_options_simplest, verbose
from libs import filetype



################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python {program} OPTIONS <candidates.xml>

The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).


OPTIONS may be:

-c <comb> OR --combination <comb>
    The name of the frequency combination heuristics that will be calculated. If 
    the option is not defined, the script calculates all available combinations.
    Combination names should be separated by colon ":" and should be in the list 
    of supported combination heuristics below:

    uniform -- Same uniform weight 1/n for all n frequency sources
    inverse -- Weight inversely proportional to the corpus size of the freq. 
    source
    backoff -- If main_freq is below automatically calculated threshold, use the
    web frequencies. A web freq. contains "google" or "yahoo" in its name.

-o <name> OR --original <name>
    The name of the frequency source from which the candidates were extracted
    originally. This is only necessary if you are using backoff to combine the
    counts. In this case, you MUST define the original count source and it must
    be a valid name described through a <corpussize> element in the meta header.

{common_options}
"""
supported_combination = [ "uniform", "inverse", "backoff" ]
corpussize_dict = {}
combination = supported_combination

################################################################################

def backoff_threshold( corpus_size ):
    """
        Based on the corpus size, calculates automatically a threshold below
        which the original frequency will be discarded and the mean of web 
        frequencies will be used instead.
        
        @param corpus_size Integer with the size (nb. of word tokens) of 
        original frequency source
        
        @return A threshold value below which the original count is replaced by
        backed-off count.
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
        
        @param freqs A list of the names of all frequency sources in the file
        
        @return A list containing a subset of the input list, corresponding to
        the names of web frequencies.
    """
    result = {}
    for (name, freq) in freqs.items() :
        if "yahoo" in name.lower() or "google" in name.lower() :
            result[ name ] = freq
    return result

################################################################################

def combine( method, freqs ):
    """
        Generates a unique count using a given combination heuristic and a list
        of original counts.
        
        @param method A string with the name of the combination heuristic to 
        use. This name may be one of the following: "uniform", "inverse", 
        "backoff". All other values will be ignored.
        
        @param freqs A list of integers containing the original word counts. The
        list contains as many elements as there are frequency sources in the
        candidates list.
        
        @return A tuple cotaining (combined_count, backed_off). The former is a
        float containing the combined count using a given method, the latter is
        a boolean flag that indicates that the combined count was backed off.
    """
    global corpussize_dict
    global main_freq
    # Weight of each corpus is its size
    if method =="uniform" :
        avg_count = float( sum( freqs.values() ) ) / len( freqs.values() )
        return ( avg_count, False )
    # Corpora have all the same weight, frequencies are 0..1
    elif method == "inverse" :
        result = 0.0
        total_size = float( sum( corpussize_dict.values() ) )
        for ( name, freq ) in freqs.items() :
            weight = ( ( total_size - corpussize_dict[ name ] ) / total_size )
            result += weight * freq
        return ( result, False )
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
                    avg_web = - ( sum(w_freqs.values()) / len(w_freqs.values()))
                    return ( avg_web, backed_off )
                else :
                    backed_off = False
                    return ( freq, backed_off )


################################################################################     

class FreqCombinerHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, None)
        self.chain.before_file(fileobj, info)

    def handle_meta(self, meta, info={}) :
        """
            Adds new meta-features corresponding to the new frequency sources that
            are being added to the corpus. The new corpus sizes are calculated based
            on the combination heuristics.
            
            @param meta The `Meta` header that is being read from the XML file.       
        """
        global corpussize_dict, combination
        for corpus_size in meta.corpus_sizes :
            corpussize_dict[ corpus_size.name ] = float(corpus_size.value)
        for comb in combination :        
            if comb == "backoff" :
                w_freqs = web_freqs( corpussize_dict )
                combined = int( combine( "uniform", w_freqs )[ 0 ] )
                meta.add_corpus_size( CorpusSize( comb, combined ) )
            else :
                combined = int( combine( comb, corpussize_dict )[ 0 ] )
                meta.add_corpus_size( CorpusSize( comb, combined ) )
        self.chain.handle_meta(meta)


    def handle_candidate(self, candidate, info={}) :
        """
            For each candidate in the file, add the combined frequencies both for 
            the whole n-gram and for the individual words. The resulting candidate
            contains both the original counts from the original frequency sources
            and the new combined counts calculated based on the original counts.
            
            @param candidate The `Candidate` that is being read from the XML file.    
        """
        global corpussize_dict
        global combination
        global main_freq
        joint_freq = {}    
        backed_off = False    
        # Convert all these integers to floats...
        for freq in candidate.freqs :
            joint_freq[ freq.name ] = float( freq.value )

        for comb in combination :
            (combined, bo) = combine( comb,joint_freq )
            if bo :
                backed_off = True
            candidate.add_frequency( Frequency( comb, int( combined ) ) )

        for word in candidate :
            singleword_freq = {}
            for freq in word.freqs :
                singleword_freq[ freq.name ] = float( freq.value )
            for comb in combination :
                # Force backing off individual words if the whole n-gram was backed
                # off.
                if comb == "backoff" and backed_off :
                    singleword_freq[ main_freq ] = 0.0 # Forces to backoff
                    combined = int( combine( comb, singleword_freq )[ 0 ] )
                word.add_frequency(Frequency(comb,combined))
        self.chain.handle_candidate(candidate, info)


################################################################################

def interpret_combinations( combination_string ) :
    """
        Parses the names of the combination heuristics from the command line. 
        It verifies that the names of the combination heuristics are valid names 
        of available combinations that can be calculated by the script.
        
        @param combination_string A string containing the names of the 
        combination heuristics the user    wants to calculate separated by ":"
        colon.
        
        @return A list os strings containing the names of the combinaiton 
        heuristics we need to calculate.    
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
    global combination
    global supported_combination
    global main_freq
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
        
    for ( o, a ) in opts:
        if o in ( "-c", "--combination" ) :
            try :
                combination = []
                combination = interpret_combinations( a )
            except ValueError as message :
                print >> sys.stderr, message
                print >> sys.stderr, "ERROR: argument must be list separated"+ \
                                     "by \":\" and containing the names: "+\
                                     str( supported_combination )
                usage( usage_string )
                sys.exit( 2 )
        elif o in ( "-o", "--original" ) :
            main_freq = a
    
################################################################################
# MAIN SCRIPT

longopts = [ "combination=", "original=" ]
args = read_options( "c:o:", longopts, treat_options, -1, usage_string )

filetype.parse(args, FreqCombinerHandler())
