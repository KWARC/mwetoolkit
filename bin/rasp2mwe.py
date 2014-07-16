#!/usr/bin/python
# -*- coding:UTF-8 -*-

###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Maitê Dupont
#
# rasp2xml.py is part of mwetoolkit
#
# mwetoolkit is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# mwetoolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with mwetoolkit.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
"""
	This script transforms the output format of Rasp 2 to the XML format of
	a corpus, as required by the mwetoolkit scripts. Only UTF-8 text is
	accepted. For generating the surface forms (not provided by RASP), please
	indicate the path to morphg program, provided with older versions of RASP
	and unfortunately not available anymore (but send me an email if you need
	it ;-)
	
	For more information, call the script with no parameter and read the
	usage instructions.
"""

import sys
import os
import string
import pdb
from util import read_options, verbose, treat_options_simplest, strip_xml
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER
import subprocess as sub

###############################################################################
# GLOBALS 
morph_path="X"
morph=None
generate_text=False
work_path=os.getcwd()
d=["index","surface","lemma","pos", "syn"]
usage_string = """Usage: 
	
python %(program)s OPTIONS <file_in>
	The <file_in> file must be rasp output when used without the -m option of 
	rasp parser.

OPTIONS may be:

-m OR --morphg
	Path to morphg. If this option is activated, you should provide the absolute 
	path to the morphg installation folder.
	
-x OR --moses
	Generate the Moses factored text format instead of the usual mwetoolkit
	XML file. We will gradually move to this format and abandon the old 
	verbose XML files for corpora, since they create too large files.

"""
###############################################################################
def treat_options( opts, arg, n_arg, usage_string):
	"""  
	Callback function that handles the command options of this script.

	@param opts The options parsed by getopts. Ignored.

	@param arg The argument list parsed by getopts.

	@param n_arg The number os arguments expected for this script.

	@param usage_string Instructions that appear if you run the program with
	the wrong parameters or options.
	"""
	global morph_path
	global morph
	global generate_text
	treat_options_simplest(opts,arg,n_arg,usage_string)
	for (o, a) in opts:
		if o in ("-m","--morphg"):
			a=a.split('/')
			morph=a.pop()
			a=string.join(a, '/')
			morph_path=a
		if o in ("-x","--moses"):
			generate_text = True
	if not os.path.exists(morph_path): #Just testing if the file exists
		print >> sys.stderr, "WARNING: morphg not found!",
		print >> sys.stderr, " Outputting analysed forms"
		morph_path=None
	
###############################################################################

def write_entry(n_line, sent):
	""" 
		This function writes one sentence from the tagged corpus after 
		formating it into xml or Moses factored text.

		@param n_line Number of this line in the corpus, starting with 0
		
		@param sent Contains dictionaries corresponding to each word in the
		sentence.
	"""
	global generate_text
	if generate_text :
		sent_templ ="%(sent)s"
		word_templ="%(surface)s|%(lemma)s|%(pos)s|%(syn)s"
	else :
		sent_templ ="<s s_id=\""+str(n_line)+"\">%(sent)s</s>"
		word_templ="<w surface=\"%(surface)s\" lemma=\"%(lemma)s\" pos="+\
		           "\"%(pos)s\" syn=\"%(syn)s\" />"
	print sent_templ % { "sent":" ".join(map(lambda x: word_templ % x, sent)) }

###############################################################################
def search_entry(lst,n):
	""" 
		This function searches in a list of dictionaries for the entry 
with index n.

		@param lst List of ditionaries containing attributes lemma, surface, 
syn, pos and index for each word of the sentence being parsed.
		
		@param n Index to be found in lst

		@return Position in the list of the entry with "index" n.
	"""
	i=0
	for entry in lst:
		if entry['index'] == n:
			return i
		i+=1
	return -1

###############################################################################
def is_number(string):
	""" 
		Returns true if the string is a number. False otherwise.
	"""
	try:
		float(string)
		return True
	except ValueError:
		return False

###############################################################################

