#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
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
    into a corresponding representation in owl. In the current implementation,
    the only information output is the base form of the candidate.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import re

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest
from xmlhandler.classes.__common import WILDCARD, XML_HEADER, XML_FOOTER
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s [OPTIONS] <file.xml>

    OPTIONS may be:    
    
-s OR --surface
    Counts surface forms instead of lemmas. Default false.

%(common_options)s

    The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).
"""     
surface_instead_lemmas = False
OWL_HEADER = XML_HEADER.replace( "SYSTEM \"dtd/mwetoolkit-%(root)s.dtd\"", """[
    <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
    <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
    <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
    <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >] 
""" ) % \
             { "root" : "rdf:RDF", \
               "ns" : """xmlns="http://www.mwetoolkiteval.org/.owl#"
    xml:base="http://www.mwetoolkiteval.org/ontologies/2010/2/Ontology1269282494031.owl"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" """ }

OWL_FOOTER = XML_FOOTER % { "root" : "rdf:RDF" }
            
################################################################################     
       
def treat_entity( entry ) :
    """
        For each `Candidate`, print the candidate as if it was a class in the
        artificial ontology.
        
        @param candidate The `Entry` that is being read from the XML file.
    """
    global surface_instead_lemmas
    owl_cand = "<owl:Class rdf:about=\"#"
    for word in entry :
        if surface_instead_lemmas :
            form = word.surface
        else :
            form = word.lemma
        # Special symbols can break the ontology systems, better avoid them
        form = form.replace( "&quot;", "QUOTSYMBOL" )
        form = form.replace( "&amp;", "ANDSYMBOL" )
        form = form.replace( "&gt;", "GTSYMBOL" )
        form = form.replace( "&lt;", "LTSYMBOL" )
        owl_cand += form + "_"
    owl_cand = owl_cand[:len(owl_cand)-1] + "\"/>" # remove extra underline char
    
    print owl_cand.encode( 'utf-8' )

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    mode = []
    for ( o, a ) in opts:
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True        
    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################     
# MAIN SCRIPT

longopts = [ "surface" ]
arg = read_options( "s", longopts, treat_options, -1, usage_string ) 

parser = xml.sax.make_parser()
handler = GenericXMLHandler( treat_entity=treat_entity,
                             gen_xml=False )
parser.setContentHandler( handler )
print OWL_HEADER
if len( arg ) == 0 :
    parser.parse( sys.stdin )
else :
    for a in arg :
        input_file = open( a )
        parser.parse( input_file )
        footer = handler.footer
        input_file.close()
        entity_counter = 0
print OWL_FOOTER
