# -*- coding: utf_8 -*-

#script created by Victor Yoshiaki Miyai
#contact: darkagma@gmail.com, vymiyai@inf.ufrgs.br

#coded in 11/04/2010, dd/mm/yyyy
#extended in 22/05/2010, dd/mm/yyyy

#to run this script, you must have Python in your machine
#the input is a file that contains a list of candidates from the mwetoolkit
#the output is the same name of the input file plus the extension .xml

#usage:
#in the terminal, type: 
#"python google_to_xml.py [OPTION] [FILE]"
#	OPTION:
#		-s <separator character>
#				sets the field separator character to one defined by the user.
#				if not specified, the default is the tab character.
#	FILE:
#		<filename>
#			the file to be processed.

#developed in Python 2.6.4


import string
import re
import sys

sepChar = "	"

#gets the arguments passed in the command line, returns a string list
def getFileNames():
	#removes the first argument, the script name itself
	sys.argv.pop(0)
	#retrieve the -s argument, the field separator character
	argument = sys.argv.pop(0)
	if argument == "-s":
		sepChar = sys.argv.pop(0)
		return sys.argv
	else:
		return [argument]


#gets file contents. filename is the name of the file. returns a string
def getFileContent(filename):
	file = open(filename,'r+')
	content = file.read()
	file.close()
	return content


#creates a list of lines that were separated by line breaks in the text
def contentSlicer(content):
	lineList = string.split(content, "\n")
	return lineList


#splits a string on sepChar characters and create a list with those elements
def lineSlicer(line):
	elementList = string.split(line, sepChar)
	return elementList


#calculates content to be written in meta area from a list of lists
def calculateMetafeats(lineList):
	#get the first element from the P column to be used as reference
	sample = lineList[1][1]
	#the metafeat counter based on the sample
	metafeatCounter = 1
	#iterator
	index = 2
	#calculates number of metafeats
	while lineList[index][1] == sample:
		metafeatCounter = metafeatCounter + 1
		index = index + 1
	#builds the list that will fill the comments in the final xml file (<!-- x -->)
	metafeatList = [lineList[i+1][2] for i in range(metafeatCounter)]
	return metafeatList


#from the properly sliced list, create a list for each n-gram [[lemma],[pos],[feats]]
def calculateCands(metafeatList, sliceList):
	#number of entries in the input file refering to the same n-gram
	interval = len(metafeatList)
	#number of entries in the input file
	entries = len(sliceList)
	#list of the n-grams and feats that will be returned
	candList = []
	for x in range (1,entries,interval):
		lemma = [sliceList[x][0], sliceList[x][1]]
		pos = [sliceList[0][0], sliceList[0][1]]
		featList = []
		for y in range(interval):
			featList.append([metafeatList[y], sliceList[x+y][3]])
		candList.append([lemma, pos, featList])
	return candList


#writes the header, same for all xml files created with this program
def writeHeader(newXml):
	newXml.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	newXml.write("<!DOCTYPE candidates SYSTEM \"dtd/mwttoolkit-candidates.dtd\">\n")
	

#auxiliary procedure to write data to the final xml file
def writeCandidates(metafeatList, candList, newXml):
	newXml.write("<candidates>\n")
	writeMeta(metafeatList, newXml)
	writeCand(candList, newXml)
	newXml.write("</candidates>\n")


#translates the Sentence to a feat name
def calculateFeatName(feat):
		name = string.lower(feat)
		name = string.replace(name, " ", "-")
		name = string.replace(name, "*", "n")
		name = re.sub("-\(.*\)", "_google", name)
		return name


#write data to the meta area
def writeMeta(metafeatList, newXml):
	newXml.write("<meta>\n")
	for comment in metafeatList:
		name = calculateFeatName(comment)
		newXml.write("	<metafeat name=" + name + " type=\"integer\"/>	<!-- " + comment + "-->\n")
	newXml.write("</meta>\n\n")


#write data to the cand area
def writeCand(candList, newXml):
	for ngram in candList:
		#retrieve information from candList
		lemma = ngram[0]
		pos = ngram[1]
		featList = ngram[2]
		#write data
		newXml.write( "<cand>\n")
		newXml.write( "<ngram>")
		for x in range(len(lemma)):
			newXml.write( "<w lemma=\"" + lemma[x] + "\" pos=\"" + pos[x] + "\"/>")
		newXml.write( "</ngram>\n")
		newXml.write( "<occurs></occurs>\n")
		newXml.write( "<features>\n")
		for x in range(len(featList)):
			name = featList[x][0]
			name = calculateFeatName(name)
			value = featList[x][1]
			value = string.replace(value, " \r", "")
			value = string.replace(value, " \n", "")
			value = string.replace(value, " ", "")
			newXml.write( "	<feat name=" + name +" value=\"" + value + "\"/>\n")
		newXml.write( "</features>\n")
		newXml.write( "</cand>\n\n")



#main program
if __name__ == '__main__':
	files = getFileNames()
	for file in files:
		lineList = contentSlicer(getFileContent(file))
		sliceList = []
		for x in lineList:
			line = lineSlicer(x)
			#create a new list of non-empty sliced lines 
			if line != ['']:
				sliceList.append(line)
		metafeatList = calculateMetafeats(sliceList)
		candList = calculateCands(metafeatList, sliceList)
		newXml = open(file + ".xml",'w+')  
		writeHeader(newXml)
		writeCandidates(metafeatList, candList, newXml)
		newXml.close() 
	
	
	
	
	
