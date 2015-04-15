<h2>Preprocessing a corpus using TreeTagger</h2>

<p align="justify">This page explains how to use the POS tagger, <a href="http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/">TreeTagger</a>, to obtain a XML corpus from a plain textual corpus.</p>

<h3>Installing TreeTagger</h3>

<p align="justify">To install TreeTagger, just follow the instructions in the "Download" section of <a href="http://www.ims.uni-stuttgart.de/projekte/corplex/TreeTagger/">TreeTagger's webpage</a>. In addition to TreeTagger itself, you will need to download parameter files for each language you wish to use the tagger with. We recommend that you add the path to TreeTagger to your PATH variable as suggested by the TreeTagger installation script, this will allow you to call it without using the full path.</p>

<h3>Converting TreeTagger's output to XML</h3>

<p align="justify">After installing TreeTagger, you can run it by running <tt>path-to-tree-tagger/cmd/tree-tagger-<I>language</I> <I>input-file</I></tt>, where <tt><I>language</I></tt> is the language of the input file. TreeTagger will read the corpus from <tt><I>input-file</I></tt> and print each word, together with its surface form and part of speech, as a separate line to standard output.</p>

<p align="justify">The <tt>mwetoolkit</tt> comes with a script,
<tt>from_tagger.sh</tt>, which takes TreeTagger's output and converts it to
XML (or any other output filetype supported by <code>mwetoolkit</code>, using
the option <tt>--to</tt>). All you have to do is feed TreeTagger's output to it:</p>

<pre>path-to-tree-tagger/cmd/tree-tagger-english corpus.txt | </pre>
<pre>python path-to-mwetoolkit/bin/from_treetagger.py -s SENT &gt;corpus.xml</pre>

<p align="justify"><b>Attention:</b> When working in a language other than
English, you must specify the appropriate POS-tag that works as a sentence delimiter, otherwise the result may look like a corpus with a single (very long) line.
For example, when working with Spanish, you will need to use "<tt>-s FS</tt>"
instead of "<tt>-s SENT</tt>".

<p align="justify">From there on you can process the XML corpus using <tt>mwetoolkit</tt>'s tools, such as is shown in the <a href="http://mwetoolkit.sourceforge.net/PHITE.php?sitesig=MWE&page=MWE_002_Quick_Start">Quick Start</a> page.</p>
