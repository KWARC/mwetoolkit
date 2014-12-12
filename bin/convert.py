#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# convert.py is part of mwetoolkit
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
    This script converts between file formats.
    By default, the output is generated in mwetoolkit's XML format,
    but many input/output formats are available.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest
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

--to <output-filetype-ext>
    Convert input to given filetype extension.
    (By default, converts input to "XML" format):
    {descriptions.output[ALL]}

{common_options}
"""

input_filetype_ext = None
output_filetype_ext = "XML"


################################################################################

class ConverterHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, output_filetype_ext)
        self.chain.before_file(fileobj, info)


def treat_options(opts, arg, n_arg, usage_string):
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global input_filetype_ext
    global output_filetype_ext

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for (o, a) in opts:
        if o in ("--from"):
            input_filetype_ext = a
        elif o in ("--to"):
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)


################################################################################
# MAIN SCRIPT

longopts = ["from=", "to="]
args = read_options("", longopts, treat_options, -1, usage_string)
filetype.parse(args, ConverterHandler(), input_filetype_ext)
