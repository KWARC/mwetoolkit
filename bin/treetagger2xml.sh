#!/bin/bash
# 
# Script to convert the output of treetagger into the XML format required by the
# mwetoolkit.
################################################################################



cat $@ |
sed -e 's/\&/\&amp;/g' -e 's/"/\&quot;/g' -e 's/>/\&gt;/g' -e 's/</\&lt;/g' -e "s/\t\t/\t/g" |
awk '
BEGIN{ 
	print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"; print "<!DOCTYPE corpus SYSTEM \"dtd/mwetoolkit-corpus.dtd\">"; print "<corpus>"; s_id=0; printf ( "<s s_id=\"%d\">", s_id++ ); FS="\t" }{ lemma = $3; if ( lemma == "&lt;unknown&gt;" ){ lemma = $1 } printf( "<w surface=\"%s\" lemma=\"%s\" pos=\"%s\"/>",$1,lemma,$2) }/SENT/{ printf( "</s>\n<s s_id=\"%d\">", s_id++ ); getline; }END{ printf( "</s>\n" ); print "</corpus>";  }' 
