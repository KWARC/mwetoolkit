#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# meta.py is part of mwetoolkit
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
    This module provides the `Meta` class. This class represents the header of 
    the XML file, describing several meta-information about the canidate list 
    that the file contains.
"""

################################################################################

class Meta :
    """
        Meta-information at the header of a candidates list XML file. The `Meta`
        header includes information about the corpora used to calculate word and
        ngram frequencies, the types of the features that were calculated for
        each candidate and the number of evaluation base for the True
        Positive judgement of each candidate.
    """

################################################################################
    
    def __init__( self, corpus_sizes, meta_feats, meta_tpclasses ) :
        """
            Instanciates a `Meta` heeader with the corresponding lists of corpus
            sizes, meta-features and meta-TP base.
            
            @param corpus_sizes A list of objects of type `CorpusSize` that 
            describe the number of tokens of the corpora used in this candidate
            list for generating ngram and word frequencies.
            
            @param meta_feats A list of objects of type `MetaFeat` that describe
            the name and type of each feature of each candidate. The types may
            be one of the valid types according to WEKA's arff file format.
            
            @param meta_tpclasses A list of objects of type `MetaTPClass` that
            describe the number of base of each evaluation (`TPClass`) of the
            candidate. The evaluation can be 2-base, in which case
            MetaTPClass will probably have the type "{True,False}", or 
            multiclass, where a larger number of possible base is defined.
            
            @return A new instance of `Meta` information header.
        """                 
        self.corpus_sizes = corpus_sizes
        self.meta_feats = meta_feats
        self.meta_tpclasses = meta_tpclasses

################################################################################
        
    def is_dummy( self ) :
        """
            Return True iff this is an empty Meta object.
        """
        return 0 == len(self.corpus_sizes) == len(self.meta_feats) \
                 == len(self.meta_tpclasses)

################################################################################
        
    def add_corpus_size( self, corpus_size ) :
        """
            Add a corpus size information to the list of corpora sizes of the 
            candidate.
            
            @param feat A `CorpusSize` of this candidate. No test is performed 
            in order to verify whether this is a repeated feature in the list.        
        """
        self.corpus_sizes.append( corpus_size )

################################################################################
        
    def add_meta_feat( self, meta_feat ) :
        """
            Add a meta-feature to the list of meta-features of the candidate.
            
            @param feat A `MetaFeat` of this candidate. No test is performed in 
            order to verify whether this is a repeated feature in the list.        
        """
        self.meta_feats.append( meta_feat )

################################################################################

    def add_meta_tpclass( self, meta_tpclass ) :
        """
            Add a meta True Positive class to the list of features of the 
            candidate.
            
            @param feat A `MetaTPClass` of this candidate. No test is performed 
            in order to verify whether this is a repeated feature in the list.
        """
        self.meta_tpclasses.append( meta_tpclass )

################################################################################
        
    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <meta> with its internal
            structure, according to mwetoolkit-candidates.dtd.
        """
        result = "<meta>\n"
        for corpus_size in self.corpus_sizes :
            result = result + "    " + corpus_size.to_xml() + "\n"
        for meta_feat in self.meta_feats :
            result = result + "    " + meta_feat.to_xml() + "\n"            
        for meta_tpclass in self.meta_tpclasses :
            result = result + "    " + meta_tpclass.to_xml() + "\n"            
        result = result + "</meta>"        
        return result    
        
################################################################################

    def get_feat_type( self, feat_name ) :
        """
        """
        for feat in self.meta_feats :
            if feat.name == feat_name :
                return feat.value
        return None

################################################################################

if __name__ == "__main__" :
    import doctest
    doctest.testmod()
