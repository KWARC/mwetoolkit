#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# filter.py is part of mwetoolkit
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
    This script filters the candidate list based:
        1) On the number of occurrences of the candidate. The threshold might
        be defined individually for each corpus. Candidates occurring less than
        the threshold are filtered out.
        2) On the order of the candidates. Only the top n candidates are kept in
        the list. This operation is called "crop" the candidate list. The script
        "head.py" does exactly the same thing (duh!).
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax

from xmlhandler.candidatesXMLHandler import CandidatesXMLHandler
from util import usage, read_options, treat_options_simplest, verbose
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s [OPTIONS] <candidates.xml>

OPTIONS may be:

-t <source>:<value> OR --threshold <source>:<value>    
    Defines a frequency threshold below which the candidates are filtered out.
    This means that if a certain candidates appears less than <value> times in a
    corpus named <source>, these candidate be removed from the output. Only 
    candidates occurring <value> times or more in the <source> corpus are 
    considered. Please remark that the <source> name must be provided exactly as
    it appears in the candidate list. If no <source> is given, all the corpora
    will be considered with the same threshold value (this might not be a good 
    idea when corpora sizes differ significantly). The <value> argument must be
    a non-negative integer, but setting <value> to 0 is the same as not 
    filtering the candidates at all.

-c <n> OR --crop <n>
    Defines the number of candidates that will be kept in the output list. If
    the resulting list contains more than <n> candidates, the remainder will be
    ignored. This means that only the first <n> candidates are kept in the list.
    
    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""
thresh_source = None
thresh_value = 0
crop_limit = -1
crop_count = 0
entity_counter = 0
     
################################################################################
       
def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.
        
        @param meta The `Meta` header that is being read from the XML file.        
    """   
    
    print meta.to_xml().encode( 'utf-8' ) 

################################################################################
       
def treat_candidate( candidate ) :
    """
        For each candidate, verifies whether its number of occurrences in a 
        given source corpus is superior or equal to the threshold. If no source
        corpus was provided (thresh_source is None), then all the corpora will
        be considered when verifying the threshold constraint. A candidate is
        printed to stdout only if it occurrs thres_value times or more in the
        corpus names thresh_source.
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    global thresh_source, thresh_value, crop_limit, crop_count, entity_counter
    if entity_counter % 100 == 0 :
        verbose( "Processing candidate number %(n)d" % { "n":entity_counter } )

    print_it = True    
    for freq in candidate.freqs :
        if thresh_source :
            if ( thresh_source == freq.name or \
                 thresh_source == freq.name + ".xml" ) and \
                 freq.value < thresh_value :
                print_it = False
        else :
            if freq.value < thresh_value :
                print_it = False
                
    if crop_limit > -1 and crop_count >= crop_limit :
        print_it = False
        
    if print_it :   
        print candidate.to_xml().encode( 'utf-8' )
        crop_count = crop_count + 1
    entity_counter += 1
    
################################################################################

def interpret_threshold( a ) :
    """
        Interprets the argument of the -t option, that describes a threshold 
        value given a certain source corpus name, in the form <source>:<value>.
        The first part, <source>:, might be ommited, in which case the threshold
        will be applied for all corpora in which the candidate was counted.
        
        @param a The string argument of the -t option
        
        @return a tuple containing (source, value) - where source can be None if
        undefined - that corresponds to the argument. If the provided argument
        is not valid (not a valid pair <source>:<value>), this function returns
        None. No verification is made in order to assure whether <source> is a 
        valid corpus name: this should be done by the user.
    """
    argument_parts = a.split( ":" )
    try :
        if len(argument_parts) == 1 :
            return ( None, int( argument_parts[0] ) )
        elif len(argument_parts) == 2 :
            return ( argument_parts[ 0 ], int( argument_parts[ 1 ] ) )
        else :
            return None
    except TypeError :
        return None        
    except ValueError : # No integer provided in second part
        return None

################################################################################

def interpret_crop( a ) :
    """
        Interprets the argument of the -c option, that describes a cropping 
        limit, i.e. the number of top candidates to be considered.
        
        @param a The string argument of the -t option
        
        @return An integer containing the crop limit, or `None` if it is invalid
    """
    try :
        crop_limit = int( a )
        if crop_limit >= 0 :
            return crop_limit
        else :
            return None
    except TypeError :
        return None        
    except ValueError : # No integer provided in second part
        return None


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global thresh_source, thresh_value, crop_limit
    for ( o, a ) in opts:
        if o in ( "-t", "--threshold" ) : 
            threshold = interpret_threshold( a )
            if threshold :
                (thresh_source, thresh_value) = threshold
            else :
                print >> sys.stderr, "The format of the -t argument must be" + \
                                     " <source>:<value>"
                print >> sys.stderr, "<source> must be a valid corpus name " + \
                                     "and <value> must be a non-negative " + \
                                     "integer"
                usage( usage_string )
                sys.exit( 2 ) 
        elif o in ( "-c", "--crop" ) :  
            crop_limit = interpret_crop( a )
            if crop_limit is None :
                print >> sys.stderr, "The format of the -c argument must be" + \
                                     " <n>"
                print >> sys.stderr, "<n> must be a non-negative integer"
                usage( usage_string )
                sys.exit( 2 )            
            
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################
# MAIN SCRIPT

longopts = [ "verbose", "threshold=", "crop=" ]
arg = read_options( "vt:c:", longopts, treat_options, 1, usage_string )

try :    
    print """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE candidates SYSTEM "dtd/mwetoolkit-candidates.dtd">
<candidates>
"""     
    input_file = open( arg[ 0 ] )        
    parser = xml.sax.make_parser()
    candHandler = CandidatesXMLHandler( treat_meta, treat_candidate )
    parser.setContentHandler( candHandler ) 
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
