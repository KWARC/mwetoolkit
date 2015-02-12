#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# indexlib.py is part of mwetoolkit
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
# ###############################################################################

"""
    index.py - Routines for index manipulation.
"""

# In release 0.5, we add the ability to use either the C indexer or the
# original (more well tested) Python indexer. We face the doubt of how to
# implement that:
#
# 1. Subclassing: we implement a class for interfacing with the C indexer
# as as subclass of the current one (or make both the current one and the
#  C one subclasses of a new generic/abstract Index class).
#
#  2. Lots of if/elses. (Not so many of them, actually.)
#
# Approach 1 would work fine for normal index generation (as done by index.py):
# index.py instantiates the right class, then creates the indices. However, for
# dynamic index building (attribute fusion), we have already instantiated 
# mrkrrhgrghgrgrh, rethink all of this.

from __future__ import division
from __future__ import print_function
# Incompatibility with array library
#from __future__ import unicode_literals
from __future__ import absolute_import

import sys
import os
import array
import xml.sax
import tempfile
import subprocess
import struct

from ..base.sentence import Sentence
from ..util import verbose, strip_xml, warn, error
from ..base.word import Word, WORD_ATTRIBUTES
from ..base.__common import ATTRIBUTE_SEPARATOR, WILDCARD, C_INDEXER_PROGRAM
from .. import filetype


NGRAM_LIMIT = 16

################################################################################

def copy_list(ls):
    return map(lambda x: x, ls)


################################################################################

def make_array(initializer=None):
    if initializer is None:
        return array.array('i')
    else:
        return array.array('i', initializer)


################################################################################

# Taken from counter.py
def load_array_from_file(an_array, a_filename):
    """
        Fills an existing array with the contents of a file.
    """
    MAX_MEM = 10000
    fd = open(a_filename)
    isMore = True
    while isMore:
        try:
            an_array.fromfile(fd, MAX_MEM)
        except EOFError:
            isMore = False  # Did not read MAX_MEM_ITEMS items? Not a problem...
    fd.close()


################################################################################

def save_array_to_file(array, path):
    """
        Dumps an array to a file.
    """
    file = open(path, "w")
    array.tofile(file)
    file.close()


################################################################################

def load_symbols_from_file(symbols, path):
    """
        Fills an existing symbol table with the contents of a file.
    """

    file = open(path, "rb")
    id = 0
    symbols.number_to_symbol = []
    symbols.symbol_to_number = {}
    for line in file:
        sym = line.rstrip('\n').decode("utf-8")
        symbols.symbol_to_number[sym] = id
        symbols.number_to_symbol.append(sym)
        id += 1

    file.close()


################################################################################

def save_symbols_to_file(symbols, path):
    """
        Dumps a symbol table to a file.
    """
    file = open(path, "wb")
    for sym in symbols.number_to_symbol:
        file.write(sym.encode("utf-8") + '\n')
    file.close()


################################################################################

def read_attribute_from_index(attr, path):
    """
        Returns an iterator that yields the value of the attribute `attr`
        for every word in an index's corpus array. This allows one to recover
        the corpus from the index, and is used for attribute fusion.
    """

    corpus_file = open(path + "." + attr + ".corpus", "rb")
    symbols = SymbolTable()
    load_symbols_from_file(symbols, path + "." + attr + ".symbols")

    while True:
        ## Assuming 32-bit int! (right in x86 and x86-64)
        wordcode = corpus_file.read(4)
        if wordcode == "":
            return
        wordnum = struct.unpack('i', wordcode)[0]
        yield symbols.number_to_symbol[wordnum]

    corpus_file.close()


################################################################################

