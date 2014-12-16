#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# xml2evita.py is part of mwetoolkit
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
    This script converts a candidates file in XML (mwetoolkit-candidates.dtd)
    into a corresponding representation in the file format defined by Evita
    Linardaki in her email of 02 Jan 2010. The file format is a list of entries
    that are described by the following example:
    
    candid=0  pos="AJ  N "
    "αχίλλειος πτέρνα"
    "Αχίλλειος πτέρνα"
    "αχίλλειο πτέρνα"
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest
from libs.base.__common import SEPARATOR, WORD_SEPARATOR
from libs import filetype


################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

%(common_options)s

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""

################################################################################     

class EvitaInfo(filetype.common.FiletypeInfo):
    description = "Evita Linardaki's filetype format"
    filetype_ext = "Evita"
    comment_prefix = "#"

    def operations(self):
        return filetype.common.FiletypeOperations(None, None, EvitaPrinter)


INFO = EvitaInfo()


class EvitaPrinter(filetype.common.AbstractPrinter):
    filetype_info = INFO
    valid_categories = ["candidates"]

    def handle_candidate(self, candidate, info={}):
        """For each `Candidate`, print the candidate ID, its POS pattern and the 
        list of occurrences one per line
        
        @param candidate The `Candidate` that is being read from the XML file.
        """
        pos = candidate.get_pos_pattern()
        pos = pos.replace(SEPARATOR, " ")
        self.add_string("candid=%(id)s pos=\"%(pos)s\"\n" % \
                {"id": candidate.id_number, "pos": pos})
        for form in candidate.occurs:
            form.set_all(lemma="", pos="")
            occur = form.to_string()
            occur = occur.replace(SEPARATOR, "")
            occur = occur.replace(WORD_SEPARATOR, " ")
            self.add_string(("\"%(occur)s\"\n" % {"occur": occur}).encode('utf-8'))
        self.add_string("\n")

################################################################################     
# MAIN SCRIPT

args = read_options("", [], treat_options_simplest, -1, usage_string)
filetype.parse(args, EvitaPrinter("candidates"))
