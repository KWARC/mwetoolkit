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

SEPCHAR = "	"
THRESHOLD = 10
DEFAULT_CORPUS_SIZE = -1

#these variables store all data that will be used
frequencies = []
words = []
features = []
tpclasses = []
indexes = []
corpora = []
frequency_dict = []

"""

<candidates>
	<meta>
		<corpussize* name="" value="">
		<metafeat* name="" type="">
		<metatpclass* name="" type="{1,0}">
	</meta>
	<cand candid="">
		<ngram>
			<w+ surface="" lenma="" pos="">
				<freq name="" value="">
			</w>
			<freq name="" value="">
		</ngram>
		<occurs></occurs>
		<features>
			<feat* name="" value="">
		</features>
		<tpclass name="" value="">
	</cand>
</candidates>

all frequency data will be f.*_.*
all metatp data will be will be tp_.*

"""

def isInt(x):
	try:
		intX = int(x)
		return True
	except ValueError:
		return False
	
def isFloat(x):
	try:
		floatX = float(x)
		return True
	except ValueError:
		return False



def initialize( filename ):
	
	f = open( filename , "r" )


	#get the file header, so we can start processing
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	global frequencies
	global words
	global features
	global tpclasses
	global indexes
	global corpora
	global frequency_dict
	
	#header items are sorted by their groups (frequencies, words, feature, tpclasses)
	#all data is stored in global variables, so we can use them afterwards
	for item in header:
		frequencies	=	frequencies	+	re.findall ( "f.*_.+" , item )
		words		=	words		+	re.findall ( "w.*_.+" , item )
		tpclasses	=	tpclasses +	re.findall ( "tp_.+" , item )
	
	#features are everything that do not enter any other category
	removeList = frequencies + words + tpclasses
	for x in header:
		if x not in removeList:
			features.append(x)
			
#	print frequencies
#	print words
#	print features
#	print tpclasses

	#dictionary that maps a header element to its index
	indexes = dict(zip( header , range(len(header)) ))
#	print indexes
	
	#list of all corpora available
	corpora = set()
	for frequency in frequencies:
		corpus = frequency.split("_")
		corpora.add(corpus[1])
#	print corpora
	
	#dictionary that maps a corpus to its frequencies
	frequency_dict = dict( zip ( corpora , [ [] , [] ] ) )
	
	for corpus in corpora:
		#build the list of all frequencies of the corpus
		for frequency in frequencies:
			if corpus in frequency:
				frequency_dict[corpus].append(frequency)
		#sort the list of frequencies of this corpus
		#frequencies are ordered by the numbers in their names
		#if provided, the last frequency in the new list will be the whole ngram frequency 
		newFrequencyList = range(len(frequency_dict[corpus]))
		for frequency in frequency_dict[corpus]:
			freqIndex = re.findall ( "f(.*)_.+" , frequency )
			if freqIndex[0] == "":
				newFrequencyList [ len( frequency_dict [ corpus ] ) - 1 ] = frequency
			else:
				newFrequencyList [ int ( freqIndex [ 0 ] ) - 1 ] = frequency
		frequency_dict[corpus] = newFrequencyList
		
#	print frequency_dict






def getMeta( filename ):
#	all frequency data shall be f.*_.+ and f_.+ is the ngram total frequency
#	features will be detected when they don't have prefixes
#	metatp data shall be tp_.+ and everything after the underscore is the name
#	the number of columns will be always the same for each line

	global corpora


	f = open( filename , "r" )

	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	#corpussize
	print "<meta>"
	for corpus in corpora:
		print '<corpussize name="' + str ( corpus ) + '" value="' + str ( DEFAULT_CORPUS_SIZE ) + '"/>'
		
		
	featType = dict ( [ ( feature , set() ) for feature in features ] )
	lineCounter = 0
	for row in f:
		lineCounter = lineCounter + 1
		line = string.split ( row.strip ( "\n" ) , SEPCHAR )
		if len ( line ) != len ( header ):
			print "the number of columns in line " + str ( lineCounter ) + " and header is different"
			exit ( 0 )
		for feature in features:
			#get feature value
			feat = line [ indexes [ feature ] ]
			if isInt ( feat ):
				featType [ feature ] = "int"
			elif isFloat ( feat ):
				featType [ feature ] = "float"
			else:
				#while the threshold is not reached, the feature type is a list of elements
				if featType [ feature ] != "string":
					featType [ feature ].add ( feat )
				#threshold reached, feature type is assigned to string
				if len ( featType [ feature ] ) > THRESHOLD:
					featType [ feature ] = "string"
	for feature in featType:
		if featType [ feature ] not in ["int","float","string"]:
			featType [ feature ] = list ( featType [ feature ] )
	
	transTable = string.maketrans("[]", "{}")
	for feature in features:
		featType [ feature ] = string.translate ( str ( featType [ feature ] ) , transTable , "' " )
		print '<metafeat name="' + str ( feature ) + '" type="' + str ( featType [ feature ] ) + '"/>'
		
	for tpclass in tpclasses:
		tpclassName = tpclass.split ( "_" ) [ 1 ]
		print '<metatpclass name="' + str ( tpclassName ) + '" type="' + str ( "{0,1}" ) + '"/>'
	
	
	print "</meta>"


def getCand( filename ):

	f = open( filename , "r" )

	#remove the file header, so we can start processing
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	#initialize candidate id counter
	candid = 0
	
	for row in f:
		line = string.split ( row.strip ( "\n" ) , SEPCHAR )
		print '<cand candid="' + str(candid) + '"/>'
		print "<ngram>"
		wordCounter = 0
		for word in words:
			print '<w lemma="' + line[indexes[word]] + '">'
			for corpus in corpora:
				frequency = frequency_dict[corpus][wordCounter]
				print '<freq name="' + corpus + '" value="' + line[indexes[frequency]] + '"/>'
			print "</w>"
			wordCounter = wordCounter + 1
		for corpus in corpora:
			frequency = frequency_dict [ corpus ] [ len ( frequency_dict [ corpus ] ) - 1 ]
			if "f_" in frequency:
				print '<freq name="' + corpus + '" value="' + line[indexes[frequency]] + '"/>'
				
		print "</ngram>"
		print "<occurs>"
		print "</occurs>"
		if len ( features ) != 0:
			print "<features>"
			for feat in features:	
				print '<feat name="' + feat + '" value="' + line [ indexes [ feat ] ] + '"/>'
			print "</features>"
			
			
		if len ( tpclasses ) != 0:
			for tpclass in tpclasses:
				tpclassName = tpclass.split ( "_" ) [ 1 ]
				print '<tpclass name="' + tpclassName + '" value="' + line [ indexes [ tpclass ] ] + '"/>'
		
		
		print "</cand>"
		#increase candidate id counter
		candid = candid + 1

	f.close()




#gets the arguments passed in the command line, returns a string list
def getFileNames():
	#removes the first argument, the script name itself
	sys.argv.pop(0)
	#retrieve the -s argument, the field separator character
	argument = sys.argv.pop(0)
	if argument == "-s":
		SEPCHAR = sys.argv.pop(0)
		return sys.argv
	else:
		return [argument]


#main program
if __name__ == '__main__':
	files = getFileNames()
	for file in files:
		initialize(file)
		print "<candidates>"
		getMeta(file)
		getCand(file)
		print "</candidates>"

	
