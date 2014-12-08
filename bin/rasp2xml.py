#!/usr/bin/python
# -*- coding:UTF-8 -*-

###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos, Maitê Dupont
#
# rasp2xml.py is part of mwetoolkit
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
###############################################################################
"""
    This script transforms the output format of Rasp to the XML format of
    a corpus, as required by the mwetoolkit scripts. Only UTF-8 text is
    accepted. For generating the surface forms (not provided by RASP), please
    indicate the path to morphg program, provided with older versions of RASP
    and unfortunately not available anymore (but send me an email if you need
    it ;-)
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import os
import os.path
from subprocess import Popen, PIPE

from libs.util import read_options, verbose, treat_options_simplest, strip_xml,\
                 warn, error
from libs.base.__common import XML_HEADER, XML_FOOTER



###############################################################################
# GLOBALS 
morphg_folder = "X"
morphg_file = "X"
generate_text = False
work_path = os.getcwd() #store current working directory to restore later
d = ["index","surface","lemma","pos", "syn"]
usage_string = """Usage: 

python %(program)s OPTIONS <file_in>
    The <file_in> file must be rasp output when used without the -m option of 
    RASP parser (version 2 or 3).

OPTIONS may be:

-m OR --morphg
    Path to morphg. If this option is activated, you should provide the absolute
    path to the morphg installation folder.
    
-x OR --moses
    Generate the Moses factored text format instead of the usual mwetoolkit
    XML file. We will gradually move to this format and abandon the old 
    verbose XML files for corpora, since they create too large files.

%(common_options)s

