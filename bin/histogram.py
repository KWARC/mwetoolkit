#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
# 
# histogram.py is part of mwetoolkit
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
    Calculates a histogram based on the candidate raw frequencies. In the future
    this script may be adapted to calculate histograms for other features as 
    well.
    
    This script is to be called on a xml candidates file, not on other sorts of
    lists.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import pdb
import math

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import usage, read_options, treat_options_simplest, verbose

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (mwttoolkit-candidates.dtd). 
"""
hist = {}
#ignore_pos = False
#surface_instead_lemmas = False
entity_counter = 0
limit = None

################################################################################         

def treat_candidate( candidate ) :
    """
    """
    global hist
    global entity_counter
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )    
    for f in candidate.freqs :
        one_freq_hist = hist.get( f.name, {} )
        one_freq_hist[ f.value ] = one_freq_hist.get( f.value, 0 ) + 1
        hist[ f.name ] = one_freq_hist
    entity_counter += 1

################################################################################         
       
def print_histogram() :
    global hist
    global limit
    for fname in hist.keys() :
        print "FREQUENCY SOURCE : %(source)s" % { "source" : fname }
        print "Number of candidates : %(n)d" % { "n" : entity_counter }
        print
        h = hist[ fname ]
        entropy = 0
        #entropy_delta = 0
        counter = 0
        for f in sorted( h.keys() ) :        
            p = float( h[ f ] ) / entity_counter
            entropy -= p * math.log( p, 2 )
            #entropy_delta -= p_delta * math.log( p_delta, 2 )
            counter = counter + 1
            if limit is None or counter <= limit :
                print "%(f)d : %(c)d (%(p)f)" % { "f" : f, "c" : h[f], "p" : p }

        print "Entropy : %(e)f" % { "e" : entropy }
        
################################################################################           
  
def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global limit
    for ( o, a ) in opts:
        if o in ("-n", "--number") :
            try :
                limit = int( a )
                if limit < 0 :
                    raise ValueError
            except ValueError :
                print >> sys.stderr, "ERROR: You must provide a positive " + \
                                     "integer value as argument of -n option."
                usage( usage_string )
                sys.exit( 2 )

    treat_options_simplest( opts, arg, n_arg, usage_string )  
       
################################################################################         
# MAIN SCRIPT

longopts = [ "verbose", "number=" ]
arg = read_options( "vn:", longopts, treat_options, -1, usage_string )

try :
    parser = xml.sax.make_parser()
    handler = CandidatesXMLHandler( treat_candidate=treat_candidate,
                                    gen_xml=False )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :        
        parser.parse( sys.stdin )
        print_histogram()        
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            print_histogram()            
            input_file.close()
            hist = {}
            entity_counter = 0
            total  = 0
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"

################################################################################


