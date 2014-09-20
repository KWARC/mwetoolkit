#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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

        2) On whether they match one of a set of patterns. The patterns are
        in the same format as used by candidates.py, except that they are
        'anchored' by default (i.e., they must match the whole n-gram, not just
        part of it).
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
import sys

from libs.genericXMLHandler import GenericXMLHandler
from libs.patternlib import parse_patterns_file, match_pattern
from libs.util import read_options, treat_options_simplest, verbose, \
    parse_xml, error
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s [OPTIONS] <candidates.xml>

OPTIONS may be:

-p <patterns.xml> OR --patterns <patterns.xml>
    The patterns to keep in the file, valid XML (mwetoolkit-dict.dtd)
    Note that unlike candidates.py, this scripts treats patterns as 'anchored',
    i.e., they must match the whole ngram, not just a part of it.

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

-e <name>:<value> OR --equals <name>:<value>
    Defines an equality filter on the value of a feature. Only the candidates
    where the feature <name> is equal to <value> will be kept in the list.

-r OR --reverse
    Reverses the filtering mechanism, in order to print out only those 
    candidates that do NOT obbey the criteria.

%(common_options)s

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""
reverse = False
thresh_source = None
thresh_value = 0
equals_name = None
equals_value = None
entity_counter = 0
patterns = []
longest_pattern = 0
shortest_pattern = sys.maxint
     
################################################################################
       
def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.
        
        @param meta The `Meta` header that is being read from the XML file.        
    """   
    
    print(meta.to_xml().encode( 'utf-8' ))

################################################################################
       
def treat_entity( entity ) :
    """
        For each candidate, verifies whether its number of occurrences in a 
        given source corpus is superior or equal to the threshold. If no source
        corpus was provided (thresh_source is None), then all the corpora will
        be considered when verifying the threshold constraint. A candidate is
        printed to stdout only if it occurrs thres_value times or more in the
        corpus names thresh_source.
        
        @param entity The `Ngram` that is being read from the XML file.
    """
    global thresh_source
    global thresh_value
    global equals_name
    global equals_value
    global entity_counter
    global reverse
    global patterns

    if entity_counter % 100 == 0 :
        verbose( "Processing entity number %(n)d" % { "n":entity_counter } )

    print_it = True
    ngram_to_print = entity

    # Threshold test
    for freq in entity.freqs :
        if thresh_source :
            if ( thresh_source == freq.name or
                 thresh_source == freq.name + ".xml" ) and \
                 freq.value < thresh_value :
                print_it = False
        else :
            if freq.value < thresh_value :
                print_it = False
    # Equality test
    if print_it and equals_name :
        print_it = False
        for feat in entity.features :
            if feat.name == equals_name and feat.value == equals_value :
                print_it = True


    # NOTE: Different patterns may match the same ngram, with different
    # results, when the 'ignore' pattern attribute is involved. Currently,
    # we are only printing the first such match.
    if print_it and patterns :
        print_it = False
        words = entity
        for pattern in patterns :
            for (match_ngram, wordnums) in match_pattern(pattern, words) :
                print_it = True
                ngram_to_print = match_ngram
                break
            if print_it :
                break

    if reverse :
        print_it = not print_it

    if print_it :   
        print(ngram_to_print.to_xml().encode( 'utf-8' ))
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

def interpret_equals( a ) :
    """
        Interprets the argument of the -e option, that describes an equality
        filter.
        
        @param a The string argument of the -e option
        
        @return A pair of strings with the name and the value of the filtering
        criterium. None if the argument is invalid.
    """
    argument_parts = a.split( ":" )
    if len(argument_parts) == 2 :
        return ( argument_parts[ 0 ], argument_parts[ 1 ] )
    else :
        return None

################################################################################

def read_patterns_file( filename ) :
    """
        NEW:
        Opens the patterns XML file and parses it using patternlib.

        @param filename The string name of the patterns file.
    """
    global patterns

    try:
        patterns = parse_patterns_file(filename, anchored=True)
    except IOError as err:
        error(str(err))

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global thresh_source
    global thresh_value
    global equals_name
    global equals_value
    global reverse
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
    for ( o, a ) in opts:
        if o in ( "-t", "--threshold" ) : 
            threshold = interpret_threshold( a )
            if threshold :
                (thresh_source, thresh_value) = threshold
            else :
                error( "The format of the -t argument must be <source>:"
                       "<value>\n<source> must be a valid corpus name and "
                       "<value> must be a non-negative integer")
        elif o in ( "-e", "--equals" ) :
            equals = interpret_equals( a )
            if equals :
                ( equals_name, equals_value ) = equals
            else :
                error( "The format of the -e argument must be <name>:"
                       "<value>\n<name> must be a valid feat name and "
                       "<value> must be a non-empty string")
        elif o in ("-p", "--patterns") :
            verbose( "Reading patterns file" )
            read_patterns_file( a )
        elif o in ("-r", "--reverse") :
            reverse = True
            verbose( "Option REVERSE active")
            
################################################################################

def reset_entity_counter( filename ) :
    """
        After processing each file, simply reset the entity_counter to zero.
        
        @param filename Dummy parameter to respect the format of postprocessing
        function
    """
    global entity_counter
    entity_counter = 0
    
################################################################################
# MAIN SCRIPT

longopts = [ "threshold=", "equals=", "patterns=", "reverse" ]
arg = read_options( "t:e:p:r", longopts, treat_options, -1, usage_string )
handler = GenericXMLHandler( treat_meta=treat_meta,
                             treat_entity=treat_entity,
                             gen_xml=True )
parse_xml( handler, arg, reset_entity_counter )
print(handler.footer)

