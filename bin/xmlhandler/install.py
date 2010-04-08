#!/usr/bin/python
"""
    Use this file if you want to work in a folder and you have a single 
    mwttoolkit  installation in another folder. First, replace the value of the
    variable below by the appropriate path to the installation folder. Then, 
    copy this script to your work folder and, in your python scripts that call 
    the mwttoolkit, import this module. Everything will work as if you were in
    the installation directory.
"""

PATH_TO_MWTTOOLKIT="../.."

################################################################################

import sys

sys.path.append( PATH_TO_MWTTOOLKIT + "/bin" )

import config
