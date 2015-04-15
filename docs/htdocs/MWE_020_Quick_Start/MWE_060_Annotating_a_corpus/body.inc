<h2>Annotating a corpus</h2>

<p>The mwetoolkit now supports adding MWE annotation on running text, as
explained below.</p>


<p>Both the input and the output format can be in any of the formats
supported by the toolkit under the "corpus" category.  In the example below,
we will learn how to take a corpus such as the
<a href="https://wit3.fbk.eu/" target="_blank">TED English corpus</a>, annotate
its phrasal verbs and generate an
<a href="TED-English-sample.html">HTML output such as this one</a>, where
the annotation is represented in visible colors (other output formats will
represent the same annotation differently).</p>

<pre>
# Create a copy of an existing "patterns" file:
cp mwetoolkit-code/test/candidates/VerbParticle/patterns.xml ./my_patterns.xml

# Extract list of possible MWEs:
mwetoolkit-code/bin/candidates.py -p ./my_patterns.xml \
  mwetoolkit-code/test/inputs/ted500.xml &gt;./mwe_candidates.xml

# Annotate corpus with MWE list:
mwetoolkit-code/bin/annotate_mwe.py --filter-and-annot --to=HTML \
  -c ./mwe_candidates.xml mwetoolkit-code/test/inputs/ted500.xml &gt; ./output.html
</pre>

<p>
That's it! Now you can open the file "./output.html" in a browser to visualize
the annotated sentences in the corpus.
</p>


<p>
Now you can try other things, such as:
</p>


<ul>
  <li>Run annotate_mwe.py without the "--filter-and-annot" flag to see
  all sentences in the whole corpus.</li>

  <li>Generate a file in another output format: for example, generate
  an output in "PlainCorpus" format instead of "HTML". Look at the
  occurrences of the "_" (underscore) character in the output.</li>

  <li>Modify "./my_patterns.xml" and introduce your own patterns.
  The XML pattern syntax is described <a
  href="?sitesig=MWE&page=MWE_020_Quick_Start&subpage=MWE_030_Defining_Patterns">here</a>.
  </li>

  <li>Apply the modified patterns in another corpus of yours.</li>
</ul>
