#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# xml2html.py is part of mwetoolkit
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

from libs.util import read_options, treat_options_simplest, parse_xml
from libs import filetype

     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s OPTIONS <file.xml>

OPTIONS may be:

%(common_options)s

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""
input_filetype_ext = None
output_filetype_ext = "XML"

################################################################################


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
        if o in ("--to"):
            output_filetype_ext = a


################################################################################
# MAIN SCRIPT

longopts = ["from=", "to="]
args = read_options("", longopts, treat_options, -1, usage_string)
printer = filetype.AutomaticPrinterHandler(output_filetype_ext)
filetype.parse(args, printer, input_filetype_ext)
