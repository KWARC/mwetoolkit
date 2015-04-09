<h2>XML candidates</h2>

<!-- Short description -->
<p>A list of MWE candidates represented in XML.</p>

<h3>Characteristics</h3>

<p>See the generic <a href="PHITE.php?sitesig=MWE&page=MWE_060_File_types">XML description</a>.</p>


<h3>Details</h3>

<p>The root element of a candidates XML file is called <tt>&lt;candidates&gt;</tt>. 
A candidates list file is a list containing one optional <tt>&lt;meta&gt;</tt> element,
followed by a list of candidates delimited by tags <tt>&lt;cand&gt;</tt> and 
<tt>&lt;/cand&gt;</tt>. 

<h4>Meta element</h4>

<p>Meta-data describing the candidates. Elements can be of two types:</p>
<ul>
  <li><tt>&gt;metafeat&lt;</tt>: SOON</li>
  <li><tt>&gt;metatpclass&lt;</tt>: SOON</li>
  <li><tt>&gt;corpussize&lt;</tt>: SOON</li>  
</ul>

<h4>Cand element</h4>

Each candidate must have a unique numerical ID, indicated as 
attribute <tt>candid="..."</tt>. A candidate contains several subparts:

<ul>
<li><tt>&lt;ngram&gt;</tt>: The main candidate entry is a list of words with lemmas 
and POS. In some cases, lemmas are replaced by surface forms (option <tt>-s</tt> of 
<tt>candidates.py</tt>) and POS may be omitted (option <tt>-g</tt> of 
<tt>candidates.py</tt>)  Each word is an XML element <tt>&lt;w/&gt;</tt> with 3 
optional attributes (either lemma or surface must appear):
<ul>
<li><tt>surface</tt> : surface form, word as it occurs in running text.</li>
<li><tt>lemma</tt> : canonical word form, e.g. infinitive for verbs and singular for nouns</li>
<li><tt>pos</tt> : part of speech, that is, morphosyntactic categories like NOUN, ADVERB, etc.</li>
</ul> 
A word and the n-gram may have several <tt>&lt;freq/&gt;</tt> elements which correspond to counts in corpora. The <tt>&lt;freq/&gt;</tt> element has a <tt>name</tt>, corresponding to the corpus name, and a <tt>value</tt>, corresponding to the number of occurrences.
</li>
<li><tt>&lt;occurs&gt;</tt>: A list of n-grams containing only surface and POS information. Each n-gram is an inflected occurrence of the base entry. There may be frequency information attached to each occurrence.</li> 
<li><tt>&lt;features&gt;</tt>: Contains a list of <tt>&lt;feat&gt;</tt> and <tt>&lt;tpclass&gt;</tt> elements. Features are name-value pairs, as frequency information, containing the name and the value of the feature. TP classes are the same as features, but they are interpreted as the expected output, in the sense of machine learning. Both should be coherent with the metadata.</li>
</ul>
 
 <p>A candidate may contain other elements like <tt>&gt;bigrams&lt;</tt> and <tt>&gt;vars&lt;</tt>. These are not widely supported and can be ignored.</p>




<p>
Each word is implicitly numbered according to its position, starting at 1. The HEAD information in syn attribute uses this number to indicate the position of the head. REL names should not contain colons. An absent attribute should be ommited, an attribute value should never be empty. 
</p>

<p>An example of corpus file would have the following structure:</p>

<pre>
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE corpus SYSTEM "dtd/mwetoolkit-corpus.dtd"&gt;
&lt;corpus&gt;
&lt;s s_id="1"&gt;
  &lt;w surface="X" lemma="X" pos="X" syn="X:2" /&gt;
  ...
&lt;/s&gt;
...
&lt;/corpus&gt;
</pre>

<h3>Example</h3>

<p>You can have a look at a sample <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype-samples/candidates.xml">candidates</a>
file.</p>

<hr/>

