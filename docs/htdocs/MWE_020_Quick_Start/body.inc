<h2>Getting started</h2>

<p>To start using the mwetoolkit, you need first to <a href="">install it</a>. The toolkit currently works at the command line. If you are not familiar with it, you can simply follow the steps below and copy-paste the commands. This tutorial is based on the slides of <a href="downloads/mwetk-tutorial-files.zip">the mwetoolkit tutorial</a> (last updated for WG2 Parseme meeting in March 20, 2015). Each command is explained and you can try and adapt the options to your corpus, MWE patterns, and so on. In the scripts below, we use the variable${MWETKBIN} to indicate the path to your mwetoolkit <tt>bin</tt> folder. The commands are also available in the mwetoolkit itself in the form of a script in folder <tt>toy</tt>, called <tt>run-tutorial.sh</tt>.</p>

<h3>1. Introduction</h3>

<p>The mwetoolkit is composed of python scripts, so you do not need to do anything to compile it. As long as you have a python 2.6+ interpreter, it's fine. However, part of it is written in C for increased speed, so we recommend that you compile the C indexer before getting started. Therefore, simply run <tt>make</tt> in the root mwetoolkit folder.</p>

<p>For the next steps, remember that you can always run a script passing option <tt>-h</tt>, to obtain a detailed list of its functionalities, arguments and options. For example :</p>

<pre>${MWETKBIN}/index.py -h</pre>

<h3>2. Indexing the corpus</h3>

<p>In this tutorial, we use the TED English corpus, an excerpt from the <a href="https://wit3.fbk.eu/mt.php?release=2014-01" target="_blank">bilingual English-French TED talks</a>. The corpus was parsed using <a href="http://users.sussex.ac.uk/~johnca/rasp/" target="_blank">RASP</a> and then converted to <a href="?sitesig=MWE&page=MWE_070_File_types&subpage=MWE_010_CONLL">CONLL format</a>. This format contains one word per line, and one word information per column. Take a look at the file to see what it contains.</p>

<pre>zcat ted-en-sample.conll.gz | head</pre>

<p>You can uncompress the file so that it is easier to inspect it using command line tools or a text editor like nano, vim, gedit or emacs. Nonetheless, you can use <a href="?sitesig=MWE&page=MWE_070_File_types">compressed files directly</a> as input to the mwetoolkit.</p>

<pre>gunzip -c ted-en-sample.conll.gz &gt; ted-en-sample.conll</pre>

<p>Let us generate an index for fast corpus access. This is not required for most scripts, but since we want to count n-grams, we will need it (counter.py). Since our corpus contains around half a million words, this will take some time (30 secs to a couple of minutes, depending on your computer)</p>

<pre>mkdir -p index 
${MWETKBIN}/index.py -v -i index/ted ted-en-sample.conll 
</pre>

<p>If you look at the <tt>index</tt> folder, you will notice the creation of many files prefixed by <tt>ted</tt>. This is because you specified that the index should be created with prefix <tt>index/ted</tt> using <tt>-i</tt> option. We recommend always creating a folder and storing all index files in this folder.

<pre>ls index</pre>

<h3>3. Candidate extraction</h3>

<p>Once you have indexed the corpus, you are ready for candidate extraction. You  must first define the pattern you are interested in. For instance, we use the file <tt>pat_nn.xml</tt> which describes sequences of nouns and prepositional phrases that start with a noun. This corresponds roughly to noun phrases in English. You can look at the example pattern to get familiarised with the XML format  used to describe it. The online documentation on the <a href="?sitesig=MWE&page=MWE_070_File_types&subpage=MWE_060_XML">XML format</a> and on <a href="?sitesig=MWE&page=MWE_020_Quick_Start&subpage=MWE_030_Defining_Patterns">defining patterns</a> should also help.</p>

<pre>cat pat_nn.xml</pre>

<pre>
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE dict SYSTEM "dtd/mwetoolkit-patterns.dtd"&gt;
&lt;patterns&gt;
&lt;!-- Pattern that extract noun-noun compounds, optionally using preposition "of" --&gt;
	  &lt;pat&gt;
	      &lt;w pos="NN*"/&gt;
	      &lt;pat repeat="+"&gt;
	          &lt;pat repeat="?"&gt;
	              &lt;w lemma="of" pos="IO"/&gt;
	          &lt;/pat&gt;
	          &lt;w pos="NN*"/&gt;
        &lt;/pat&gt;
	  &lt;/pat&gt;
&lt;/patterns&gt;
&lt;/pre&gt;
</pre>

