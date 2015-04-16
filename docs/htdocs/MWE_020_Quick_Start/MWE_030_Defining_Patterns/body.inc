<h2>Defining patterns for extraction</h2>    

<p>The <tt>mwetoolkit</tt> extracts MWE candidates by matching each sentence in the corpus against a set of patterns specified by the user. These patterns are read from XML files. This document describes the format of such files.</p>

<p>The root element of the XML patterns file is <tt>&lt;patterns&gt;</tt>. Inside this element comes a list of patterns, introduced by the tag <tt>&lt;pat&gt;</tt>. The <tt>candidates.py</tt> script will try to match each sentence of the corpus against each pattern listed:</p>

<pre>
&lt;patterns&gt;
    &lt;pat&gt;...&lt;/pat&gt;
    &lt;pat&gt;...&lt;/pat&gt;
    ...
&lt;/patterns&gt;
</pre>


<h3>Literal matches</h3>

<p>The simplest kind of pattern is one that matches literal occurrences of one or more attributes in the corpus. This is done with the tag <tt>&lt;w attribute="value" .../&gt;</tt>. For example, to match an adjective followed by a noun, one could use the pattern:</P>
<pre>
&lt;pat&gt;
    &lt;w pos="A" /&gt;
    &lt;w pos="N" /&gt;
&lt;/pat&gt;
</pre> 

<p>It is possible, inside the attribute value, to add a star to match any sequence of characters, for instance, a trailing star like in <tt>&lt;w pos="V*" /&gt;</tt> represents a word which POS starts with the capital letter "V". This can be very useful, for instance, to match a verb in any form (VBG, VVG, VVD,...). You could also match all the words with a given suffix, for instance, all the regular verbs (ending in "-ed") in past tense: <tt>&lt;w pos="VVD" surface="*ed" /&gt;</tt></p>

<p><strong>Note:</strong> The actual part-of-speech tags depends on the convention used to tag the corpus, of course. Some tagging tools tag nouns with <tt>SUBST</tt> or <tt>NN</tt>, for instance.)</P>

<h3>Repetitions and optional elements</h3>

<p>It is possible to define regular-expression-like patterns, containing elements that can appear a variable number of times. This is done with the <tt>repeat</tt> attribute of the <tt>pat</tt> tag and with the <tt>either</tt> element. The <tt>repeat</tt> attribute specifies how many times a pattern can be repeated, for instance:</p> 
<ul>
<li><tt>repeat="?"</tt>: the pattern may appear 0 or 1 times (in other words, it is optional, as it may or may not occur)</li>
<li> <tt>repeat="*"</tt>: the pattern may appear from 0 to any number of times</li>
<li><tt>repeat="+"</tt>: similar to above, except that the pattern must appear at least 1 time </li>
<li><li><tt>repeat="{m,n}"</tt>: the pattern may appear from <em>m</em> to <em>n</em> times (with m &leq; n). If you omit the first (or second) boundary, it defines an upper (or lower) bound on the number of occurrences.</li>
</ul>

<p>Note that <tt>pat</tt> elements can be nested. More advanced repetition operators are also possible, like the non-greedy versions that match a minimal sequence. Since the <tt>mwetookit</tt> is implemented using Python, you can check the <a href="http://docs.python.org/2/library/re.html">Python regular expression library</a> documentation.</p>

<p>The <tt>either</tt> element represents an alternative match, that is, the sequence will return a positive match when either one of the child elements are matched. Here are some examples of how repetition and alternative can be combined in order to define very generic patterns:</p>

<pre>
&lt;patterns&gt;
    &lt;!-- Pattern for matching a simple noun phrase. --&gt;
    &lt;pat&gt;
        &lt;pat repeat="?"&gt;&lt;w pos="Det" /&gt;&lt;/pat&gt;  &lt;!-- an optional determiner (appearing 0 or 1 times) --&gt;
        &lt;pat repeat="*"&gt;&lt;w pos="A" /&gt;&lt;/pat&gt;    &lt;!-- any number (including zero) of adjectives --&gt;
        &lt;pat repeat="+"&gt;&lt;w pos="N" /&gt;&lt;/pat&gt;    &lt;!-- one or more nouns --&gt;
    &lt;/pat&gt;

    &lt;pat&gt;
        &lt;pat repeat="{3,5}"&gt;&lt;w pos="A" /&gt;&lt;/pat&gt;    &lt;!-- 3 to 5 adjectives --&gt;
        &lt;w pos="N" lemma="dog" /&gt;                  &lt;!-- followed by the noun "dog" --&gt;
    &lt;/pat&gt;
    
    &lt;!-- A sequence of nouns or adjectives followed by a final noun --&gt;
    &lt;pat&gt;
        &lt;pat repeat="*"&gt;
        &lt;either&gt;
            &lt;pat&gt;
                &lt;w pos="N"/&gt;
            &lt;/pat&gt;
            &lt;pat&gt;
                &lt;w pos="A"/&gt;
            &lt;/pat&gt;
        &lt;/either&gt;
        &lt;/pat&gt;
        &lt;w pos="N"/&gt;
    &lt;/pat&gt;
&lt;/patterns&gt;
</pre>    

<h3>Negation</h3>

<p>With the <tt>neg</tt> element, you can match words that do NOT use a given
pattern. For instance, if you want to match any word that is not a verb, you
can use this pattern:</p>

<pre>
&lt;w&gt; &lt;neg pos="V"&gt; &lt;/w&gt;
</pre>    

