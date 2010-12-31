#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# feat_contrast.py is part of mwetoolkit
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
    This script adds a new feature which is the contrastive score of a frequency
    compared to another "contrastive" corpus. The idea is to filter 
    out-of-domain candidate MWEs out of the data.
    
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
    
python %(program)s -o <name> OPTIONS <candidates.xml>

-o <name> OR --original <name>
    The name of the frequency source from which the candidates were extracted
    originally. This is only necessary because all other frequency sources will
    be considered as contrastive corpora. You may choose if you'd like to have 
    one feature per contrastive corpus or a single feature for all the 
    contrastive corpora as in the original formulation of the measure.

OPTIONS may be:

-m <meas> OR --measures <meas>
    The name of the measures that will be calculated. If this option is not
    defined, the script calculates all available measures. Measure names should
    be separated by colon ":" and should be in the list of supported measures
    below:

    csmwe -- Original measure proposed by Bonin et al. 2010
    simplediff -- Simply divides the original frequency by contrastive frequency
    ...

-a OR --all
    Join all contrastive corpora and consider it as a single corpus. The default
    behaviour of this script is to calculate one contrastive score per
    contrastive corpora.

-v OR --verbose
    Print messages that explain what is happening.

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""
supported_measures = [ "csmwe", "simplediff", "simplecsmwe" ]
corpussize_dict = {}
totals_dict = {}
measures = supported_measures
# TODO: Parametrable combine function
# heuristic_combine = lambda l : sum( l ) / len( l ) # Arithmetic mean
entity_counter = 0
join_all_contrastive=False
main_freq_name = None
     
################################################################################     
       
def add_metafeatures( meta ) :
    """
        Adds new meta-features corresponding to the features that we add to
        each candidate. The meta-features define the type of the features, which
        is a real number for each of the contrastive measures in each corpus.
        
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

def initialise_totals( meta ) :
    """
        Reads the `corpus_size` meta header and initializes a global counter
        dictionary with zero for each corpus. This dict will contain the total
        number of candidate frequencies summed up, as in the csmwe original
        formulation.
    
        @param meta The `Meta` header that is being read from the XML file.          
    """
    global totals_dict, main_freq_name
    main_freq_valid = False    
    for corpus_size in meta.corpus_sizes :
        totals_dict[ corpus_size.name ] = 0
        if corpus_size.name == main_freq_name :
            main_freq_valid = True    
    if not main_freq_valid :
        print >> sys.stderr, "ERROR: main frequency must be a valid freq. name"
        print >> sys.stderr, "Possible values: " + str( totals_dict.keys() ),
        raise ValueError
          
################################################################################     

def calculate_totals( candidate ) :
    """
        For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates four features that correspond to the Association
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global totals_dict
    for freq in candidate.freqs :
        totals_dict[ freq.name ] += freq.value
           
################################################################################     
       
def calculate_measures( candidate ) :
    """
        For each candidate and for each `CorpusSize` read from the `Meta` 
        header, generates features that correspond to the Contrastive
        Measures described above.
        
        @param candidate The `Candidate` that is being read from the XML file.    
    """
    global corpussize_dict
    global totals_dict
    global main_freq_name
    global entity_counter
    if entity_counter % 100 == 0 :
        verbose( "Processing candidate number %(n)d" % { "n":entity_counter } )
    # get the original corpus freq, store the others in contrastive corpus dict
    # We use plus one smoothing to avoid dealing with zero freqs    
    contrast_freqs = {}
    if join_all_contrastive :
        contrast_freqs[ "all" ] = 1
    main_freq = None
    for freq in candidate.freqs :
        if freq.name == main_freq_name :
            main_freq = float( freq.value ) + 1 
        elif join_all_contrastive :
            contrast_freqs[ "all" ] += float( freq.value )
        else :
            contrast_freqs[ freq.name ] = float( freq.value ) + 1
    
    for contrast_name in contrast_freqs.keys() :                    
        try :            
            feats = calculate_indiv( corpussize_dict[ main_freq_name ],
                                     corpussize_dict[ contrast_name ],
                                     main_freq, 
                                     contrast_freqs[ contrast_name ], 
                                     totals_dict[ contrast_name ],                                      
                                     contrast_name )
        except Exception :
            print "Error in calculating the measures. Starting Python debugger"
            pdb.set_trace()
                
        for feat in feats :
            candidate.add_feat( feat )
    print candidate.to_xml().encode( 'utf-8' )
    entity_counter = entity_counter + 1

################################################################################

def calculate_indiv( n_main, n_cont, main_freq, 
                     contrast_freq, total_freq, corpus_name ) :
    """
        Calculates the contrastive measures for an individual candidate.
        
    """
    global measures
    feats = []
    if "csmwe" in measures :
        k = math.log( main_freq, 2 )
        x = main_freq / ( contrast_freq / total_freq )
        csmwe = math.atan( k * x )
        feats.append( Feature( "csmwe_" + corpus_name, csmwe ) )
    if "simplediff" in measures :
        simplediff = main_freq / contrast_freq
        feats.append( Feature( "simplediff_" + corpus_name, simplediff ) )
    if "simplecsmwe" in measures :
        simplecsmwe = math.log( main_freq, 2 ) * ( main_freq / contrast_freq )
        feats.append( Feature( "simplecsmwe_" + corpus_name, simplecsmwe ) )            
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
    global measures, supported_measures, main_freq_name, join_all_contrastive
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
        elif o in ( "-o", "--original" ) :
            main_freq_name = a
        elif o in ( "-a", "--all" ) :
            join_all_contrastive = True
    
    if not main_freq_name :
        print >> sys.stderr, "Option -o is mandatory"
        usage( usage_string )
        sys.exit( 2 )
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
################################################################################
# MAIN SCRIPT

longopts = ["verbose", "measures=", "original=", "all"]
arg = read_options( "vm:o:a", longopts, treat_options, 1, usage_string )

try :
    parser = xml.sax.make_parser()
    
    totalcalculator = CandidatesXMLHandler( treat_meta=initialise_totals,
                                            treat_candidate=calculate_totals,
                                            gen_xml=False )
          
    handler = CandidatesXMLHandler( treat_meta=add_metafeatures,
                                    treat_candidate=calculate_measures,
                                    gen_xml="candidates" )

    for a in arg :
        verbose( "Pass 1 for " + a )
        parser.setContentHandler( totalcalculator )    
        input_file = open( a )
        # First calculate Nc for each contrastive corpus        
        parser.parse( input_file )
        input_file.close()
        verbose( "Pass 2 for " + a )
        parser.setContentHandler( handler )            
        input_file = open( a )
        parser.parse( input_file )        
        footer = handler.footer
        handler.gen_xml = False
        input_file.close()        
        entity_counter = 0
    print footer

except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-candidates.dtd)"
