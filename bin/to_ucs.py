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
    This script converts a candidates file in a given format
    into a corresponding representation in the "UCS" format.
    Since UCS works only with pairs (2-grams), all ngrams with
    sizes other than 2 are discarded.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

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

from libs.util import read_options, treat_options_simplest
from libs.filetype import ft_ucs
from libs import filetype

     
################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <input-file>

The <input-file> must be in one of the filetype
formats accepted by the `--from` switch.


OPTIONS may be:

--from <input-filetype-ext>
    Force reading of corpus with given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[corpus]}

-s OR --surface
    Outputs surface forms instead of lemmas. Default false.
    
-p OR --lemmapos
    Outputs the corpus in lemma/pos format. Default false.

-f <name> OR --freq-source <name>
    Uses the frequencies from the frequency source <name>.
    By default, the first frequency source found in each entity is used.

{common_options}
"""   
surface_instead_lemmas = False  
lemmapos = False
freq_source = None

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
    global input_filetype_ext
    
    treat_options_simplest( opts, arg, n_arg, usage_string )

    for ( o, a ) in opts:        
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True
        elif o in ("-p", "--lemmapos") : 
            lemmapos = True   
        elif o in ("-f", "--freq-source") : 
            freq_source = a
        elif o == "--from":
            input_filetype_ext = a                          
        else:
            raise Exception("Bad arg: " + o)

################################################################################     
# MAIN SCRIPT

longopts = [ "surface", "lemmapos", "freq-source=" "from=" ]
args = read_options( "spf:", longopts, treat_options, -1, usage_string )
handler = ft_ucs.UCSPrinter("candidates", freq_source=freq_source,
        lemmapos=lemmapos, surfaces=surface_instead_lemmas)
filetype.parse(args, handler, input_filetype_ext)
