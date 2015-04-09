<h2><code>mwetoolkit</code> Installation: Linux Requirements</h2>

<p>Most Linux distributions already include all required packages to install and use the <code>mwetoolkit</code>. If you are running a Debian-based distribution like Debian, Ubuntu or Mint, the following command can be used to verify and/or install dependencies:</p>

<pre>sudo apt-get install subversion python gcc \
                  python-simplejson make wdiff \
                  libxml2 diffutils wget unzip</pre>

<p>This will ask for the root password and require confirmation if it is necessary to download and install missing packages. Alternatively, you can use a GUI package manager like Synaptic. If you are running another Linux distribution, please use your regular package management method to install the packages listed above.</p>

<p>Once you have checked and installed missing packages, open a Terminal and follow the <a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit">general <code>mwetoolkit</code> installation instructions.</a>

<p><strong>Note:</strong> Some of these packages are optional, like <code>wdiff</code> and <code>libxml2</code>, but they are needed for unit testing.</p>



