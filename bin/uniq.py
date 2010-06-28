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
    Prints the unique entities of a list. Works like the "uniq" command in
    the unix platform, only it takes a non-sorted file in xml format as input.

    This script is DTD independent, that is, it might be called on a corpus
    file, on a list of candidates or on a dictionary.

    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import pdb

from xmlhandler.classes.frequency import Frequency
from xmlhandler.genericXMLHandler import GenericXMLHandler
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from xmlhandler.classes.entry import Entry
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.__common import WILDCARD
from util import read_options, treat_options_simplest, verbose

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS <files.xml>

OPTIONS may be:

-g OR --ignore-pos
     Ignores parts of speech when uniquing candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be treated
     as the same entity. Default false.

-s OR --surface
    Consider surface forms instead of lemmas. Default false.

-v OR --verbose
    Print messages that explain what is happening.

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
ignore_pos = False
surface_instead_lemmas = False
entity_counter = 0
entity_buffer = {}

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
        
        
        @param entity A subclass of `Ngram` that is being read from the XM.
    """
    global entity_counter, entity_buffer, limit
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    # TODO: improve the "copy" method
    if isinstance( entity, Candidate ) :
        copy_ngram = Candidate( 0, [], [], [], [] )
    elif isinstance( entity, Entry ) :
        copy_ngram = Entry( 0, [], [], [] )
    elif isinstance( entity, Sentence ) :
        copy_ngram = Sentence( [], 0 )
    else :
        copy_ngram = Ngram( [], [] )
    for w in entity :
        copy_w = Word( w.surface, w.lemma, w.pos, [] )
        copy_ngram.append( copy_w )
    if ignore_pos :
        copy_ngram.set_all( pos=WILDCARD )
    if surface_instead_lemmas :
        copy_ngram.set_all( lemma=WILDCARD )
    else :
        copy_ngram.set_all( surface=WILDCARD )

    internal_key = unicode( copy_ngram.to_string() ).encode('utf-8')
    #pdb.set_trace()

    if isinstance( entity, Candidate ) :
        # TODO: Generalise this!
        old_entry = entity_buffer.get( internal_key, None )
        if old_entry :
            #pdb.set_trace()
            copy_ngram.occurs = list( set( old_entry.occurs ) | set( entity.occurs ) )
            copy_ngram.features = list( set( old_entry.features ) | set( entity.features ) )
            copy_ngram.tpclasses = list( set( old_entry.tpclasses ) | set( entity.tpclasses ) )
            copy_ngram.freqs = list( set( old_entry.freqs ) | set( entity.freqs ) )
        else :
            copy_ngram.occurs = entity.occurs
            copy_ngram.features = entity.features
            copy_ngram.tpclasses = entity.tpclasses
            copy_ngram.freqs = entity.freqs
    elif isinstance( entity, Entry ) :
        pass
    elif isinstance( entity, Sentence ) :
        pass
    #entity_buffer[ internal_key ] = old_entry

    entity_buffer[ internal_key ] = copy_ngram
    entity_counter += 1
    
################################################################################    

def print_entities() :
    """
        After we read all the XML file, we can finally be sure about which lines
        need to be printed. Those correspond exactly to the unique lines added
        to the buffer.
    """
    global entity_buffer, entity_counter
    uniq_counter = 0
    for entity in entity_buffer.values() :
        entity.id_number = uniq_counter
        if isinstance( entity, Candidate ) :
            # WARNING: This is sort of specific for the VERBS 2010 paper. This
            # whole script should actually be redefined and documented. But for
            # the moment it's useful and I have no time to be a good programmer
            # -Carlos
            freq_sum = {}
            for freq in entity.freqs :
                freq_entry = freq_sum.get( freq.name, 0 )
                freq_entry += int( freq.value )
                freq_sum[ freq.name ] = freq_entry
            entity.freqs = []
            for ( name, value ) in freq_sum.items() :
                entity.add_frequency( Frequency( name, value ) )
        print entity.to_xml().encode( 'utf-8' )
        uniq_counter += 1
    verbose( "%(n)d entities, %(u)d unique entities" % { "n":entity_counter, \
                                                         "u":uniq_counter } )
    
################################################################################  

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global ignore_pos, surface_instead_lemmas
    for ( o, a ) in opts:
        if o in ("-g", "--ignore-pos") :
            ignore_pos = True
        elif o in ("-s", "--surface") :
            surface_instead_lemmas = True
                             
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################    
# MAIN SCRIPT

longopts = [ "ignore-pos", "surface", "verbose" ]
arg = read_options( "gsv", longopts, treat_options, -1, usage_string )

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
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid XML file," +\
#                         " please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-*.dtd)"


