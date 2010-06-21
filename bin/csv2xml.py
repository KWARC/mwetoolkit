#!/usr/bin/python
# -*- coding:UTF-8 -*-

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

#script created by Victor Yoshiaki Miyai
#contact: darkagma@gmail.com, vymiyai@inf.ufrgs.br
#coded in 11/04/2010, dd/mm/yyyy
#last update in 20/06/2010, dd/mm/yyyy
#developed in Python 2.6.4

"""
	This script parses a plian text file and generates a .xml file, usable
	by other scripts in mwetoolkit.
"""

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

################################################################################
#GLOBALS

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



usage_string = """Usage: 
    
python %(program)s [OPTIONS] [FILE]

OPTIONS:
	-F <separator character>
		Sets the field separator character to one defined by the 
		user. If not specified, the default is the tab character.
				
	-s
		Enables the option to assign the words in a ngram to the
		surface	item. The default is to assign it to the lemma item.
			
FILE:
	<filename>
		The text file to be processed.
			
"""

################################################################################

def isInt(x):
	"""
		Tests if a value is of type "int". 
	
		@param x The value to be tested. x can be of any type.
		
		@return True, if x is of type "int", False otherwise
	"""
	
	try:
		intX = int(x)
		return True
	except ValueError:
		return False
	
################################################################################

def isFloat(x):
	"""
		Tests if a value is of type "float". 
	
		@param x The value to be tested. x can be of any type.
		
		@return True, if x is of type "float", False otherwise
	"""
	
	try:
		floatX = float(x)
		return True
	except ValueError:
		return False

################################################################################

def setToString( input ):
	"""
		Converts a set to a string. Lists of types in this script are compliant
		to Weka's ARFF format. To achieve this, some changes are needed. 
		
		Pythons's set:
			set('x', 'y', 'z')
		Converts to list:
			['x', 'y', 'z']
		Replaces square brackets to curly brackets.
			{'x', 'y', 'z'}
		Removes blank spaces and single quotes:
			{x,y,z}

	
		@param input A set of strings.
		
		@return a string representation of a Weka's ARFF formatted list of 
		elements.
	"""
	
	translateTable = string.maketrans("[]", "{}")
	
	input = list ( input )
	input.sort ()
	input = string.translate ( str ( input ) , translateTable , "' " )
	return input
	
################################################################################

def initialize( filename ):
	"""
		Initializes all global variables to be used in the process of
		transformation from text to xml.
		
		"frequencies" is a list that contains the frequency identifiers
		in the input file's header (file's first line).
		
		"words" is a list of all word identifiers in the header.
		
		"features" is a list of all feature identifiers in the header.
		
		"tpclasses" is a list of all tpclass identifiers in the header.
		
		"indexes" is a dictionary that maps all header's identifiers to
		their indexes (order of appearance) in the file.
		
		"corpora" is a list of all corpora's names.
		
		"frequency_dict" is a dictionary that maps a corpus' name in "corpora"
		to a list of all related frequencies (i.e. 'bnc':['f1_bnc', 'f2_bnc']).
		
		@param filename String of a file's name to be processed.
	"""
	
	global frequencies
	global words
	global features
	global tpclasses
	global indexes
	global corpora
	global frequency_dict
	
	f = open( filename , "r" )

	# get the file header, so we can start processing
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )
	
	# header items are sorted by their identifiers (frequencies, words, feature, tpclasses)
	# all data is stored in global variables, so we can use them afterwards
	for item in header:
		frequencies	=	frequencies	+	re.findall ( "f.*_.+" , item )
		words		=	words		+	re.findall ( "w.*_.+" , item )
		tpclasses	=	tpclasses +	re.findall ( "tp_.+" , item )
	
	# features are everything that do not enter any other category
	removeList = frequencies + words + tpclasses
	for x in header:
		if x not in removeList:
			features.append(x)

	# creates a dictionary that maps a header element to its index in the line
	indexes = dict(zip( header , range(len(header)) ))
	
	# creates a list of all available corpora
	corpora = set()
	for frequency in frequencies:
		corpus = frequency.split("_")
		corpora.add(corpus[1])
	
	# creates a dictionary that maps a corpus to its frequencies
	frequency_dict = dict( zip ( corpora , [ [] for corpus in corpora  ] ) )
	
	# creates a dictionary that maps a corpus' name to it's related frequencies
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
	"""
		Generates the <meta> section of the .xml file. The process stops
		if the input file do not have the same number of columns of data
		for each line.
		
		@param filename String of a file's name to be processed.
	"""

	global corpora
	global features
	global tpclasses

	f = open( filename , "r" )

	# remove the header, so we can get to the data
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	# create a Meta object to be printed in the end
	objectMeta = Meta ( [] , [] , [] )
	
	# add corpus size data to Meta
	for corpus in corpora:
		objectCorpusSize = CorpusSize ( str ( corpus ) , str ( DEFAULT_CORPUS_SIZE ) )
		objectMeta.add_corpus_size( objectCorpusSize )

	# maps a feature (name) to it's proper type (int, float, string or list)
	featType	= dict ( [ ( feature , set() ) for feature in features ] )
	
	# maps a tpclass (name) to a set of types
	tpclassType	= dict ( [ ( tpclass , set() ) for tpclass in tpclasses ] )
	
	# get the features' and the tpclasses' types
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
				# while the threshold is not reached, the feature type is a list of elements
				if featType [ feature ] != "string":
					featType [ feature ].add ( feat )
				# threshold reached, feature type is assigned to string
				if len ( featType [ feature ] ) > THRESHOLD:
					featType [ feature ] = "string"
		#get tpclass types
		for tpclass in tpclasses:
			tpclassType [ tpclass ].add ( line [ indexes [ tpclass ] ] )

	# creates a metafeat object to be added to the meta object
	for feature in features:
		if featType [ feature ] not in ["int","float","string"]:
			featType [ feature ] = setToString ( featType [ feature ] )
		objectMetaFeat = MetaFeat ( feature , featType [ feature ] )
		objectMeta.add_meta_feat ( objectMetaFeat )

	# creates a tpclass object to be added to the meta object
	for tpclass in tpclassType:
		tpclassName = tpclass.split ( "_" ) [ 1 ]
		tpclassType [ tpclass ] = setToString ( tpclassType [ tpclass ] )
		objectMetaTPClass = MetaTPClass ( tpclassName , tpclassType [ tpclass ] )
		objectMeta.add_meta_feat ( objectMetaTPClass )

	# prints the meta object
	print objectMeta.to_xml().encode( 'utf-8' )


