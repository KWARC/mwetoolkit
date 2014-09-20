import sys

from libs.indexlib import Index
from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.feature import Feature
from xmlhandler.classes.meta import Meta
from xmlhandler.classes.meta_feat import MetaFeat
from xmlhandler.classes.corpus_size import CorpusSize
from xmlhandler.classes.candidate import Candidate
from bin.libs.base.ngram import Ngram
from xmlhandler.classes.word import Word
from util import read_options, treat_options_simplest, verbose, interpret_ngram


usage_string = """Usage:

python %(program)s OPTIONS <index>

OPTIONS may be:

-n <min>:<max> OR --ngram <min>:<max>
    The length of ngrams to extract. For instance, "-n 3:5" extracts ngrams 
    that have at least 3 words and at most 5 words. If you define only <min> or
    only <max>, the default is to consider that both have the same value, i.e. 
    if you call the program with the option "-n 3", you will extract only 
    trigrams while if you call it with the options "-n 3:5" you will extract 
    3-grams, 4-grams and 5-grams. Default "2:8".

-s OR --surface
    Counts surface forms instead of lemmas. Default false.

-S OR --source
    Output a <source> tag with the IDs of the sentences where each ngram occurs.

-l <size> OR --limit <size>
    Extract candidates from the first <size> words in the corpus only. The full
    corpus is still used to calculate frequencies.

-G <glue> OR --glue <glue>
    Use <glue> as the glue measure. Currently only 'scp' is supported.

-f <freq> OR --freq <freq>
    Output only candidates with a frequency of at least <freq>. Default 2.

-v OR --verbose
    Print messages that explain what is happening.

    <index> is the base name for the index files, as created by
"index.py -i <index>".
"""

def print_args(*args):
    print args

def extract(index, array_name, gluefun, min_ngram=2, max_ngram=8, corpus_length_limit=None, dumpfun=print_args):
    """
        Extract candidates from the corpus, read from an index, using the
        LocalMaxs algorithm.

        @param index The `Index` from which to read the corpus

        @param array_name Attribute to use (lemma, surface) in candidate
        extraction.

        @param gluefun The glue function.

        @param min_ngram Minimum ngram size of a candidate to extract.
        Defaults to 2.

        @param max_ngram Maximum ngram size of a candidate to extract.
        Defaults to 8.

        @corpus_length_limit Limit the search for candidates to the first N
        words in the corpus. The full corpus is still used to compute
        word frequencies.

        @dumpfun Function to be called on found candidates. Usually a function
        that will store the candidates in some data structure, or print them
        to a file.
    """

    sufarray = index.arrays[array_name]
    sentence_id = 0
    pos = 0
    corpus_length = corpus_length_limit or len(sufarray.corpus)
    corpus_size = index.metadata['corpus_size']  # corpus_size does not count sentence separators.

    while pos < corpus_length:
        if sentence_id%10 == 0:
            print >>sys.stderr, "Processing sentence %d" % sentence_id

        sentence_length = 0
        while sufarray.corpus[pos + sentence_length] != 0:
            sentence_length += 1

        gluevals = {}
        positions = {}
        absolute_positions = {}
        select = {}

        for ngram_size in range(1, max_ngram+2):  # ngram_size in [1 .. max_ngram+1]
            for i in range(sentence_length - ngram_size + 1):
                words_pos = range(pos+i, pos+i+ ngram_size)
                key = tuple([sufarray.corpus[j] for j in words_pos])
                glue = gluefun(gluevals, sufarray, corpus_size, key)
                gluevals[key] = glue
                select[key] = True
                positions[key] = range(i, i+ngram_size)
                absolute_positions[key] = range(i+pos, i+pos+ngram_size)

                if ngram_size >= 2:
                    for subkey in [key[0:-1], key[1:]]:
                        if glue < gluevals[subkey]:
                            select[key] = False
                        elif glue > gluevals[subkey]:
                            select[subkey] = False

        # Save results.
        for key in select:
            if len(key) > 1 and len(key) <= max_ngram and select[key]:
                dumpfun(sentence_id, positions[key], absolute_positions[key], key, gluevals[key])

        sentence_id+=1
        pos += sentence_length + 1


def scp_glue(gluevals, sufarray, corpus_size, key):
    """
        Glue function: SCP.
    """

    main_prob = ngram_prob(sufarray, corpus_size, key)
    square_main_prob = main_prob ** 2
    if len(key) == 1:
        return square_main_prob
    
    avp = 0
    for i in range(1, len(key)):
        avp += (ngram_prob(sufarray, corpus_size, key[0:i]) *
                ngram_prob(sufarray, corpus_size, key[i:]))
    avp = avp / (len(key)-1)

    if avp > 0:
        return square_main_prob / avp
    else:
        return 0

