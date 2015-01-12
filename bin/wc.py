#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# wc.py is part of mwetoolkit
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
    This script simply gives some stats about a XML file, such as number
    of words, etc. Output is written on stderr.

    This script is DTD independent, that is, it might be called on a corpus
    file, on a list of candidates or on a dictionary!
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.util import read_options, treat_options_simplest, verbose
from libs import filetype


################################################################################     
# GLOBALS     
     
usage_string = """Usage: 

python {program} OPTIONS <input-file>

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

{common_options}
"""    
input_filetype_ext = None


################################################################################     

class CounterHandler(filetype.InputHandler):
    def before_file(self, fileobj, info={}):
        self.entity_counter = self.word_counter = self.char_counter = 0

    def handle_comment(self, comment, info={}):
        pass  # We just ignore it

    def _fallback_entity(self, entity, info={}) :
        """For each candidate/sentence, counts the number of occurrences, the 
        number of words and the number of characters (except spaces and XML).
        @param entity A subclass of `Ngram` that is being read from the XML.
        """
        for word in entity:
            self.word_counter += 1
            self.char_counter += len( word )
        self.entity_counter += 1


    def after_file(self, fileobj, info={}) :
        """Prints the entity, word and character counters on stderr. The
        filename is only used to print the stats. All counters are reset
        after a call to this function.
        """
        filename = fileobj.name
        print(unicode(self.entity_counter) + " entities in " + filename,file=sys.stderr)
        print(unicode(self.word_counter) + " words in " + filename,file=sys.stderr)
        print(unicode(self.char_counter) + " characters in " + filename,file=sys.stderr)


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    """
    global input_filetype_ext
    
    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o == "--from":
            input_filetype_ext = a
        else:
            raise Exception("Bad arg")


################################################################################
# MAIN SCRIPT

longopts = ["from="]
args = read_options("", longopts, treat_options, -1, usage_string)
filetype.parse(args, CounterHandler(), input_filetype_ext)
