<h2><code>mwetoolkit</code> Installation: Mac OS Requirements</h2>

<p>You will need to download and to configure some specific programs and libraries. </p>

<h3>MacPorts</h3>

<p>This software allows you to install Linux packages from the command line, similar to Linux's <code>apt-get</code>. If you don't have MacPorts yet, install it from <a href="http://www.macports.org/install.php/">the official website</a>.</p>

<p><strong>Note:</strong> You will need to update or install XCode and XCode Command Line Tools as a pre-requisite of MacPorts. They are available from the AppleStore and from the Apple Developer Website. Detailed instructions are available on a <a href="https://guide.macports.org/#installing.xcode" target="_blank">dedicated section of the MacPorts installation guide</a>.</p>

<h3>Additional packages (through MacPorts)</h3>

<p>To get this done is pretty simple, once you have MacPorts set up correctly (you can type <code>man port</code> and get a manual page). Just run the following command:</p>

<pre>sudo port install coreutils subversion python27 \
                  py27-simplejson gmake wdiff gcc48 \
                  libxml2 diffutils wget unzip</pre>


<!--<p>The Python installation comes with a handy utility called easy_install, which easily installs missing components: <code>sudo easy_install simplejson</code></p>-->

<p>Once you have checked and installed missing packages, open a Terminal and follow the <a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit">general <code>mwetoolkit</code> installation instructions.</a>

<p><strong>Note:</strong> Some of these packages are optional, like <code>wdiff</code> and <code>libxml2</code>, but they are needed for unit testing.</p>

<p><strong>Note:</strong>In Mac OS, some unit tests appear to fail because of floating point rounding differences in the last digits. This can be safely ignored.</p>

