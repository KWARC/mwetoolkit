#!/usr/bin/python
# -*- coding:UTF-8 -*-

#script created by Victor Yoshiaki Miyai
#contact: darkagma@gmail.com, vymiyai@inf.ufrgs.br

#coded in 11/04/2010, dd/mm/yyyy
#extended in 22/05/2010, dd/mm/yyyy



################################################################################
#
# Copyright 2010 Carlos Ramisch, Victor Yoshiaki Miyai
#
# csv2xml.py is part of mwetoolkit
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
from xmlhandler.classes.meta import Meta
from xmlhandler.classes.corpus_size import CorpusSize
from xmlhandler.classes.meta_tpclass import MetaTPClass
from xmlhandler.classes.meta_feat import MetaFeat
from xmlhandler.classes.ngram import Ngram
from xmlhandler.classes.word import Word
from xmlhandler.classes.feature import Feature
from xmlhandler.classes.tpclass import TPClass
from xmlhandler.classes.candidate import Candidate
from xmlhandler.classes.frequency import Frequency
from util import read_options
from xmlhandler.classes.__common import *

SEPCHAR = "	"
THRESHOLD = 10
DEFAULT_CORPUS_SIZE = -1
SURFACE_FLAG = 0

#these variables store all data that will be used
frequencies		= []
words 			= []
features 		= []
tpclasses 		= []
indexes 		= []
corpora 		= []
frequency_dict 	= []

# NEED TO BE COMPLETED
usage_string = """Usage: 
    
python %(program)s <corpus.xml>

    The <corpus.xml> file must be valid XML (dtd/mwetoolkit-corpus.dtd).
"""

################################################################################

def isInt(x):
	try:
		intX = int(x)
		return True
	except ValueError:
		return False
	
################################################################################

def isFloat(x):
	try:
		floatX = float(x)
		return True
	except ValueError:
		return False

################################################################################

def setToString( input ):
	
	translateTable = string.maketrans("[]", "{}")
	
	input = list ( input )
	input.sort ()
	input = string.translate ( str ( input ) , translateTable , "' " )
	return input
	
################################################################################

def initialize( filename ):
	"""
	to complete
	"""
	
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


	#dictionary that maps a header element to its index in the line
	indexes = dict(zip( header , range(len(header)) ))
	
	#list of all available corpora
	corpora = set()
	for frequency in frequencies:
		corpus = frequency.split("_")
		corpora.add(corpus[1])
	
	#dictionary that maps a corpus to its frequencies
	frequency_dict = dict( zip ( corpora , [ [] for corpus in corpora  ] ) )
	
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

################################################################################

def getMeta( filename ):
#	all frequency data shall be f.*_.+ and f_.+ is the ngram total frequency
#	features will be detected when they don't have prefixes
#	metatp data shall be tp_.+ and everything after the underscore is the name
#	the number of columns will be always the same for each line

	global corpora
	global features
	global tpclasses

	f = open( filename , "r" )

	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	#create Meta to be printed in the end
	objectMeta = Meta ( [] , [] , [] )
	
	#add corpus size data to Meta
	for corpus in corpora:
		objectCorpusSize = CorpusSize ( str ( corpus ) , str ( DEFAULT_CORPUS_SIZE ) )
		objectMeta.add_corpus_size( objectCorpusSize )



	#corpussize
#	print "<meta>"
#	for corpus in corpora:
#		print '<corpussize name="' + str ( corpus ) + '" value="' + str ( DEFAULT_CORPUS_SIZE ) + '"/>'
		
	#maps a feature (name) to it's proper type (int, float, string or list)
	featType	= dict ( [ ( feature , set() ) for feature in features ] )
	
	#maps a tpclass (name) to a set of types
	tpclassType	= dict ( [ ( tpclass , set() ) for tpclass in tpclasses ] )
	
	lineCounter = 0
	for row in f:
		lineCounter = lineCounter + 1
		line = string.split ( row.strip ( "\n" ) , SEPCHAR )
		if len ( line ) != len ( header ):
			print >> sys.stderr, "the number of columns in line " + str ( lineCounter ) + " and header is different"
			sys.exit( 1 )
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

		#get tpclass types
		for tpclass in tpclasses:
			tpclassType [ tpclass ].add ( line [ indexes [ tpclass ] ] )
	
	#convert all sets to lists and sort them
