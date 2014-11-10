#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# check_format.py is part of mwetoolkit
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
    Script designed to simply check a corpus, candidates or patterns file so 
    that the format is OK. If it is not, will output error messages
    
    INCOMPLETE - ONLY WORKS FOR MOSES FACTORED
    TODO:
      - Support to CONLL format
      - Support to mwetoolkit custom XML formats - DTD (cands, corpus, patterns)
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.util import verbose, warn, error, strip_xml, treat_options_simplest, \
                 read_options
from libs.parser_wrappers import parse, InputHandler

################################################################################
# GLOBALS

usage_string = """Usage: 
    
python %(program)s OPTIONS <file>

-i <format> OR --input <format>
    Format of the input file to check:
    * Moses : Moses factored file format, one sentence per line, 
    space-separated tokens, factors separated by vertical bar |
    * OTHER FORMATS NOT IMPLEMENTED YET
    
-s OR --syntax
    Check the format of the syntactic element (e.g. \"type1:head1,type2:head2\")
    
-x OR --xml
    Check if tokens contain unescaped XML characters        
    
-f OR --first
    Stop verifying at first error (default False, checks the whole file)

%(common_options)s

    In case of format problem, the script will warn the user on stderr.
"""

################################################################################

class MosesCheckerHandler(InputHandler):

    def __init__( self ) :
        self.check_syntax = False
        self.check_xml = False
        self.stop_first = False
        self.synt_types = {}
        self.nproblems = 0
        self.nline = 0
        self.nparts = None
        
#############################

    def _report( self, ntoken, problem_description, token=None ) :
        warn( "Line %d, token %d" % ( self.nline, ntoken+1 ) )
        if token:
            warn( "Token: %s" % token )
        warn( problem_description )
        self.nproblems = self.nproblems + 1
        if self.stop_first :
            error( "Found a format problem, stopping verification" )
            
#############################

    def _check_syntax( self, synt, ntoken, tokens ) :
        if not synt : # Empty synt element
            return      
        rels = synt.split( ";" )
        for rel in rels:
            try :
                (reltype,head) = rel.split( ":" )
                if int(head) > len(tokens) :
                    self._report( ntoken, "Syntax head out of sentence: %s" % \
                                  head, tokens[ ntoken ] )                                            
                # Store all possible syntactic relation types in dict
                # Allows verifying if there is no spurious relation
                reltypeparts = reltype.split( "_" )
                for reltypepart in reltypeparts :
                    self.synt_types[ reltypepart ] = 1     
            except ValueError:
                pass # Unary relation                               
                
#############################     

    def handle_line( self, line, info={} ):
        self.nline = self.nline + 1
        tokens = unicode( line.strip(), "utf-8" ).split( " " )
        for (ntoken, token) in enumerate( tokens ) :
            parts = token.split( "|" )
            try :
                if len(parts) != self.nparts :                
                    self._report( ntoken, "Expected %d, found %d factors" % \
                                (self.nparts, len(parts)), token)
            except TypeError : # First time
                self.nparts = len(parts)
                verbose( "Number of factors: %d" % self.nparts )                
            if self.check_xml and strip_xml( token ) != token :                
                self._report(ntoken, "Token contains unescaped XML: %s" % token)  
            if self.check_syntax and len(parts) >= 4:
                self._check_syntax( parts[ 3 ], ntoken, tokens )
                            
#############################     
                      
    def after_file( self, fileobj ) :
        if self.check_syntax :
            nsynttypes = len( self.synt_types )
            verbose( "Found %d types of synt. relation:" % nsynttypes )
            for synt_type in self.synt_types.keys() :
                verbose( "* %s" % synt_type )
        print( "Number of problems: %d" % self.nproblems )

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """Callback function that handles the command line options of this script.
    @param opts The options parsed by getopts. Ignored.
    @param arg The argument list parsed by getopts.
    @param n_arg The number of arguments expected for this script.    
    """
    
    global checker_class, checker

    treat_options_simplest(opts, arg, n_arg, usage_string)
    stop_first = False
    check_syntax = False
    check_xml = False    
    for (o, a) in opts:
        if o in ("-i", "--input"):
            checkers = {
                #"XML": XMLPrinter, 
                #"Text": SurfacePrinter, 
                "Moses": MosesCheckerHandler
            }
            checker_class = checkers[a]
        if o in ("-f", "--first"):
            stop_first = True
        if o in ("-s", "--syntax"):
            check_syntax = True
        if o in ("-x", "--xml"):
            check_xml = True            
    checker = checker_class( )
    checker.stop_first = stop_first
    checker.check_syntax = check_syntax
    checker.check_xml = check_xml    
  
    
################################################################################
# MAIN       

checker_class = MosesCheckerHandler # Default type of checker - others not implemented
checker = None          

longopts = [ "first", "syntax", "xml", "input" ]
arg = read_options( "fsxi:", longopts, treat_options, -1, usage_string )
parse(arg, checker)
