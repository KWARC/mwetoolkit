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
    This script converts a corpus file in XML into a corresponding simple HTML.
    The HTML can be viewed in a browser with a specific CSS stylesheet so that
    it is easier to read the sentences and see linguistic information if 
    required. MWE annotation is also provided.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.genericXMLHandler import GenericXMLHandler
from libs.util import read_options, treat_options_simplest, parse_xml
from libs.parser_wrappers import XMLParser
from libs.printers import HTMLPrinter
import datetime
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s OPTIONS <file.xml>

OPTIONS may be:

%(common_options)s

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""

################################################################################

class XML2HTMLParser(XMLParser):

    def __init__(self, in_files, printer):
        super(XML2HTMLParser, self).__init__(in_files, printer)

    def treat_sentence(self, entity):
        self.printer.add( entity )


################################################################################
# MAIN SCRIPT

arg = read_options( "", [], treat_options_simplest, -1, usage_string )
XML2HTMLParser( arg, HTMLPrinter( arg[0] if arg else "stdin" ) ).parse()

