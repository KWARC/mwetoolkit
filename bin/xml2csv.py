#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
#
# xml2csv.py is part of mwetoolkit
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
    into a corresponding representation in the file format 
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import xml.sax
import re

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import read_options, treat_options_simplest
from xmlhandler.classes.__common import WILDCARD
     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python %(program)s <candidates.xml>

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""     
            
################################################################################     

def treat_meta( meta ) :
    """
    """
    string_cand = "id\tngram\tpos\t"
    for cs in meta.corpus_sizes :
        string_cand = string_cand + cs.name + "\t"
    string_cand = string_cand + "occurs\t"
    for cs in meta.meta_tpclasses :
        string_cand = string_cand + cs.name + "\t"
    for cs in meta.meta_feats :
        string_cand = string_cand + cs.name + "\t"  
        
    print string_cand.encode( 'utf-8' )       
       
################################################################################     
       
def treat_entity( entity ) :
    """
        For each `Candidate`, print the candidate ID, its POS pattern and the 
        list of occurrences one per line
        
        @param candidate The `Candidate` that is being read from the XML file.
    """
    string_cand = ""
    if entity.id_number >= 0 :
        string_cand += str( entity.id_number )
    string_cand = string_cand.strip() + "\t"    
    
    for w in entity :
        if w.lemma != WILDCARD :            
            string_cand += w.lemma + " "
        else :
            string_cand += w.surface + " "
    string_cand = string_cand.strip() + "\t"
    
    for w in entity :
        string_cand += w.pos + " "
    string_cand = string_cand.strip() + "\t"
    
    for freq in entity.freqs :
        string_cand += str( freq.value ) + "\t"

    try :
        for tpclass in entity.tpclasses :
            string_cand += str( tpclass.value ) + "\t"
    except AttributeError:
        # This kind of entry probably doesnt have tpclass
        string_cand = string_cand.strip()

    try :
        occur_dict = {}
        for occur in entity.occurs :
            surfaces = []
            for w in occur :
                surfaces.append( w.surface )
            occur_dict[ " ".join( surfaces ) ] = True

        string_cand += "; ".join( occur_dict.keys() ) + "\t"
    except AttributeError:
        # This kind of entry probably doesnt have occurs
        string_cand = string_cand.strip() + "\t-\t"

    try :
        for feat in entity.features :
            string_cand += str( feat.value ) + "\t"
    except AttributeError:
        # This kind of entry probably doesnt have tpclass
        string_cand = string_cand.strip()
        
    string_cand = string_cand.strip()

    print string_cand.encode( 'utf-8' )

################################################################################     
# MAIN SCRIPT

longopts = [ "verbose" ]
arg = read_options( "v", longopts, treat_options_simplest, -1, usage_string )

try :
    parser = xml.sax.make_parser()
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=treat_entity,
                                 gen_xml=False )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :
        parser.parse( sys.stdin )
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            handler.gen_xml = False
            input_file.close()
            entity_counter = 0
    
except IOError, err :
    print >> sys.stderr, err
except Exception, err :
    print >> sys.stderr, err
    print >> sys.stderr, "You probably provided an invalid candidates file," + \
                         " please validate it against the DTD " + \
                         "(dtd/mwetoolkit-candidates.dtd)"
