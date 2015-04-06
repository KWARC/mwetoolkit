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
from .feature import FeatureSet
from .frequency import Frequency
from .__common import UNKNOWN_FEAT_VALUE



class CandidateFactory(object):
    r"""Instances of CandidateFactory can be used
    to create instances of Candidate with automatic
    definition of its `id_number` attribute.

    Call `self.make(word_list)` to create a Candidate.

    Call `self.uniquified(candidate_instance)` to add it to
    an internal mapping word_list -> Candidate.  The new
    `candidate_instance` is returned by this method.
    """
    FIRST_ID = 1
    def __init__(self):
        self.prev_id = self.FIRST_ID-1
        self.mapping = {}

    def make_uniq(self, word_list, **kwargs):
        r"""Utility function that calls `make` and returns it `uniquified`.
        The word list must ALREADY be full if calling `make_uniq`."""
        return self.uniquified(self.make(word_list, **kwargs))

    def make(self, word_list=[], id_number=None, **kwargs):
        r"""Calls `Candidate(id_number, word_list, ...)` to create a Candidate."""
        self.prev_id = int(id_number if id_number is not None else self.prev_id+1)
        return Candidate(base=word_list, id_number=self.prev_id, **kwargs)

    def uniquified(self, candidate):
        r"""Return uniq'd version of this Candidate.
        Make sure that `candidate.word_list` elements
        will NOT be changed anymore.
        """
        # TODO implement Word.freeze and call it here, to avoid bugs
        key = tuple(w.to_string() for w in candidate.word_list)
        try:
            ret = self.mapping[key]
        except KeyError:
            ret = self.mapping[key] = candidate
        else:
            ret.merge_from(candidate)
        return ret


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
        super(Candidate,self).__init__(id_number,base,None,features)
        self.bigrams = set(bigrams or ())
        self.occurs = set(occurs or ())  # Ngram list
        assert not tpclasses or isinstance(tpclasses, FeatureSet), tpclasses
        self.tpclasses = tpclasses or FeatureSet("tpclass", lambda x,y: x+y)  # TPClass list
        self.vars = set(vars or ())
        
################################################################################

    def merge_from(self, other):
        r"""Merge `other` into `self`."""
        super(Candidate, self).merge_from(other)
        self.occurs.update(other.occurs)
        self.features.merge_from(other.features)
        self.tpclasses.merge_from(other.tpclasses)

################################################################################

    def to_plaincandidate(self):
        r"""Return this Candidate in the PlainCandidates format."""
        return "_".join(w.lemma_or_surface() for w in self)

################################################################################

    def to_xml(self):
        """Provides an XML string representation of the
        current object, including internal variables.
            
        @return A string containing the XML element <ngram> with its 
        internal structure, according to mwetoolkit-candidates.dtd.
        """
        ret = ['<cand candid="', unicode(self.id_number), '">']
        self._to_xml_into(ret)
        ret.append("</cand>")
        return "".join(ret)


    def _to_xml_into( self, output ) :
        r"""Output stuff into `output`, to be "".join()'ed
        inside the `to_xml` caller function.
        """
        output.append("\n    <ngram>")
        super(Candidate, self)._to_xml_into(output, _print_features=False)
        output.append("</ngram>\n")

        if self.bigrams :
            output.append("    <bigram>\n")
            for bigram in self.bigrams :
                output.append("       ")
                output.append(bigram.to_xml())
                output.append("\n")
            output.append("    </bigram>\n")

        if self.occurs :
            output.append("    <occurs>\n")
            for occur in self.occurs :
                # XXX use 8 spaces here, not 4 (but only after we have
                # regression tests ready)
                output.append("    ")
                output.append(occur.to_xml())
                output.append("\n")
            output.append("    </occurs>\n")

        if self.vars :
            output.append("    <vars>\n")
            for var in self.vars :
                output.append("        ")
                output.append(var.to_xml())
                output.append("\n")
            output.append("    </vars>\n")

        if self.features :
            output.append("    <features>\n")
            self.features._to_xml_into(output, indent=8, after_each="\n")
            output.append("    </features>\n")

        if self.tpclasses :
            self.tpclasses._to_xml_into(output, indent=4, after_each="\n")

        
################################################################################

    def add_bigram( self, bigram ) :
        """
            Add an bigram to the list of bigrams of the candidate.
            
            @param bigram `Ngram` that corresponds to an bigram of this 
            candidate. 
        """
        self.bigrams.add( bigram )

################################################################################

    def add_occur( self, occur ) :
        """
            Add an occurrence to the list of occurrences of the candidate.
            
            @param occur `Ngram` that corresponds to an occurrence of this 
            candidate. No test is performed in order to verify whether this is a 
            repeated occurrence in the list.
        """
        self.occurs.add( occur )

################################################################################

    def add_var( self, var ) :
        """
            Add a variation to the list of variations of the candidate.

            @param var `Ngram` that corresponds to a variation of this
            candidate. No test is performed in order to verify whether this is a
            repeated variation in the list.
        """
        self.vars.add( var )

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
        self.tpclasses.add( tpclass.name, tpclass.value )

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
        return self.tpclasses.get_feature(tpclass_name, UNKNOWN_FEAT_VALUE).value
