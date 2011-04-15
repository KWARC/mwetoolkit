import sys
import array
import shelve
import codecs
import xml.sax
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word
from util import verbose

import gc
gc.set_debug(gc.DEBUG_LEAK)


NGRAM_LIMIT=16

# TODO: Unify this with patternlib and the rest of the toolkit.
ATTRIBUTE_SEPARATOR="\35"

def make_array(initializer=None):
	if initializer is None:
		return array.array('L')
	else:
		return array.array('L', initializer)


# Taken from counter.py
def load_array_from_file( an_array, a_filename ) :
    MAX_MEM = 10000
    fd = open( a_filename )
    isMore = True
    while isMore :
        try :    
            an_array.fromfile( fd, MAX_MEM )
        except EOFError :
            isMore = False # Did not read MAX_MEM_ITEMS items? Not a problem...
    fd.close()

def save_array_to_file(array, path):
	file = open(path, "w")
	array.tofile(file)
	file.close()

def load_symbols_from_file(symbols, path):
	file = codecs.open(path, "r", "utf-8")
	id = 0
	symbols.number_to_symbol = []
	symbols.symbol_to_number = {}
	for line in file:
		sym = line.rstrip('\n')
		symbols.symbol_to_number[sym] = id
		symbols.number_to_symbol.append(sym)
		id += 1

	file.close()

def save_symbols_to_file(symbols, path):
	file = codecs.open(path, "w", "utf-8")
	for sym in symbols.number_to_symbol:
		file.write(sym + '\n')
	file.close()


#def compare_indices(corpus, max, pos1, pos2):
#	while pos1<max and pos2<max and corpus[pos1] == corpus[pos2]:
#		pos1 += 1
#		pos2 += 1
#
#	if pos1>=max:
#		return -1
#	elif pos2>=max:
#		return 1
#	else:
#		return int(corpus[pos1] - corpus[pos2])

def compare_ngrams(ngram1, pos1, ngram2, pos2, ngram1_exhausted=-1, ngram2_exhausted=1, limit=NGRAM_LIMIT):
	max1 = len(ngram1)
	max2 = len(ngram2)
	i = 0
	while pos1<max1 and pos2<max2 and ngram1[pos1]==ngram2[pos2] and i<NGRAM_LIMIT:
		pos1 += 1
		pos2 += 1
		i += 1

	if pos1>=max1 and pos2>=max2:
		return 0
	elif pos1>=max1:
		return ngram1_exhausted
	elif pos2>=max2:
		return ngram2_exhausted
	else:
		return int(ngram1[pos1] - ngram2[pos2])

def fuse_suffix_arrays(array1, array2):
	# Returns a new SuffixArray fusing the 'corpus' data of each input array.
	# This is used to generate indices for combined attributes (e.g., lemma+pos).

	fused_array = SuffixArray()
	for i in xrange(len(array1.corpus)):
		sym1 = array1.symbols.number_to_symbol[array1.corpus[i]]
		sym2 = array2.symbols.number_to_symbol[array2.corpus[i]]
		fused_array.append_word(sym1 + ATTRIBUTE_SEPARATOR + sym2)

	return fused_array


class SymbolTable:
	def __init__(self):
		self.symbol_to_number = {'': 0}
		self.number_to_symbol = ['']
		self.last_number = 0

	def intern(self, symbol):
		if not self.symbol_to_number.has_key(symbol):
			self.last_number += 1
			self.symbol_to_number[symbol] = self.last_number
			#self.number_to_symbol[self.last_number] = symbol
			self.number_to_symbol.append(symbol)  # Risky and not intention-expressing

		return self.symbol_to_number[symbol]


class SuffixArray:
	def __init__(self):
		self.corpus = make_array()    # List of word numbers
		self.suffix = make_array()    # List of word positions
		self.symbols = SymbolTable()  # word<->number conversion table

	def set_basepath(self, basepath):
		self.basepath = basepath
		self.corpus_path = basepath + ".corpus"
		self.suffix_path = basepath + ".suffix"
		self.symbols_path = basepath + ".symbols"

	def load(self):
		load_array_from_file(self.corpus, self.corpus_path)
		load_array_from_file(self.suffix, self.suffix_path)
		load_symbols_from_file(self.symbols, self.symbols_path)

	def save(self):
		save_array_to_file(self.corpus, self.corpus_path)
		save_array_to_file(self.suffix, self.suffix_path)
		save_symbols_to_file(self.symbols, self.symbols_path)

	def append_word(self, word):
		self.corpus.append(self.symbols.intern(word))

	# For debugging.
	def append_string(self, sentence):
		for w in sentence.split():
			self.append_word(w)

	def build_suffix_array(self):
		tmpseq = range(0, len(self.corpus))
		tmpsuf = sorted(tmpseq, cmp=(lambda a,b: compare_ngrams(self.corpus, a, self.corpus, b)))
		self.suffix = make_array(tmpsuf)


	def find_ngram_range(self, ngram, min=0, max=None):
		# Returns a tuple (min, max) of matching ngram positions in suffix array
		# TODO: We will need a more "incremental" approach for searching for
		# patterns that use multple word attributes.
		
		if max is None:
			max = len(self.suffix) - 1

		first = self.binary_search_ngram(ngram, min, max, (lambda a,b: a >= b))
		last  = self.binary_search_ngram(ngram, min, max, (lambda a,b: a > b))

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

	def binary_search_ngram(self, ngram, first, last, cmp):
		# Find the least suffix that satisfies suffix `cmp` ngram.

		# 'max' must be one more than 'last', for the case no suffix
		# satisfies the comparison.
		max = last + 1
		min = first

		while min < max:
			mid = (min+max)/2
			if cmp(compare_ngrams(self.corpus, self.suffix[mid], ngram, 0, ngram2_exhausted=0), 0):
				max = mid      # If 'mid' satisfies, then what we want *is* mid or *is before* mid
			else:
				mid += 1
				min = mid      # If 'mid' does not satisfy, what we want *must be after* mid.

		if mid > last:
			return None
		else:
			return mid


	# For debugging.
	def dump_suffixes(self, limit=10):
		for pos in self.suffix:
			print "%4d:" % pos,
			for i in range(pos, pos+limit):
				if i < len(self.corpus):
					print self.symbols.number_to_symbol[self.corpus[i]],
				else:
					print "*",

			print ""


