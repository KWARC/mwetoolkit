#!/bin/bash
for file; do
	barename="${file%.*}"
	barename="${barename##*/}"
	dir="."
	[[ $file == */* ]] && dir="${file%/*}"
	outname="$dir/autoheaders/$barename.h"

	# NOTA: Estas regras assumem que o "{" das definições fique na mesma linha
	# do início da definição em questão.
	sed -n -E -f headersregex.sed <"$file" >"$outname"
done
