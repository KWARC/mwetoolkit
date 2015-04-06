#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# uniq.py is part of mwetoolkit
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import collections

from libs.base.frequency import Frequency
from libs.base.ngram import Ngram
from libs.base.word import Word
from libs.base.entry import Entry
from libs.base.sentence import Sentence
from libs.base.candidate import Candidate
from libs.base.__common import WILDCARD
from libs.util import read_options, treat_options_simplest, verbose
from libs import filetype


################################################################################
# GLOBALS

usage_string = """Usage: 
    
python {program} OPTIONS <candidates>

The <candidates> input file must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

-g OR --ignore-pos
     Ignores parts of speech when uniquing candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be treated
     as the same entity. Default false.

-s OR --surface
    Consider surface forms instead of lemmas. Default false.

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[candidates]}

{common_options}
"""
ignore_pos = False
surface_instead_lemmas = False
entity_buffer = collections.OrderedDict()

input_filetype_ext = None
output_filetype_ext = None


################################################################################


class UniqerHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)


    def _fallback_entity(self, entity, info={}) :
        """Add each entity to the entity buffer, after pre-processing it. This
        buffer is used to keep track of repeated items, so that only a copy
        of an item is saved.

        @param entity A subclass of `Ngram` that is being read from the XM.
        """
        global entity_buffer
        global ignore_pos, surface_instead_lemmas

        # XXX after we're sure this is all working, use the entity
        # itself as a key, as it is an Ngram, and Ngram's now have __cmp__
        internal_key = unicode(entity.to_string()).encode('utf-8')

        if ignore_pos :
            entity.set_all( pos=WILDCARD )

        if surface_instead_lemmas :
            entity.set_all( lemma=WILDCARD )        
        else :
            entity.set_all( surface=WILDCARD )
            
        if internal_key not in entity_buffer:
            entity_buffer[internal_key] = (entity, info)
        else:
            old_entity, info = entity_buffer[internal_key]
            old_entity.merge_from(entity)


    def finish(self, info={}):
        """After we read all input, we can finally be sure about which lines
        need to be printed. Those correspond exactly to the unique lines added
        to the buffer.
        """
        global entity_buffer
        verbose( "Output the unified ngrams..." )
        for uniq_counter, (entity, info) in enumerate(entity_buffer.values()):
            #entity.id_number = uniq_counter
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
                entity.freqs.clear()
                for ( name, value ) in freq_sum.items() :
                    entity.add_frequency( Frequency( name, value ) )
            elif isinstance( entity, Entry ) :
                pass
            elif isinstance( entity, Sentence ) :
                pass          
            self.chain.handle(entity, info)
        self.chain.finish(info)
                
        

################################################################################    

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global ignore_pos
    global surface_instead_lemmas
    global input_filetype_ext
    global output_filetype_ext
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    

    for ( o, a ) in opts:
        if o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o in ("-g", "--ignore-pos") :
            ignore_pos = True
        elif o in ("-s", "--surface") :
            surface_instead_lemmas = True
        else:
            raise Exception("Bad arg: " + o)


                
################################################################################    
# MAIN SCRIPT

longopts = [ "from=", "to=", "ignore-pos", "surface" ]
args = read_options( "gst", longopts, treat_options, -1, usage_string )

filetype.parse(args, UniqerHandler(), input_filetype_ext)
