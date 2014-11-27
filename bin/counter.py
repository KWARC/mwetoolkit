#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# counter.py is part of mwetoolkit
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
    This script calculates individual word frequencies for a given candidate 
    list in a given corpus. The corpus may be a valid corpus word index 
    generated by the `index.py` script (-i option) or it may be the World Wide 
    Web through Google's Web Search interface (-w or -u options). Yahoo's Web 
    Search interface (-y option) is not supported anymore as they shut their 
    free search API down in April 2011, just after merging with Microsoft ;-)

    For more information, call the script with no parameter and read the
    usage instructions.
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import re
import subprocess

from libs.genericXMLHandler import GenericXMLHandler
from libs.base.frequency import Frequency
from libs.base.googleFreq import GoogleFreq
from libs.base.googleFreqUniv import GoogleFreqUniv
from libs.base.corpus_size import CorpusSize
from libs.util import read_options, treat_options_simplest, \
        verbose, error, warn
from libs.indexlib import Index, ATTRIBUTE_SEPARATOR
from libs.base.__common import DEFAULT_LANG
from libs import filetype

################################################################################
# GLOBALS    

usage_string = """Usage: 
    
python {program} [-w | -u <id> | -T <dir> | -i <index-corpus>] OPTIONS <candidates>

-i <index-corpus> OR --index <index-corpus>
    Calculate frequencies of individual words in given corpus.
    The corpus must be given as the path to the `.info` file
    in a BinaryIndex instance.

-y OR --yahoo
    Search for frequencies in the Web using Yahoo Web Search as approximator for
    Web document frequencies.
    ** THIS OPTION IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE SEARCH API **    
    
-w OR --google
    Search for frequencies in the Web using Google Web Search as approximator 
    for Web document frequencies.
    
-u <id> OR --univ <id>
    Same as -w (Google frequencies) but uses Google University Research program
    URL and ID. The ID must be registered with a static IP address at:
    http://research.google.com/university/search/

-T <dir> OR --web1t <dir>
    Use Google's Web 1T 5-gram corpus. <dir> is the a directory containing the
    union of the contents of the data/ directories of each corpus CD as
    distributed by Google.

The <candidates> input file must be in one of the filetype
formats accepted by the `--candidates-from` switch.

You must choose exactly one of -u, -w or -i
(more than one is not allowed at the same time).

    
OPTIONS may be:

--candidates-from <candidates-filetype>
    Force reading candidates from given filetype extension.
    (By default, file type is automatically detected):
    {descriptions.input[candidates]}

--corpus-from <corpus-filetype>
    Only works if the `--corpus` switch has been given as well.
    Force reading corpus from given filetype extension.
    XXX Currently, only "BinaryIndex" is accepted.

--to <corpus-filetype>
    Output candidates in given filetype format
    (by default, outputs in "XML" file format):
    {descriptions.output[candidates]}

-g OR --ignore-pos
     Ignores Part-Of-Speech when counting candidate occurences. This means, for
     example, that "like" as a preposition and "like" as a verb will be counted 
     as the same entity. If you are using -w or -u, this option will be ignored. 
     Default false.

-s OR --surface
    Counts surface forms instead of lemmas. Default false.

-x OR --text
    Instead of traditional candidates in XML, takes as input a textual list with 
    one query per line. The output will have the query followed by the number of 
    web occurrences. MUST be used with -u or -w option.
   
-a OR --vars
    Instead of counting the candidate, counts the variances in the <vars> 
    element. If you also want to count the candidate lemma, you should call the
    counter twice, first without this option then with this option.

-l <lang> OR --lang <lang>
    Two-letter language code of the language of the candidates. This is only 
    used for the web-as-corpus counters -w and -u. The language codes depend
    on the search engine, please take a look at the Google documentation:    
    http://code.google.com/apis/customsearch/docs/ref_languages.html    
    ** YAHOO IS DEPRECATED AS THEY SHUT DOWN THEIR FREE SEARCH API **    

-J OR --no-joint
   Do not count joint ngram frequencies; count only individual word frequencies.

-B OR --bigrams
   Count bigrams frequencies in each ngram.

-o OR --old
    Use the old (slower) Python indexer, even when the C indexer is available.
    
{common_options}
"""

index = None  # Index()
suffix_array = None  # SuffixArray()

get_freq_function = None
freq_name = "?"
web_freq = None
the_corpus_size = -1
low_limit = -1
up_limit = -1
text_input = False
count_vars = False
count_joint_frequency = True
count_bigrams = False
language = DEFAULT_LANG

