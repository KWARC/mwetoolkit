<h2>Getting started</h2>

<h3>Tutorial</h3>

<p>You can download and follow the instructions on the slides of <a href="downloads/mwetk-tutorial-files.zip">the mwetoolkit tutorial</a> (last updated for WG2 Parseme meeting in March 20, 2015)</p>

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

<!--<p>Next, it runs the command <tt>candidates.py -p patterns.xml corpus.xml &gt;candidates-from-xml.xml</tt>. This performs the same extraction as the previous command, but reads the corpus from the XML file instead of the index (note the absence of the <tt>-i</tt> option). The results are the same; the only diference is that extracting from the index is slightly faster, and extracting from the XML file consumes less memory. In the next pass, the script checks whether the output of both extractions are indeed equal (they must be).-->

<p>Once candidates have been extracted, the frequencies of the individual words in each candidates are computed with the command <tt>counter.py -i index/corpus candidates.xml &gt; candidates-counted.xml</tt>. These counts are used by other scripts to compute statistics on the candidates. Word frequency cannot be computed directly from the XML file (it is done through binary search on the index). Instead of a corpus, you can count estimated word frequencies from the Web, using either the Yahoo (option <tt>-y</tt> - DEPRECATED) or Google (option <tt>-w</tt>) search engine. You can also count word frequencies from an indexed corpus different from the one used for the extraction.</p>

<p>After word frequencies have been counted, association measures are calculated with the command <tt>feat_association.py -m mle:pmi:ll:t:dice candidates-counted.xml >candidates-featureful.xml</tt>. The <tt>-m <em>measures</em></tt> option is a colon-separated list specifying which measures are to be computed: Maximum Likelihood Estimator (<tt>mle</tt>), Pointwise Mutual Information (<tt>pmi</tt>), Student's t test score (<tt>t</tt>), Dice's Coefficient (<tt>dice</tt>), and Log-likelihood (<tt>ll</tt>, for bigrams only).</p>

<p>The association measures can be used in several ways. Here, we simply chose an association measure that we consider good, the t score, and sort the candidates according to this score, with the command <tt>sort.py -f t_corpus candidates-featureful.xml &gt; candidates-sorted.xml</tt>. The next script then works as Linux <tt>head</tt> command, cropping the sorted file and keeping only candidates with higher t score values. Finally, we compare the resulting candidates with a reference list containing some expressions that are already in a dictionary for the Genia biomedical domain. This is quite standard in MWE extraction, even though it only gives you an underestimation of the quality of the candidates as dictionaries are not complete. The command used in the evaluation is <tt>eval_automatic.py -r reference.xml -g candidates-crop.xml &gt; eval.xml 2&gt; eval-stats.txt</tt>. The <tt>-g</tt> option tells the script to ignore parts of speech while the <tt>-r</tt> option indicates the file containing the reference gold standard in XML format. The final figures of precision and recall is in file <tt>eval-stats.txt</tt>. Remember that this is only a toy experiment and that with such a small corpus, the association measures cannot be trusted</p>

<p>For more advanced options, you can call the scripts using the <tt>--help</tt> option. This will print a message telling what the script does, what are the mandatory arguments and optional parameters. If you still have questions, write to our gmail addres, username mwetoolkit, and we'll be happy to help!</p>


