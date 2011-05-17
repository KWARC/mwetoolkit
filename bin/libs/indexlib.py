import sys
import array
import shelve
import xml.sax
from xmlhandler.corpusXMLHandler import CorpusXMLHandler
from xmlhandler.classes.sentence import Sentence
from xmlhandler.classes.word import Word, WORD_ATTRIBUTES
from xmlhandler.classes.__common import ATTRIBUTE_SEPARATOR
from util import verbose

NGRAM_LIMIT=16

def copy_list(ls):
	return map(lambda x: x, ls)

def make_array(initializer=None):
	if initializer is None:
		return array.array('i')
	else:
		return array.array('i', initializer)


# Taken from counter.py
def load_array_from_file( an_array, a_filename ) :
	"""
		Fills an existing array with the contents of a file.
	"""
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
	"""
		Dumps an array to a file.
	"""
	file = open(path, "w")
	array.tofile(file)
	file.close()

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

def save_symbols_to_file(symbols, path):
	"""
		Dumps a symbol table to a file.
	"""
	file = open(path, "wb")
	for sym in symbols.number_to_symbol:
		file.write(sym.encode("utf-8") + '\n')
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
	"""
		Returns a new `SuffixArray` fusing the `corpus` data of each input array.
		This is used to generate indices for combined attributes (e.g., lemma+pos).
	"""

	fused_array = SuffixArray()
	for i in xrange(len(array1.corpus)):
		sym1 = array1.symbols.number_to_symbol[array1.corpus[i]]
		sym2 = array2.symbols.number_to_symbol[array2.corpus[i]]
		fused_array.append_word(sym1 + ATTRIBUTE_SEPARATOR + sym2)

	return fused_array


class SymbolTable():
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
			self.number_to_symbol.append(symbol)  # Risky and not intention-expressing

		return self.symbol_to_number[symbol]


class SuffixArray():
	"""
		Class containing the corpus and suffix arrays and the symbol table
		for one attribute of a corpus.
	"""

	def __init__(self):
		self.corpus = make_array()    # List of word numbers
		self.suffix = make_array()    # List of word positions
		self.symbols = SymbolTable()  # word<->number conversion table

	def set_basepath(self, basepath):
		"""
			Sets the base path for the suffix array files.
		"""
		self.basepath = basepath
		self.corpus_path = basepath + ".corpus"
		self.suffix_path = basepath + ".suffix"
		self.symbols_path = basepath + ".symbols"

	def load(self):
		"""
			Loads the suffix array from the files at `self.basepath`.
		"""
		load_array_from_file(self.corpus, self.corpus_path)
		load_array_from_file(self.suffix, self.suffix_path)
		load_symbols_from_file(self.symbols, self.symbols_path)

	def save(self):
		"""
			Saves the suffix array to the files at `self.basepath`.
		"""
		save_array_to_file(self.corpus, self.corpus_path)
		save_array_to_file(self.suffix, self.suffix_path)
		save_symbols_to_file(self.symbols, self.symbols_path)

	def append_word(self, word):
		"""
			Adds a new word to the end of the corpus array, putting it in the
			symbol table if necessary.
		"""
		self.corpus.append(self.symbols.intern(word))

	# For debugging.
	def append_string(self, sentence):
		for w in sentence.split():
			self.append_word(w)

	def build_suffix_array(self):
		"""
			Builds the sorted suffix array from the corpus array.
		"""
		tmpseq = range(0, len(self.corpus))
		tmpseq.sort(cmp=(lambda a,b: compare_ngrams(self.corpus, a, self.corpus, b)))
		self.suffix = make_array(tmpseq)


	def find_ngram_range(self, ngram, min=0, max=None):
		"""
			Returns a tuple `(first, last)` of matching ngram positions in
			the suffix array, or `None` if there is no match.
		"""
		# TODO: We will need a more "incremental" approach for searching for
		# patterns that use multple word attributes. (Can't be done!)
		
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
		"""
			Find the least suffix that satisfies `suffix <cmp> ngram`, or
			`None` if there is none.
		"""

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
	def dump_suffixes(self, limit=10, start=0, max=None):
		"""
			Prints the suffix array to standard output (for debugging).
		"""
		if max is None:
			max = len(self.suffix)

		#for pos in self.suffix:
		for suf in xrange(start, max):
			pos = self.suffix[suf]
			print "%4d:" % pos,
			for i in range(pos, pos+limit):
				if i < len(self.corpus):
					sym = self.symbols.number_to_symbol[self.corpus[i]]
					if sym == "":
						sym = "#"
					print sym,
				else:
					print "*",

			print ""


