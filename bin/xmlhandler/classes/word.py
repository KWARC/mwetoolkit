#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010 Carlos Ramisch
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
    word (as in mwttoolkit-corpus.dtd, mwttoolkit-patterns.dtd and 
    mwttoolkit-candidates.dtd) defined by a surface form, a lemma and a POS tag.
"""

from __common import WILDCARD, SEPARATOR

################################################################################

class Word :
    """
        An orthographic word (in languages for which words are separated from 
        each other by a space) is the simplest lexical unit recognisable by a
        native speaker, and it is characterized by its surface form, its lemma 
        and its Part Of Speech tag.
    """

################################################################################

    def __init__( self, surface, lemma, pos, freqs ) :
        """
            Instanciates a new `Word`. A Word might be one of: a token in a 
            corpus, in which case it will probably have at least a defined 
            surface form (mwttoolkit-corpus.dtd); a part of a pattern, in which
            case it will probably contain some `WILDCARD`s; a part of a 
            reference or gold standard entry, in which case it will have at 
            least a defined lemma (mwttoolkit-patterns.dtd); a part of an n-gram
            in a candidates list, in which case most of the parts should be
            defined (mwttoolkit-candidates.dtd). Besides the surface form, the
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
            before you use mwttoolkit. The tag set, i.e. the set of valid POS
            tags, is your choice. You can use a very simple set that 
            distinguishes only top-level classes ("N", "A", "V") or a fine-
            grained classification, e.g. "NN" is a proper noun, "NNS" a proper
            noun in plural form, etc.
            
            
            @param freqs A list of `Frequency`ies corresponding to counts of 
            occurrences of this word in a certain corpus. Please notice that
            the frequencies correspond to occurrences of a SINGLE word in a 
            corpus. Joint `Ngram` frequencies are attached to the corresponding 
            `Ngram` object that contains this `Word`, if any.
        """
        self.surface = surface
        self.lemma = lemma
        self.pos = pos
        self.freqs = freqs

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
        
######################################################################         
        
    def from_string( self, s ) :
        """ 
            Instanciates the current word by converting to an object 
            an internal string representation where each part of the word is 
            separated with a special `SEPARATOR`. This is only used internally 
            by the scripts and is of little use to the user because of reduced 
            legibility. Deconversion is made by the function `to_string`.
            
            @param the_string A string with a special internal representation of 
            the word, as generated by the function `to_string`
        """
        [ self.surface, self.lemma, self.pos ] = s.split( SEPARATOR )
        
################################################################################

    def to_xml( self ) :
        """
            Provides an XML string representation of the current object, 
            including internal variables.
            
            @return A string containing the XML element <w> with its 
            internal structure, according to mwttoolkit-candidates.dtd, 
            mwttoolkit-patterns.dtd and mwttoolkit-corpus.dtd. Attributes that
            do not have a defined value (i.e. are `WILDCARD`) are not printed.
        """
        result = "<w "
        if( self.surface != WILDCARD ) :
            result += "surface=\"" + self.surface + "\" "
        if( self.lemma != WILDCARD ) :
            result += "lemma=\"" + self.lemma + "\" "
        if( self.pos != WILDCARD ) :
            result += "pos=\"" + self.pos + "\" " 
        if not self.freqs :       
            return result + "/>"
        else :
            result = result + ">"
            for freq in self.freqs :
                result = result + freq.to_xml()                
            return result + "</w>"
        
################################################################################
        
    def to_xml_custom( self, print_surface=True, print_lemma=True,                        
                       print_pos=True, print_freqs=True ) :
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
            and internal structure, according to mwttoolkit-candidates.dtd, 
            mwttoolkit-patterns.dtd and mwttoolkit-corpus.dtd and 
            depending on the input flags.
        """
        result = "<w "
        if( self.surface != WILDCARD and print_surface ) :
            result += "surface=\"" + self.surface + "\" "
        if( self.lemma != WILDCARD and print_lemma ) :
            result += "lemma=\"" + self.lemma + "\" "
        if( self.pos != WILDCARD and print_pos ) :
            result += "pos=\"" + self.pos + "\" "        
        if not self.freqs or not print_freqs:       
            return result + "/>"
        else :
            result = result + ">"
            for freq in freqs :
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
        
    def match( self, w ) :
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
        if ((self.surface != WILDCARD and self.surface == w.surface) or \
             self.surface == WILDCARD) and \
           ((self.lemma != WILDCARD and self.lemma == w.lemma) or \
             self.lemma == WILDCARD) and \
           ((self.pos != WILDCARD and self.pos == w.pos) or \
             self.pos == WILDCARD) :
            return True
        else :
            return False
        
