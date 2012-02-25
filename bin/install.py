#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Vitor De Araujo
#
# install.py is part of mwetoolkit
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
    Use this file if you want to work in a folder and you have a single 
    mwetoolkit  installation in another folder. First, replace the value of the
    variable below by the appropriate path to the installation folder. Then, 
    copy this script to your work folder and, in your python scripts that call 
    the mwetoolkit, import this module. Everything will work as if you were in
    the installation directory.
"""

PATH_TO_MWETOOLKIT="/home/ceramisch/Work/develop/mwetoolkit"

################################################################################

import sys

sys.path.append( PATH_TO_MWETOOLKIT + "/bin" )

import config