<p>Then, you can run the candidates.py script to extract from the indexed corpus. the candidates that match the pattern. It takes as argument the pattern file (<tt>-p</tt>), the corpus file format (<tt>--from</tt>) and the corpus file, which in our case  is the <tt>.info</tt> file corresponding to a <tt>BinaryIndex</tt>. Option <tt>-S</tt> will keep  information about the source sentences in which the candidates were found</p>

<pre>${MWETKBIN}/candidates.py -p pat_nn.xml -S -v --from=BinaryIndex index/ted.info &gt; cand.xml</pre>

<p>The resulting file is in XML format, each lemmatised candidate containing some  information about its occurrences and source sentences.</p>

<p>You can count how many candidates were extracted using the wc.py script</p>

<pre>${MWETKBIN}/wc.py cand.xml</pre>

<p>You can count the number of occurrences of each candidate, and also of each word contained in a candidate. Therefore, we run the counter.py script which internally uses the index to obtain n-gram counts very fast.</p>

<pre>${MWETKBIN}/counter.py -v -i index/ted.info cand.xml > cand-count.xml</pre>

<p>The resulting file is identical to the input XML, with added <freq> elements. You can count MWE candidates either in the source corpus, as we did here, or in other corpora (e.g. for contrastive methods of terminology extraction).</p>

<pre>head cand-count.xml | grep --color "&lt;freq"</pre>

<h3>4. Candidate filtering</h3>

<p>There are several available filtering tools included in the mwetoolkit. It is possible to filter using simple criteria such as frequency and n-gram length, using the filter.py script. Below, we show an example that filters out every  n-gram that occurred only once in the corpus. This is generally a good idea if we want to obtain reliable association measures for further filtering (see  below)</p>

<pre>${MWETKBIN}/filter.py -v -t ted:2 cand-count.xml > cand-count-f1.xml</pre>

<p>You can see that a large number of candidates was removed from the list,  because they only occurred once in the corpus</p>

<pre>${MWETKBIN}/wc.py cand-count-f1.xml</pre>

<p>It is probably more interesting to use lexical association scores, like pointwise mutual information and log-likelihood score, to filter out  candidates which are frequent only because, by pure chance, they are composed of frequent words. Therefore, let us first calculate the 5 standard  association measures of the mwetoolkit: <tt>mle</tt>, <tt>dice</tt>, <tt>pmi</tt>, <tt>t</tt> and <tt>ll</tt>, which stand for Maximum Likelihood (a.k.a. relative frequency), Dice's coefficient,  pointwise mutual information, Student's t score and log-likelihood score. The latter is only applicable for 2-word candidates, so it is normal that the  script will print a warning message, since some of our candidates are 3+-grams</p>

<pre>${MWETKBIN}/feat_association.py -v cand-count-f1.xml &gt; cand-feat.xml</pre>

<p>Now each candidate has a set of features which are real-valued association scores:</p>

<tt>
&lt;cand candid="1009"&gt;<br/>
&nbsp;&nbsp;     &lt;ngram&gt; &lt;w lemma="greenhouse" pos="NNL1" &gt; &lt;freq name="ted" value="21" /&gt; &lt;/w&gt;  &lt;w lemma="gas" pos="NN2" &gt; &lt;freq name="ted" value="10" /&gt; &lt;/w&gt;  &lt;freq name="ted" value="9" /&gt; &lt;/ngram&gt;<br/>
&nbsp;&nbsp;     &lt;occurs&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;     &lt;ngram&gt; &lt;w surface="greenhouse" lemma="greenhouse" pos="NNL1" /&gt;  &lt;w surface="gases" lemma="gas" pos="NN2" /&gt;  &lt;freq name="ted" value="9" /&gt; &lt;sources ids="2605:10,11;2877:5,6;13435:20,21;13509:21,22;20331:15,16;20331:35,36;20332:37,38;20336:8,9;26415:24,25"/&gt; &lt;/ngram&gt;<br/>
&nbsp;&nbsp;     &lt;/occurs&gt;<br/>
<span style="color:#F0F">&nbsp;&nbsp;     &lt;features&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;         &lt;feat name="mle_ted" value="1.65500805437e-05" /&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;         &lt;feat name="pmi_ted" value="14.5084093745" /&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;         &lt;feat name="t_ted" value="2.99987127739" /&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;         &lt;feat name="dice_ted" value="0.58064516129" /&gt;<br/>
&nbsp;&nbsp;&nbsp;&nbsp;         &lt;feat name="ll_ted" value="80.3358849639" /&gt;<br/>
&nbsp;&nbsp;     &lt;/features&gt;<br/></span>
&lt;/cand&gt; <br/>
</tt>

