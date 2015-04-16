<h2>XML dict</h2>

<!-- Short description -->
<p>A list of MWEs in a reference gold standard.</p>


<h3>Characteristics</h3>

<p>See the generic <a href="?sitesig=MWE&page=MWE_070_File_types&subpage=MWE_060_XML">XML description</a>.</p>



<h3>Details</h3>

<p>The root element of a dict XML file is called <tt>&lt;dict&gt;</tt>. 
A dict file contains essentially a list of <tt>&lt;entry&gt;</tt> elements,
where each entry represents an n-gram.

<h4>Overall structure</h4>

<p>A "dict" file should have the following structure:</p>

<pre>
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE corpus SYSTEM "dtd/mwetoolkit-corpus.dtd"&gt;
&lt;dict&gt;

&lt;entry&gt;
  &lt;w surface="A" lemma="a" pos="Det" /&gt;
  &lt;w surface="multiword" lemma="multiword" pos="Adj" /&gt;
  &lt;w surface="expression" lemma="expression" pos="Noun" /&gt;
&lt;/entry&gt;

&lt;entry&gt;
  ...
&lt;/entry&gt;

...
&lt;/dict&gt;
</pre>


<h3>Example</h3>

<p>You can have a look at a sample <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype-samples/dict.xml">dict</a>
file.</p>

<hr/>

