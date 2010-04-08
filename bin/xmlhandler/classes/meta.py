#!/usr/bin/python
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
        each candidate and the number of evaluation classes for the True 
        Positive judgement of each candidate.
    """

################################################################################
    
    def __init__( self, corpus_sizes, meta_feats, meta_tpclasses ) :
        """
            Instanciates a `Meta` heeader with the corresponding lists of corpus
            sizes, meta-features and meta-TP classes.
            
            @param corpus_sizes A list of objects of type `CorpusSize` that 
            describe the number of tokens of the corpora used in this candidate
            list for generating ngram and word frequencies.
            
            @param meta_feats A list of objects of type `MetaFeat` that describe
            the name and type of each feature of each candidate. The types may
            be one of the valid types according to WEKA's arff file format.
            
            @param meta_tpclasses A list of objects of type `MetaTPClass` that
            describe the number of classes of each evaluation (`TPClass`) of the
            candidate. The evaluation can be 2-classes, in which case 
            MetaTPClass will probably have the type "{True,False}", or 
            multiclass, where a larger number of possible classes is defined.
            
            @return A new instance of `Meta` information header.
        """                 
        self.corpus_sizes = corpus_sizes
        self.meta_feats = meta_feats
        self.meta_tpclasses = meta_tpclasses

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
            structure, according to mwttoolkit-candidates.dtd.
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