def ngram_count(sufarray, key):
    """
        Returns the number of ocurrences of `key` in the `SuffixArray`.
    """
    range = sufarray.find_ngram_range(key)
    if range is None:
        return 0
    else:
        return range[1] - range[0] + 1

def ngram_prob(sufarray, corpus_size, key):
    """
        Returns the probability (a real between 0 and 1) of occurrence of `key`
        in the `SuffixArray`.
    """
    count = ngram_count(sufarray, key)
    return count / float(corpus_size)


surface_instead_lemmas = False
corpus_length_limit = None
index_basepath = None
gluefun = scp_glue
min_ngram = 2
max_ngram = 8
min_frequency = 2

def main():
    candidates = {}
    
    if surface_instead_lemmas:
        base_attr = 'surface'
    else:
        base_attr = 'lemma'

    def dump(sentence_id, positions, absolute_positions, key, glue):
        (surfaces_dict, total_freq, _) = candidates.get(key, ({}, 0, -1))
        surface_key = tuple([index.arrays['surface'].corpus[j] for j in absolute_positions])
        surfaces_dict.setdefault(surface_key, []).append(
            str(sentence_id) + ":" + ",".join(map(str, positions)))
        candidates[key] = (surfaces_dict, total_freq + 1, glue)

    index = Index(index_basepath)
    index.load_metadata()
    index.load(base_attr)
    index.load('surface')
    extract(index, base_attr, gluefun, dumpfun=dump, min_ngram=min_ngram,
            max_ngram=max_ngram, corpus_length_limit=corpus_length_limit)

    verbose("Outputting candidates file...")
    print XML_HEADER % { "root": "candidates", "ns": "" }

    meta = Meta([CorpusSize("corpus", index.metadata["corpus_size"])],
                [MetaFeat("glue", "real")], [])
    print meta.to_xml().encode('utf-8')

    id_number = 0

    for key in candidates:
        (surfaces_dict, total_freq, glue) = candidates[key]
        if total_freq >= min_frequency:
            # Make <cand> entry (usually lemma-based)
            cand = Candidate(id_number, [], [], [], [], [])
            for j in key:
                w = Word(WILDCARD, WILDCARD, WILDCARD, WILDCARD, [])
                setattr(w, base_attr, index.arrays[base_attr].symbols.number_to_symbol[j])
                cand.append(w)
            freq = Frequency('corpus', total_freq)
            cand.add_frequency(freq)
            cand.add_feat(Feature("glue", glue))


            # Add surface forms.
            for surface_key in surfaces_dict:
                occur_form = Ngram([], [])
                for j in surface_key:
                    w = Word(WILDCARD, WILDCARD, WILDCARD, WILDCARD, [])
                    w.surface = index.arrays['surface'].symbols.number_to_symbol[j]
                    occur_form.append(w)
                sources = surfaces_dict[surface_key]
                freq_value = len(sources)
                freq = Frequency('corpus', freq_value)
                occur_form.add_frequency(freq)
                occur_form.add_sources(sources)
                cand.add_occur(occur_form)

            print cand.to_xml().encode('utf-8')
            id_number += 1

    print XML_FOOTER % { "root": "candidates" }

    #words = map(lambda i: index.arrays['lemma'].symbols.number_to_symbol[i], key)
    #print ' '.join(words).encode('utf-8'), candidates[key][0][2]


def treat_options( opts, arg, n_arg, usage_string ) :
    """
        Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.    
    """
    global surface_instead_lemmas, print_source, corpus_length_limit, gluefun
    global min_ngram, max_ngram, min_frequency

    mode = []
    for ( o, a ) in opts:
        if o in ("-s", "--surface") : 
            surface_instead_lemmas = True
        elif o in ("-S", "--source") :
            print_source = True
        elif o in ("-l", "--limit") :
            corpus_length_limit = int(a)
        elif o in ("-f", "--freq") :
            min_frequency = int(a)
        elif o in ("-n", "--ngram") :
            (min_ngram, max_ngram) = interpret_ngram(a)
        elif o in ("-G", "--glue"):
            if a == "scp":
                gluefun = scp_glue
            else:
                print >>sys.stderr, "Unknown glue function '%s'" % a
                sys.exit(1)

    treat_options_simplest( opts, arg, n_arg, usage_string )

longopts = ["surface", "source", "verbose", "limit=", "glue=", "ngram=", "freq="]
arg = read_options("sSvl:G:n:f:", longopts, treat_options, 1, usage_string)
index_basepath = arg[0]

main()
