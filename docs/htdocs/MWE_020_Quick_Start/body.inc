<h2>Getting started</h2>

<p>To start using the mwetoolkit, you need first to <a href="">install it</a>. The toolkit currently works at the command line. If you are not familiar with it, you can simply follow the steps below and copy-paste the commands. This tutorial is based on the slides of <a href="downloads/mwetk-tutorial-files.zip">the mwetoolkit tutorial</a> (last updated for WG2 Parseme meeting in March 20, 2015). Each command is explained and you can try and adapt the options to your corpus, MWE patterns, and so on. In the scripts below, we use the variable${MWETKBIN} to indicate the path to your mwetoolkit <tt>bin</tt> folder. The commands are also available in the mwetoolkit itself in the form of a script in folder <tt>toy</tt>, called <tt>run-tutorial.sh</tt>.</p>

<h3>1. Introduction</h3>

<p>The mwetoolkit is composed of python scripts, so you do not need to do anything to compile it. As long as you have a python 2.6+ interpreter, it's fine. However, part of it is written in C for increased speed, so we recommend that you compile the C indexer before getting started. Therefore, simply run <tt>make</tt> in the root mwetoolkit folder.</p>

<p>For the next steps, remember that you can always run a script passing option <tt>-h</tt>, to obtain a detailed list of its functionalities, arguments and options. For example :</p>

<pre>${MWETKBIN}/index.py -h</pre>

echo -e "\nStep 2 - Indexing the corpus"

# In this tutorial, we use the TED English corpus, an excerpt from the bilingual
# English-French TED talks from https://wit3.fbk.eu/mt.php?release=2014-01
# The corpus was parsed using RASP and then converted to CONLL format. This 
# format contains one word per line, and one word information per column. Take
# a look at the file to see what it contains.
zcat ted-en-sample.conll.gz | head

# You can uncompress the file so that it is easier to inspect it using command 
# line tools or a text editor like nano, vim, gedit or emacs. Nonetheless, you
# can use compressed files directly as input to the mwetoolkit.
gunzip -c ted-en-sample.conll.gz > ted-en-sample.conll

