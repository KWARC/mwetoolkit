#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# Convert from RASP output format to mwe toolkit input XML format.
# ./rasp2mwe.py <file_in> <file_out>
# @A : Maitê Dupont 2012
################################################################################

def writeXML_header(f):
	f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	f.write("<!DOCTYPE corpus SYSTEM \"dtd/mwetoolkit-corpus.dtd\">\n")
	f.write("<corpus >\n")
def write_entry(f,n_line, sentence):
	f.write("<s s_id=\""+repr(n_line)+"\">")
	for elem in sentence:
		f.write("<w surface=\""+elem["surface"]+"\" lemma=\""+elem["lemma"]+"\" pos=\""+elem["pos"]+"\" syn=\""+elem["syn"]+"\" /> ")
	f.write("</s>\n")
def search_son(d,n):
	i=0
	for entry in d:
		if entry['index'] == n:
			return i
		i+=1
	return -1
def escape(s):
	if '&' in s:
		s=s.replace("&","&amp;")
	if '>' in s:
		s=s.rreplace(">","&gt;")
	if '<'  in s:
		s=s.replace("<","&lt;")
	if '"' in s:
		s=s.replace('"',"&quot;")
	return s
def process_line(l, phrase):
	if '|ellip|' in l:
		return

	del phrase[:]
	words=l.split("|")
	words.pop()		#remove last element => )
	words.pop(0)	#remove first element => (
	del phrase[:]
	for word in words : #e.g.: resume+ed:7_VVN
		if word!=" ": #words are separated by ' '
			try:
				s, aux_morph=word.split(":") # ':' gives something like |::4_:| that cannot be split in 2 pieces
			except ValueError:
				index=word.split(":")[2].replace('_','')
				lemma=':'
				surface=':'
				pos=':'	
			else:
				index, pos=aux_morph.split("_")
				pos=escape(pos)		
				if "+" in s:
					lemma=escape(s).split('+')[0]
					print lemma
					raw_input()
					if s.split('+')[1] != '':#because 's is followed by + => |'s+:12_$|
						s=s+'_'+pos
						p = os.popen('echo '+s+' | ${morphg_res:-./morphg.ix86_linux -t}') 	#generates the surface form using morphg
						l = p.readline()
						p.close()
						surface=l.split('_')[0]
						surface=escape(surface)
					else:#it's an 's, then
							surface=lemma
				else:#if it doesn't have a '+', then 
					surface=escape(s)
					lemma=surface		
			phrase.append({'index':index, 'surface':surface, 'lemma':lemma, 'pos':pos, 'syn':''})
	
	

def process_tree_branch(l, phrase):
###########  Process tree
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
		i=search_son(phrase,son_index)
		if i >=0:
			if phrase[i]['syn'] == "":
				phrase[i]['syn']=relation+':'+father_index
			else:
				phrase[i]['syn']=phrase[i]['syn']+';'+relation+':'+father_index
	elif len(b)==3: #son has two parents
		father_index=b[0].split(':')[1].split('_')[0]
		father2_index=b[1].split(':')[1].split('_')[0]
		son_index=b[2].split(':')[1].split('_')[0]	
		i=search_son(phrase,son_index)
		if i >=0:
			if phrase[i]['syn']=="":
				phrase[i]['syn']=relation+':'+father_index+';'+relation+':'+father2_index
			else:
				phrase[i]['syn']=phrase[i]['syn']+';'+relation+':'+father_index+';'+relation+':'+father2_index


import sys
import os
import string
import subprocess as sub

if len(sys.argv) != 3:
	print "\n\n"
	print "Usage: ./rasp2mwe.py <file_in_name> <file_out_name>"
	print "File in is the output of RASP."
	print "\n\n"
	sys.exit(0)

try:
	rasp=open(sys.argv[1], 'r')
except IOError as e:
	print 'Error opening file for reading.'
	exit(1)
try:
	mwe=open(sys.argv[2], 'w')
except IOError as e:
	print 'Error opening file for writing.'
	exit(1)

DIR=os.getcwd() #store current working directory to restore later
SRC=DIR+'/'+sys.argv[0]
SRC=SRC.split('/')
SRC.pop()  #remove file name
SRC=string.join(SRC,'/')
SRC=SRC+'/morph'

os.chdir(SRC) #change directory to morph so morphg can locate verbstem.list

###########  Initialization
n_line=0
l_empty=2
first_line=True
l=rasp.readline()
phrase = []

writeXML_header(mwe)

while l != "":
	if l=="\n":
		l_empty+=1
		if l_empty == 2:
			write_entry(mwe,n_line,phrase)
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
	write_entry(mwe,n_line,phrase) #save last entry
mwe.write("</corpus>")
os.chdir(DIR)
rasp.close()
mwe.close()
