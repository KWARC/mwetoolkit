#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# head.py is part of mwetoolkit
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
    Prints the first N entities of a list. Works like the "head" command in
    the unix platform, only it takes a file in xml format as input.
    
    This script is DTD independent, that is, it might be called on a corpus 
    file, on a list of candidates or on a dictionary.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.genericXMLHandler import GenericXMLHandler
from libs.util import read_options, treat_options_simplest, verbose, parse_xml,\
    error
from libs.parser_wrappers import StopParsing

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s OPTIONS <files.xml>

OPTIONS may be:

-n OR --number
    Number of entities that you want to print out. Default value is 10.

%(common_options)s

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
limit = 10
entity_counter = 0

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
        For each entity in the file, prints it if the limit is still not
        achieved. No buffering as in tail, this is not necessary here.

        @param entity A subclass of `Ngram` that is being read from the XML.
    """
    global entity_counter, limit
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    if entity_counter < limit :
        print(entity.to_xml().encode('utf-8'))
    else :
        raise StopParsing
    entity_counter += 1

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global limit
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
        
    for ( o, a ) in opts:
        if o in ("-n", "--number") :
            try :
                limit = int( a )
                if limit < 0 :
                    raise ValueError
            except ValueError :
                error("You must provide a positive " + \
                                     "integer value as argument of -n option.")

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

arg = read_options( "n:", [ "number=" ], treat_options, -1, usage_string )
handler = GenericXMLHandler( treat_meta=treat_meta,
                             treat_entity=treat_entity,
                             gen_xml=True )                             
parse_xml( handler, arg, reset_entity_counter )
print(handler.footer)