def compare_ngrams(ngram1, pos1, ngram2, pos2, ngram1_exhausted=-1,
                   ngram2_exhausted=1, limit=NGRAM_LIMIT):
    """
        Compares the ngram at position `pos1` in the word list `ngram1` with
        the ngram at position `pos2` in the word list `ngram2`. Returns an
        integer less than, equal or greater than 0 if the first ngram is less
        than, equal or greater than the second, respectively. At most the first 
        `limit` words will be compared.

        @param ngram1 A list or array of numbers, each representing a word.
        Likewise for `ngram2`.

        @param pos1 Position where the first ngram begins in `ngram1`.
        Likewise for `pos2`.

        @param ngram1_exhausted Value returned if the first ngram ends before
        the second and the ngrams have been equal so far. The default is `-1`,
        which means that an ngram `[1, 2]` will be considered lesser than
        `[1, 2, 3]`. Likewise for `ngram2_exhausted`.

        @param limit Compare at most `limit` words. Defaults to `NGRAM_LIMIT`.
    """

    max1 = len(ngram1)
    max2 = len(ngram2)
    i = 0
    while pos1 < max1 and pos2 < max2 and ngram1[pos1] == ngram2[pos2] and \
                    i < limit:
        pos1 += 1
        pos2 += 1
        i += 1

    if pos1 >= max1 and pos2 >= max2:
        return 0
    elif pos1 >= max1:
        return ngram1_exhausted
    elif pos2 >= max2:
        return ngram2_exhausted
    else:
        return int(ngram1[pos1] - ngram2[pos2])


################################################################################

def fuse_suffix_arrays(array1, array2):
    """
        Returns a new `SuffixArray` fusing the `corpus` data of each input array
        This is used to generate indices for combined attributes (eg lemma+pos)
    """
    fused_array = SuffixArray()
    for i in xrange(len(array1.corpus)):
        sym1 = array1.symbols.number_to_symbol[array1.corpus[i]]
        sym2 = array2.symbols.number_to_symbol[array2.corpus[i]]
        fused_array.append_word(sym1 + ATTRIBUTE_SEPARATOR + sym2)

    return fused_array


################################################################################
################################################################################

class SymbolTable(object):
    """
        Handles the conversion between word strings and numbers.
    """

    def __init__(self):
        self.symbol_to_number = {'': 0}
        self.number_to_symbol = ['']
        self.last_number = 0

    def intern(self, symbol):
        """
            Adds the string `symbol` to the symbol table.
        """
        if not self.symbol_to_number.has_key(symbol):
            self.last_number += 1
            self.symbol_to_number[symbol] = self.last_number
            #self.number_to_symbol[self.last_number] = symbol
            # Risky and not intention-expressing            
            self.number_to_symbol.append(symbol)

        return self.symbol_to_number[symbol]


################################################################################
################################################################################

class SuffixArray(object):
    """
        Class containing the corpus and suffix arrays and the symbol table
        for one attribute of a corpus.
    """

################################################################################

    def __init__(self):
        self.corpus = make_array()  # List of word numbers
        self.suffix = make_array()  # List of word positions
        self.symbols = SymbolTable()  # word<->number conversion table

################################################################################

    def set_basepath(self, basepath):
        """
            Sets the base path for the suffix array files.
        """
        self.basepath = basepath
        self.corpus_path = basepath + ".corpus"
        self.suffix_path = basepath + ".suffix"
        self.symbols_path = basepath + ".symbols"

################################################################################

    def load(self):
        """
            Loads the suffix array from the files at `self.basepath`.
        """
        load_array_from_file(self.corpus, self.corpus_path)
        load_array_from_file(self.suffix, self.suffix_path)
        load_symbols_from_file(self.symbols, self.symbols_path)

################################################################################

    def save(self):
        """
            Saves the suffix array to the files at `self.basepath`.
        """
        save_array_to_file(self.corpus, self.corpus_path)
        save_array_to_file(self.suffix, self.suffix_path)
        save_symbols_to_file(self.symbols, self.symbols_path)

################################################################################

    def append_word(self, word):
        """
            Adds a new word to the end of the corpus array, putting it in the
            symbol table if necessary.
        """
        self.corpus.append(self.symbols.intern(word))

################################################################################

    # For debugging.
    def append_string(self, sentence):
        for w in sentence.split():
            self.append_word(w)

################################################################################

    def build_suffix_array(self):
        """
            Builds the sorted suffix array from the corpus array.
        """
        tmpseq = range(0, len(self.corpus))
        tmpseq.sort(cmp=(lambda a, b: compare_ngrams(self.corpus, a,
                                                     self.corpus, b)))
        self.suffix = make_array(tmpseq)