"""
###############################################################################
def treat_options( opts, arg, n_arg, usage_string):
    """  
    Callback function that handles the command options of this script.

    @param opts The options parsed by getopts. Ignored.

    @param arg The argument list parsed by getopts.

    @param n_arg The number os arguments expected for this script.

    @param usage_string Instructions that appear if you run the program with
    the wrong parameters or options.
    """
    global morphg_folder
    global morphg_file
    global generate_text
    treat_options_simplest( opts, arg, n_arg, usage_string )
    for (o, a) in opts:
        if o in ("-m","--morphg"):
            morphg_folder, morphg_file = os.path.split( a )
        elif o in ("-x","--moses"):
            generate_text = True
    if not os.path.exists( os.path.join( morphg_folder, morphg_file ) ) :
        warn( "morphg not found !!! - outputting analysed forms" )
        morphg_file = None
        morphg_folder = None

###############################################################################

def write_entry(n_line, sent):
    """ 
        This function writes one sentence from the tagged corpus after 
        formating it into xml or Moses factored text.

        @param n_line Number of this line in the corpus, starting with 0
        
        @param sent Contains dictionaries corresponding to each word in the
        sentence.
    """
    global generate_text
    if generate_text :
        sent_templ ="%(sent)s"
        word_templ="%(surface)s|%(lemma)s|%(pos)s|%(syn)s"
    else :
        sent_templ ="<s s_id=\""+str(n_line)+"\">%(sent)s</s>"
        word_templ="<w surface=\"%(surface)s\" lemma=\"%(lemma)s\" pos="+\
                   "\"%(pos)s\" syn=\"%(syn)s\" />"
    print((sent_templ % { "sent":" ".join(map(lambda x: (word_templ % x), 
           sent)) }).encode("utf-8"))

###############################################################################

def get_tokens( word ) :
    """
        Given a string in RASP format representing a token like 
        "|resume+ed:7_VVN|" or "resume+ed\:7_VVN" (RASP 3), returns a tuple
        containing (lemma,index,pos). Lemma includes the +... morphological
        suffix.
    """
    if word.startswith("|") and word.endswith("|") : # regular token
        word = word[1:-1]    
    lemma_and_index, pos = word.rsplit( "_", 1 )
    lemma, index = lemma_and_index.rsplit( ":", 1 )
    if lemma.endswith("\\") :
        lemma = lemma[:-1]                           # separator was \:
    return (lemma,index,pos)

###############################################################################

def get_surface( lemma_morph, pos ) :
    """
        Given a lemma+morph in RASP format, returns a tuple containing (surface,
        lemma). Uses morphg to generate the surface, or returns 2 copies of
        the input if morphg was not provided.
    """
    global morphg_file
    parts = lemma_morph.rsplit("+",1)
    if len(parts) == 1 or lemma_morph == "+": # No inflection
        lemma = surface = lemma_morph
    elif len(parts) == 2 and "+" not in parts[0]: # Standard inflected unit
        lemma = parts[0] 
        if morphg_file is not None : 
            lemma_morph = lemma_morph.replace("\"","\\\"")
            cmd = "echo \"%s_%s\" | ${morphg_res:-./%s -t}" % \
                  ( lemma_morph, pos, morphg_file )
            p = Popen(cmd, shell=True, stdout=PIPE).stdout
            #generates the surface form using morphg
            surface = unicode(p.readline(), 'utf-8').split("_")[ 0 ]
            p.close()
        else:
            surface = lemma
    else: # the token contains one or several '+'
        lemma = surface = parts[0]
    return ( surface, lemma )

###############################################################################

def process_line( l, phrase ):
    """ 
        This function processes the tagged line, extracting each word and its 
        attributes. Information is stored in a list of dictionaries (one dict 
        per word) where will be filled all the words' attributes.

        @param l Line read from input to be processed.
        
        @param phrase List of dictionaries to be completed.
    """
    global generate_text
    words = l.split(" ")[:-3]                            #remove last 3 elements
    words = " ".join( words )[1:-1].split( " " )         # remove parentheses
    for (iword, word) in enumerate( words ) : #e.g.: resume+ed:7_VVN
        try :
            (s, index, pos) = get_tokens(word)
            (surface, lemma) = get_surface(s, pos)
            dic={d[1]:surface,d[2]:lemma,d[3]:pos,d[4]:'',d[0]:str(iword+1)}
            for key in dic.keys() :
                dic[key] = dic[key].replace(" ","") # remove spaces
                dic[key] = strip_xml(dic[key])
                if generate_text : # escape vertical bars
                    dic[key] = dic[key].replace( "|","%%VERTICAL_BAR%%" )
            phrase[ int(index) ] = dic
        except IndexError:
            warn( "Line \"%s\" could not be processed as sentence" % l.strip() )

###############################################################################

def process_tree_branch(l, phrase):
    """ 
        This function processed the dependency tree that follows each tagged
        sentence. Information to be retrieved from here is just the 'syn'
        attribute, corresponding to the relations between father/son words.

        @param l Line read from input to be processed
        
        @param phrase List of dictionaries to be completed
    """
    parts = l.strip().replace( " _", "" ).replace( "(", "" ).replace( ")", "" ).split( " " )
    rel = ""
    members = []
    for part in parts :
        if ":" not in part :
            rel = rel + "_" + part.replace("|","")
        else:
            members.append( part )
    # First char is _
    # Also remove ; and : from rel, since they have special meanings in format
    rel = rel[1:].replace( ";", "SEMICOLON").replace( ":", "COLON" )
    if len(members) >= 1 :
        if len(members) >= 2:    # binary (typical) dependency relation                 
            # This line below converts RASP's token IDs into token positions in
            # moses format. This is required because sometimes RASP skips words
            # and assigns e.g. 1 2 4 5, so dependency 2->4 should be converted
            # into 2->3 in new sentence 1 2 3 4.
            head = phrase[ int( get_tokens( members[0] )[1] ) ][ "index" ] 
            syn = rel + ":" + head 
            if len(members) == 3 :
                syn = syn + ";" + rel + ":" + get_tokens( members[1] )[1]
            son = get_tokens( members[-1] )[1]
            entry = phrase.get( int(son), None )        
        else:                    # simple property: passive, have_to, etc.    
            word_index = get_tokens( members[ 0 ] )[ 1 ]
            entry = phrase.get( int(word_index), None )
            syn = rel
        if entry and syn :
            if entry[ "syn" ] == "" :
                entry[ "syn" ] = syn
            else :
                entry[ "syn" ] = entry[ "syn" ] + ";" + syn
    else :        
        warn( "Unrecogized grammatical relation \"%s\"" % l.strip() )

###############################################################################

def transform_format(rasp):
    """
        Reads an input file and converts it into mwetoolkit corpus XML format,
        printing the XML file to stdout.
    
        @param rasp Is the input, file or piped.
    """
    global morphg_folder
    global work_path
    if morphg_folder :
        os.chdir( morphg_folder )
    n_line=0
    l_empty=2
    first_line=True    
    phrase = {}
    l=unicode(rasp.readline(),"utf-8")
    #pdb.set_trace()
    # THIS LOOP IS HORRIBLE. PLEASE REFACTOR ME, PLEEEEASE!!!! - CR 20140905    
    while l != "":        
        if l=="\n":
            l_empty+=1
            if l_empty == 1:
                sorted_phrase = map( lambda x: x[1], sorted( phrase.items() ) )
                write_entry(n_line,sorted_phrase)
                phrase = {}
                if n_line % 100 == 0 :
                    verbose( "Processing sentence number %d" % n_line )
                n_line+=1
                first_line=True
            l=unicode( rasp.readline(), "utf-8" )
            continue
        # too long sentences not parsed because -w word limit passed to parser
        elif l.startswith( "(X " ) :
            while l != "\n" :
                l = unicode( rasp.readline(), "utf-8" )
            continue
        if first_line:
            if l_empty>=1:
                l_empty=0
                process_line(l,phrase)
                #pdb.set_trace()
                first_line=False
                l=unicode( rasp.readline(), "utf-8" ) #ignore line
            else:
                l_empty=0
                first_line=True
        else:
            process_tree_branch(l,phrase)
        l=unicode( rasp.readline(), "utf-8" )
    if l_empty != 1 and len(phrase) != 0 : #save last entry
        write_entry(n_line,map( lambda x: x[1], sorted( phrase.items() ) )) 
    if morphg_folder :
        os.chdir( work_path )

###############################################################################
# MAIN SCRIPT

longopts = ["morphg=", "moses"]
arg = read_options( "m:x", longopts, treat_options, -1, usage_string )

if not generate_text :
    print( XML_HEADER % { "category": "corpus", "ns": "" } )

if len( arg ) == 0 :
    transform_format( sys.stdin )
else :
    for a in arg :
        try:
            input_file=open(a, 'r')
        except IOError as e:
            error( 'Error opening file for reading.' )
        transform_format( input_file )
        input_file.close()    
               
if not generate_text :
    print( XML_FOOTER % { "category": "corpus" } )
