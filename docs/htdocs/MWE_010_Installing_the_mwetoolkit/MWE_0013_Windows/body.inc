<h2><code>mwetoolkit</code> Installation: Windows Requirements</h2>

<p>The <code>mwetoolkit</code> was developed and tested extensively on Linux, but this doesn't mean you cannot use it on Windows :-)</p>

<p><span style="color:red;">It is now possible to run the <code>mwetoolkit</code> in Windows environments</span> by installing a command line emmulator called <strong>Cygwin</strong>. The instructions below have been tested in Windows 7 Home Basic - 64 bits and worked perfectly. We detail below specific Cygwin installation instructions for use with the <code>mwetoolkit</code>. If you are familiar with Cygwin, you can run the installation setup and go to step 7, to install the required packages.</p>

<h3>Download the Cygwin installer</h3>

<p>First, you need to download the Cygwin setup program from <a href="https://cygwin.com/install.html" target="_blank">the official Cygwin installation website</a>. It is a very light installer, since the real system will be downloaded later. Select the appropriate version according to your computer architecture, 32 bits (setup-x86.exe) or 64 bits (setup-x86_64.exe). check the "System Information" in if you don't know which version to download. </p>

<h3>Configure and install Cygwin</h3>

Once you have downloaded the installer, double-click it to start the installation process and follow the instructions below, accepting the default configuration options.</p>

<ol>

<li>Click "Next" <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen1.png" alt="Cygwin installation screen - Step 1"/></li>
<li>Select "Install from Internet" (default) and then click "Next" <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen2.png" alt="Cygwin installation screen - Step 2"/></li>
<li>Select "All Users" (default) and then click "Next". You can change the installation directory if you want, but the default <code>C:\\cygwin</code> or <code>C:\\cygwin64</code> is just fine. <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen3.png" alt="Cygwin installation screen - Step 3"/></li>
<li>Click "Next". You can change the local package directory if you want. This is the place where all the installation files are stored. You can delete them after installation is completed, but we recommend keeping it in case you need to modify your Cygwin installation in the future. <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen4.png" alt="Cygwin installation screen - Step 4"/></li>
<li>Enter your Internet Proxy information if necessary, and click "Next". Most people don't use a proxy, so you can simply leave "Direct Connection" selected. <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen5.png" alt="Cygwin installation screen - Step 5"/></li>
<li>Select any server URL from the list, then click "Next". Any server will work fine, but you can try to find one that is geographically close to speed up the download process. For instance, if you are in Brazil, then select <code>http://linorg.usp.br</code> <br/><img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen6.png" alt="Cygwin installation screen - Step 6"/></li>


<!--<h3>3. Package selection</h3>-->

<li>Like in any Linux-based distribution, Cygwin program installation is based on <em>packages</em>. At this step, you must select the packages that you want to install in addition to the basic ones. A simple possibility would be to select all packages, but this would take hours and fill up several gigabytes of HD storage. Instead, we recommend installing only the packages listed below, required to run the mwetoolkit:
<ul>
<li><code>subversion</code> - category "Devel"</li>
<li><code>python</code> - category "Python"</li>
<li><code>gcc-core</code> - category "Devel"</li>
<li><code>make</code> - category "Devel"</li>
<li><code>python-simplejson</code> - category "Python"</li><!-- - optional, required to use Web search API</li>-->
<li><code>diffutils</code> - category "Utils"</li><!-- - optional, required for unit tests</li>-->
<li><code>wdiff</code> - category "Utils"</li><!-- - optional, clearer output in unit tests</li>-->
<li><code>libxml2</code> - category "Libs"</li><!-- - optional, required to check XML with <code>xmllint</code></li>-->
<li><code>wget</code> - category "Web"</li><!-- - optional, required to install from release</li>-->
<li><code>unzip</code> - category "Archive"</li><!-- - optional, required to install from release</li>-->
</ul>

In order to select a package for installation, type the package name in the "Search" box. Then, locate the appropriate category and expand it by clicking on the "+" sign. Find the package whose name matches EXACTLY the name of one of the packages listed above. The name of the package is found in the last column, and appears just before the colon, as in the example below. Finally, click ONCE on the first column where the "Skip" keyword will be replaced by the version number of the package to be installed. If by accident you click twice, this will select another version. Click two more times and the correct version is selected again. When the package is selected, two checkboxes appear in the second and third columns, indicating that the package will be installed. Repeat the process exemplified below with the packages in the list above, then click "Next".<br/>
<img style="margin-bottom: 40px; width: 680px;" src="images/printscreen/cygwin-screen7.png" alt="Cygwin installation screen - Step 7 - package selection"/></li>
<li>Confirm that you want to install the selected packages, and click "Next". Leave the checkbox "Select required packages (RECOMMENDED)" checked (default).<br/>
<img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen8.png" alt="Cygwin installation screen - Step 8"/></li>
<li>Once you have confirmed the installation, you can click "Next" and wait while the packages are downloaded and installalled. This can take a long time depending on your Internet connection. Remember that you should have enough free disk space.<br/>
<img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen9.png" alt="Cygwin installation screen - Step 9"/></li>
<li>Choose whether you want to create shortcuts on Desktop or in Start Menu, and click "Finish"<br/>
<img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen10.png" alt="Cygwin installation screen - Step 10"/></li>
<li>Now, open the Cygwin Terminal through one of the shortcuts and now follow the <a href="?sitesig=MWE&page=MWE_010_Installing_the_mwetoolkit">general <code>mwetoolkit</code> installation instructions.</a><br/>
<img style="margin-bottom: 40px;" src="images/printscreen/cygwin-screen11.png" alt="Cygwin installation screen - Step 11"/></li>
</ol>

<p><em>WARNING</em>: when emmulated in Cygwin, we remarked that the <code>mwetoolkit</code> runs considerably slower than in Linux. Consider using Linux if you want to process very large corpora</p>