################################################################################

    def find_ngram_range(self, ngram, min=0, max=None):
        """
            Returns a tuple `(first, last)` of matching ngram positions in
            the suffix array, or `None` if there is no match.
        """
        # TODO: We will need a more "incremental" approach for searching for
        # patterns that use multple word attributes. (Can't be done!)

        if max is None:
            max = len(self.suffix) - 1

        first = self.binary_search_ngram(ngram, min, max, array.array.__ge__)
        last = self.binary_search_ngram(ngram, min, max, array.array.__gt__)

        if first is None:
            return None
        if last is None:
            last = max
        else:
            last -= 1

        if first <= last:
            return (first, last)
        else:
            return None

################################################################################

    def binary_search_ngram(self, ngram, first, last, cmp):
        """
            Find the least suffix that satisfies `suffix <cmp> ngram`, or
            `None` if there is none.
        """

        # 'max' must be one more than 'last', for the case no suffix
        # satisfies the comparison.
        maxi = last + 1
        mini = first
        ngram_array = make_array(ngram)
        length = len(ngram)
        mid = -1
        while mini < maxi:
            mid = (mini + maxi) // 2
            midsuf = self.suffix[mid]
            #if cmp(compare_ngrams(self.corpus, self.suffix[mid], ngram, 0, \
            #                      ngram2_exhausted=0), 0):
            if cmp(self.corpus[midsuf: midsuf + length], ngram_array):
                # If 'mid' satisfies, then what we want *is* mid or *is before*
                # mid            
                maxi = mid
            else:
                # If 'mid' does not satisfy, what we want *must be after* mid.            
                mid += 1
                mini = mid
        if mid > last:
            return None
        else:
            return mid

################################################################################

    # For debugging.
    def dump_suffixes(self, limit=10, start=0, max=None):
        """
            Prints the suffix array to standard output (for debugging).
        """
        if max is None:
            max = len(self.suffix)

        #for pos in self.suffix:
        for suf in xrange(start, max):
            pos = self.suffix[suf]
            print("%4d:" % pos, end="")
            for i in range(pos, pos + limit):
                if i < len(self.corpus):
                    sym = self.symbols.number_to_symbol[self.corpus[i]]
                    if sym == "":
                        sym = "#"
                    print(sym, end="")
                else:
                    print("*", end="")

            print("")


################################################################################
################################################################################

class CSuffixArray(SuffixArray):
    """
        This class implements an interface to the C indexer. Appended words
        go to a temporary text file, and build_suffix_array invoked the C
        indexer upon that file. After array construction, one must call
        array.load() to load the array into 'python-space'.
    """

################################################################################

    def __init__(self):
        SuffixArray.__init__(self)
        self.basepath = None

        (fd, path) = tempfile.mkstemp()
        self.wordlist_file = os.fdopen(fd, 'w+')
        self.wordlist_path = path

################################################################################

    def append_word(self, word):
        self.wordlist_file.write(word.encode('utf-8') + '\n')

################################################################################

    def build_suffix_array(self):
        if self.basepath is None:
            error("Base path not specified for suffix array to be built " + \
                  "with C indexer")
            sys.exit(2)

        self.wordlist_file.seek(0)
        verbose("Using C indexer to build suffix array %s" % self.basepath)
        subprocess.call([C_INDEXER_PROGRAM, self.basepath],
                        stdin=self.wordlist_file)

################################################################################

    def save(self):
        self.wordlist_file.close()
        os.remove(self.wordlist_path)


################################################################################
################################################################################

class Index(object):
    """
        This class holds the `SuffixArray`s for all attributes of a corpus,
        plus metadata which is common for all attributes.
    """

    make_suffix_array = None
    c_indexer_program = None

