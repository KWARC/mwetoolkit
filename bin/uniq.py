#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
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
import re

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

-t OR --retokenise
    Re-tokenises the words of the candidate by removing all the slashes and 
    dashes. For example, "gel assay" and "gel-assay" will be uniqued into a 
    single candidate.

%(common_options)s

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
ignore_pos = False
surface_instead_lemmas = False
perform_retokenisation = False
entity_counter = 0
entity_buffer = {}
split_characters = "/-"

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' ) 

################################################################################

def create_instance( entity ) :
    """
        Create an empty instance of the same type as 'entity'.
    """
    if isinstance( entity, Candidate ) :
        return Candidate( 0, [], [], [], [], [] )
    elif isinstance( entity, Entry ) :
        return Entry( 0, [], [], [] )
    elif isinstance( entity, Sentence ) :
        return Sentence( [], 0 )
    else :
        return Ngram( [], [] )
################################################################################    

def retokenise( ngram ) :
    """
        Retokenises an ngram, splitting words containing some kinds of
        separators into individual words.
    """
    global split_characters
    global surface_instead_lemmas
    split_form = create_instance( ngram )
    for w in ngram :
        if surface_instead_lemmas :
            splittable = w.surface
        else :
            splittable = w.lemma        
        for c in list( split_characters ) :
            splittable = splittable.replace( c, "-" )
        for part in splittable.split( "-" ) :
            part = part.strip()
            # Little workaround for digits
            if part.isdigit() :
                pos = "NUM"
            else :
                pos = w.pos
            #pdb.set_trace()
            # Impossible to replace, one of the parts does never appear as
            # an individual word.
            if part != "" :
                if surface_instead_lemmas :
                    split_form.append( Word( part, WILDCARD, pos, WILDCARD, [] ) )
                else :
                    split_form.append( Word( WILDCARD, part, pos, WILDCARD, [] ) )
    #pdb.set_trace()
    return split_form
            
    
################################################################################
       
def treat_entity( entity ) :
    """
        Add each entity to the entity buffer, after pre-processing it. This
        buffer is used to keep track of repeated items, so that only a copy
        of an item is saved.

        @param entity A subclass of `Ngram` that is being read from the XM.
    """
    global entity_counter, entity_buffer
    global perform_retokenisation, ignore_pos, surface_instead_lemmas

    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )
    # TODO: improve the "copy" method
    copy_ngram = create_instance( entity )
    for w in entity :
        copy_w = Word( w.surface, w.lemma, w.pos, w.syn, [] )
        copy_ngram.append( copy_w )
        
    if perform_retokenisation :
        copy_ngram = retokenise( copy_ngram )
        
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
            #copy_ngram.features = list( set( old_entry.features ) | set( entity.features ) )
            copy_ngram.features = uniq_features(old_entry.features, entity.features)
            copy_ngram.tpclasses = list( set( old_entry.tpclasses ) | set( entity.tpclasses ) )
            #copy_ngram.freqs = list( set( old_entry.freqs ) | set( entity.freqs ) )
            unify_freqs = {}
            for f in list( set( old_entry.freqs ) | set( entity.freqs ) ) :
                unify_freqs[ f.name ] = unify_freqs.get( f.name, 0 ) + f.value
            for ( k, v ) in unify_freqs.items() :
                copy_ngram.add_frequency( Frequency( k, v ) )
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


def position(item, list, key=lambda x: x):
    """
        Returns the index of an element in a list, or None if the element
        is not found.
    """
    for i in xrange(len(list)):
        if item == key(list[i]):
            return i

    return None


def uniq_features(*featlists):
    """
        Merges the lists of Features passed in as arguments. If the same
        feature appears multiple times in the lists, keep only the one
        with highest value.
    """
    result = []
    for featlist in featlists:
        for feature in featlist:
            oldpos = position(feature.name, result, key=lambda x: x.name)
            if oldpos is not None:
                if result[oldpos].value < feature.value:
                    result[oldpos] = feature
            else:
                result.append(feature)

    return result
                
        

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
        elif isinstance( entity, Entry ) :
            pass
        elif isinstance( entity, Sentence ) :
            pass          
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
    global ignore_pos, surface_instead_lemmas, perform_retokenisation
    for ( o, a ) in opts:
        if o in ("-g", "--ignore-pos") :
            ignore_pos = True
        elif o in ("-s", "--surface") :
            surface_instead_lemmas = True
        elif o in ("-t", "--retokenise") :
            perform_retokenisation = True            
                             
    treat_options_simplest( opts, arg, n_arg, usage_string )
    
################################################################################    
# MAIN SCRIPT

longopts = [ "ignore-pos", "surface", "retokenise" ]
arg = read_options( "gst", longopts, treat_options, -1, usage_string )

parser = xml.sax.make_parser()
handler = GenericXMLHandler( treat_meta=treat_meta,
                             treat_entity=treat_entity,
                             gen_xml=True )
parser.setContentHandler( handler )
if len( arg ) == 0 :        
    parser.parse( sys.stdin )
    verbose( "Output the unified ngrams..." )        
    print_entities()
    print handler.footer
else :
    for a in arg :
        input_file = open( a )            
        parser.parse( input_file )
        verbose( "Output the unified ngrams..." )
        print_entities() 
        footer = handler.footer
        handler.gen_xml = False
        input_file.close()
        entity_counter = 0
    print footer
