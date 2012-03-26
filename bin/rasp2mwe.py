#!/usr/bin/python
# -*- coding:UTF-8 -*-

################################################################################
# Converte do formato de saída do RASP para o formato XML do mwe toolkit.
# ./rasp2mwe.py _file_in file_out
#
#
################################################################################
def punctuation(w):
	if w=='.':
		return True
	elif w=='(':
		return True
	elif w==')':
		return True
	elif w==',':
		return True
	elif w==';':
		return True
	elif w==':':
		return True
	elif w=='>':
		return True
	elif w=='<':
		return True
	elif w=='{':
		return True
	elif w=='}':
		return True
	elif w=='\'':
		return True
	elif w=='"':
		return True
	else:
		return False
	
import sys

if len(sys.argv) != 3:
	print "\n\n"
	print "Usage: ./rasp2mwe.py <file_in_name> <file_out_name>"
	print "\n\n"
	sys.exit(0)
print "Open file for reading..."
rasp=open(sys.argv[1], 'r')

print "Open file for writing..."
mwe=open(sys.argv[2], 'w')

mwe.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
mwe.write("<!DOCTYPE corpus SYSTEM \"dtd/mwetoolkit-corpus.dtd\">\n")
mwe.write("<corpus >\n")

n_line=0
l_empty=2
l=rasp.readline()

while l != "":
	##process annotated line
	mwe.write("<s s_id=\""+repr(n_line)+"\">")
	words=l.split("|")
	words.pop()	#remove last element = )
	words.pop(0)	#remove first element = (

	for word in words :
		if word!=" ":
			s, aux=word.split(":")
			n_word, pos=aux.split("_")
			if len(s)==1:
				lemma=s
				surface=s
				if punctuation(s):
					pos="PCT"
			else:
				if "+" in s:
					lemma, end=s.split("+")
					surface=lemma+end
				else:
					surface=s
					lemma=surface
			mwe.write("<w surface=\""+surface+"\" lemma=\""+lemma+"\" pos=\""+pos+"\"/>")

	mwe.write("\n<s/>\n")
	n_line+=1
	##find next annotated line
	while l_empty !=0: ## phrases are separated by 2 blank lines
		l=rasp.readline()
		if l=="\n":
			l_empty-=1 
	l=rasp.readline()
	l_empty=2

rasp.close()
mwe.close()
