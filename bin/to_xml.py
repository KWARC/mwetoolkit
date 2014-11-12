#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2014 Silvio Ricardo Cordeiro
#
# to_xml.py is part of mwetoolkit
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
This script transforms any recognizable file format into an XML format
as defined by mwetoolkit. The script is language independent as it does
not transform the information.

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

OPTIONS may be:

--from <filetype-ext>
    Force conversion from given file type extension.
    (By default, file type is automatically detected).

%(common_options)s

    The <files.xml> file(s) must be a valid corpus/candidates/patterns file.
"""    

filetype_ext = None


################################################################################

class ToXMLHandler(InputHandler):
    r"""An InputHandler that converts input into XML."""
    def before_file(self, fileobj, info={}):
        self.printer = XMLPrinter(info["root"])
        self.entity_counter = 0

    def handle_entity(self, entity, info={}):
        """Generate XML for given entity.
        @param entity: An object that is being read from the input file.    
        @param info: A dictionary with info regarding `entity`.
        """
        self.entity_counter += 1
        if self.entity_counter % 100 == 0:
            verbose("Processing {} number {}".format(
                info["kind"], self.entity_counter))

        self.printer.add(entity)


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
    global filetype_ext
    treat_options_simplest(opts, arg, n_arg, usage_string)
    
    for o, a in opts:
        if o == "--from":
            filetype_ext = a
        else:
            sys.exit(1)


################################################################################     
# MAIN SCRIPT

longopts = ["from="]
args = read_options("", longopts, treat_options, -1, usage_string)
parse(args, ToXMLHandler(), filetype_hint=filetype_ext)
