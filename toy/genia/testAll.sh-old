#!/bin/bash

# This file tests the scripts of MWE extraction with mwetoolkit. All the results # are compared to standard results in the test folder, to verify consistency
# over time (regression test).

path_mwetk="../../bin"
python="/usr/bin/python"
testcounter=0
failcounter=0
successcounter=0

function testtoolkit {
    name=$1
    standard="test/"${name}
    command=$2
    if [ $3 ]; then
        ${python} ${path_mwetk}/${command} < $3 &> tmp
    else
        ${python} ${path_mwetk}/${command} &> tmp
    fi
    diff tmp ${standard} &> diffresult    

    # Verify that the generated XML (if any) is also valid (helps to keep consistency with newer DTDs
    is_xml=`expr match "${standard}" ".*\.xml"`
    if [ ${is_xml} -gt 0 ]; then
        xmllint --valid --path dtd --stream tmp &>> validresult
    else
        print > validresult
    fi
    diffresult=`cat diffresult`
    validresult=`cat validresult`
    testresult=`cat diffresult validresult`
    
    if [ "${testresult}" ]; then
        echo "*** :-[ Test ${name} failed ***"
        failcounter=`expr $failcounter + 1`
        if [ "$diffresult" ]; then
            echo -e "\n>> Expected:"
            head -n 5 ${standard}
            echo "..."
            echo -e "\n>> Found:"
            head -n 5 tmp
            echo "..."            
            echo -e "\n>> Differences:"
            head -n 5 diffresult
            echo "..."            
        else
            echo -e "\n>> Result correct, invalid XML:"
            head -n 5 validresult 
            echo "..."            
        fi
    else
        echo "*** :-] Test ${name} passed *** "
        successcounter=`expr $successcounter + 1`    
    fi
    rm tmp        
    rm diffresult
    rm validresult
    testcounter=`expr $testcounter + 1`    
}

################################################################################

echo "1) Testing wc.py script..."

testtoolkit "corpus_stats" "wc.py corpus.xml"
testtoolkit "reference_stats" "wc.py reference.xml"
testtoolkit "patterns_stats" "wc.py patterns.xml"
testtoolkit "corpus_stats_stdin" "wc.py" "corpus.xml"
testtoolkit "reference_stats_stdin" "wc.py" "reference.xml"
testtoolkit "patterns_stats_stdin" "wc.py" "patterns.xml"

################################################################################

echo "2) Testing head.py script..."

testtoolkit "head_corpus_default.xml" "head.py corpus.xml"
testtoolkit "head_corpus_big.xml" "head.py -n 50000 corpus.xml"
testtoolkit "head_corpus_small.xml" "head.py -n 25 corpus.xml"
testtoolkit "head_corpus_zero.xml" "head.py -n 0 corpus.xml"
testtoolkit "head_corpus_invalid1" "head.py -n as corpus.xml"
testtoolkit "head_corpus_invalid2" "head.py -n corpus.xml"
testtoolkit "head_corpus_stdin.xml" "head.py -n 20" "corpus.xml"
#############
testtoolkit "head_reference_default.xml" "head.py reference.xml"
testtoolkit "head_reference_big.xml" "head.py -n 50000 reference.xml"
testtoolkit "head_reference_small.xml" "head.py -n 25 reference.xml"
testtoolkit "head_reference_zero.xml" "head.py -n 0 reference.xml"
#############
testtoolkit "head_patterns_default.xml" "head.py patterns.xml"
testtoolkit "head_patterns_big.xml" "head.py -n 50000 patterns.xml"
testtoolkit "head_patterns_small.xml" "head.py -n 25 patterns.xml"
testtoolkit "head_patterns_zero.xml" "head.py -n 0 patterns.xml"
#############
testtoolkit "head_join_default.xml" "head.py patterns.xml reference.xml"

################################################################################

echo "2) Testing tail.py script..."

testtoolkit "tail_corpus_default.xml" "tail.py corpus.xml"
testtoolkit "tail_corpus_big.xml" "tail.py -n 50000 corpus.xml"
testtoolkit "tail_corpus_small.xml" "tail.py -n 25 corpus.xml"
testtoolkit "tail_corpus_zero.xml" "tail.py -n 0 corpus.xml"
testtoolkit "tail_corpus_invalid1" "tail.py -n as corpus.xml"
testtoolkit "tail_corpus_invalid2" "tail.py -n corpus.xml"
testtoolkit "tail_corpus_stdin.xml" "tail.py -n 20" "corpus.xml"
#############
testtoolkit "tail_reference_default.xml" "tail.py reference.xml"
testtoolkit "tail_reference_big.xml" "tail.py -n 50000 reference.xml"
testtoolkit "tail_reference_small.xml" "tail.py -n 25 reference.xml"
testtoolkit "tail_reference_zero.xml" "tail.py -n 0 reference.xml"
#############
testtoolkit "tail_patterns_default.xml" "tail.py patterns.xml"
testtoolkit "tail_patterns_big.xml" "tail.py -n 50000 patterns.xml"
testtoolkit "tail_patterns_small.xml" "tail.py -n 25 patterns.xml"
testtoolkit "tail_patterns_zero.xml" "tail.py -n 0 patterns.xml"
#############
testtoolkit "tail_join_default.xml" "tail.py patterns.xml reference.xml"

################################################################################

echo "3) Testing candidates.py script..."

################################################################################
#                                   SUMMARY                                    #
################################################################################

percent=`echo "($successcounter * 100 ) / $testcounter" | bc`
echo -e "****************************************************************"
echo -e "*  Executed $testcounter tests:"
echo -e "*    > Succeeded $successcounter tests out of $testcounter"
echo -e "*    > Failed $failcounter       tests out of $testcounter"
echo -e "*  Retrocompatibility rate: ${percent}%"
echo -e "****************************************************************"