<p>We will use the value of one of these features to sort the candidates list in descending order using <tt>sort.py</tt> with <tt>-d</tt> option. The feature used in our example is <tt>t_ted</tt>, but you can test other association measures and see if the top-100 retrieved expressions seem more interesting. Remark that the mwetoolkit has scripts that are similar to common Linux commands like sort, head, tail, etc. Here, we use head.py to keep only the top 100 candidates sorted by t-score.</p>
 
<pre>python ${MWETKBIN}/sort.py -d -v -f t_ted cand-feat.xml | ${MWETKBIN}/head.py -v -n 100 &gt; cand-feat-ft.xml</pre>

<h3>5. Annotating a corpus</h3>

<p>Once we have obtained a reasonably clean list of MWE candidates, we can then project it back onto the original corpus. Note that this is actually different from applying an extraction pattern directly on the corpus, since we performed various filtering steps to obtain better MWE candidates. In the example below,  we "annotate" the original TED corpus with our filtered candidates using the source information present in the candidates themselves. This will take a time that is proportional to the number of sentences in the corpus.</p>

<pre>${MWETKBIN}/annotate_mwe.py -v --detector=Source -c cand-feat-ft.xml --to PlainCorpus ted-en-sample.conll &gt; ted-en-sample-mwe.txt</pre>

<p>The output is similar to the original corpus, but MWEs are single tokens  joined by underscore (this is how we represent MWEs in plain txt format), like in the excerpt below:</p>
                             
<tt>
In fact , the West has lost its <span style="color:#F0F">work_ethic</span> . <br/>
Who is got the <span style="color:#F0F">work_ethic</span> now ? <br/>
Because the <span style="color:#F0F">killer_apps</span> can be downloaded . <br/>
</tt>

<p>Like any other mwetoolkit script, it is possible to produce more friendly  output formats. For instance, the command below generates an <a href="?sitesig=MWE&page=MWE_070_File_types&subpage=MWE_025_Output:_HTML">HTML corpus file</a> (<tt>--to HTML</tt>) containing only sentences that contain MWEs (<tt>--filter-and-annot</tt>). Also remember that it is possible to project a candidates list or lexicon onto another, different corpus, using a <tt>ContiguousLemma</tt> detector. In our example, we use <tt>ContiguousLemma</tt> on the same extraction corpus, but we also allow for 1-word gaps (<tt>-g 1</tt>)</p>

<pre>${MWETKBIN}/annotate_mwe.py -v --detector=ContiguousLemma -g 1 -c cand-feat-ft.xml --to HTML --filter-and-annot ted-en-sample.conll &gt; ted-mwe.html</pre>

<p> This file can be opened by your favourite web browser, like Firefox, Chrome,  Safari or Explorer. It is quite easy to visualise POS and lemmas by hovering  words and seeing MWEs annotated in different colours. See, for instance, how sentence 1121 contains a nested MWE [World [Trade Center]], while sentence  1328 contains a gappy MWE "lot of [the] time". Not all of these MWEs are  interesting, since the list contains some noise due to 100% automatic candidate extraction and filtering.</p>

<h3>6. Evaluation</h3>

<p>One problem that often arises in automatic MWE discovery is to decide whether a given MWE candidate list contains interesting expressions. This work is  generally done by manually inspecting the list and selecting interesting  expressions. Therefore, it is better to use some more readable format, like CSV.</p>

<pre>${MWETKBIN}/transform.py --from XML --to CSV cand-feat-ft.xml &gt; cand-feat-ft.csv</pre>

<p>The output of <tt>transform.py</tt> can the be imported into your favourite spreadsheet editor (LibreOffice Calc, Microsoft Excel). Don't forget to set "TAB" as the  field separator and nothing as string delimiter. You can sort the columns  according to different association scores, and mark the interesting MWEs. The toolkit also provides a script called <tt>eval_automatic.py</tt>, which compares a  candidates list with a reference dictionary, calculating precision, recall and F1. It is also possible to calculate average precision of a given feature  using <tt>avg_precision.py</tt>.</p>

<p>Also, do not hesitate to test other patterns like the one in pat_open.xml, and the <a href="?sitesig=MWE&page=MWE_020_Quick_Start&subpage=MWE_030_Defining_Patterns">examples described on the website</a>.</p>





































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

