#!/usr/bin/python
# -*- coding:UTF-8 -*-

# ###############################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos, Venera Arnaoudova
#
# eval_manual.py is part of mwetoolkit
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

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

__author__ = 'Neni'

"""
    This contributed utility script was developed by Venera Arnaoudova as a
    simple command-line interface to manually validate a list of MWE candidates
    in XML format and save the result in CSV format. It the CSV file already 
    exists, annotation continues from the last annotated line.
    
    For more information, call the script with no parameter and read the
    usage instructions. 
"""

import os
from lxml import etree

from libs.util import read_options, treat_options_simplest


################################################################################     
# GLOBALS     
usage_string = """Usage: 
    
python {program} OPTIONS <candidates.xml> <output.csv>


OPTIONS may be:

{common_options}

    The <candidates.xml> file must be valid XML (dtd/mwetoolkit-candidates.dtd).
"""


################################################################################   

def annotate_candidates():
    """Main function, opens both files (candidates and output), looks for the 
    next MWE to annotate and launches annotation interface.
    """
    global candidates_filename
    global output_filename
    parser = etree.HTMLParser(remove_blank_text=True)
    tree = etree.parse(candidates_filename, parser)
    validatedMWEfileName = output_filename

    alreadyValidated = []
    totalValidated = -1

    if os.path.exists(validatedMWEfileName):
        validatedMWEfile = file(validatedMWEfileName, "r")
        for line in validatedMWEfile:
            print("READ:" + line)
            alreadyValidated.append(line.split(";")[0])
            totalValidated = totalValidated + 1
        validatedMWEfile.close()
        validatedMWEfile = file(validatedMWEfileName, "a")
    else:
        validatedMWEfile = file(validatedMWEfileName, "w")
        header = "Cand id;Frequency;word1;word2;word3;validation\n"
        validatedMWEfile.write(header)
        totalValidated = totalValidated + 1

    print("Total validated:", str(totalValidated))

    for cand in tree.xpath('.//cand'):
        ngram = cand.find('ngram')
        ngrams = cand.findall('occurs/ngram')
        candidateId = cand.get('candid')
        if alreadyValidated.__contains__(candidateId + ";"):
            print("Already validated:" + candidateId)
            continue

        print("----------\nNgram ", candidateId, ", Freq.:",
              ngram.find('freq').get("value"))

        for currentNgram in ngrams:
            print()
            for word in currentNgram.xpath('./w'):
                print("\t " + str(word.attrib))

        currentMWE = candidateId + ";" + ngram.find('freq').get("value") + ";"

        print()
        for word in ngram.xpath('./w'):
            print(word.attrib)
            currentMWE = currentMWE + str(word.attrib) + ";"
        if currentMWE.count(";") == 4:
            currentMWE = currentMWE + ";"
        validation = raw_input("Is this a MWE: ")
        print("\t You entered: ", validation)
        if validation == ".":
            validatedMWEfile.close()
            exit()
        currentMWE = currentMWE + validation
        validatedMWEfile.write(currentMWE + "\n")
        totalValidated = totalValidated + 1
        print("\t ---> Total validated:", str(totalValidated))

    validatedMWEfile.close()

################################################################################
# MAIN SCRIPT

args = read_options("", [], treat_options_simplest, 2, usage_string)
candidates_filename = args[0]
output_filename = args[1]
annotate_candidates()
