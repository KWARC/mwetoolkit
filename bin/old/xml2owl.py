#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# xml2owl.py is part of mwetoolkit
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
    into a corresponding representation in OWL. In the current implementation,
    the only information output is the base form of the candidate.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest
from libs.base.__common import WILDCARD
from libs import filetype
from libs.filetype import ft_xml

     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} [OPTIONS] <file.xml>


OPTIONS may be:    
    
-s OR --surface
    Counts surface forms instead of lemmas. Default false.

{common_options}

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""     
surface_instead_lemmas = False


OWL_HEADER = ft_xml.XML_HEADER.replace("SYSTEM \"dtd/mwetoolkit-{category}.dtd\"", """[
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >] 
""" ).format(category="rdf:RDF", ns="""xmlns="http://www.mwetoolkiteval.org/.owl#"
    xml:base="http://www.mwetoolkiteval.org/ontologies/2010/2/Ontology1269282494031.owl"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" """)

OWL_FOOTER = ft_xml.XML_FOOTER.format(category="rdf:RDF")
            

################################################################################     

class OwlInfo(filetype.common.FiletypeInfo):
    description = "OWL filetype format"
    filetype_ext = "OWL"

    # The comment below was mysteriously found in the original xml2owl script
    # We're still wondering what it means CR 2014-12-16
    # "Special symbols can break the ontology systems, better avoid them"
    escape_pairs = ft_xml.INFO.escape_pairs + [ ("$", "${dollar}"),
                   ("&amp;","${amp}"), ("&quot;","${quot}"), ("&lt;","${lt}"),
                   ("&gt;","${gt}") ]

    def operations(self):
        return filetype.common.FiletypeOperations(None, None, OwlPrinter)


INFO = OwlInfo()


class OwlPrinter(ft_xml.XMLPrinter):
    filetype_info = INFO
    valid_categories = ["candidates"]
    
    def before_file(self, fileobj, info={}):
        self.add_string(OWL_HEADER, "\n")

    def after_file(self, fileobj, info={}):
        self.add_string(OWL_FOOTER, "\n")


    def handle_candidate(self, entry, info={}):
        """For each `Candidate`, print the candidate as if it was a class in the
        artificial ontology.
        
        @param candidate The `Entry` that is being read from the XML file.        """

        owl_cand = ["<owl:Class rdf:about=\"#"]
        for word in entry :
            form = word.surface if word.lemma == WILDCARD else word.lemma
            form = self.escape(form)


            owl_cand.append(form)
        owl_cand = "_".join(owl_cand) + "\"/>\n"
        self.add_string(owl_cand)


def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
    mode = []
    for ( o, a ) in opts:
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True
        else:
            raise Exception("Bad arg: " + o)


################################################################################     
# MAIN SCRIPT

longopts = [ "surface" ]
args = read_options( "s", longopts, treat_options, -1, usage_string ) 
filetype.parse(args, OwlPrinter("candidates"))
