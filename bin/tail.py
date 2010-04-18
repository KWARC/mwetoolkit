#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# tail.py is part of mwetoolkit
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
    Prints the last N entities of a list. Works like the "tail" command in
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
from util import usage, read_options, treat_options_simplest, verbose

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS <files.xml>

OPTIONS may be:    
    
-n OR --number
    Number of entities that you want to print out. Default value is 10.

-v OR --verbose
    Print messages that explain what is happening.

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
limit = 10
entity_counter = 0
entity_buffer = [ None ] * limit

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
        For each entity in the corpus, puts it in a circular buffer. This is
        necessary because we do not know the total number of lines, so we always
        keep the last n lines in the global buffer.
        
        @param entity A subclass of `Ngram` that is being read from the XM.
    """
    global entity_counter, entity_buffer, limit
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    if limit > 0 :
        entity_buffer[ entity_counter % limit ] = entity
        entity_counter += 1
    
################################################################################    

def print_entities() :
    """
        After we read all the XML file, we can finally be sure about which lines
        need to be printed. Those correspond exactly to the N last lines added
        to the buffer.
    """
    global entity_buffer, entity_counter
    for i in range( min( limit, entity_counter ) ) :
        #pdb.set_trace()
        # entity_buffer is a circular buffer. In order to print the entities in
        # the correct order, we go from the cell imediately after the last one
        # stored in the buffer (position entity_counter) until the until the
        # last one stored in the buffer (position entity_counter-1). If there
        # are less entities in the file than the limit, this padding is not
        # needed and we simply go from 0 until entity_counter-1
        index = ( entity_counter + i ) % min( limit, entity_counter )
        if entity_buffer[ index ] != None :
            print entity_buffer[ index ].to_xml().encode( 'utf-8' )
        else :
            break
    
################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global limit,  entity_buffer
    for ( o, a ) in opts:
        if o in ("-n", "--number") :
            try :
                limit = int( a )
                entity_buffer = [ None ] * limit
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
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=treat_entity,
                                 gen_xml=True )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :        
        parser.parse( sys.stdin )
        print_entities()
        print handler.footer
    else :
        for a in arg :
            input_file = open( a )            
            parser.parse( input_file )
            print_entities() 
            footer = handler.footer
            handler.gen_xml = False
            input_file.close()
            entity_counter = 0
        print footer
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid XML file," +\
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-*.dtd)"


