import sys
import tempfile
from libs.indexlib import Index


from xmlhandler.classes.frequency import Frequency
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from xmlhandler.classes.entry import Entry
from util import usage, read_options, treat_options_simplest, verbose

from xmlhandler.classes.__common import WILDCARD, \
                                        TEMP_PREFIX, \
                                        TEMP_FOLDER, \
                                        XML_HEADER, \
                                        XML_FOOTER
def make_temp_file():
	return tempfile.NamedTemporaryFile(prefix=TEMP_PREFIX, dir=TEMP_FOLDER)

def print_args(*args):
	print args

def extract(index, array_name, gluefun, min_ngram=2, max_ngram=8, corpus_length_limit=None, dumpfun=print_args):
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

		for ngram_size in range(1, max_ngram+1):
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
						else:
							select[subkey] = False

		# Save results.
		for key in select:
			if len(key) > 1 and len(key) < max_ngram and select[key]:
				dumpfun(sentence_id, positions[key], absolute_positions[key], key, gluevals[key])

		sentence_id+=1
		pos += sentence_length + 1


def scp_glue(gluevals, sufarray, corpus_size, key):
	main_prob = ngram_prob(sufarray, corpus_size, key)
	square_main_prob = main_prob ** 2
	if len(key) == 1:
		return square_main_prob
	
	avp = 0
	for i in range(1, len(key)):
		avp += (ngram_prob(sufarray, corpus_size, key[0:i]) *
		        ngram_prob(sufarray, corpus_size, key[i:]))
	if avp > 0:
		return square_main_prob / avp
	else:
		return 0

def ngram_count(sufarray, key):
	range = sufarray.find_ngram_range(key)
	if range is None:
		return 0
	else:
		return range[1] - range[0] + 1

def ngram_prob(sufarray, corpus_size, key):
	count = ngram_count(sufarray, key)
	return count / float(corpus_size)


def main(args):
	temp_file = open("/tmp/outout", "w")
	candidates = {}
	base_attr = 'lemma'

	def dump(sentence_id, positions, absolute_positions, key, glue):
		(surfaces_dict, total_freq) = candidates.get(key, ({}, 0))
		surface_key = tuple([index.arrays['surface'].corpus[j] for j in absolute_positions])
		surfaces_dict.setdefault(surface_key, []).append(str(sentence_id) + ":" + ",".join(map(str, positions)))
		candidates[key] = (surfaces_dict, total_freq + 1)

	index = Index(args[0])
	index.load_main()
	extract(index, base_attr, scp_glue, dumpfun=dump, corpus_length_limit=2000)


	verbose("Outputting candidates file...")
	print XML_HEADER % { "root": "candidates", "ns": "" }
	print "<meta></meta>"
	id_number = 0

	for key in candidates:
		(surfaces_dict, total_freq) = candidates[key]
		if total_freq >= 2:
			cand = Candidate(id_number, [], [], [], [], [])
			for j in key:
				w = Word(WILDCARD, WILDCARD, WILDCARD, WILDCARD, [])
				setattr(w, base_attr, index.arrays[base_attr].symbols.number_to_symbol[j])
				cand.append(w)
			freq = Frequency('corpus', total_freq)
			cand.add_frequency(freq)

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

	print XML_FOOTER % { "root": "candidates" }

	#words = map(lambda i: index.arrays['lemma'].symbols.number_to_symbol[i], key)
	#print ' '.join(words).encode('utf-8'), candidates[key][0][2]


main(sys.argv[1:])