# Let us generate an index for fast corpus access. This is not required for most
# scripts, but since we want to count n-grams, we will need it (counter.py).
# Since our corpus contains around half a million words, this will take some 
# time (30 secs to a couple of minutes, depending on your computer)
mkdir -p index 
rm -rf index/*  
${MWETKBIN}/index.py -v -i index/ted ted-en-sample.conll 

# If you look at the index folder, you will notice the creation of many files
# prefixed by "ted". This is because you specified that the index should be
# created with prefix index/ted using -i option. We recommend always creating
# a folder and storing all index files in this folder.
ls index

echo -e "\nStep 3 - Candidate extraction\n"
# Once you have indexed the corpus, you are ready for candidate extraction. You 
# must first define the pattern you are interested in. For instance, we use the
# file pat_nn.xml which describes sequences of nouns and prepositional phrases
# that start with a noun. This corresponds roughly to noun phrases in English. 
# You can look at the example pattern to get familiarised with the XML format 
# used to describe it. The online documentation on the XML format and on 
# defining patterns should also help.
cat pat_nn.xml

# Then, you can run the candidates.py script to extract from the indexed corpus.
# the candidates that match the pattern. It takes as argument the pattern file 
# (-p), the corpus file format (--from) and the corpus file, which in our case 
# is the .info file corresponding to a BinaryIndex. Option -S will keep 
# information about the source sentences in which the candidates were found
${MWETKBIN}/candidates.py -p pat_nn.xml -S -v --from=BinaryIndex index/ted.info > cand.xml

# The resulting file is in XML format, each lemmatised candidate containing some 
# information about its occurrences and source sentences.
head cand.xml

# You can count how many candidates were extracted using the wc.py script
${MWETKBIN}/wc.py cand.xml 

# You can count the number of occurrences of each candidate, and also of each
# word contained in a candidate. Therefore, we run the counter.py script which
# internally uses the index to obtain n-gram counts very fast.
${MWETKBIN}/counter.py -v -i index/ted.info cand.xml > cand-count.xml

# The resulting file is identical to the input XML, with added <freq> elements.
# You can count MWE candidates either in the source corpus, as we did here, or
# in other corpora (e.g. for contrastive methods of terminology extraction).
head cand-count.xml | grep --color "<freq"

echo -e "\nStep 4 - Candidate filtering\n"

# There are several available filtering tools included in the mwetoolkit. It is
# possible to filter using simple criteria such as frequency and n-gram length,
# using the filter.py script. Below, we show an example that filters out every 
# n-gram that occurred only once in the corpus. This is genrally a good idea if
# we want to obtain reliable association measures for further filtering (see 
# below)
${MWETKBIN}/filter.py -v -t ted:2 cand-count.xml > cand-count-f1.xml

# You can see that a large number of candidates was removed from the list, 
# because they only occurred once in the corpus
${MWETKBIN}/wc.py cand-count-f1.xml

# It is probably more interesting to use lexical association scores, like 
# pointwise mutual information and log-likelihood score, to filter out 
# candidates which are frequent only because, by pure chance, they are composed
# of frequent words. Therefore, let us first calculate the 5 standard 
# association measures of the mwetoolkit: mle, dice, pmi, t and ll, which stand
# for Maximum Likelihood (a.k.a. relative frequency), Dice's coefficient, 
# pointwise mutual information, Student's t score and log-likelihood score. The
# latter is only applicable for 2-word candidates, so it is normal that the 
# script will print a warning message, since some of our candidates are 3+-grams
${MWETKBIN}/feat_association.py -v cand-count-f1.xml > cand-feat.xml

# Now each candidate has a set of features which are real-valued association 
# scores
head -n 30 cand-feat.xml | grep -B 5 -A 7 "<features"

# We will use the value of one of these features to sort the candidates list in
# descending order using sort.py with -d option. The feature used in our example
# is t_ted, but you can test other association measures and see if the top-100
# retrieved expressions seem more interesting. Remark that the mwetoolkit has
# scripts that are similat to common Linux commands like sort, head, tail, etc.
# Here, we use head.py to keep only the top 100 candidates sorted by t-score.
python ${MWETKBIN}/sort.py -d -v -f t_ted cand-feat.xml | 
${MWETKBIN}/head.py -v -n 100 > cand-feat-ft.xml

echo -e "\nStep 5 - Annotating a corpus\n"

# Once we have obtained a reasonably clean list of MWE candidates, we can then
# project it back onto the original corpus. Note that this is actually different
# from applying an extraction pattern directly on the corpus, since we performed
# various filtering steps to obtain better MWE candidates. In the example below, 
# we "annotate" the original TED corpus with our filtered candidates using the
# source information present in the candidates themselves. This will take a time
# that is proportional to the number of sentences in the corpus.
${MWETKBIN}/annotate_mwe.py -v --detector=Source -c cand-feat-ft.xml \
                            --to PlainCorpus ted-en-sample.conll \
                            > ted-en-sample-mwe.txt
                            
# The output is similar to the original corpus, but MWEs are single tokens 
# joined by underscore (this is how we represent MWEs in plain txt format). 
head -n 50 ted-en-sample-mwe.txt | grep --colour -B 2 -A 2 ".*_.*" 

# Like any other mwetoolkit script, it is possible to produce more friendly 
# output formats. For instance, the command below generates an HTML corpus file
# (--to HTML) containing only sentences that contain MWEs (--filter-and-annot).
# Also remember that it is possible to project a candidates list or lexicon onto
# another, different corpus, using a ContiguousLemma detector. In our example,
# the corpus is the same but we allow for 1-word gaps (-g 1)
${MWETKBIN}/annotate_mwe.py -v --detector=ContiguousLemma -g 1 \
                            -c cand-feat-ft.xml --to HTML --filter-and-annot \
                            ted-en-sample.conll > ted-mwe.html

# This file can be opened by your favorite web browser, like Firefox, Chrome, 
# Safari or Explorer. It is quite easy to visualise POS and lemmas by hovering 
# words and seeing MWEs annotated in different colours. See, for instance, how
# sentence 1121 contains a nested MWE [World [Trade Center]], while sentence 
# 1328 contains a gappy MWE "lot of [the] time". Not all of these MWEs are 
# interesting, since the list contains some noise due to 100% automatic 
# candidate extraction and filtering.

echo -e "\nStep 6 - Evaluation\n"
# One problem that often arises in automatic MWE discovery is to decide whether
# a given MWE candidate list contains interesting expressions. This work is 
# generally done by manually inspecting the list and selecting interesting 
# expressions. Therefore, it is better to use some more readable format, like 
# CSV.
${MWETKBIN}/transform.py --from XML --to CSV cand-feat-ft.xml > cand-feat-ft.csv

# The output of transform.py can the be imported into your favourite spreadsheet 
# editor (LibreOffice Calc, Microsoft Excel). Don't forget to set "TAB" as the 
# field separator and nothing as string delimiter. You can sort the columns 
# according to different association scores, and mark the interesting MWEs. The
# toolkit also provides a script called eval_automatic.py, which compares a 
# candidates list with a reference dictionary, calculating precision, recall and
# F1. It is also possible to calculate average precision of a given feature 
# using avg_precision.py.

# Also, do not hesitate to test other patterns like the one in pat_open.xml, and
# the examples described on our website.

# In the end, we can remove the corpus and keep only the gzipped version, if we 
# want to save some disk space.
# rm ted-en-sample.conll

# If you want to remove all temporary files, uncomment the lines below
# rm -f cand-feat-ft.csv ted-mwe.html ted-en-sample-mwe.txt cand-feat-ft.xml \
#       cand-count-f1.xml index/* cand.xml cand-count.xml ted-en-sample.conll





































<!--
<h3>Step-by-step guide (NOT UP-TO-DATE!)</h3>

<p><tt>mwetoolkit</tt> works by extracting MWE candidates from a corpus using a set of morphosyntactical patterns. Then it can apply a number of statistics to filter the extracted candidates. <del>Input corpora, patterns and candidates are stored as XML files, following the format described by the DTDs in the <tt>dtd</tt> directory in the distribution.</del> The toolkit consists of a set of scripts performing each phase of candidate extraction and analysis; these scripts are in the <tt>bin</tt> directory.</p>

<p><tt>mwetoolkit</tt> receives as input a corpus in one of the many accepted filetypes. This file contains a list of the sentences of the corpus. Each sentence is a list of words, and each word has a set of attributes (surface form, lemma, part of speech, and dependency syntax information, if available). To obtain this information from a plain textual corpus without annonations, usually a <em>part-of-speech tagger</em> or <em>parser</em> is used.</p>

<p>To obtain a XML corpus from a plain textual corpus, you will usually use a tagger program or parser, such as explained in <a HREF="http://mwetoolkit.sourceforge.net/PHITE.php?sitesig=MWE&page=MWE_004_Preprocessing_a_corpus_using_TreeTagger">Preprocessing a corpus using TreeTagger</a> and <a HREF="http://mwetoolkit.sourceforge.net/PHITE.php?sitesig=MWE&page=MWE_005_Preprocessing_a_corpus_using_Rasp">Preprocessing a corpus using Rasp</a> .</p>

<p><strong>Tip:</strong> create a working folder somewhere in your computer to place the corpus, pattenrns and candidates XML files. Please do not forget that the MWE toolkit expects a <tt>dtd</tt> folder in the working directory in order to validate the structure of the XML files. This means that, in practice, you should create a symbolic link to the <tt>dtd</tt> folder of the <tt>mwetoolkit</tt> in each of your working folders using the command <tt>ln -s /path/to/mwetoolkit/dtd</tt> when in this folder.</p>

<h3>An example</h3>

<p>The toolkit comes with example files for a toy experiment in the directory <tt>toy/genia</tt>:</p>
<ul>
	<li><tt>corpus.xml</tt> - A small subset of the Genia corpus.</li>
	<li><tt>patterns.xml</tt> - A set of patterns for matching noun compounds.</li>
	<li><tt>reference.xml</tt> - A MWE reference (gold standard) for comparing the results of the candidate extraction against.</li>
</ul>

<p>This directory also contains a script, <tt>testAll.sh</tt>, which runs a number of scripts on the example files. For each script run, it displays the action performed and the full command line used to run the script. It creates an <tt>output</tt> directory where it places the output files of each command.</p>

<p>Let's analyse each command that is run by <tt>testAll.sh</tt>. First, it runs <tt>index.py</tt> to generate an index for the corpus. This index contains suffix arrays for each word attribute in the corpus (lemma, surface form, part-of-speech, syntax annotation), which are used to search for and count the occurrences of an n-gram in the corpus. The full command executed is <tt>index.py -v -i index/corpus corpus.xml</tt>. The option <tt>-i <em>index/corpus</em></tt> tells the script to use <tt><em>index/corpus</em></tt> as the prefix pathname for all index files (the <tt>index</tt> folder must exist). The <tt>-v</tt> option tells it to run in verbose mode (this is valid for all scripts).</p>

<p>After generating the index for the Genia fragment, it performs a candidate extraction by running <tt>candidates.py -p patterns.xml -i index/corpus &gt; candidates.xml</tt>. This invokes the candidate extraction script, telling it to use the patterns described in the file <tt>patterns.xml</tt>, and to use the corpus contained in the index files whose prefix is <tt>corpus</tt> (this is the same name given to the <tt>index.py</tt> script). Instead of using a patterns file, you could specify the <tt>-n <em>min:max</em></tt> option to extract all ngrams with size between <em>min</em> and <em>max</em>.</p>

<p>Next, it runs the command <tt>candidates.py -p patterns.xml corpus.xml &gt;candidates-from-xml.xml</tt>. This performs the same extraction as the previous command, but reads the corpus from the XML file instead of the index (note the absence of the <tt>-i</tt> option). The results are the same; the only diference is that extracting from the index is slightly faster, and extracting from the XML file consumes less memory. In the next pass, the script checks whether the output of both extractions are indeed equal (they must be).

<p>Once candidates have been extracted, the frequencies of the individual words in each candidates are computed with the command <tt>counter.py -i index/corpus candidates.xml &gt; candidates-counted.xml</tt>. These counts are used by other scripts to compute statistics on the candidates. Word frequency cannot be computed directly from the XML file (it is done through binary search on the index). Instead of a corpus, you can count estimated word frequencies from the Web, using either the Yahoo (option <tt>-y</tt> - DEPRECATED) or Google (option <tt>-w</tt>) search engine. You can also count word frequencies from an indexed corpus different from the one used for the extraction.</p>

<p>After word frequencies have been counted, association measures are calculated with the command <tt>feat_association.py -m mle:pmi:ll:t:dice candidates-counted.xml >candidates-featureful.xml</tt>. The <tt>-m <em>measures</em></tt> option is a colon-separated list specifying which measures are to be computed: Maximum Likelihood Estimator (<tt>mle</tt>), Pointwise Mutual Information (<tt>pmi</tt>), Student's t test score (<tt>t</tt>), Dice's Coefficient (<tt>dice</tt>), and Log-likelihood (<tt>ll</tt>, for bigrams only).</p>

<p>The association measures can be used in several ways. Here, we simply chose an association measure that we consider good, the t score, and sort the candidates according to this score, with the command <tt>sort.py -f t_corpus candidates-featureful.xml &gt; candidates-sorted.xml</tt>. The next script then works as Linux <tt>head</tt> command, cropping the sorted file and keeping only candidates with higher t score values. Finally, we compare the resulting candidates with a reference list containing some expressions that are already in a dictionary for the Genia biomedical domain. This is quite standard in MWE extraction, even though it only gives you an underestimation of the quality of the candidates as dictionaries are not complete. The command used in the evaluation is <tt>eval_automatic.py -r reference.xml -g candidates-crop.xml &gt; eval.xml 2&gt; eval-stats.txt</tt>. The <tt>-g</tt> option tells the script to ignore parts of speech while the <tt>-r</tt> option indicates the file containing the reference gold standard in XML format. The final figures of precision and recall is in file <tt>eval-stats.txt</tt>. Remember that this is only a toy experiment and that with such a small corpus, the association measures cannot be trusted</p>

<p>For more advanced options, you can call the scripts using the <tt>--help</tt> option. This will print a message telling what the script does, what are the mandatory arguments and optional parameters. If you still have questions, write to our gmail addres, username mwetoolkit, and we'll be happy to help!</p>
-->

