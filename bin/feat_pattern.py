#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# feat_pattern.py is part of mwetoolkit
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
    This script adds two new features for each candidate in the list. These two
    features correspond to the POS pattern and to the number of words in the
    candidate base form. The former is the sequence of Part Of Speech tags in
    the candidate, for example, a sequence of Nouns or Adjectives. The latter is
    the value of n in the ngram that describes the base for of the candidate.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from libs.base.feature import Feature
from libs.base.meta_feat import MetaFeat
from libs.util import read_options, treat_options_simplest, verbose
from libs.base.__common import SEPARATOR
from libs import filetype

     
################################################################################     
# GLOBALS     
     
usage_string = """Usage: 
    
python {program} <candidates.xml>

The <candidates.xml> file must be valid XML (mwetoolkit-candidates.dtd).


OPTIONS may be:

{common_options}
"""     
all_patterns = {}



################################################################################

class RecovererHandler(filetype.InputHandler):
    def handle_candidate(self, candidate, info={}) :
        """
            Simply stores the candidate's POS pattern into a dictionary. This allows
            us to know what are all the different possible values for this feature.
            
            @param candidate The `Candidate` that is being read from the XML file.
        """
        global all_patterns
        pattern = candidate.get_pos_pattern().replace( SEPARATOR, "-" )
        all_patterns[ pattern ] = 1    


################################################################################

class FeatGeneratorHandler(filetype.ChainedInputHandler):
    def before_file(self, fileobj, info={}):
        if not self.chain:
            self.chain = self.make_printer(info, "XML")
        self.chain.before_file(fileobj, info)

    def handle_meta(self, meta, info={}) :
        """
            Adds two new meta-features corresponding to the features that we add to
            each candidate. The meta-features define the type of the features, which
            is an enumeration of all possible POS patterns for the POS pattern and
            an integer number for the size n of the candidate.
            
            @param meta The `Meta` header that is being read from the XML file.        
        """
        global all_patterns
        pattern_feat_values = "{"
        for pattern_value in all_patterns.keys() :
            pattern_feat_values = pattern_feat_values + pattern_value + ","
        pattern_feat_values = pattern_feat_values[0:len(pattern_feat_values) - 1] 
        pattern_feat_values = pattern_feat_values + "}"    
        meta.add_meta_feat( MetaFeat( "pos_pattern", pattern_feat_values ) ) 
        meta.add_meta_feat( MetaFeat( "n", "integer" ) )
        meta.add_meta_feat( MetaFeat( "capitalized", "{UPPERCASE,Firstupper,lowercase,MiXeD}" ) )    
        meta.add_meta_feat( MetaFeat( "hyphen", "{True,False}" ) )        
        self.chain.handle_meta(meta, info)


    def handle_candidate(self, candidate, info={}) :
        """
            For each candidate, generates two new features that correspond to the
            POS pattern and to the number of words in the candidate. Then, prints
            the new candidate with the two extra features.
            
            @param candidate The `Candidate` that is being read from the XML file.
        """
        pattern = candidate.get_pos_pattern().replace( SEPARATOR, "-" )
        candidate.add_feat( Feature( "pos_pattern", pattern ) )
        candidate.add_feat( Feature( "n", len( candidate ) ) )
        case_classes = {}
        #pdb.set_trace()
        has_hyphen = False
        for w in candidate :
            case_class = w.get_case_class()
            count_class = case_classes.get( case_class, 0 )
            case_classes[ case_class ] = count_class + 1
            has_hyphen = has_hyphen or "-" in w.lemma
        argmax_case_class = max( zip( case_classes.values(), 
                                      case_classes.keys() ) )[ 1 ]
        candidate.add_feat( Feature( "capitalized", argmax_case_class ) )        
        candidate.add_feat( Feature( "hyphen", str( has_hyphen ) ) )
        self.chain.handle_candidate(candidate, info)


################################################################################
# MAIN SCRIPT

args = read_options( "", [], treat_options_simplest, 1, usage_string )

# Done in 2 passes, one to define the type of the feature and another to
# print the feature values for each candidate
verbose( "1st pass : recover all POS patterns for meta feature" )
# Will ignore meta information and simply recover all the possible patterns
filetype.parse(args, RecovererHandler())

# Second pass to print the metafeat header with all possible pattern values
verbose( "2nd pass : add the features" )
filetype.parse(args, FeatGeneratorHandler())
