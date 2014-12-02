# !/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# candidate.py is part of mwetoolkit
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
    This module provides the Candidate class. This class is a representation of 
    a MWE candidate, including base form, id, occurrences, features and the TP
    class (true/false MWE).
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from .entry import Entry
from .__common import UNKNOWN_FEAT_VALUE

################################################################################

class Candidate ( Entry ) :
    """
        A MWE candidate is a sequence of words extracted from the corpus. The
        sequence of words has a base form ngram (generally lemmas) and a list of
        occurrence ngrams. Features may me added to the candidate, such as 
        Association Measures. The candidate also might be evaluated as a True
        Positive according to several gold standards (references) so it also 
        contains a list of TP judgements.
    """

################################################################################

    def __init__( self, id_number, base=None, features=None,
                 bigrams=None, occurs=None, tpclasses=None, vars=None ) :
        """
            Instanciates the Multiword Expression candidate.
            
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

           @param bigrams List of `Ngram`s that represent all the different 
           bigrams of this candidate. 
           
           @param features List of `Feature`s that describe the candidate in the
           sense of Machine Learning features. A feature is a pair name-value
           and can be an Association Measure, linguistic information, etc.
           
           @param tpclasses List of `TPClass`es that represent an evaluation of
           the candidate. It can correspond, for example, to a list of human
           judgements about it being or not a MWE. The class is probably boolean
           but multiclass values are allowed, as long as the concerned machine
           learning algorithm can deal with it.

           @param vars The list of possible variations of a candidate. These
           variations may be used to validade different syntactic configurations
           in the Web or in a corpus. For more information, take a look at the
           variation entropy measure suggested in the paper "Picking them up
           and Figuring them out" that we published in CoNLL 2008.
           
           @return A new Multiword Term `Candidate` .
        """
        super(Candidate,self).__init__(id_number,base,features)
        self.bigrams = bigrams if bigrams else []
        self.occurs = occurs if occurs else []             # Ngram list
        self.tpclasses = tpclasses if tpclasses else []        # TPClass list
        self.freqs = []
        self.features = features if features else []
        self.vars = vars if vars else []
        
################################################################################

    def to_plaincandidate(self):
        r"""Return this Candidate in the PlainCandidates format."""
        return "_".join(w.lemma_or_surface() for w in self)

################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <cand> with its internal
            structure, according to mwetoolkit-candidates.dtd.
        """
        result = "<cand"
        if self.id_number >= 0 :
            result = result + " candid=\"" + str(self.id_number) + "\">\n"

        # Unicode support          
        base_string = super( Candidate, self ).to_xml()
        if isinstance( base_string, str ) :
            base_string = unicode( base_string, 'utf-8')
        result = result + "    " + base_string + "\n"        

        if self.bigrams :
            result = result + "    <bigram>\n"
            for bigram in self.bigrams :
                # Unicode support
                bigram_string = bigram.to_xml()
                if isinstance( bigram_string, str ) :
                    bigram_string = unicode( bigram_string, 'utf-8')
                result = result + "    " + bigram_string +"\n"
            result = result + "    </bigram>\n"

        if self.occurs :
            result = result + "    <occurs>\n"
            for occur in self.occurs :
                # Unicode support
                occur_string = occur.to_xml()
                if isinstance( occur_string, str ) :
                    occur_string = unicode( occur_string, 'utf-8')
                result = result + "    " + occur_string +"\n"
            result = result + "    </occurs>\n"

        if self.vars :
            result = result + "    <vars>\n"
            for var in self.vars :
                # Unicode support
                var_string = var.to_xml()
                if isinstance( var_string, str ) :
                    var_string = unicode( var_string, 'utf-8')
                result = result + "    " + var_string +"\n"
            result = result + "    </vars>\n"

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

    def add_bigram( self, bigram ) :
        """
            Add an bigram to the list of bigrams of the candidate.
            
            @param bigram `Ngram` that corresponds to an bigram of this 
            candidate. 
        """
        self.bigrams.append( bigram )

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

    def add_var( self, var ) :
        """
            Add a variation to the list of variations of the candidate.

            @param var `Ngram` that corresponds to a variation of this
            candidate. No test is performed in order to verify whether this is a
            repeated variation in the list.
        """
        self.vars.append( var )

################################################################################

    def add_tpclass( self, tpclass ) :
        """
            Add a True Positive class to the list of TP classes of the 
            candidate.
            
            @param tpclass A `TPClass` corresponding to an evaluation or 
            judgment of this candidate concerning its appartenance to a 
            reference list (gold standard) or its MWE status according to an 
            expert. No test is performed in order to verify whether this is a 
            repeated TP class in the list.                
        """
        self.tpclasses.append( tpclass )

################################################################################

    def get_tpclass_value( self, tpclass_name ) :
        """
            Returns the value of a `TPClass` in the tpclasses list. The TP class
            is identified by the class name provided as input to this
            function. If two classes have the same name, only the first
            value found will be returned.

            @param tpclass_name A string that identifies the `TPClass` of the
            candidate for which you would like to know the value.

            @return Value of the searched tpclass. If there is no tpclass with
            this name, then it will return `UNKNOWN_FEAT_VALUE` (generally "?"
            as in the WEKA's arff file format).
        """
        for tpclass in self.tpclasses :
            if tpclass.name == tpclass_name :
                return tpclass.value
        return UNKNOWN_FEAT_VALUE
