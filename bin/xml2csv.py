#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import read_options, treat_options_simplest, parse_xml
from libs.base.__common import WILDCARD
from libs.util import verbose
from libs import filetype


################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <candidates.xml>

The <candidates.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).


OPTIONS may be:

-s OR --surface
    Outputs surface forms instead of lemmas. Default false.
    
-p OR --lemmapos
    Outputs the corpus in lemma/pos format. Replaces slashes by "@SLASH@". 
    Default false.

{common_options}
"""   
surface_instead_lemmas = False  
lemmapos = False
sentence_counter = 0
            

################################################################################     

class CSVInfo(filetype.common.FiletypeInfo):
    description = "Tab-separated CSV filetype format"
    filetype_ext = "CSV"
    comment_prefix = "#"

    def operations(self):
        return filetype.common.FiletypeOperations(None, None, CSVPrinter)


INFO = CSVInfo()


class CSVPrinter(filetype.common.AbstractPrinter):
    filetype_info = INFO
    valid_categories = ["candidates"]

    def handle_meta(self, meta, info={}):
        string_cand = "id\tngram\tpos\t"
        for cs in meta.corpus_sizes :
            string_cand = string_cand + cs.name + "\t"
        string_cand = string_cand + "occurs\tsources\t"
        for cs in meta.meta_tpclasses :
            string_cand = string_cand + cs.name + "\t"
        for cs in meta.meta_feats :
            string_cand = string_cand + cs.name + "\t"  
        self.add_string(string_cand, "\n")
       

    def handle_candidate(self, entity, info={}):
        """
            For each `Candidate`, print the candidate ID, its POS pattern and the 
            list of occurrences one per line
            
            @param candidate The `Candidate` that is being read from the XML file.
        """
        global surface_instead_lemmas
        global lemmapos
        global sentence_counter
        if sentence_counter % 100 == 0 :
            verbose( "Processing sentence number %(n)d" % { "n":sentence_counter } )
        string_cand = ""
        if entity.id_number >= 0 :
            string_cand += str( entity.id_number )
        string_cand = string_cand.strip() + "\t"    
        
        for w in entity :
            if lemmapos :
                string_cand += w.lemma.replace( "/", "@SLASH@" ) + "/" + w.pos + " "
            elif w.lemma != WILDCARD and not surface_instead_lemmas :            
                string_cand += w.lemma + " "
            else :
                string_cand += w.surface + " "
        string_cand = string_cand.strip() + "\t"
        
        if not lemmapos :
            for w in entity :
                string_cand += w.pos + " "
        string_cand = string_cand.strip() + "\t"
        
        try :
            for freq in entity.freqs :
                string_cand += str( freq.value ) + "\t"
        except TypeError:
            # This kind of entry probably doesnt have tpclass
            string_cand = string_cand.strip()
        except AttributeError :
            # This kind of entry probably doesnt have tpclass
            string_cand = string_cand.strip()

        try :
            for tpclass in entity.tpclasses :
                string_cand += str( tpclass.value ) + "\t"
        except AttributeError:
            # This kind of entry probably doesnt have tpclass
            string_cand = string_cand.strip()

        try :
            occur_dict = {}
            sources = []
            for occur in entity.occurs :
                surfaces = []
                sources.extend(occur.sources)
                for w in occur :
                    surfaces.append( w.surface )
                occur_dict[ " ".join( surfaces ) ] = True

            string_cand += "; ".join( occur_dict.keys() ) + "\t"
            string_cand += ";".join(sources) + "\t"

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

        self.add_string(string_cand, "\n")
        sentence_counter += 1
    

################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    global lemmapos
    
    treat_options_simplest( opts, arg, n_arg, usage_string )
        
    mode = []
    for ( o, a ) in opts:        
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True     
        elif o in ("-p", "--lemmapos") : 
            lemmapos = True                 
        else:
            raise Exception("Bad arg: " + o)

################################################################################     
# MAIN SCRIPT

longopts = [ "surface", "lemmapos" ]
args = read_options( "sp", longopts, treat_options, -1, usage_string )
filetype.parse(args, CSVPrinter("candidates"))
