#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# 
# Copyright 2010 Carlos Ramisch
# 
# lemmatise.py is part of mwetoolkit
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
   Simple lemmatisation algorithm.
"""

import pdb
import sys
import math
import xml.sax

from xmlhandler.genericXMLHandler import GenericXMLHandler
from util import usage, read_options, treat_options_simplest, verbose
from xmlhandler.classes.yahooFreq import YahooFreq
from xmlhandler.classes.googleFreq import GoogleFreq
from config import DEFAULT_LANG

################################################################################
# GLOBALS

usage_string = """Usage:

python %(program)s [OPTIONS] <files.xml>

OPTIONS may be:

-v OR --verbose
    Print messages that explain what is happening.

-w OR --google
    Search for frequencies in the Web using Google Web Search as approximator
    for Web document frequencies (DEFAULT).

-y OR --yahoo
    Search for frequencies in the Web using Yahoo Web Search as approximator for
    Web document frequencies.

    The <files.xml> file(s) must be valid XML (dtd/mwetoolkit-*.dtd).
"""
web_freq = GoogleFreq()
lang = DEFAULT_LANG
entity_counter = 0

################################################################################

def treat_meta( meta ) :
    """
        Simply prints the meta header to the output without modifications.

        @param meta The `Meta` header that is being read from the XML file.
    """

    print meta.to_xml().encode( 'utf-8' )

################################################################################

def lemmatise_en( w ) :
        """
        Heuristic singularisation of English nouns is done as follows:

        Remark: we assume regular plurals. Special cases like men, people or
        children are ignored.

        Examples that work nicely: virus, analyses, access, abnormalities,
        heroes, days, airways...
        """
        MAX_RATIO = 6 # Maximum number of times a plural must occur more than a
                      # singular to avoid lemmatisation        
        surf = w.surface
        # Nouns finishing with "s"
        if surf.endswith( "s" ) and w.pos == "N" and len( surf ) > 2:
            # avoid problems with "access", "weakness", "analysis", "virus", "bolus"
            if surf.endswith( "ss" ) or surf.endswith( "is" ) or surf.endswith( "us" ) :
                return surf
            elif surf.endswith ( "ies" ) : # body - bodies
                s_form = surf[ 0 : len( surf ) - 3 ] + "y"
            elif w.surface.endswith ( "oes" ) : # hero - heroes
                s_form = surf[ 0 : len( surf ) - 2 ]
            else :
                s_form = surf[ 0 : len( surf ) - 1 ]
            freq_plural = web_freq.search_frequency( w.surface )
            freq_singular = web_freq.search_frequency( s_form )
            if freq_singular > MAX_RATIO * freq_plural :
                return s_form
            else :
                if s_form.endswith( "xe" ) or s_form.endswith( "che" ) or s_form.endswith( "she" ):
                    ses_form = s_form[ 0 : len( s_form ) - 1 ]
                    freq_ses = web_freq.search_frequency( ses_form )
                    if freq_ses > freq_singular :
                        return ses_form
                    else :
                        return surf
                elif s_form.endswith( "se" ) :
                    ses_form = s_form[ 0 : len( s_form ) - 1 ]
                    sis_form = s_form[ 0 : len( s_form ) - 1 ] + "is" # Case for analysis and similars
                    freq_ses = web_freq.search_frequency( ses_form )
                    freq_sis = web_freq.search_frequency( sis_form )
                    if ( freq_sis > freq_ses and freq_ses >= freq_singular ) or ( freq_sis > freq_singular and freq_singular >= freq_ses ) :
                        return sis_form
                    elif ( freq_ses > freq_sis and freq_sis >= freq_singular ) or ( freq_ses > freq_singular and freq_singular >= freq_sis ):
                        return ses_form
                    else :
                        return s_form
                else :
                    # I.e. the plural form is highly predominant
                    # The term log(freq_singular) was added because it adds a
                    # lot of value to singular forms with high frequencies. Ex.
                    # f(circumstances) is 376000000
                    # f(circumstance) is 46400000
                    if freq_singular != 0 \
                            and freq_plural > MAX_RATIO * math.log( freq_singular ) * freq_singular:
                        return surf
                    else :
                        return s_form
        else : # TODO: treat other types of words, not only nouns (or use a real
               # lemmatiser!)
            return w.surface

################################################################################

def treat_entity( entity ) :
    """
        For each sentence in the corpus, lemmatise its words.

        @param entity A subclass of `Ngram` that is being read from the XML file
    """
    global lang, entity_counter
    if entity_counter % 100 == 0 :
        verbose( "Processing ngram number %(n)d" % { "n":entity_counter } )    
    for w in entity :
        if lang == "en" :
            w.lemma = lemmatise_en( w )
    print entity.to_xml().encode( 'utf-8' )
    entity_counter += 1

################################################################################

def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.

        @param opts The options parsed by getopts. Ignored.

        @param arg The argument list parsed by getopts.

        @param n_arg The number of arguments expected for this script.
    """
    global web_freq
    mode = []
    for ( o, a ) in opts:
        if o in ( "-y", "--yahoo" ) :
            web_freq = YahooFreq()
            mode.append( "yahoo" )
        elif o in ( "-w", "--google" ) :
            web_freq = GoogleFreq()
            mode.append( "google" )

    if len(mode) > 1 :
        print >> sys.stderr, "At most one option -y or -w, should be provided"
        usage( usage_string )
        sys.exit( 2 )

    treat_options_simplest( opts, arg, n_arg, usage_string )

################################################################################
# MAIN SCRIPT

longopts = [ "verbose", "google", "yahoo" ]
arg = read_options( "vwy", longopts, treat_options, -1, usage_string )

try :
    parser = xml.sax.make_parser()
    handler = GenericXMLHandler( treat_meta=treat_meta,
                                 treat_entity=treat_entity,
                                 gen_xml=True )
    parser.setContentHandler( handler )
    if len( arg ) == 0 :
        parser.parse( sys.stdin )
        print handler.footer
    else :
        for a in arg :
            input_file = open( a )
            parser.parse( input_file )
            footer = handler.footer
            handler.gen_xml = False
            input_file.close()
            entity_counter = 0
        print footer
except IOError, err :
    print >> sys.stderr, err
#except Exception, err :
#    print >> sys.stderr, err
#    print >> sys.stderr, "You probably provided an invalid XML file," +\
#                         " please validate it against the DTD " + \
#                         "(dtd/mwetoolkit-*.dtd)"
finally :
    if web_freq :
        web_freq.flush_cache()
