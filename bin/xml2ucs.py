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
    into the UCS data set format. Since UCS works only with pairs (2-grams),
    all ngrams with sizes other than 2 are discarded.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys

from libs.util import read_options, treat_options_simplest, verbose, warn
from libs.base.__common import WILDCARD
from libs import filetype

     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <file.xml>

The <file.xml> file must be valid XML (dtd/mwetoolkit-*.dtd).


OPTIONS may be:

-s OR --surface
    Outputs surface forms instead of lemmas. Default false.
    
-p OR --lemmapos
    Outputs the corpus in lemma/pos format. Replaces slashes with "@SLASH@". 
    Default false.

-f <name> OR --freq-source <name>
    Uses the frequencies from the frequency source <name>. By default,
    the first frequency source found in each entity is used.

{common_options}
"""   
surface_instead_lemmas = False  
lemmapos = False

xml_meta = None
freq_source = None
corpus_size_string = None


################################################################################           
            
def freq_value(items):
    """Given a list of items with a `name` and a `value` attribute, return
    the item whose name is the same as that of `freq_source`.
    """
    for item in items:
        if freq_source is None or item.name == freq_source:
            return item.value

    warn("Frequency source '%s' not found!" % freq_source)
    return 0


################################################################################     


class UCSInfo(filetype.common.FiletypeInfo):
    description = "UCS filetype format"
    filetype_ext = "UCS"

    comment_prefix = "#"

    def operations(self):
        return filetype.common.FiletypeOperations(None, None, UCSPrinter)


INFO = UCSInfo()


class UCSPrinter(filetype.common.AbstractPrinter):
    filetype_info = INFO
    valid_categories = ["candidates"]

    def handle_meta(self, meta, info={}):
        """Print the header for the UCS dataset file,
        and save the corpus size."""
        global xml_meta, corpus_size_string
        string_cand = "id\tl1\tl2\tf\tf1\tf2\tN"

        #for cs in meta.corpus_sizes :
        #    string_cand = string_cand + cs.name + "\t"
        #string_cand = string_cand + "occurs\tsources\t"

        #for cs in meta.meta_tpclasses :
        #    string_cand = string_cand + cs.name + "\t"
        #for cs in meta.meta_feats :
        #    string_cand = string_cand + cs.name + "\t"  
        xml_meta = meta
        corpus_size_string = str(freq_value(xml_meta.corpus_sizes))
        self.add_string(string_cand, "\n")
       

    def handle_candidate(self, entity, info={}):
        """Print each `Candidate` as a UCS data set entry line.
        @param entity: The `Candidate` that is being read from the XML file.
        """
        global surface_instead_lemmas
        global lemmapos

        string_cand = ""
        if entity.id_number >= 0 :
            string_cand += unicode( entity.id_number )
        string_cand = string_cand.strip() + "\t"    
        
        if len(entity) != 2:
            warn("Ignoring entity %s, of length %d!=2" % (entity.id_number, len(entity)))
            return

        for w in entity :
            if lemmapos :
                string_cand += w.lemma.replace( "/", "@SLASH@" ) + "/" + w.pos + "\t"
            elif w.lemma != WILDCARD and not surface_instead_lemmas :
                string_cand += w.lemma + "\t"
            else :
                string_cand += w.surface + "\t"
        string_cand += "%f\t" % freq_value(entity.freqs)

        try:
            for w in entity:
                string_cand += "%f\t" % freq_value(w.freqs)
        except:
            string_cand += "0\t"
            warn("Word frequency information missing for"\
                        " entity %d" % entity.id_number)
        string_cand += corpus_size_string
        self.add_string(string_cand, "\n")

            
################################################################################     

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas
    global lemmapos
    global freq_source
    
    treat_options_simplest( opts, arg, n_arg, usage_string )    
    
    mode = []
    for ( o, a ) in opts:        
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True     
        if o in ("-p", "--lemmapos") : 
            lemmapos = True
        if o in ("-f", "--freq-source"):
            freq_source = a

################################################################################
# MAIN SCRIPT

longopts = [ "surface", "lemmapos", "freq-source" ]
args = read_options( "spf:", longopts, treat_options, -1, usage_string )
filetype.parse(args, UCSPrinter("candidates"))
