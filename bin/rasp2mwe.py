#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
#
# Copyright 2010-2012 Carlos Ramisch, Maitê Dupont
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
################################################################################
"""
    This script transforms the output format of Rasp to the XML format of
    a corpus, as required by the mwetoolkit scripts. The script is language
    independent as it does not transform the information. Only
    UTF-8 text is accepted.
    
    For more information, call the script with no parameter and read the
    usage instructions.
"""

import sys
import os
import string
from util import read_options, verbose, treat_options_simplest, strip_xml
from xmlhandler.classes.__common import XML_HEADER, XML_FOOTER
import subprocess as sub

################################################################################     
# GLOBALS 
morph_path=None
work_path=os.getcwd()
usage_string = """Usage: 
    
python %(program)s OPTIONS <file_in>
    The <file_in> file must be rasp output when used without the -m option.

OPTIONS may be:

-m OR --morphg
    KePath to morphg. If this option is
    activated, you should provide the absolute path to the morphg 
	installation folder.

"""
################################################################################  
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
	treat_options_simplest(opts,arg,n_arg,usage_string)
	for (o, a) in opts:
		if o in ("-m","--morphg"):
			morph_path=a
	if not os.path.exists(morph_path): #Just testing if the file exists
		print >> sys.stderr, "WARNING: morphg not found! Outputting analysed forms"
		morph_path=None
	
################################################################################  

def write_entry(n_line, sentence):
	""" 
		This function writes one sentence from the tagged corpus after 
formating it to xml.

		@param n_line Number of this line in the corpus, starting with 0
		
		@param sentence Contains dictionaries corresponding to each word 
in the sentence.
	"""
	print"<s s_id=\""+repr(n_line)+"\">",
	for elem in sentence:
		print "<w surface=\""+elem["surface"]+"\" lemma=\""+elem["lemma"]+"\" pos=\""+elem["pos"]+"\" syn=\""+elem["syn"]+"\" /> ",
	print"</s>"

################################################################################  

def search_entry(d,n):
	""" 
		This function searches in a list of dictionaries for the entry 
with index n.

		@param d List of ditionaries containing attributes lemma, surface, 
syn, pos and index for each word of the sentence being parsed.
		
		@param n Index to be found in d

		@return Position in the list of the entry with "index" n.
	"""
	i=0
	for entry in d:
		if entry['index'] == n:
			return i
		i+=1
	return -1

################################################################################  

def process_line(l, phrase):
	""" 
		This function Process the tagged line, extracting each word and it's attributes.
		Information is stored in a list of dictionaries (one dict per word) 
where will be filled all the words attributes.

		@param l Line read from input to be processed.
		
		@param phrase List of dictionaries to be completed.
	"""

	if '|ellip|' in l:
		return

	del phrase[:] #for each sentence has to be cleaned
	words=l.split("|")
	words.pop()		#remove last element => )
	words.pop(0)	#remove first element => (
	del phrase[:]
	for word in words : #e.g.: resume+ed:7_VVN
		if word!=" ": #words are separated by ' '
			try:
				s, aux_morph=word.split(":") # ':' gives something like |::4_:|
											# that cannot be split in 2 pieces
			except ValueError:
				index=word.split(":")[2].replace('_','')
				lemma=':'
				surface=':'
				pos=':'	
			else:
				index, pos=aux_morph.split("_")
				pos=strip_xml(pos)		
				if "+" in s:
					lemma=strip_xml(s).split('+')[0]
					if s.split('+')[1] != '':#because 's is followed 
												#by + => |'s+:12_$|
						s=s+'_'+pos
						if morph_path != None:
							os.chdir(morph_path)
							p = os.popen('echo '+s+' | ${morphg_res:-./morphg.ix86_linux -t}') 	
							#generates the surface form using morphg
							l = p.readline()
							p.close()
							os.chdir(work_path)
							surface=l.split('_')[0]
							surface=strip_xml(surface)
						else:
							surface=lemma
					else:#it's an 's, then
							surface=lemma
				else:#if it doesn't have a '+', then 
					surface=strip_xml(s)
					lemma=surface		
			phrase.append({'index':index, 'surface':surface, 'lemma':lemma, 'pos':pos, 'syn':''})
	
################################################################################  

def process_tree_branch(l, phrase):
	""" 
		This function processed the dependency tree that follows each tagged sentence. Information to be retrieved from here is just the 'syn' attribute, corresponding to the relations between father/son words.

		@param l Line read from input to be processed
		
		@param phrase List of dictionaries to be completed
	"""
	b=l.replace("(","").replace(")","").replace("|","").replace(" _",'').replace('\n','').split(' ')
	relation=b[0]
	del b[0]
	i=0
	while i < len(b):
		if ':' not in b[i]:
			relation=relation+'_'+b[i]
			del b[i]
		else:
			i+=1
	if len(b)==1:
		return
	elif len(b)==2: #son has one parent		
		father_index=b[0].split(':')[1].split('_')[0]
		son_index=b[1].split(':')[1].split('_')[0]	
		i=search_entry(phrase,son_index)
		if i >=0:
			if phrase[i]['syn'] == "":
				phrase[i]['syn']=relation+':'+father_index
			else:
				phrase[i]['syn']=phrase[i]['syn']+';'+relation+':'+father_index
		else:
			print "Son not found. Dependency tree error on sentence ", n_line
	elif len(b)==3: #son has two parents
		father_index=b[0].split(':')[1].split('_')[0]
		father2_index=b[1].split(':')[1].split('_')[0]
		son_index=b[2].split(':')[1].split('_')[0]	
		i=search_entry(phrase,son_index)
		if i >=0:
			if phrase[i]['syn']=="":
				phrase[i]['syn']=relation+':'+father_index+';'+relation+':'+father2_index
			else:
				phrase[i]['syn']=phrase[i]['syn']+';'+relation+':'+father_index+';'+relation+':'+father2_index
		else:
			print "Son not found. Dependency tree error on sentence .", n_line

################################################################################     

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

	for l in rasp.readlines():
		if l=="\n":
			l_empty+=1
			if l_empty == 2:
				write_entry(n_line,phrase)
				n_line+=1
				first_line=True
			l=rasp.readline()
			continue
	
		if first_line:
			if l_empty>=2:
				l_empty=0
				process_line(l,phrase)
				first_line=False
				l=rasp.readline() #ignore line
			else:
				l_empty=0
				first_line=True
		else:
			process_tree_branch(l,phrase)
		l=rasp.readline()
	if l_empty != 2:
		write_entry(n_line,phrase) #save last entry

################################################################################     
# MAIN SCRIPT

work_path=os.getcwd() #store current working directory to restore later

longopts = ["morphg="]
arg = read_options( "m:", longopts, treat_options, -1, usage_string )

print XML_HEADER % { "root": "corpus", "ns": "" }

if len( arg ) == 0 :
	transform_format( sys.stdin )        
else :
	for a in arg :
		try:
			input_file=open(a, 'r')
		except IOError as e:
			print 'Error opening file for reading.'
			exit(1)
		transform_format( input_file )
		input_file.close()           

print XML_FOOTER % { "root": "corpus" }

