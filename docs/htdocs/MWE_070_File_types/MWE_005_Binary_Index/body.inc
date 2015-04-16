<h2>BinaryIndex file type</h2>

<!-- Short description -->
<p>
A group of binary files that represents a corpus based on the concept of suffix
arrays.  This format is very efficient when looking up text in corpora (see
e.g. <tt>counter.py</tt>), where each lookup is performed in O(log n) time.
</p>

<p>
When used as input, you must specify the path to the <code>.info</code>
file and have all other files in the same directory.  This filetype format
cannot be read directly from stdin.
</p>



<h3>Characteristics</h3>

<table border="1">
<tr><td><strong>String name<sup><a href="#fn1" id="ref1">1</a></sup></strong></td><td>"BinaryIndex"</td></tr>
<tr><td><strong>Categories</strong></td><td>"corpus" (input only; output with index.py)</td></tr>
<tr><td><strong>Encoding</strong></td><td>Binary + UTF-8 textual</td></tr>
<tr><td><strong>Source</strong></td><td>&mdash;</td></tr>
<tr><td><strong>Automatic detection</strong></td><td>Yes (by seeing a <code>corpus_size</code> entry)</td></tr>
</table>



<h3>Details</h3>

<p>The "BinaryIndex" file type is composed of a group of files
with same basename and different extensions, each one storing
some information about the original corpus.</p>

<ul>
  <li>File BASENAME.info: Stores the corpus size and name.</li>
  <li>File BASENAME.ATTR.symbols: vocabulary file, associates an integer to each word type.</li>
  <li>File BASENAME.ATTR.corpus: corpus file containing the words in order of appeareance, using integer identifiers</li>
  <li>File BASENAME.ATTR.suffix: suffix array file, containing the corpus positions of sorted suffixes</li>
</ul>

<p>Files that have an ATTRibute in their name will store information about that
attribute (lemma, surface, POS...) only. Some files may have fused information, 
e.g. storing information about <tt>lemma+pos</tt>. They can be created by 
<tt>index.py</tt> or on the fly by <tt>counter.py</tt>, if needed.</p>

<p>The data structure used to store the corpus is a <a href="http://en.wikipedia.org/wiki/Suffix_array" target="_blank">suffix array</a>.
It stores the position of each corpus suffix, sorted in lexicographic order. When
looking for an n-gram, we perform binary search (O(log(n)) to find the first and
last position of the n-gram in the suffix array. The difference of last and first
positions is the number of occurrences of the n-gram in the corpus.
</p>

<img height="250px" width="auto" src="images/suffixarray.png" alt="Example of suffix array"/>

<h3>Escape table</h3>

No escaping is performed.


<h3>Code comments</h3>

<p>Comments are currently not supported.</p>


<h3>Example</h3>

<p>You can have a look at a sample <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype-samples/corpus.BinaryIndex">corpus directory</a>
file.</p>

<hr/>

<sup id="fn1">1. Case-sensitive string to be used with script options such as <tt>--from</tt>.<a href="#ref1" title="Jump back to footnote 1 in the text.">↩</a></sup>