<p>You can have as many &lt;neg&gt; tags as you want, and each tag is able to
negate several word attributes at a time. For instance, this pattern matches any
word that has neither surface "is", nor lemma "be", nor part-of-speech "V".</p>
<pre>
&lt;w&gt; &lt;neg surface="is"&gt; &lt;neg lemma="be" neg pos="V"&gt; &lt;/w&gt;
</pre>
<p>Multiple negations are allowed for the same word attribute, as long as each
negation appears in a different &lt;neg&gt; element. For example, the following
pattern could be used to match any occurrence of "smart" that is neither a verb
nor a noun:</p>
<pre>
&lt;w lemma="smart"&gt; &lt;neg pos="V"&gt; &lt;neg pos="N"&gt; &lt;/w&gt;
</pre>

<p>Negation is currently only supported at word level.  You cannot directly
negate a sequence, repetition or alternative pattern, only attributes of
individual words.  A workaround in this case could be negating attributes under
the <tt>either</tt> tag. For example, in order to match 2 words while
forbidding specifically the sequence "of the", one could use the pattern:</p>
<pre>
&lt;either&gt;
    &lt;pat&gt;
       &lt;w&gt;&lt;neg lemma="of"&gt;&lt;/w&gt;
       &lt;w/&gt;
    &lt;/pat&gt;
    &lt;pat&gt;
       &lt;w/&gt;
       &lt;w&gt;&lt;neg lemma="the"&gt;&lt;/w&gt;
    &lt;/pat&gt;
&lt;/either&gt;
</pre>

<h3>Ignoring parts of the match</h3>

<p>You can discard parts of a match by specifying an <tt>ignore</tt> attribute to the <tt>&lt;pat&gt;</tt> element:</p>
<pre>
&lt;pat&gt;
    &lt;!-- Match a determiner, followed by any number of adjectives, followed by a noun.
         The adjectives are discarded from the match. --&gt;
    &lt;w pos="Det" /&gt;
    &lt;pat repeat="*" ignore="true"&gt;&lt;w pos="A" /&gt;&lt;/pat&gt;
    &lt;w pos="N" /&gt;
&lt;/pat&gt;
</pre>

<p><strong>ATTENTION</strong> : When using this option, the script <tt>counter.py</tt> does not output the appropriate counts anymore, since it looks up the index for <em>contiguous</em> occurrences of the candidate. In order to workaround this problem, you should use <tt>-f</tt> option of <tt>candidates.py</tt> in order to output the number of times the pattern was matched (sum of occurrences), and subsequently pass option <tt>-J</tt> to <tt>counter.py</tt> in order to output only word frequencies and not the sequence frequency.</p>


<h3>Backpatterns</h3>

<p>It is possible to create patterns with backreferences, e.g., you can match a word that has the same lemma as a previously matched word. To do this, you assign an <tt>id</tt> to the first word, and use <tt>back:id.attribute</tt> as the value of an attribute in a subsequent word:</p>

<pre>
&lt;pat&gt;
    &lt;!-- Match N1-prep-N1 compounds (e.g., step by step, day after day) --&gt;
    &lt;w pos="N" id="n1" /&gt;                &lt;!-- Match a noun, labeled n1 --&gt;
    &lt;w pos="Prep" /&gt;                     &lt;!-- Match a preposition --&gt;
    &lt;w pos="N" lemma="back:n1.lemma" /&gt;  &lt;!-- Match a noun whose lemma is the same as the lemma of n1 --&gt;
&lt;/pat&gt;
</pre>    

<p>Previous versions of the toolkit used <tt>&lt;backw lemma="n1" /&gt;</tt> instead of <tt>&lt;w lemma="back:n1.lemma" /&gt;</tt>. There is no way of specifying both a literal attribute and a backreference with the old syntax.</p>


<h3>Syntactic patterns</h3>
<p>The toolkit supports corpora with syntactic annotations: the <tt>&lt;w&gt;</tt> element can contain a <tt>syn</tt> attribute, which contains a list of the syntactic dependencies of the word in the sentence, in the format <tt>deptype1:wordnum1;deptype2:wordnum2;...</tt>, where <tt>deptype<I>n</I></tt> is the type of the dependency, and <tt>wordnum<I>n</I></tt> is the number of the word that is the target of the dependency (first word is <tt>1</tt>). For example, <tt>&lt;w lemma="book" pos="N" syn="dobj:4" /&gt;</tt> in the corpus represents a noun, <tt>book</tt>, which is the direct object of the fourth word in the sentence. (Again, the syntactic tag will vary depending on the convention used in the corpus.)</p>

<p>You can specify a pattern with syntactic dependencies with the attribute <tt>syndep</tt> in the <tt>&lt;w&gt;</tt> element of the patterns file. First you assign an id to a word, and then you refer to it with the syntax <tt>&lt;w syndep="deptype:id"&gt;</tt>. This is so that the pattern is not dependent on the actual word numbers. For example:</p>

<pre>
&lt;!-- Match a verb and its direct object, with possible irrelevant intervening material. --&gt;
&lt;pat&gt;
    &lt;w pos="V" id="v1"/&gt;
    &lt;pat repeat="*" ignore="true"&gt;&lt;w/&gt;&lt;/pat&gt;
    &lt;w pos="N" syndep="dobj:v1" /&gt;
&lt;/pat&gt;
</pre>    

<p>Both "backward" and "forward" syntactic dependencies are supported. That is, the word on which the <tt>syndep</tt> attribute depends may occur before or after the current word. However, if you want to acquire both back and forth dependencies simultaneously, you must define both in an <tt>either</tt> element, e.g. to extract adjectives that modify nouns, independently of the position of the noun relative to the adjective, like <em>bella casa</em> and <em>casa bella</em> in Spanish.</p>