#	for feature in featType:
#		if featType [ feature ] not in ["int","float","string"]:
#			featType [ feature ] = list ( featType [ feature ] )
#			featType [ feature ].sort ()
	
#	transTable = string.maketrans("[]", "{}")
	for feature in features:
#		featType [ feature ] = string.translate ( str ( featType [ feature ] ) , transTable , "' " )
		if featType [ feature ] not in ["int","float","string"]:
			featType [ feature ] = setToString ( featType [ feature ] )
		objectMetaFeat = MetaFeat ( feature , featType [ feature ] )
		objectMeta.add_meta_feat ( objectMetaFeat )
#		print '<metafeat name="' + str ( feature ) + '" type="' + str ( featType [ feature ] ) + '"/>'

	for tpclass in tpclassType:
		tpclassName = tpclass.split ( "_" ) [ 1 ]
		tpclassType [ tpclass ] = setToString ( tpclassType [ tpclass ] )
		objectMetaTPClass = MetaTPClass ( tpclassName , tpclassType [ tpclass ] )
		objectMeta.add_meta_feat ( objectMetaTPClass )
		
	print objectMeta.to_xml().encode( 'utf-8' )
#		print '<metatpclass name="' + str ( tpclassName ) + '" type="' + str ( tpclassType [ tpclass ] ) + '"/>'

#	print "</meta>"

################################################################################

def getCand( filename ):

	global corpora
	global words
	global frequency_dict
	global indexes
	global features
	global tpclasses

	f = open( filename , "r" )

	#remove the file header, so we can start processing
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	#initialize candidate id counter
	candid = 0
	
	for row in f:
		line = string.split ( row.strip ( "\n" ) , SEPCHAR )

		
		#creates a new ngram
		objectNgram = Ngram( [] , [] )
		wordCounter = 0
		for word in words:
			if SURFACE_FLAG == 0:
				#Option -s was not activated
				objectWord = Word( "" , line [ indexes [ word ] ] , "" , [] )
			else:
				#Option -s was activated
				objectWord = Word( line [ indexes [ word ] ] , "" , "" , [] )
			
			#Set the word frequencies for each corpus
			for corpus in corpora:
				frequency = frequency_dict[corpus][wordCounter]
				objectFrequency = Frequency ( corpus , line [ indexes [ frequency ] ] )
				objectWord.add_frequency ( objectFrequency )
			wordCounter = wordCounter + 1
			objectNgram.append ( objectWord )
			
			
		#ngram total frequency
		for corpus in corpora:
			ngramFreqPos = len ( frequency_dict [ corpus ] ) - 1
			ngram_frequency = frequency_dict [ corpus ] [ ngramFreqPos ]
			if "f_" in ngram_frequency:
				objectFrequency = Frequency ( corpus , line [ indexes [ ngram_frequency ] ] )
				objectNgram.add_frequency ( objectFrequency )
				

		
		#objectFeature is a list that contains other features. those features 
		objectFeature = []
		if len ( features ) != 0:
			for feat in features:	
				objectFeature.append ( Feature ( feat , line [ indexes [ feat ] ] ) )
				
		#creation of a new candidate
		objectCand = Candidate( candid , objectNgram , objectFeature , [] , [] )	
			
			
		if len ( tpclasses ) != 0:
			for tpclass in tpclasses:
				tpclassName = tpclass.split ( "_" ) [ 1 ]
				objecttp = TPClass( tpclassName, line [ indexes [ tpclass ] ] )
				objectCand.add_tpclass( objecttp )

		#print final candidate 
		print objectCand.to_xml().encode( 'utf-8' )
		
		#increase candidate id counter
		candid = candid + 1

	f.close()

################################################################################

#gets the arguments passed in the command line, returns a string list
def treat_options_csv2xml( opts, arg, n_arg, usage_string ):
	
	global SEPCHAR
	global SURFACE_FLAG
	
	for ( o , a ) in opts:
		if o == "-F":
			SEPCHAR = a
		elif o == "-s":
			SURFACE_FLAG = 1
		else:
			print >> sys.stderr, "Option " + " is not a valid option"
			usage( usage_string )
			sys.exit( 0 )

################################################################################

#main program
if __name__ == '__main__':
	
	files = read_options( "F:s", [], treat_options_csv2xml, 2, usage_string )

	for file in files:
		initialize(file)
		print XML_HEADER % { "root":"candidates", "ns":"" }
		getMeta(file)
		getCand(file)
		print XML_FOOTER % { "root":"candidates" }

	