################################################################################

    def use_c_indexer(wants_to_use):
        """
            Class method that sets the appropriate indexer to use (C or Python).

            @param `wants_to_use` Whether we want to use the C indexer.
            Possible values are True, False and None (we don't care about it).
            If value is None, and use_c_indexer has never been called before,
            it defaults to True; otherwise it does not touch the current state.

        """

        if wants_to_use is None and Index.make_suffix_array is None:
            wants_to_use = True

        can_use = True
        # Find whether the C indexer exists.
        if wants_to_use:
            if os.path.isfile(C_INDEXER_PROGRAM):
                Index.c_indexer_program = C_INDEXER_PROGRAM
            elif os.path.isfile(C_INDEXER_PROGRAM + ".exe"):
                Index.c_indexer_program = C_INDEXER_PROGRAM + ".exe"
            else:
                can_use = False

        if can_use and wants_to_use:
            Index.make_suffix_array = CSuffixArray
        else:
            if wants_to_use:
                warn(
                    "C indexer not found; using (slower) Python indexer instead.")
            Index.make_suffix_array = SuffixArray

    use_c_indexer = staticmethod(use_c_indexer)

################################################################################

    def __init__(self, basepath=None, used_word_attributes=None,
                 use_c_indexer=None):
        self.arrays = {}
        self.metadata = {"corpus_size": 0}

        Index.use_c_indexer(use_c_indexer)

        if used_word_attributes is not None:
            self.used_word_attributes = used_word_attributes
        else:
            self.used_word_attributes = copy_list(WORD_ATTRIBUTES)

        if basepath is not None:
            self.set_basepath(basepath)

################################################################################

    def fresh_arrays(self):
        """
            Creates empty suffix arrays for each used attribute in the index.
        """
        for attr in self.used_word_attributes:
            self.arrays[attr] = Index.make_suffix_array()

################################################################################

    def set_basepath(self, path):
        """
            Sets the base path for the index files.
        """
        self.basepath = path
        self.metadata_path = path + ".info"

################################################################################

    def array_file_exists(self, attr):
        return os.path.isfile(self.basepath + "." + attr + ".corpus")

################################################################################

    def load(self, attribute):
        """
            Load an attribute from the corresponding index files.
            If the attribute is of the form `a1+a2` and the corresponding
            file does not exist, creates a new suffix array fusing the 
            arrays for attributes `a1` and `a2`.
        """
        #pdb.set_trace()
        if self.arrays.has_key(attribute):
            return self.arrays[attribute]

        if not self.array_file_exists(attribute):
            if '+' in attribute:
                self.make_fused_array(attribute.split('+'))
            else:
                warn("Cannot load attribute %s; index files not present."
                     % attribute)
                return None

        verbose("Loading corpus files for attribute \"%s\"." % attribute)
        array = SuffixArray()
        path = self.basepath + "." + attribute
        array.set_basepath(path)
        array.load()

        self.arrays[attribute] = array
        return array

################################################################################

    def make_fused_array(self, attrs):
        """
            Make an array combining the attributes `attrs`. This array must be
            loaded after creation.
        """

        verbose("Making fused array for " + '+'.join(attrs) + "...")
        generators = [read_attribute_from_index(attr, self.basepath) \
                      for attr in attrs]

        sufarray = Index.make_suffix_array()
        sufarray.set_basepath(self.basepath + "." + '+'.join(attrs))
        while True:
            try:
                g = ""
                next_words = [g.next() for g in generators]
                if g == "":
                    sufarray.append_word("")
                else:
                    sufarray.append_word(ATTRIBUTE_SEPARATOR.join(next_words))

            except StopIteration:
                break

        sufarray.build_suffix_array()
        sufarray.save()

        # Is this any good? (May be with the old indexer; must test)
        sufarray = None
        print("objects collected by gc.collect()", file=sys.stderr)

################################################################################

    def save(self, attribute):
        """
            Saves the suffix array for `attribute` to the corresponding files.
        """
        array = self.arrays[attribute]
        array.set_basepath(self.basepath + "." + attribute)
        array.save()

################################################################################

    def load_metadata(self):
        """
            Loads the index metadata from the corresponding file.
        """
        metafile = open(self.metadata_path)
        for line in metafile:
            key, type, value = line.rstrip('\n').split(" ", 2)
            if type == "int":
                value = int(value)
            self.metadata[key] = value

        metafile.close()

