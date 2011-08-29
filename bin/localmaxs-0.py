import sys
from libs.indexlib import Index

def extract(index, array_name, gluefun, min_ngram=2, max_ngram=8, outstream=sys.stdout):
	sufarray = index.arrays[array_name]
	sentence_id = 0
	pos = 0
	corpus_length = len(sufarray.corpus)
	corpus_size = index.metadata['corpus_size']  # corpus_size does not count sentence separators.

	while pos < corpus_length:
		if sentence_id%10 == 0:
			print >>sys.stderr, "Processing sentence %d" % sentence_id

		sentence_length = 0
		while sufarray.corpus[pos + sentence_length] != 0:
			sentence_length += 1

		gluevals = {}
		select = {}

		for ngram_size in range(1, max_ngram+1):
			for i in range(sentence_length - ngram_size + 1):
				key = tuple(range(pos+i, pos+i+ ngram_size))
				glue = gluefun(gluevals, sufarray, corpus_size, key)
				gluevals[key] = glue
				select[key] = True

				if ngram_size >= 2:
					for subkey in [key[0:-1], key[1:]]:
						if glue < gluevals[subkey]:
							select[key] = False
						else:
							select[subkey] = False

		# Print results.
		for key in select:
			if len(key) > 1 and len(key) < max_ngram and select[key]:
				try:
					print >>outstream, ' '.join([sufarray.symbols.number_to_symbol[num] for num in key]), "(glue %s)"%gluevals[key]
				except Exception, err:
					print key
					for num in key:
						if num > len(sufarray.symbols.number_to_symbol):
							print "Tiu ne forgesas: %d" % num

		print >>outstream, "---"
		outstream.flush()
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


# Test.
h = Index("/home/vitor/BolsaPLN/genia/index/corpus")
h.load_main()
out = open("/tmp/outout", "w")
extract(h, 'lemma', scp_glue, outstream=out)
out.close()