filetype_corpus_ext = "BinaryIndex"
filetype_candidates_ext = None
output_filetype_ext = "XML"


################################################################################

class CounterPrinter(filetype.AutomaticPrinterHandler):
    r"""Adds info and outputs the result."""
    def before_file(self, fileobj, info={}):
        super(CounterPrinter, self).before_file(fileobj, info)
        self.entity_counter = 0

    def handle_meta(self, meta, info={}):
        """Adds a `CorpusSize` meta-information to the header and prints the 
        header. The corpus size is important to allow the calculation of 
        statistical Association Measures by the `feat_association.py` script.
        
        @param meta The `Meta` header that is being read from the XML file.        
        """
        global freq_name, the_corpus_size
        meta.add_corpus_size(CorpusSize(name=freq_name, value=the_corpus_size))
        self.delegate.handle_meta(meta, info)

    def handle_candidate(self, candidate, info={}):
        """For each candidate, searches for the individual word frequencies of the
        base ngram. The corresponding function, for a corpus index or for yahoo,
        will be called, depending on the -i or -w/-u options. The frequencies 
        are added as a child element of the word and then the candidate is 
        printed.
        
        @param candidate The `Candidate` that is being read from the XML file.
        """
        global low_limit, up_limit
        global count_vars
        if self.entity_counter % 100 == 0:
            verbose("Processing ngram number %(n)d" % {"n": self.entity_counter})
        if ( self.entity_counter >= low_limit or low_limit < 0 ) and \
                ( self.entity_counter <= up_limit or up_limit < 0 ):
            if count_vars:
                for var in candidate.vars:
                    append_counters(var)
            else:
                append_counters(candidate)
        self.delegate.handle_candidate(candidate, info)
        self.entity_counter += 1


################################################################################

def append_counters(ngram):
    """
        Calls the frequency function for each word of the n-gram as well as for
        the n-gram as a whole. The result is appended to the frequency list
        of the `Ngram` given as input.

        If the option "--bigrams" is active, calls the frequency function for
        each bigram in the 'Ngram'.
        
        @param ngram The `Ngram` that is being counted.
    """
    global get_freq_function, freq_name, count_joint_frequency, count_bigrams
    ( c_surfaces, c_lemmas, c_pos ) = ( [], [], [] )
    for w in ngram:
        c_surfaces.append(w.surface)
        c_lemmas.append(w.lemma)
        c_pos.append(w.pos)
        freq_value = get_freq_function([w.surface],
                                       [w.lemma],
                                       [w.pos])
        w.add_frequency(Frequency(freq_name, freq_value))
    # Global frequency
    if count_joint_frequency:
        freq_value = get_freq_function(c_surfaces, c_lemmas, c_pos)
        ngram.add_frequency(Frequency(freq_name, freq_value))
    # Bigrams frequency
    if count_bigrams:
        i = 0
        while i < len(ngram) - 1:
            freq_value = get_freq_function(c_surfaces[i:i + 2],
                                           c_lemmas[i:i + 2], c_pos[i:i + 2])
            i = i + 1
            ngram.add_bigram(Frequency(freq_name, freq_value))


################################################################################

def get_freq_index(surfaces, lemmas, pos):
    """
        Gets the frequency (number of occurrences) of a token (word) in the
        index file. Calling this function assumes that you called the script
        with the -i option and with a valid index file.
        
        @param surfaces A string corresponding to the surface form of a word.

        @param lemmas A string corresponding to the lemma of a word.
        
        @param pos A string corresponding to the Part Of Speech of a word.
    """
    global build_entry, suffix_array
    ngram_ids = []
    #pdb.set_trace()
    for i in range(len(surfaces)):
        word = build_entry(surfaces[i], lemmas[i], pos[i])
        wordid = suffix_array.symbols.symbol_to_number.get(word, None)
        if wordid:
            ngram_ids.append(wordid)
        else:
            return 0

    #i_last = binary_search(ng_ids, ngrams_file,corpus_file,lambda a, b:a > b)
    #i_first = binary_search(ng_ids, ngrams_file,corpus_file,lambda a, b:a >= b)
    indexrange = suffix_array.find_ngram_range(ngram_ids)
    if indexrange is not None:
        first, last = indexrange
        return last - first + 1
    else:
        return 0


################################################################################

