<h2>For developers</h2>


<!--

    UML class diagrams: api.genmymodel.com
    Pretty sequence diagram: www.websequencediagrams.com

-->




<p>
This page describes the internals of the <tt>mwetoolkit</tt>.
If you just want to use the toolkit without implementing extra functionality,
you do not need to read this.
</p>



<h3>General description</h3>
<p>
The <tt>mwetoolkit</tt> is a collection of tools
that can be usually composed together through Unix pipes.
Most of the times, a tool will have the following usage syntax:

<pre>
    mwetoolkit/bin/toolname.py [OPTIONS] &lt;file-inputs&gt;
</pre>

The input will come from either <code>&lt;file-inputs&gt;</code> or, if no filenames are explicitly given, it will come from <code>stdin</code>. Output should be sent to <code>stdout</code>. Warnings and errors should be printed in <code>stderr</code>.
</p>

<p>
In order to simplify this architecture, the toolkit has a shared library that can be used by the python tools: <code>mwetoolkit/bin/lib</code>.
This library is basically divided between the <code>base</code> package, which defines the internal representation of things in the toolkit; and the <code>filetype</code> package, which converts between the toolkit's <a href="PHITE.php?sitesig=MWE&page=MWE_070_File_types">accepted filetypes</a> and the internal representation in memory.
</p>

<style type="text/css">
img.centered {
    display: block;
    margin-left: auto;
    margin-right: auto }
</style>



<h3>The <code>base</code> package</h3>
<p>
The main component inside the toolkit is the Word.
Currently, words are completely mutable (you can set its attributes directly).
</p>

<p>
FeatureSets are essentially python <tt>dict</tt>s, and may in the future be converted into dicts when the "features" are simple (as in word frequencies, which always have integer values that can be combined through sum).  Features are essentially a <tt>(key, value)</tt> tuple (and might actually be reimplemented as a <tt>namedtuple</tt> in the near future).
</p>

<img class="centered" src="images/mwet4devs_base1.jpg" alt="Class diagrams: Word and FeatureSet"/>


<p>
Ngrams, sentences and MWE candidates contain a list of words as their main attribute. An MWE occurrence is a mapping between a candidate and the internals of a sentence.
</p>
<img class="centered" src="images/mwet4devs_base2.jpg" alt="Class diagram: Ngram and subclasses"/>




<h3>The <code>filetype</code> package</h3>
<p>
The next figure is a rough diagram of the sequence of events that characterizes a tool in the <tt>mwetoolkit</tt> that takes a list of corpora as its input files. Notice how the parser delegates the handling of each <tt>Sentence</tt> object to a chain of <tt>InputHandler</tt>s, each of which will manipulate the object and pass it on to the next handler through <tt>handle_sentence</tt>.
</p>
<img class="centered" src="images/mwet4devs_parsing_corpus.png" alt="Diagram of messages being sent Parser->FirstInputHandler(->ChainedInputHandlers)->InputHandler: loop(before_file, handle_sentence, handle_sentence, ..., after_file), finish"/>


<p>
The execution always begins with <tt>filetype.parse</tt>, which receives a list of file objects, wraps them into <tt>InputFile</tt> instances and passes each one to the <tt>parse</tt> method of an instance of of <tt>AbstractParser</tt>. This parser then reads the input file and calls the callbacks in the <tt>FirstInputHandler</tt>.  In order to simplify this process for line-based filetypes, the <tt>AbstractTxtParser</tt> is also provided by the toolkit's filetype library.
</p>

<img class="centered" src="images/mwet4devs_parser.jpg" alt="Class diagram: AbstractParser and subclasses"/>


<p>
The last <tt>InputHandler</tt> in the chain is the one that is implemented by a given tool in the toolkit. It may just handle the input by itself (as the <tt>CounterHandler</tt> does in <tt>mwetoolkit/bin/wc.py</tt>), or may even delegate to a further <tt>InputHandler</tt> in the chain, which will usually be a subclass of <tt>AbstractPrinter</tt> (as <tt>HeadPrinterHandler</tt> does in <tt>mwetoolkit/bin/head.py</tt>).
</p>

<img class="centered" src="images/mwet4devs_inputhandler.jpg" alt="Class diagram: InputHandler and subclasses"/>


<p>
There are other internal parts of the toolkit that are still not completely stable. For example, the <tt>info</tt> dictionary that keeps being passed around is not very well formally defined. In the future, we should define a <tt>ContextInfo</tt> class and use that to carry around information about the parsing context.  (The reason it's currently a dictionary is because we initially had no idea what kind of information we would want to have, and the information was not even always available...)
</p>
