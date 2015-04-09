<h2>Preprocessing a corpus using Rasp</h2>

<p>This page explains how to use the Parser, <a href="http://www.informatics.susx.ac.uk/research/groups/nlp/rasp/">Rasp</a>, to obtain a XML corpus from a plain textual corpus.</p>

<h3>Installing Rasp</h3>

<p>Rasp doesn't need to be installed. Just download it from <a href="http://ilexir.co.uk/applications/rasp/download/">Rasp Download</a>. However, it assumes that you have downloaded it to your home directory, so do it and save yourself some headache. The current version of RASP, RASP3, has a bug concerning tokenisation. Therefore, the script for format conversion only works for RASP2. Please contact us if you want to use RASP3 instead.</p>

<h3>Converting Rasp's output to XML</h3>

<p>After downloading Rasp, you can run it by running <tt>path-to-rasp/scripts/rasp.sh</tt> < <tt><I>input-file</I></tt>. Rasp will read the corpus from <tt><I>input-file</I></tt> and print for each sentence it's words, together with surface form, lemma and part of speech. Then will print the grammatical relations, which can be viewed as a  kind of dependency tree, from where will be extracted the syntatic property, in separate lines to standard output.</p>

<p><tt>mwetoolkit</tt> comes with a script, <tt>rasp2mwe.py</tt>, which takes Rasp's output and converts it to XML. All you have to do is feed Rasp's output to it:</p>

<pre>path-to-rasp/scripts/rasp.sh < corpus.txt | </pre>
<pre>python path-to-mwetoolkit/bin/rasp2mwe.py &gt;corpus.xml</pre>

<p>From there on you can process the XML corpus using <tt>mwetoolkit</tt>'s tools, such as is shown in the <a href="http://mwetoolkit.sourceforge.net/PHITE.php?sitesig=MWE&page=MWE_002_Quick_Start">Quick Start</a> page.</p>