################################################################################

    def save_metadata(self):
        """
            Saves the index metadata to the corresponding file.
        """
        metafile = open(self.metadata_path, "w")
        for key, value in self.metadata.items():
            if isinstance(value, int):
                type = "int"
            else:
                type = "string"

            metafile.write("%s %s %s\n" % (key, type, value))

        metafile.close()

################################################################################

    # Load/save main (non-composite) attributes and metadata
    def load_main(self):
        self.load_metadata()
        present_attributes = []
        for attr in self.used_word_attributes:
            present = self.load(attr)
            if present:
                present_attributes.append(attr)
        self.used_word_attributes = present_attributes

    ################################################################################

    def save_main(self):
        self.save_metadata()
        for attr in self.used_word_attributes:
            self.save(attr)

################################################################################


    def append_end_sentence(self, nb_words):
        for attr in self.used_word_attributes:
            # '' (symbol 0)  means end-of-sentence
            self.arrays[attr].append_word('')
        self.metadata["corpus_size"] += nb_words
    
################################################################################

    def append_sentence(self, sentence):
        """
            Adds a `Sentence` (extracted from a XML file) to the index.
        """
        for attr in self.used_word_attributes:
            for word in sentence:
                value = getattr(word, attr)
                self.arrays[attr].append_word(value)
                # '' (symbol 0)  means end-of-sentence
        self.append_end_sentence(len(sentence))

################################################################################

    def build_suffix_arrays(self):
        """
            Build suffix arrays for all attributes in the index.
        """
        for attr in self.arrays.keys():
            verbose("Building suffix array for %s..." % attr)
            ## REFACTOR FIXME
            self.arrays[attr].set_basepath(self.basepath + "." + attr)
            self.arrays[attr].build_suffix_array()

################################################################################

    def iterate_sentences(self):
        """
            Returns an iterator over all sentences in the corpus.
        """

        id = 1
        guide = self.used_word_attributes[0]  # guide?
        length = len(self.arrays[guide].corpus)
        words = []
        for i in range(0, length):
            if self.arrays[guide].corpus[i] == 0:
                # We have already a whole sentence.
                sentence = Sentence(words, id)
                id += 1
                words = []
                yield sentence

            else:
                args_dict = {}
                args = []
                for poss_attr in WORD_ATTRIBUTES:
                    args_dict[poss_attr] = WILDCARD
                for attr in self.used_word_attributes:
                    number = self.arrays[attr].corpus[i]
                    symbol = self.arrays[attr].symbols.number_to_symbol[number]
                    args_dict[attr] = symbol
                for poss_attr in WORD_ATTRIBUTES:
                    args.append(args_dict[poss_attr])
                args.append([])
                words.append(Word(*args))

################################################################################

    # For debugging.
    def print_sentences(self):
        for sentence in self.iterate_sentences():
            for word in sentence:
                print(word.surface, end="")
            print("")


################################################################################
################################################################################

def populate_index(index, corpus_fileobjs, filetype_hint=None):
    """Generates an `Index` from a corpus file."""
    handler = IndexPopulatorHandler(index)
    filetype.parse(corpus_fileobjs, handler, filetype_hint)
    handler.flush()

################################################################################

class IndexPopulatorHandler(filetype.InputHandler):
    def __init__(self, index):
        self.index = index
        self.index.fresh_arrays()

    def handle_sentence(self, sentence, info={}):
        self.index.append_sentence(sentence)

    def finish(self):
        self.index.build_suffix_arrays()
        self.index.save_main()


################################################################################
#t = fuse_suffix_arrays(h.arrays["surface"], h.arrays["pos"])

# For debugging.
def standalone_main(argv):
    if len(argv) != 3:
        print("Usage: python indexlib.py <basepath> <corpus>", file=sys.stderr)
        return 1

    basepath = argv[1]
    corpus = argv[2]

    index = _index_from_corpus(corpus, basepath)
    index.save_main()
    print("Done.", file=sys.stderr)


def _index_from_corpus(corpus, basepath=None, attrs=None):
    index = Index(basepath, attrs)
    populate_index(index, [corpus])
    return index

################################################################################

if __name__ == "__main__":
    standalone_main(sys.argv)