class Index:
	# Attribute order must be the same as the parameters of 'Word'
	WORD_ATTRIBUTES = ['surface', 'lemma', 'pos', 'syn']

	def __init__(self, basepath=None):
		self.arrays = {}
		self.metadata = { "corpus_size": 0 }
		if basepath is not None:
			self.set_basepath(basepath)

	def fresh_arrays(self):
		for attr in Index.WORD_ATTRIBUTES:
			self.arrays[attr] = SuffixArray()

	def set_basepath(self, path):
		self.basepath = path
		self.metadata_path = path + ".info"

	def load(self, attribute):
		if self.arrays.has_key(attribute):
			return self.arrays[attribute]

		verbose("Loading corpus files for attribute \"%s\"." % attribute)
		array = SuffixArray()
		path = self.basepath + "." + attribute
		array.set_basepath(path)
		try:
			array.load()
		except IOError, err:
			# If attribute is composed, fuse the corresponding suffix arrays.
			if '+' in attribute:
				attr1, attr2 = attribute.rsplit('+', 1)
				array = fuse_suffix_arrays(self.load(attr1), self.load(attr2))

				array.set_basepath(path)
				array.build_suffix_array()
				array.save()

			else:
				raise err

		self.arrays[attribute] = array
		return array

	def save(self, attribute):
		array = self.arrays[attribute]
		array.set_basepath(self.basepath + "." + attribute)
		array.save()

	def load_metadata(self):
		metafile = open(self.metadata_path)
		for line in metafile:
			key, type, value = line.rstrip('\n').split(" ", 2)
			if type == "int":
				value = int(value)
			self.metadata[key] = value

		metafile.close()
	
	def save_metadata(self):
		metafile = open(self.metadata_path, "w")
		for key, value in self.metadata.items():
			if isinstance(value, int):
				type = "int"
			else:
				type = "string"

			metafile.write("%s %s %s\n" % (key, type, value))

		metafile.close()


	# Load/save main (non-composite) attributes and metadata
	def load_main(self):
		self.load_metadata()
		for attr in Index.WORD_ATTRIBUTES:
			self.load(attr)

	def save_main(self):
		self.save_metadata()
		for attr in Index.WORD_ATTRIBUTES:
			self.save(attr)


	def append_sentence(self, sentence):
		# Adds a sentence (presumably extracted from a XML file) to the index.

		for attr in Index.WORD_ATTRIBUTES:
			for word in sentence.word_list:
				value = getattr(word, attr)
				self.arrays[attr].append_word(value)
			self.arrays[attr].append_word('')  # '' (symbol 0)  means end-of-sentence

		self.metadata["corpus_size"] += len(sentence.word_list)

	def build_suffix_arrays(self, save=False, free_after=False):
		for attr in self.arrays.keys():
			print "Building suffix array for %s..." % attr
			self.arrays[attr].build_suffix_array()
			if save:
				self.save(attr)
			if free_after:
				del self.arrays[attr]

	def iterate_sentences(self):
		# Returns an iterator over all sentences in the corpus.

		id = 1
		guide = Index.WORD_ATTRIBUTES[0]        # guide?
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
				args = []
				for attr in Index.WORD_ATTRIBUTES:
					number = self.arrays[attr].corpus[i]
					symbol = self.arrays[attr].symbols.number_to_symbol[number]
					args.append(symbol)
				
				args.append([])
				words.append(Word(*args))

	# For debugging.
	def print_sentences(self):
		for sentence in self.iterate_sentences():
			for word in sentence.word_list:
				print word.surface,
			print ""



# For testing.
#h = SuffixArray()
#s = "the quick brown fox jumps over the lazy dog which wanted the fox to jump away into the house"
#h.append_string(s)
#h.build_suffix_array()

# For more testing.
def index_from_corpus(basepath, corpus_file):
	#file = open(corpus_file)
	parser = xml.sax.make_parser()
	index = Index()
	index.set_basepath(basepath)
	index.fresh_arrays()
	parser.setContentHandler(CorpusXMLHandler(index.append_sentence))
	parser.parse(corpus_file)
	index.save_metadata()
	index.build_suffix_arrays(save=True, free_after=True)
	return index

#h = index_from_corpus("../toy/genia/corpus.xml")
#h.set_basepath("/tmp/foo")
#h.save_main()

#t = fuse_suffix_arrays(h.arrays["surface"], h.arrays["pos"])

def standalone_main(argv):
	if len(argv) < 3:
		print >>sys.stderr, "Usage: python indexlib.py <basepath> <corpus> [<attr>:<attr>:...]"
		return 1

	basepath = argv[1]
	corpus = argv[2]

	# Gambiarra -- FIXME FIXME FIXME
	if len(argv) > 3:
		Index.WORD_ATTRIBUTES = argv[3].split(":")

	index = index_from_corpus(basepath, corpus)
	print >>sys.stderr, "Done."

if __name__ == "__main__":
	standalone_main(sys.argv)
