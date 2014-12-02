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

from libs.util import read_options, treat_options_simplest, \
        verbose, parse_xml, error
from libs import filetype

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s OPTIONS <input-file>

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

-n OR --number
    Number of entities that you want to print out. Default value is 10.

--from <input-filetype-ext>
    Force conversion from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[ALL]}

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, keeps input in original format):
    {descriptions.output[ALL]}

{common_options}

"""
limit = 10
input_filetype_ext = None
output_filetype_ext = None


################################################################################

class HeadPrinterHandler(filetype.AutomaticPrinterHandler):
    """For each entity in the file, prints it if the limit is still not
    achieved. No buffering as in tail, this is not necessary here.
    """
    def __init__(self, limit):
        super(HeadPrinterHandler, self).__init__(output_filetype_ext)
        self.limit = limit

    def before_file(self, fileobj, info={}):
        super(HeadPrinterHandler, self).before_file(fileobj, info)
        self.counter = 0

    def handle_entity(self, entity, info={}):
        """For each entity in the file, prints it if the limit is still not
        achieved. No buffering as in tail, this is not necessary here.

        @param entity: A subclass of `Ngram` that is being read from the XML.
        """
        if self.counter % 100 == 0:
            verbose( "Processing ngram number %(n)d" % { "n":self.counter } )
        if self.counter < self.limit:
            self.chain.handle_by_kind(info["kind"], entity, info)
        else:
            raise filetype.StopParsing
        self.counter += 1


################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global limit
    global input_filetype_ext
    global output_filetype_ext
    
    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o == "--from":
            input_filetype_ext = a
        elif o == "--to":
            output_filetype_ext = a
        elif o in ("-n", "--number"):
            try:
                limit = int( a )
                if limit < 0:
                    raise ValueError
            except ValueError:
                error("You must provide a positive " \
                         "integer value as argument of -n option.")
        else:
            raise Exception("Bad arg")

################################################################################
# MAIN SCRIPT

longopts = ["from=", "to=", "number="]
args = read_options("n:", longopts, treat_options, -1, usage_string)
filetype.parse(args, HeadPrinterHandler(limit), input_filetype_ext)
