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

from libs.util import read_options, treat_options_simplest
from libs.base.__common import WILDCARD
from libs.util import verbose
from libs.filetype import ft_csv
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
filetype.parse(args, ft_csv.CSVPrinter(lemmapos=lemmapos,
                                       surfaces=surface_instead_lemmas,
                                       category="candidates"))
