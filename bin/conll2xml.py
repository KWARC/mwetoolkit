#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
#
# conll2xml.py is part of mwetoolkit
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
This script transforms the CONLL file format to the XML corpus format of
required by the mwetoolkit scripts. The script is language independent
as it does not transform the information. Only UTF-8 text is accepted,
as per CONLL specification.

For more information, call the script with no parameter and read the
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
    
python %(program)s OPTIONS <files.xml>

OPTIONS:
%(common_options)s

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""    


################################################################################

class ConllToXMLHandler(InputHandler):
    r"""An InputHandler that converts CONLL into XML."""
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
       
def treat_options( opts, arg, n_arg, usage_string ) :
    """
    Callback function that handles the command line options of this script.
    
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.
    @param usage_string Instructions that appear if you run the program with
    the wrong parameters or options.
    """
    treat_options_simplest(opts, arg, n_arg, usage_string)
    
    for o, a in opts:
        sys.exit(1)


################################################################################     
# MAIN SCRIPT

longopts = []
args = read_options("", longopts, treat_options, -1, usage_string)
parse(args, ConllToXMLHandler(), "CONLL")
