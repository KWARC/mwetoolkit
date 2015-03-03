#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# word.py is part of mwetoolkit
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
    This module provides the `Word` class. This class represents an orthographic
    word (as in mwetoolkit-corpus.dtd, mwetoolkit-patterns.dtd and 
    mwetoolkit-candidates.dtd) defined by a surface form, a lemma and a POS tag.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

from xml.sax.saxutils import quoteattr
from .__common import WILDCARD, SEPARATOR


# List of valid word attributes. Must appear in the same order as the
# arguments for the Word class constructor.
WORD_ATTRIBUTES = ["surface", "lemma", "pos", "syn"]


################################################################################

class Word :
    """
        An orthographic word (in languages for which words are separated from 
        each other by a space) is the simplest lexical unit recognisable by a
        native speaker, and it is characterized by its surface form, its lemma 
        and its Part Of Speech tag.
    """

################################################################################

    def __init__(self, surface=WILDCARD, lemma=WILDCARD,
            pos=WILDCARD, syn=WILDCARD, freqs=None):
        """
            Instantiates a new `Word`. A Word might be one of: a token in a 
            corpus, in which case it will probably have at least a defined 
            surface form (mwetoolkit-corpus.dtd); a part of a pattern, in which
            case it will probably contain some `WILDCARD`s; a part of a 
            reference or gold standard entry, in which case it will have at 
            least a defined lemma (mwetoolkit-patterns.dtd); a part of an n-gram
            in a candidates list, in which case most of the parts should be
            defined (mwetoolkit-candidates.dtd). Besides the surface form, the
            lemma and the Part Of Speech tag, a word also contains a list of
            `Frequency`ies, each one corresponding to its number of occurrences 
            in a given corpus.
            
            @param surface A string corresponding to the surface form of the
            word, i.e. the form in which it occurs in the corpus. A surface form
            might include morphological inflection such as plural and gender
            marks, conjugation for verbs, etc. For example, "went", "going", 
            "go", "gone", are all different surface forms for a same lemma, the
            verb "(to) go".
            
            @param lemma A string corresponding to the lemma of the word, i.e.
            the normalized non-inflected form of the word. A lemma is generally
            the preferred simplest form of a word as it appears in a dictionary,
            like infinitive for verbs or singular for nouns. Notice that a lemma
            is a well formed linguistic word, and thus differs from a root or
            a stem. For example, the lemma of the noun "preprocessing" is
            "preprocessing" while the root (without prefixes and suffixes) is
            "process". Analagously, the lemma of the verb "studied" is "(to) 
            study" whereas a stem would be "stud-", which is not an English
            word.
            
            @param pos A string corresponding to a Part Of Speech tag of the 
            word. A POS tag is a morphosyntactic class like "Noun", "Adjective"
            or "Verb". You should use a POS tagger system to tag your corpus
            before you use mwetoolkit. The tag set, i.e. the set of valid POS
            tags, is your choice. You can use a very simple set that 
            distinguishes only top-level classes ("N", "A", "V") or a fine-
            grained classification, e.g. "NN" is a proper noun, "NNS" a proper
            noun in plural form, etc.

            @param syn A string corresponding to a syntax information of the
            word. AS the jungle of syntactic formalisms is wild, we assume that
            each word has a string that encodes the syntactic information. If
            you use a dependency parser, for instance, you might encode the
            syntax information as "rel:>index" where "rel" is the type of
            syntactic relation (object, subject, det, etc.) and the "index" is
            the index of the word on which this word depends. An example can be
            found in the corpus DTD file.
            
            @param freqs A list of `Frequency`ies corresponding to counts of 
            occurrences of this word in a certain corpus. Please notice that
            the frequencies correspond to occurrences of a SINGLE word in a 
            corpus. Joint `Ngram` frequencies are attached to the corresponding 
            `Ngram` object that contains this `Word`, if any.
        """
        self.surface = surface
        self.lemma = lemma
        self.pos = pos
        self.syn = syn
        self.freqs = freqs or []

################################################################################

    def dup(self):
        r"""Return a copy of this Word."""
        return Word(self.surface, self.lemma,
                self.pos, self.syn, list(self.freqs))

################################################################################

    def lemma_or_surface(self):
        r"""Return lemma if it is defined; otherwise, return surface."""
        if self.lemma != WILDCARD:
            return self.lemma
        if self.surface != WILDCARD:
            return self.surface
        return None

################################################################################

    def add_frequency( self, freq ) :
        """
            Add a `Frequency` to the list of frequencies of the word.
            
            @param freq `Frequency` that corresponds to a count of this word in 
            a corpus. No test is performed in order to verify whether this is a 
            repeated frequency in the list.
        """
        self.freqs.append( freq )

