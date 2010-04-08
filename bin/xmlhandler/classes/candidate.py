#!/usr/bin/python
"""
    This module provides the Candidate class. This class is a representation of 
    a MWT candidate, including base form, id, occurrences, features and the TP 
    class (true/false MWT).
"""

from __common import UNKNOWN_FEAT_VALUE

################################################################################

class Candidate :
    """
        A MWT candidate is a sequence of words extracted from the corpus. The
        sequence of words has a base form ngram (generally lemmas) and a list of
        occurrence ngrams. Features may me added to the candidate, such as 
        Association Measures. The candidate also might be evaluated as a True
        Positive according to several gold standards (references) so it also 
        contains a list of TP judgements.
    """

################################################################################

    def __init__( self, base, id_number, occurs, features, tpclasses ) :
        """
            Instanciates the Multiword Term candidate.
            
            @param base `Ngram` that represents the base form of the candidate.
            A base form is generally a non-inflected sequence of lemmas (unless
            you specified to consider surface forms instead of lemmas)
            
           @param id_number Unique integer that identifies this candidate in its
           context.
           
           @param occurs List of `Ngram`s that represent all the different 
           occurrences of this candidate. It is possible to find different
           occurrences when, for instance, several inflections are employed to
           a verb inside the candidate, but all these inflections correspond to
           a single lemma or base form of the verb.
           
           @param features List of `Feature`s that describe the candidate in the
           sense of Machine Learning features. A feature is a pair name-value
           and can be an Association Measure, linguistic information, etc.
           
           @param tpclasses List of `TPClass`es that represent an evaluation of
           the candidate. It can correspond, for example, to a list of human
           judgements about it being or not a MWT. The class is probably boolean
           but multiclass values are allowed, as long as the concerned machine
           learning algorithm can deal with it.
           
           @return A new Multiword Term `Candidate` .
        """
        self.base = base                  # Ngram
        self.id_number = id_number        # int
        self.occurs = occurs              # Ngram list
        self.features = features          # Feature list
        self.tpclasses = tpclasses        # TPClass list
        
################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <cand> with its internal
            structure, according to mwttoolkit-candidates.dtd.
        """
        result = "<cand"
        if self.id_number >= 0 :
            result = result + " candid=\"" + str(self.id_number) + "\">\n"

        # Unicode support          
        base_string = self.base.to_xml()
        if isinstance( base_string, str ) :
            base_string = unicode( base_string, 'utf-8')
        result = result + "    " + base_string + "\n"        

        result = result + "    <occurs>\n"             
        if self.occurs :
            for occur in self.occurs :
                # Unicode support
                occur_string = occur.to_xml()
                if isinstance( occur_string, str ) :
                    occur_string = unicode( occur_string, 'utf-8')
                result = result + "    " + occur_string +"\n"
        result = result + "    </occurs>\n"                
        if self.features :
            result = result + "    <features>\n"
            for feat in self.features :
                result = result + "        " + feat.to_xml() + "\n"
            result = result + "    </features>\n" 
        if self.tpclasses :
            for tpclass in self.tpclasses :
                result = result + "    " + tpclass.to_xml() + "\n"                         
        return result + "</cand>"
        
################################################################################

    def add_occur( self, occur ) :
        """
            Add an occurrence to the list of occurrences of the candidate.
            
            @param occur `Ngram` that corresponds to an occurrence of this 
            candidate. No test is performed in order to verify whether this is a 
            repeated occurrence in the list.
        """
        self.occurs.append( occur )
        
################################################################################

    def add_feat( self, feat ) :
        """
            Add a feature to the list of features of the candidate.
            
            @param feat A `Feature` of this candidate. No test is performed in 
            order to verify whether this is a repeated feature in the list.        
        """
        self.features.append( feat )     

################################################################################

    def add_tpclass( self, tpclass ) :
        """
            Add a True Positive class to the list of TP classes of the 
            candidate.
            
            @param tpclass A `TPClass` corresponding to an evaluation or 
            judgment of this candidate concerning its appartenance to a 
            reference list (gold standard) or its MWT status according to an 
            expert. No test is performed in order to verify whether this is a 
            repeated TP class in the list.                
        """
        self.tpclasses.append( tpclass ) 
        
################################################################################

    def get_feat_value( self, feat_name ) :
        """
            Returns the value of a `Feature` in the features list. The feature
            is identified by the feature name provided as input to this 
            function. If two features have the same name, only the first 
            value found will be returned.
            
            @param feat_name A string that identifies the `Feature` of the 
            candidate for which you would like to know the value.
            
            @return Value of the searched feature. If there is no feature with
            this name, then it will return `UNKNOWN_FEAT_VALUE` (generally "?"
            as in the WEKA's arff file format).
        """
        for feat in self.features :
            if feat.name == feat_name :
                return feat.value
        return UNKNOWN_FEAT_VALUE                   

################################################################################
        
if __name__ == "__main__" :
    import doctest
    doctest.testmod()               
