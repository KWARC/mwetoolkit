<h2>File type overview</h2>

<p>
The <code>mwetoolkit</code> does not deal with a specific parser/tagger format
&mdash; rather, it can seamlessly read data from many different file types, and
provides several tools to convert from external formats (such as "TreeTagger",
"RASP", "Palavras", etc) to one of the accepted input formats.
If your data is already encoded in a supported filetype format (e.g. "CONLL"),
you can use it directly as input to <code>mwetoolkit</code> scripts.
</p>

<p>
With the exception of the &quot;<code>BinaryIndex</code>&quot; format,
all other input/output formats accepted by the toolkit are represented
as a single file (possibly streaming from <code>stdin</code> or to
<code>stdout</code>), and will be automatically
decompressed<sup><a href="#fn1" id="ref1">1</a></sup> if necessary.
</p>
<!-- we also support Bz2, but only after python 3.3+... -->

<p>
Any given input/output to the <code>mwetoolkit</code> must belong to exactly
one of the following "categories":
</p>

 <ul>
  <li>Category <code>candidates</code>: A list of MWE candidates.</li>
  <li>Category <code>corpus</code>: A list of sentences (sequences of words, possibly annotated somehow).</li>
  <li>Category <code>dict</code>: A list of MWE candidates to be used as part of a gold standard.</li>
  <li>Category <code>patterns</code>: A list of token-based patterns, to be used in MWE identification.</li>
</ul>

<p>
For example, a file with filetype &quot;<code>XML</code>&quot; and category &quot;<code>candidates</code>&quot; can store only a list of
MWE candidates according to the <code>mwetoolkit</code>-defined XML filetype
format, and nothing else.
Note that some filetype+category combinations may not be supported &mdash; e.g. the
&quot;<code>PlainCandidates</code>&quot; filetype can only represent MWE candidates (that is, one cannot
have a corpus or a list of patterns using with this filetype).
</p>

<p>
The main menu to the left contains some links to the detailed description
of each specific file type.
You can also have a look at <a
href="http://sourceforge.net/p/mwetoolkit/code/HEAD/tree/test/filetype_samples">sample
files</a>.
</p>



<h2>Escaping characters</h2>
All file types supported by the <code>mwetoolkit</code> require that you escape
potentially problematic input characters before feeding your input to the
toolkit. For example, when you have a tab-delimited "CONLL" input with a tab
character <em>that is part of an entry</em>, you must escape it as
"${tab}".  Also, due to the choice of "$" as the escaping character, you should
escape the occurrences of "$" itself as "${dollar}".




<h2>Code comments</h2>

All file types supported by the <code>mwetoolkit</code> allow comments
that will be ignored by the underlying algorithm and simply passed on unchanged output.

In most text-based formats (e.g. "CONLL", "PlainCandidates"),
you can add a comment by prefixing any line with the special character "#".
In this case, the "#" character will have to be escaped when appearing on the
input, and will be automatically escaped by the <code>mwetoolkit</code> when
generating output.

In the XML-based filetype formats, you can add a comment using standard
XML comment format: "<code>&lt;!-- comment --&gt;</code>".


<h2>MWETOOLKIT directives</h2>

The <code>mwetoolkit</code> supports code directives, which instruct the
toolkit with extra information not present in the underlying filetype format.
For example, you can add the directive below as a comment in the first line of
a "CONLL" file to explicitly indicate to the <code>mwetoolkit</code> that your
file has "CONLL" filetype:

<blockquote>
<code>
# MWETOOLKIT: filetype="CONLL" 
</code>
</blockquote>

If such a comment is absent, automatic file detection will be attempted by the
<code>mwetoolkit</code>, but not all file formats can be detected, and the heuristics
may fail in some corner cases.  If you want to explicitly specify the filetype from
command-line, some <code>mwetoolkit</code> scripts will allow a syntax such as
"--from=CONLL" or "--to=CONLL".  Additionally, remember that you can always
convert to XML and take it from there.



<h2>Syntactic information in corpora</h2>

To conform with internal representation, dependency syntax has a special
format in the <code>mwetoolkit</code>:

<blockquote>
<code>
synrel1:synhead1,synrel2:synhead2,...,synrelN:synheadN
</code>
</blockquote>

<p/>
The toolkit supports corpora with syntactic annotations: the <w> element can
contain a syn attribute, which contains a list of the syntactic dependencies of
the word in the sentence, in the format
<code>deptype1:wordnum1;deptype2:wordnum2;...deptypeN:wordnumN</code>,
where deptypeN is the type of the dependency, and wordnumN is the number of
the word that is the target of the dependency (first word is 1).

<p/>
For example, the entry

<blockquote>
<code>
&lt;w lemma="book" pos="N" syn="dobj:4" /&gt;
</code>
</blockquote>

in an "XML" corpus represents a noun, "book", which is the direct object of the
fourth word in the sentence.
(Again, the syntactic tag will vary depending on the convention used in the corpus).

This means that you should <em>manually</em> escape any occurrences
of ":" or "," in the synrel/deprel names if they appear in the parser tag-set.

<!-- Hmmmm this is literally true, but maybe escaping input is enough anyway:
Also note that the <code>mwetoolkit</code> will <em>not</em> escape them
automatically when generating output. -->
</p>


<h2>Fallback to XML format</h2>
<p>
The file type &quot;<code>XML</code>&quot; is the only format originally
accepted by the <code>mwetoolkit</code>, and is hence the most generic and
flexible one.  If you have any problem with other input filetypes, you can
always try to <code>transform.py</code> your file into &quot;<code>XML</code>&quot;
format and take it from there.
</p>


<hr />

<sup id="fn1">1. Supported formats are gzip, zip (with only 1 file inside) and
bzip2 (only if running python 3.3+). Tar is not supported, as it is an archive
format, and we deal with simple files only.
<a href="#ref1" title="Jump back to footnote 1 in the text.">↩</a></sup>