def get_freq_web(surfaces, lemmas, pos):
    """
        Gets the frequency (number of occurrences) of a token (word) in the
        Web through Yahoo's or Google's index. Calling this function assumes 
        that you called the script with the -u or -w option.
        
        @param surfaces A list corresponding to the surface forms of a word.

        @param lemmas A list corresponding to the lemmas of a word.
        
        @param pos A list corresponding to the Part Of Speeches of a word. This
        parameter is ignored since Web search engines dos no provide linguistic 
        information.
    """
    # POS is ignored
    global web_freq, build_entry, language
    search_term = ""
    for i in range(len(surfaces)):
        search_term = search_term + build_entry(surfaces[i], lemmas[i],
                                                pos[i]) + " "
    return web_freq.search_frequency(search_term.strip(), language)


################################################################################

def read_file(path):
    fh = open(path)
    txt = fh.read()
    fh.close()
    return txt


################################################################################

def get_freq_web1t(surfaces, lemmas, pos):
    """
        Gets the frequency (number of occurrences) of an ngram in Google's
        Web 1T 5-gram Corpus.
    """

    global build_entry, web1t_data_path

    length = len(surfaces)

    if length > 5:
        warn("Cannot count the frequency of an n-gram, n>5!")
        return 0

    search_term = ' '.join(map(build_entry, surfaces, lemmas, pos))

    # Find the file in which to look for the ngram.
    if length == 1:
        filename = web1t_data_path + "/1gms/vocab.gz"
    else:
        indexfile = web1t_data_path + "/%dgms/%dgm.idx" % (length, length)
        filenames = [x.split("\t") for x in read_file(indexfile).split("\n")]
        filename = None
        for (name, first) in filenames:
            # Assumes byte-value-based ordering!
            if first > search_term:
                break
            else:
                filename = name

        if filename is None:
            return 0
        filename = "%s/%dgms/%s" % (web1t_data_path, length, filename)

    verbose("WEB1T: Opening %s, looking for %s" % (filename, search_term))

    # This has been absurdly slow in Python.
    #file = gzip.open(filename, "rb")
    #
    #search_term += "\t"
    #freq = 0
    #
    #for line in file:
    #    if line.startswith(search_term):
    #        freq = int(line.split("\t")[1])
    #        break
    #
    #print >>sys.stderr, "buenito: %d" % freq
    #
    #file.close()

    file = subprocess.Popen(
        ["zgrep", "--", "^" + re.escape(search_term) + "\t", filename],
        stdout=subprocess.PIPE).stdout
    line = file.read()
    file.close()
    if line:
        freq = int(line.split("\t")[1])
    else:
        freq = 0
    verbose("freq =" + str(freq))
    return freq


################################################################################

def open_index(prefix):
    """
    Open the index files (valid index created by the `index.py` script). 
    @param prefix The string name of the index file.
    """
    global freq_name, the_corpus_size
    global index, suffix_array
    assert prefix.endswith(".info")
    prefix = prefix[:-len(".info")]
    try:
        verbose("Loading index files... this may take some time.")
        index = Index(prefix)
        index.load_metadata()
        freq_name = re.sub(".*/", "", prefix)
        #pdb.set_trace()
        the_corpus_size = index.metadata["corpus_size"]
    except IOError:
        error("Error opening the index.\nTry again with another index filename")
    except KeyError:
        error("Error opening the index.\nTry again with another index filename")

################################################################################

def treat_text( line ):
    """
        Treats a text file by getting the frequency of the lines. Useful for 
        quick web queries from a text file containing one query per line.
        
        @param line Lines (queries) being read from file or stdin.
    """
    global web_freq
    query = line.strip()
    count = str(web_freq.search_frequency(query))
    print(query + "\t" + count)


################################################################################

