# Transforms Palavras (horrible!) text format into the moses factored format, 
# with one sentence per line, words separated by spaces and pipe symbols | to 
# separate the factors like surface|lemma|morph|synt. The morphological 
# information is not only POS, but detailed information on gender, number and 
# inflection. Each information in morph and synt is separated by _, the last 
# part of synt is :number, where number is the position on which the current 
# element depends.

# N.B. This script is very hard to understand. I hope I'll never need to modify
# it. Carlos, 2013-03-08. Updated on 2014-01-03.

# Cat the parsed corpus
# cat raw/total_????.txt_tagged_clean | 
# Some hard cleaning of serious PALAVRAS errors that generated crap
# sed -e 's/"@=[aoe] <= @=] @=> //g' -e 's/\[[^]]*\].*\[/[/g' -e 's/¤2965¤ //g' \
#    -e 's/ GER>/ <GER>/g' -e 's/ < @/ @/g' | 
for file in $@; do
    # Cat the parsed corpus
    #gunzip -c $file |
    cat $file |
    # Remove words that have double analysis
    sed -e 's/@\([^ \t]*\)[\t ]*\[.*#/@\1  #/g' |
    # Process beginning of the word, i.e. surfaces, lemmas, morph
    sed "s/^\([^ \t]*\)[ \t]\+\[\([^]]*\)\]\( <[^>]*>\)*\(\( [0-9A-Z_\/]*\)*\)*/\1|\2|\4|----- /g" | 
    # Process end of the word, i.e. syntax. Must be done in two steps
    # because of sed's limitation to \1-\9 backreferences, and I needed 10 :-(
    sed 's/|-----[^@]*\(\( @[A-Z><=\-]*\)*\) *\#[0-9]*->\([0-9]*\)/|\1:\3/g' |
    # Extra spaces at beginning and ending of morph and synt
    sed 's/ \?| \?/|/g' |
    # Extra dollar signs at beginning of punctuation surface
    sed 's/^\$//g' |
    # And extra dollar sign at beginning of slash lemma
    sed 's@/|\$/@|/@g' |
    # Artificially add info for punctuation signs
    sed 's/^\([^ \t]*\)[ \t]\+\#[0-9]*->\([0-9]*\)/\1|\1|PCT|:\2/g' |
    # Remove empty lines, "star" lines, "long" lines, "lixo", etc
    sed -e '/^$/d' -e '/^<star>$/d' -e '/^<long.*$/d' -e '/^<lixo.*$/d' |    
    # Now build the sentences. Some ill-formed senences will be discarded.
    awk -f build-sentences.awk 
    #cat
done