def process_line(l, phrase):
	""" 
		This function processes the tagged line, extracting each word and its 
		attributes.
		Information is stored in a list of dictionaries (one dict per word) 
		where we store all word attributes.

		@param l Line read from input to be processed.
		
		@param phrase List of dictionaries to be completed.

		@return True if everything went fine, False otherwise
	"""

	if '|ellip|' in l:
		return False
	lbef = l
	l = l.replace( "\\|", "@@VERTICALBAR@@" )
	del phrase[:] #for each sentence has to be cleaned
	words=l.split("|")
	try :
		words.pop()		#remove last element => )
		words.pop(0)	#remove first element => (
	except Exception:
		print >> sys.stderr, "Ignoring line \"" + l.strip() + "\""
		return False
	for word in words : #e.g.: resume+ed:7_VVN
		process=True
		if word!=" ": #words are separated by ' '
			try:
				s, aux_morph=word.split(":")
					#':' gives something like |::4_:|
					#that cannot be split in 2 pieces
			except ValueError: #word is or contains ':'
				n_colons=word.count(':')
				pieces=word.split(":")
				index=pieces[len(pieces)-1].split('_')[0]
				if n_colons ==3 and len(pieces)==4 and pieces[0]=="" and \
				pieces[3]=="": 
					lemma=':'
					surface=':'
					pos=':'	
					process=False
				else :
					aux_morph=pieces[len(pieces)-1]
					pieces.pop()
					s=':'.join(pieces)
			if process:
				try :
					index, pos=aux_morph.split("_")
				except Exception :
					print >>sys.stderr, lbef 
					print >>sys.stderr, pieces
					#print >>sys.stderr, phrase
				pos=strip_xml(pos)
				if "+" in s and not is_number(s.split('+')[1]):
					lemma=strip_xml(s).split('+')[0] 
					s = s.replace("'","\\'").replace("\"","\\\"")
					s = s.replace("`","\\`")+"_"+pos
					s=s+'_'+pos
					if morph_path != None and morph != None:							
						os.chdir(morph_path)
						cmd='echo "%s"' % s
						cmd+=' | ${morphg_res:-./'+morph+' -t}'
						p = sub.Popen(cmd, shell=True, 
									  stdout=sub.PIPE, stderr=sub.PIPE)
						#generates the surface form using morphg
						lerr = p.stderr.readlines()
						if len(lerr) > 0 :
							print >> sys.stderr, "Error morphg: " + str(lerr)
							print >> sys.stderr, "Offending command: " + cmd
						l = p.stdout.readline()
						p.stdout.close()
						p.stderr.close()
						os.chdir(work_path)
						surface=l.split('_')[0]
						surface=strip_xml(surface)
					else:
						surface=lemma
				else:#if it doesn't have a '+', then 
					lemma=strip_xml(s).replace(" ","")
					surface=lemma
			dic={d[0]:index,d[1]:surface,d[2]:lemma,d[3]:pos,d[4]:''}
			phrase.append(dic)
	return True
	
###############################################################################

def process_tree_branch(l, phrase):
	""" 
		This function processed the dependency tree that follows each tagged
		sentence. Information to be retrieved from here is just the 'syn'
		attribute, corresponding to the relations between father/son words.

		@param l Line read from input to be processed
		
		@param phrase List of dictionaries to be completed
	"""
	b=l.replace("(","").replace(")","").replace("|","")
	b=b.replace(" _",'').replace('\n','').split(' ')
	rel=b[0]
	del b[0]
	i=0
	while i < len(b):
		if ':' not in b[i]:
			rel=rel+'_'+b[i]
			del b[i]
		else:
			i+=1

	if len(b)==1:
		return
	elif len(b)==2: #son has one parent		
		father_index=b[0].split(':')[1].split('_')[0]
		son_index=b[1].split(':')
		son_index=son_index[len(son_index)-1].split('_')[0]	
		i=search_entry(phrase,son_index)
		if i >=0:
			if phrase[i]['syn'] == "":
				phrase[i]['syn']=rel+':'+father_index
			else:
				phrase[i]['syn']=phrase[i]['syn']+';'+rel+':'+father_index
		else:
			print >> sys.stderr, "Warning: Son not found. ",
			print >> sys.stderr, "Dependency tree error on sentence \n", l
			print >> sys.stderr, father_index, son_index, i
			print >> sys.stderr, phrase
	elif len(b)==3: #son has two parents
		father_index=b[0].split(':')[1].split('_')[0]
		father2_index=b[1].split(':')[1].split('_')[0]
		son_index=b[2].split(':')
		son_index=son_index[len(son_index)-1].split('_')[0]	
		i=search_entry(phrase,son_index)
		if i >=0:
			if phrase[i]['syn']=="":
				att=rel+':'+father_index+';'+rel+':'+father2_index
				phrase[i]['syn']=att
			else:
				att=phrase[i]['syn']+';'+rel+':'+father_index+';'
				att+=+rel+':'+father2_index

				phrase[i]['syn']=att
		else:
			print >> sys.stderr, "Warning: Son not found.",
			print >> sys.stderr, "Dependency tree error on sentence .",n_line

###############################################################################

def transform_format(rasp):
	"""
		Reads an input file and converts it into mwetoolkit corpus XML format,
		printing the XML file to stdout.
	
		@param rasp Is the input, file or piped.

	"""
	n_line=0
	l_empty=2
	first_line=True	
	phrase = []
	l=rasp.readline()
	while l != "":
		if l=="\n":
			l_empty+=1
			if l_empty == 1:
				write_entry(n_line,phrase)
				n_line+=1
				first_line=True
			l=rasp.readline()
			continue
	
		if first_line:
			if l_empty>=1:
				l_empty=0
				#repeats till valid line found
				while not process_line(l,phrase) : 
					l=rasp.readline()
				first_line=False
				l=rasp.readline() #ignore line
			else:
				l_empty=0
				first_line=True
		else:
			if l.startswith("(X") :
				while l != "\n": 
					l = rasp.readline()
				continue
			else :
				process_tree_branch(l,phrase)
		l=rasp.readline()
	if l_empty != 1:
		write_entry(n_line,phrase) #save last entry

###############################################################################
# MAIN SCRIPT

work_path=os.getcwd() #store current working directory to restore later

longopts = ["morphg=", "moses"]
arg = read_options( "m:x", longopts, treat_options, -1, usage_string )

if not generate_text :
	print XML_HEADER % { "root": "corpus", "ns": "" }

if len( arg ) == 0 :
	transform_format( sys.stdin )
else :
	for a in arg :
		try:
			input_file=open(a, 'r')
		except IOError as e:
			print >> sys.stderr, 'Error opening file for reading.'
			exit(1)
		transform_format( input_file )
		input_file.close()	
			   
if not generate_text :
	print XML_FOOTER % { "root": "corpus" }

