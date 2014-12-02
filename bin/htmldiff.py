#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
# 
# htmldiff.py is part of mwetoolkit
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
    This is a utility module that computes the difference between two files
    (as in unix's diff) and then shows it as an html page.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import difflib
import subprocess

from bin.libs.base.__common import TEMP_PREFIX, TEMP_FOLDER

BROWSER = "chromium-browser"

################################################################################

temp_fh = open( TEMP_FOLDER + "/" + TEMP_PREFIX + "_diff.html", "w" )
temp_name = temp_fh.name

string1 = open( sys.argv[1] ).readlines()
string2 = open( sys.argv[2] ).readlines()

differ = difflib.HtmlDiff( wrapcolumn=50 )
result = differ.make_file(string1, string2, context=True, numlines=0 )

temp_fh.write( result )
subprocess.call( [BROWSER, temp_name] )
temp_fh.close()
#os.remove( temp_name )