################################################################################
            
    def to_string( self ) :
        """
            Converts this word to an internal string representation where each           
            part of the word is separated with a special `SEPARATOR`. This is 
            only used internally by the scripts and is of little use to the
            user because of reduced legibility. Deconversion is made by the 
            function `from_string`.
            
            @return A string with a special internal representation of the 
            word.
        """
        return self.surface + SEPARATOR +\
                self.lemma + SEPARATOR +\
                self.pos
                
################################################################################
            
    def from_string( self, s ) :
        """ 
            Instanciates the current word by converting to an object 
            an internal string representation where each part of the word is 
            separated with a special `SEPARATOR`. This is only used internally 
            by the scripts and is of little use to the user because of reduced 
            legibility. Deconversion is made by the function `to_string`.
            
            @param s A string with a special internal representation of
            the word, as generated by the function `to_string`
        """
        [ self.surface, self.lemma, self.pos ] = s.split( SEPARATOR )
        
################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <w> with its 
            internal structure, according to mwetoolkit-candidates.dtd, 
            mwetoolkit-patterns.dtd and mwetoolkit-corpus.dtd. Attributes that
            do not have a defined value (i.e. are `WILDCARD`) are not printed.
        """
        # TODO merge `to_xml_custom` into `to_xml`?
        return self.to_xml_custom()


################################################################################

    def to_html( self, wid ) :
        """
            TODO
            @return TODO
        """
        # TODO: properly escape this stuff
        wtempl = "<a href=\"#\" class=\"word\">%(surface)s" \
                 "<span class=\"wid\">%(wid)d</span>" \
                 "<span class=\"lps\">%(lemma)s%(pos)s%(syn)s</span></a>"
        templ = lambda x: "<span class=\"%s\">%s</span>" % (x, getattr(self,x))
        attr_map = map( lambda x: (x, templ(x)), WORD_ATTRIBUTES) + [("wid", wid)]
        return wtempl % dict(attr_map)

################################################################################
        
    def to_xml_custom(self, print_surface=True, print_lemma=True,
                       print_pos=True, print_syn=True, print_freqs=True):
        """
            Provides an XML string representation of the current object, 
            including internal variables. The printed attributes of the word
            depend on the boolean parameters.
            
            @param print_surface If print_surface is True, will include the 
            `surface` of the word in the XML <w> element, otherwise the surface 
            form will not be printed. Default True.
            
            @param print_lemma If print_lemma is True, will include the `lemma` 
            of the word in the XML <w> element, otherwise the lemma will not be 
            printed. Default True.
            
            @param print_pos If print_pos is True, will include the `pos` of the 
            word in the XML <w> element, otherwise the Part Of Speech will not 
            be printed. Default True.
            
            @param print_freqs If print_freqs is True, will include the `freqs` 
            of the word as children of the XML <w> element, otherwise the word 
            frequencies will not be printed. Default True.
            
            @return A string containing the XML element <w> with its attributes
            and internal structure, according to mwetoolkit-candidates.dtd, 
            mwetoolkit-patterns.dtd and mwetoolkit-corpus.dtd and 
            depending on the input flags.
        """
        result = "<w"
        if self.surface != WILDCARD and print_surface:
            result += " surface=" + quoteattr(self.surface)
        if self.lemma != WILDCARD and print_lemma:
            result += " lemma=" + quoteattr(self.lemma)
        if self.pos != WILDCARD and print_pos:
            result += " pos=" + quoteattr(self.pos)
        if self.syn != WILDCARD and print_syn:
            result += " syn=" + quoteattr(self.syn)
        if not self.freqs or not print_freqs:
            return result + " />"
        else:
            result = result + " >"
            for freq in self.freqs :
                result = result + freq.to_xml()                
            return result + "</w>"

################################################################################

    def __eq__( self, a_word ) :
        """
            Equivalent to match( w )
        """
        return self.match( a_word )

################################################################################

    def __len__( self ) :
        """
            Returns the number of characters in a word. Chooses upon available
            information, in priority order surface > lemma > pos.

            @return The number of characters in this word. Zero if this is an
            empty word (or all fields are wildcards)
        """
        if self.surface != WILDCARD :
            return len( self.surface )
        elif self.lemma != WILDCARD :
            return len( self.lemma )
        elif self.pos != WILDCARD :
            return len( self.pos )
        else :
            return 0

################################################################################

    def compare( self, s1, s2, ignore_case ) :
        """
            Compares two strings for equality conditioning the type of
            comparison (case sensitive/insensitive) to boolean argument
            `ignore_case`.

            @param s1 A string to compare.

            @param s2 Another string to compare.

            @param ignore_case True if comparison should be case insensitive,
            False if comparision should be case sensitive.

            @return True if the strings are identical, False if they are
            different.
        """
        if ignore_case :
            return s1.lower() == s2.lower()
        else :
            return s1 == s2

################################################################################

    def match( self, w, ignore_case=False, lemma_or_surface=False ) :
        """
            A simple matching algorithm that returns true if the parts of the
            current word match the parts of the given word. The matching at the 
            word level considers only the parts that are defined, for example, 
            POS tags for candidate extraction or lemmas for automatic gold 
            standard evaluation. A match on a part of the current word is True 
            when this part equals to the corresponding part of `w` or when the 
            part of the current word is not defined (i.e. equals `WILDCARD`).
            All the three parts (surface, lemma and pos) need to match so that
            the match of the word is true. If ANY of these three word parts does
            not match the correspondent part of the given word `w`, this 
            function returns False.
            
            @param w A `Word` against which we would like to compare the current 
            word. In general, the current word contains the `WILDCARD`s while 
            `w` has all the parts (surface, lemma, pos) with a defined value.
            
            @return Will return True if ALL the word parts of `w` match ALL
            the word parts of the current pattern (i.e. they have the same 
            values for all the defined parts). Will return False if
            ANY of the three word parts does not match the correspondent part of 
            the given word `w`.
        """

        if self.pos!=WILDCARD and not self.compare(self.pos, w.pos, ignore_case):
            return False

        if lemma_or_surface:
            return ((self.compare(self.lemma, w.lemma, ignore_case)
                 or (self.compare(self.lemma, w.surface, ignore_case))
                 or (self.compare(self.surface, w.lemma, ignore_case))
                 or (self.compare(self.surface, w.surface, ignore_case))))
                  
        else:
            return ((self.surface==WILDCARD or self.compare(self.surface, w.surface, ignore_case))
                  and (self.lemma==WILDCARD or self.compare(self.lemma, w.lemma, ignore_case)))


        #return ((self.surface != WILDCARD and self.compare( self.surface,w.surface,ignore_case)) or \
        #     self.surface == WILDCARD) and \
        #     ((self.lemma != WILDCARD and self.compare( self.lemma, w.lemma, ignore_case ) ) or \
        #     self.lemma == WILDCARD) and \
        #     ((self.pos != WILDCARD and self.compare( self.pos, w.pos, ignore_case ) ) or \
        #     self.pos == WILDCARD)

            
################################################################################

    def get_case_class( self, s_or_l="surface" ) :
        """
            For a given word (surface form), assigns a class that can be:        
            * lowercase - All characters are lowercase
            * UPPERCASE - All characters are uppercase
            * Firstupper - All characters are lowercase except for the first
            * MiXeD - This token contains mixed lowercase and uppercase characters
            * ? - This token contains non-alphabetic characters
            
            @param s_or_l Surface or lemma? Default value is "surface" but set it
            to "lemma" if you want to know the class based on the lemma.

            @return A string that describes the case class according to the list 
            above.
        """
        form = getattr( self, s_or_l )
        if form != WILDCARD :
            token_list = list( form )
        else :
            token_list = []
        case_class = "?"
        for letter_i in range( len( token_list ) ) :
            letter = token_list[ letter_i ]
            if letter.isupper() :
                if letter_i > 0 :
                    if case_class == "lowercase" or case_class == "Firstupper" :
                        case_class = "MiXeD"
                    elif case_class == "?" :
                        case_class = "UPPERCASE"    
                else :
                    case_class = "UPPERCASE"                
            elif letter.islower() :
                if letter_i > 0 :                
                    if case_class == "UPPERCASE" :
                        if letter_i == 1 :
                            case_class = "Firstupper"
                        else :
                            case_class = "MiXeD"
                    elif case_class == "?" :
                        case_class = "lowercase"
                else :
                    case_class = "lowercase"
        return case_class    
    
################################################################################      

    def get_freq_value( self, freq_name ) :
        """
            Returns the value of a `Frequency` in the frequencies list. The 
            frequency is identified by the frequency name provided as input to 
            this function. If two frequencies have the same name, only the first 
            value found will be returned.
            
            @param freq_name A string that identifies the `Frequency` of the 
            candidate for which you would like to know the value.
            
            @return Value of the searched frequency. If there is no frequency 
            with this name, then it will return 0.
        """
        for freq in self.freqs :
            if freq.name == freq_name :
                return freq.value
        return 0     
