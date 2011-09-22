#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# util.py is part of mwetoolkit
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
    Set of utility functions that are common to several scripts.
"""

import getopt
import sys

################################################################################

verbose_on = False

################################################################################

def set_verbose( value ) :
    """
    """
    global verbose_on
    verbose_on = value

################################################################################

def verbose( message ) :
    """
    """
    global verbose_on
    if verbose_on :
        print >> sys.stderr, message

################################################################################

def usage( usage_string ) :
    """
        Print detailed instructions about the use of this program. Each script
        that uses this function should provide a variable containing the
        usage string.
    """
    print >> sys.stderr, usage_string % {"program": sys.argv[ 0 ]}
    
################################################################################

def treat_options_simplest( opts, arg, n_arg, usage_string ) :
    """
        Verifies that the number of arguments given to the script is correct.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.
    """
    for ( o, a ) in opts:      
        if o in ("-v", "--verbose") :
            set_verbose( True )
            verbose( "Verbose mode on" )            
    
    if n_arg >= 0 and len( arg ) != n_arg :
        print >> sys.stderr, "You must provide %(n)s arguments to this script" \
                             % { "n" : n_arg }
        usage( usage_string )
        sys.exit( 2 )

################################################################################     

def read_options( shortopts, longopts, treat_options, n_args, usage_string ) :
    """
        Generic function that parses the input options using the getopt module.
        The options are then treated through the `treat_options` callback.
        
        @param shortopts Short options as defined by getopts, i.e. a sequence of
        letters and colons to indicate arguments.
        
        @param longopts Long options as defined by getopts, i.e. a list of 
        strings ending with "=" to indicate arguments.
        
        @param treat_options Callback function, receives a list of strings to
        indicate parsed options, a list of strings to indicate the parsed 
        arguments and an integer that expresses the expected number of arguments
        of this script.
    """
    try:
        opts, arg = getopt.getopt( sys.argv[ 1: ], shortopts, longopts )
    except getopt.GetoptError, err:
        # will print something like "option -a not recognized"
        print >> sys.stderr, str( err ) 
        usage( usage_string )
        sys.exit( -1 )

    treat_options( opts, arg, n_args, usage_string ) 
    return arg
        
################################################################################             

def strip_xml( the_string ) :
    """
    """
    cleanContent = the_string
    cleanContent = cleanContent.replace( "&", "&amp;" ) # Escape sequence
    cleanContent = cleanContent.replace( "<", "&lt;" ) # Escape sequence
    cleanContent = cleanContent.replace( ">", "&gt;" ) # Escape sequence
    cleanContent = cleanContent.replace( "\"", "&quot;" ) # Escape sequence
    cleanContent = cleanContent.replace( "*", "&lowast;" ) # Escape WILDCARD (TODO: better generic handling of WILDCARD, since it might be changed in config file)
    return cleanContent
        
################################################################################

def interpret_ngram( argument ) :
    """
        Parses the argument of the "-n" option. This option is of the form
        "<min>:<max>" and defines the length of n-grams to extract. For 
        instance, "3:5" extracts ngrams that have at least 3 words and at most 5 
        words. If you define only <min> or only <max>, the default is to 
        consider that both have the same value. The value of <min> is at least 
        1, <max> is at most 10. Generates an exception if the syntax is 
        incorrect, generates a None value if the arguments are incoherent 
        (e.g. <max> < <min>)
        
        @param argument String argument of the -n option, has the form 
        "<min>:<max>"
        
        @return A tuple (<min>,<max>) with the two integer limits, or None if
        the argument is incoherent.
    """
    try:
        if ":" in argument :
            [ n_min, n_max ] = argument.split( ":" )
            n_min = int(n_min)
            n_max = int(n_max)
        else :
            n_min = int(argument)
            n_max = int(argument)
        if n_min <= n_max and n_min >= 1 and n_max <= 10:                
            return ( n_min, n_max )
        else :                
            return None
    except IndexError :
        return None
    except TypeError :
        return None
    except ValueError :
        return None