class Index():
	"""
		This class holds the `SuffixArray`s for all attributes of a corpus,
		plus metadata which is common for all attributes.
	"""
	def __init__(self, basepath=None, used_word_attributes=None):
		self.arrays = {}
		self.metadata = { "corpus_size": 0 }
		self.sentence_count = 0

		if used_word_attributes is not None:
			self.used_word_attributes = used_word_attributes
		else:
			self.used_word_attributes = copy_list(WORD_ATTRIBUTES)

		if basepath is not None:
			self.set_basepath(basepath)

	def fresh_arrays(self):
		"""
			Creates empty suffix arrays for each used attribute in the index.
		"""
		for attr in self.used_word_attributes:
			self.arrays[attr] = SuffixArray()

	def set_basepath(self, path):
		"""
			Sets the base path for the index files.
		"""
		self.basepath = path
		self.metadata_path = path + ".info"

	def load(self, attribute):
		"""
			Load an attribute from the corresponding index files.
			If the attribute is of the form `a1+a2` and the corresponding
			file does not exist, creates a new suffix array fusing the 
			arrays for attributes `a1` and `a2`.
		"""

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
		"""
			Saves the suffix array for `attribute` to the corresponding files.
		"""
		array = self.arrays[attribute]
		array.set_basepath(self.basepath + "." + attribute)
		array.save()

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


	# Load/save main (non-composite) attributes and metadata
	def load_main(self):
		self.load_metadata()
		for attr in self.used_word_attributes:
			self.load(attr)

	def save_main(self):
		self.save_metadata()
		for attr in self.used_word_attributes:
			self.save(attr)


	def append_sentence(self, sentence):
		"""
			Adds a `Sentence` (presumably extracted from a XML file) to the index.
		"""

		for attr in self.used_word_attributes:
			for word in sentence.word_list:
				value = getattr(word, attr)
				self.arrays[attr].append_word(value)
			self.arrays[attr].append_word('')  # '' (symbol 0)  means end-of-sentence

		self.metadata["corpus_size"] += len(sentence.word_list)
		self.sentence_count += 1
		if self.sentence_count % 100 == 0:
			verbose("Processing sentence %d" % self.sentence_count)

	def build_suffix_arrays(self):
		"""
			Build suffix arrays for all attributes in the index.
		"""
		for attr in self.arrays.keys():
			verbose("Building suffix array for %s..." % attr)
			self.arrays[attr].build_suffix_array()

	def iterate_sentences(self):
		"""
			Returns an iterator over all sentences in the corpus.
		"""

		id = 1
		guide = self.used_word_attributes[0]        # guide?
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
				for attr in self.used_word_attributes:
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


def index_from_corpus(corpus, basepath=None, attrs=None):
	"""
		Generates an `Index` from a corpus file.
	"""
	parser = xml.sax.make_parser()
	index = Index(basepath, attrs)
	index.fresh_arrays()
	parser.setContentHandler(CorpusXMLHandler(index.append_sentence))
	parser.parse(corpus)
	index.build_suffix_arrays()
	index.save_main()
	return index

#t = fuse_suffix_arrays(h.arrays["surface"], h.arrays["pos"])

# For debugging.
def standalone_main(argv):
	if len(argv) != 3:
		print >>sys.stderr, "Usage: python indexlib.py <basepath> <corpus>"
		return 1

	basepath = argv[1]
	corpus = argv[2]

	index = index_from_corpus(corpus)
	index.set_basepath(basepath)
	index.save_main()
	print >>sys.stderr, "Done."

if __name__ == "__main__":
	standalone_main(sys.argv)
