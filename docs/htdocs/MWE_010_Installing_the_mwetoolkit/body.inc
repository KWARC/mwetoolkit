<h2>Installing the <code>mwetoolkit</code></h2>

<h3>1. Checking the requirements</h3>

<p>Before following the instructions below, please check that you have installed all the requirements according to your Operating System:</p>
<ul>
<li><a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit&subpage=MWE_0011_Linux">Linux</a></li>
<li><a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit&subpage=MWE_0012_Mac_OS">Mac OS</a></li>
<li><a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit&subpage=MWE_0013_Windows">Windows</a></li>
</ul>

<p>Once the requirements are installed, choose one installation method, <a href="#step2">from SVN</a> or <a href="#step2b">from release</a>, and follow the instructions below. As the code evolves fast and releases are not that frequent, we HIGHLY recommend you to use the SVN version.</p>

<h3 id="step2">2. Downloading from the SVN repository (RECOMMENDED)</h3>

<p>Open a command line terminal in Linux, Mac OS or Windows through Cygwin. To download the latest <code>mwetoolkit</code> version, just get it from our Sourceforge subversion repository using the following command:</p>

<code>svn co svn://svn.code.sf.net/p/mwetoolkit/code/ mwetoolkit</code>

<p>This will take some time to download all files. SVN is a version control system, meaning you can upgrade to the latest development version of the mwetoolkit at any time simply by running <code>svn up</code> in the mwetoolkit folder. When the download is complete, jump to <a href="#step3">step 3: installation</a></p>

<p><em>WARNING</em>: The sourceforge repository was migrated on Mar 24, 2013. Any checkout done before this date will be obsolete and no more commits will be made to the old repository: <br/><code>https://mwetoolkit.svn.sourceforge.net/svnroot/mwetoolkit</code><br/> Please, erase your mwetoolkit folder and run the checkout command above to obtain an up-to-date version that includes the latest developments and bug fixes.</p>

<h3 id="step2b">2b. Downloading from a release file</h3>

<p>Alternatively, the toolkit is also availaible as a (more or less) stable release at <a href="https://sourceforge.net/projects/mwetoolkit/files/latest/download">the mwetoolkit files page</a>. However, as the code evolves fast, we HIGHLY recommend you to use the SVN version instead.</p>

<p>You can download and unzip the toolkit using a graphical interface, or typing the commands below in the command line:</p>

<pre>wget -O mwetoolkit.zip \
    https://sourceforge.net/projects/mwetoolkit/files/latest/download 
unzip mwetoolkit.zip</pre>

<h3 id="step3">3. Installing the toolkit</h3>

<p>Navigate to the main folder and compile the C libraries used by the toolkit. You can use the commands below:</p>

<pre>cd mwetoolkit
make
cd ..</pre>

<p>If you used the "release" download method, you need to append the version number to the first command, e.g. <code>cd mwetoolkit_0.6</code>. Do not worry if there are warning messages, they are harmless. However, if there are ERROR messages, send us an email.</p>

<p>If you do not run this command, or if the command fails to compile the libraries, the toolkit will still work. However, it will use a Python version of the indexing and counting programs (slower and possibly obsolete). This may be OK for small corpora. </p>

<h3 id="step4">4. Testing your installation</h3>

<p>The <code>test</code> folder contains regression tests for most scripts. Navigate to this folder and then call the script <code>testAll.sh</code>:</p>

<pre>cd test
./testAll.sh
cd ..</pre>

<p>Should one of the tests fail, please send a copy of the output and a brief description of your configurations (operating system, version, machine) to our gmail, our username is mwetoolkit. In some architectures (Mac OS), the test appears to fail because of floating point rounding differences in the last digits. This can be checked in the test log files and safely ignored.</p>

<p><strong>Failed tests do not prevent you from using the mwetoolkit normally :-)</strong></p>



