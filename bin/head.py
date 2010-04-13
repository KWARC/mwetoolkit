#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
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
#!/usr/bin/python
"""
    Prints the first N entities of a list. Works like the "head" command in
    the unix platform, only it takes a file in xml format as input.
    
    This script is DTD independent, that is, it might be called on a corpus 
    file, on a list of candidates or on a dictionary.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import pdb

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import usage, read_options, treat_options_simplest

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s OPTIONS <file.xml>

    OPTIONS may be:

-n OR --number
    Number of entities that you want to print out. Default value is 10.

-v OR --verbose
    Print messages that explain what is happening.

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""
limit = 10
entity_counter = 0

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' )

################################################################################

def treat_entity( entity ) :
    """
        For each entity in the file, prints it if the limit is still not
        achieved. No buffering as in tail, this is not necessary here.

        @param entity A subclass of `Ngram` that is being read from the XML.
    """
    global entity_counter, limit
    if entity_counter < limit :
        print entity.to_xml()
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
    print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    print "<!DOCTYPE corpus SYSTEM \"dtd/mwttoolkit-corpus.dtd\">"
    print "<corpus>"
    parser = xml.sax.make_parser()
    parser.setContentHandler( GenericXMLHandler( treat_meta=treat_meta,
                                                 treat_entity=treat_entity ) )
    if len( arg ) == 0 :
        parser.parse( sys.stdin )
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            input_file.close()
    print "</corpus>"
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"


