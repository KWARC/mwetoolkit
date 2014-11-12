#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# moses2xml.py is part of mwetoolkit
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
    This script transforms the Moses factored format to the XML format of
    a corpus, as required by the mwetoolkit scripts. The script is language
    independent as it does not transform the information. Only UTF-8 text is 
    accepted.
    
    For more information, call the script with -h parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.util import read_options, treat_options_simplest, verbose

from libs.printers import XMLPrinter
from libs.parser_wrappers import parse, InputHandler
from libs.util import warn_once, warn
     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python %(program)s OPTIONS <files.moses>

OPTIONS may be:

%(common_options)s

    The <files.moses> file(s) must be valid Moses-formatted files.
"""          
################################################################################

class MosesToXMLHandler(InputHandler):
    r"""An InputHandler that converts Moses into XML."""
    def before_file(self, fileobj, info={}):
        self.printer = XMLPrinter(info["root"])
        self.sentence_counter = 0

    def handle_sentence(self, sentence, info={}):
        """Generate XML for given sentence.
        @param sentence: A `Sentence` that is being read from the XML file.    
        @param info: A dictionary with info regarding `sentence`.
        """
        self.sentence_counter += 1
        if self.sentence_counter % 100 == 0:
            verbose("Processing sentence number %(n)d"
                    % {"n": self.sentence_counter})

        self.printer.add(sentence)


################################################################################     
# MAIN SCRIPT

args = read_options("", [], treat_options_simplest, -1, usage_string)
parse(args, MosesToXMLHandler(), "Moses")