################################################################################

def getCand( filename ):
	"""
		Generates the cand section of the .xml file. Data is retrieved by
		using the global variables initialized in initialize().
		
		@param filename String of a file's name to be processed.
	"""

	global corpora
	global words
	global frequency_dict
	global indexes
	global features
	global tpclasses

	f = open( filename , "r" )

	# remove the file header, so we can start processing
	line = f.readline ()
	header = string.split ( line.strip ( "\n" ) , SEPCHAR )

	# initialize candidate id counter
	candid = 0
	
	for row in f:
		line = string.split ( row.strip ( "\n" ) , SEPCHAR )

		
		# creates a new ngram object
		objectNgram = Ngram( [] , [] )
		wordCounter = 0
		for word in words:
			if SURFACE_FLAG == 0:
				# Option -s was not activated
				objectWord = Word( "" , line [ indexes [ word ] ] , "" , [] )
			else:
				# Option -s was activated
				objectWord = Word( line [ indexes [ word ] ] , "" , "" , [] )
			
			# Set the word frequencies for each corpus
			for corpus in corpora:
				frequency = frequency_dict[corpus][wordCounter]
				objectFrequency = Frequency ( corpus , line [ indexes [ frequency ] ] )
				objectWord.add_frequency ( objectFrequency )
			wordCounter = wordCounter + 1
			objectNgram.append ( objectWord )
			
			
		# add frequency of the ngram's total frequency
		for corpus in corpora:
			ngramFreqPos = len ( frequency_dict [ corpus ] ) - 1
			ngram_frequency = frequency_dict [ corpus ] [ ngramFreqPos ]
			if "f_" in ngram_frequency:
				objectFrequency = Frequency ( corpus , line [ indexes [ ngram_frequency ] ] )
				objectNgram.add_frequency ( objectFrequency )
				

		# objectFeature is a list of features. those features will be added
		# to a candidate object in the next step
		objectFeature = []
		if len ( features ) != 0:
			for feat in features:	
				objectFeature.append ( Feature ( feat , line [ indexes [ feat ] ] ) )
				
		# creation of a new candidate
		objectCand = Candidate( candid , objectNgram , objectFeature , [] , [] )	
			
		# add tpclasses to the candidate object
		if len ( tpclasses ) != 0:
			for tpclass in tpclasses:
				tpclassName = tpclass.split ( "_" ) [ 1 ]
				objecttp = TPClass( tpclassName, line [ indexes [ tpclass ] ] )
				objectCand.add_tpclass( objecttp )

		#print candidate object. we can now start processing a new candidate
		print objectCand.to_xml().encode( 'utf-8' )
		
		#increase candidate id counter to the next candidate object
		candid = candid + 1

	f.close()

################################################################################

#gets the arguments passed in the command line, returns a string list
def treat_options_csv2xml( opts, arg, n_arg, usage_string ):
	"""
		Callback function that handles the command line options of this script.
        
        @param opts The options parsed by getopts. Ignored.
        
        @param arg The argument list parsed by getopts.
        
        @param n_arg The number of arguments expected for this script.   
	"""
	
	global SEPCHAR
	global SURFACE_FLAG
	
	for ( o , a ) in opts:
		if o == "-F":
			# sets a new separator character to be used when spliting a line
			SEPCHAR = a
		elif o == "-s":
			# sets the assignment of a word to the "surface" item.
			# default is set to "lemma".
			SURFACE_FLAG = 1
		else:
			print >> sys.stderr, "Option " + " is not a valid option"
			usage( usage_string )
			sys.exit( 0 )

################################################################################
# MAIN SCRIPT

if __name__ == '__main__':
	
	files = read_options( "F:s", [], treat_options_csv2xml, 2, usage_string )

	for file in files:
		initialize(file)
		print XML_HEADER % { "root":"candidates", "ns":"" }
		getMeta(file)
		getCand(file)
		print XML_FOOTER % { "root":"candidates" }

	
