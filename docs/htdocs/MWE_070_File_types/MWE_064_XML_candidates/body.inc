<h2>XML candidates</h2>

<!-- Short description -->
<p>A list of MWE candidates represented in XML.</p>

<h3>Characteristics</h3>

<p>See the generic <a href="?sitesig=MWE&page=MWE_070_File_types&subpage=MWE_060_XML">XML description</a>.</p>


<h3>Details</h3>

<p>The root element of a candidates XML file is called <tt>&lt;candidates&gt;</tt>. 
A candidates list file is a list containing one optional <tt>&lt;meta&gt;</tt> element,
followed by a list of candidates delimited by tags <tt>&lt;cand&gt;</tt> and 
<tt>&lt;/cand&gt;</tt>. 

<h4>Meta element</h4>

<p>Contains a sequence of meta-data entries describing the candidates:
<ul>
  <li><tt>&lt;corpussize name="CorpusName" value="CorpusSize" /&gt;</tt>:
  Indicates the size of the corpus from which the candidates were obtained.
  More than one &lt;corpussize&gt; tag may be present if the candidates came
  from multiple corpora.

  <li><tt>&lt;metafeat name="FeatureName" type="FeatureType" /&gt;</tt>:
  Pre-declares the features that can be seen in the candidates below.
  The type can be "integer", "real", "string" or "{an,enumeration,of,values}".</li>

  <li><tt>&lt;metatpclass&gt;</tt>: Similar to <tt>&lt;metafeat&gt;</tt>, but represents
  the expected value of output features.</li>
</ul>


<h4>Cand elements</h4>

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
 
 <p>A candidate may contain other elements like <tt>&lt;bigrams&gt;</tt> and <tt>&lt;vars&gt;</tt>. These are not widely supported and can be ignored.</p>

<p>
Each word is implicitly numbered according to its position, starting at 1. The HEAD information in syn attribute uses this number to indicate the position of the head. REL names should not contain colons. An absent attribute should be ommited, an attribute value should never be empty. 
</p>



<h4>Overall structure</h4>

<p>A "candidates" file should have the following structure:</p>

<pre>
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE corpus SYSTEM "dtd/mwetoolkit-corpus.dtd"&gt;
&lt;candidates&gt;

&lt;meta&gt;
  &lt;corpussize name="corpus" value="2570000" /&gt;
  &lt;metafeat name="featA" type="real" /&gt;
  &lt;metafeat name="featB" type="{foo,bar,baz}" /&gt;
  ...
  &lt;metafeat name="featN" type="integer" /&gt;
&lt;/meta&gt;

&lt;cand candid="1"&gt;
  &lt;w surface="A" lemma="a" pos="Det" /&gt;
  &lt;w surface="multiword" lemma="multiword" pos="Adj" /&gt;
  &lt;w surface="expression" lemma="expression" pos="Noun" /&gt;
  &lt;occurs&gt;
    ...
  &lt;/occurs&gt;
  &lt;features&gt;
    &lt;feat name="featA" value="3.14" /&gt;
    &lt;feat name="featB" value="bar" /&gt;
    ...
  &lt;/features&gt;
  ...
&lt;/cand&gt;

&lt;cand candid="2"&gt;
  ...
&lt;/cand&gt;

...
&lt;/candidates&gt;
</pre>

<h3>Example</h3>

<p>You can have a look at a sample <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype-samples/candidates.xml">candidates</a>
file.</p>

<hr/>