def treat_options(opts, arg, n_arg, usage_string):
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global cache_file, get_freq_function, build_entry, web_freq
    global the_corpus_size, freq_name
    global low_limit, up_limit
    global text_input, count_vars
    global language
    global suffix_array
    global count_joint_frequency
    global count_bigrams
    global web1t_data_path
    global filetype_corpus_ext
    global filetype_candidates_ext
    global output_filetype_ext

    surface_flag = False
    ignorepos_flag = False
    mode = []

    treat_options_simplest(opts, arg, n_arg, usage_string)

    for ( o, a ) in opts:
        if o in ( "-i", "--index" ):
            open_index(a)
            get_freq_function = get_freq_index
            mode.append("index")
        elif o in ( "-y", "--yahoo" ):
            error("THIS OPTION IS DEPRECATED AS YAHOO SHUT DOWN THEIR FREE "
                  "SEARCH API")
            #web_freq = YahooFreq()          
            #freq_name = "yahoo"
            #ignorepos_flag = True 
            #the_corpus_size = web_freq.corpus_size()         
            #get_freq_function = get_freq_web
            #mode.append( "yahoo" )   
        elif o in ( "-w", "--google" ):
            web_freq = GoogleFreq()
            freq_name = "google"
            ignorepos_flag = True
            the_corpus_size = web_freq.corpus_size()
            get_freq_function = get_freq_web
            mode.append("google")
        elif o in ( "-u", "--univ" ):
            web_freq = GoogleFreqUniv(a)
            freq_name = "google"
            ignorepos_flag = True
            the_corpus_size = web_freq.corpus_size()
            get_freq_function = get_freq_web
            mode.append("google")
        elif o in ("-T", "--web1t"):
            ignorepos_flag = True
            freq_name = "web1t"
            web1t_data_path = a
            the_corpus_size = int(read_file(web1t_data_path + "/1gms/total"))
            get_freq_function = get_freq_web1t
            mode.append("web1t")
        elif o in ("-s", "--surface" ):
            surface_flag = True
        elif o in ("-g", "--ignore-pos"):
            ignorepos_flag = True
        elif o in ("-f", "--from", "-t", "--to" ):
            try:
                limit = int(a)
                if limit < 0:
                    raise ValueError, "Argument of " + o + " must be positive"
                if o in ( "-f", "--from" ):
                    if up_limit == -1 or up_limit >= limit:
                        low_limit = limit
                    else:
                        raise ValueError, "Argument of -f >= argument of -t"
                else:
                    if low_limit == -1 or low_limit <= limit:
                        up_limit = limit
                    else:
                        raise ValueError, "Argument of -t <= argument of -t"
            except ValueError as message:
                error( str(message) + "\nArgument of " + o + " must be integer")
        elif o in ("-x", "--text" ):
            text_input = True
        elif o in ("-a", "--vars" ):
            count_vars = True
        elif o in ("-l", "--lang" ):
            language = a
        elif o in ("-J", "--no-joint"):
            count_joint_frequency = False
        elif o in ("-B", "--bigrams"):
            count_bigrams = True
        elif o in ("-o", "--old"):
            Index.use_c_indexer(False)
        elif o in ("--corpus-from"):
            filetype_corpus_ext = a
        elif o in ("--candidates-from"):
            filetype_candidates_ext = a
        elif o in ("-o", "--output"):
            output_filetype_ext = a
        else:
            raise Exception("Bad arg: " + o)

    if mode == ["index"]:
        if surface_flag and ignorepos_flag:
            build_entry = lambda surface, lemma, pos: surface
            suffix_array = index.load("surface")
        elif surface_flag:
            build_entry = lambda surface, lemma, pos: surface +\
                                                      ATTRIBUTE_SEPARATOR + pos
            suffix_array = index.load("surface+pos")
        elif ignorepos_flag:
            build_entry = lambda surface, lemma, pos: lemma
            suffix_array = index.load("lemma")
        else:
            build_entry = lambda surface, lemma, pos: lemma +\
                                                      ATTRIBUTE_SEPARATOR + pos
            suffix_array = index.load("lemma+pos")

    else:  # Web search, entries are single surface or lemma forms
        if surface_flag:
            build_entry = lambda surface, lemma, pos: surface
        else:
            build_entry = lambda surface, lemma, pos: lemma

    if len(mode) != 1:
        error("Exactly one option -u, -w or -i, must be provided")
    elif text_input and web_freq is None:
        error("-x option MUST be used with either -u or -w")


################################################################################
# MAIN SCRIPT

longopts = ["candidates-from=", "corpus-from=", "to=",
            "yahoo", "google", "index=", "ignore-pos", "surface", "old",
            "from=", "to=", "text", "vars", "lang=", "no-joint", "bigrams",
            "univ=", "web1t="]
args = read_options("ywi:gsof:t:xal:Jbu:T:", longopts,
        treat_options, -1, usage_string)

try:
    verbose("Counting ngrams in candidates file")
    printer = CounterPrinter(filetype_candidates_ext)
    filetype.parse(args, printer, output_filetype_ext)
finally:
    if web_freq:
        web_freq.flush_cache()  # VERY IMPORTANT!
