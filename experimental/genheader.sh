#!/bin/bash
for file; do
	barename="${file%.*}"
	barename="${barename##*/}"
	dir="."
	[[ $file == */* ]] && dir="${file%/*}"
	outname="$dir/autoheaders/$barename.h"

	sed -ne '
		/^typedef struct .*{/,/^[[:space:]]*}/p
		/^struct .*{/,/^[[:space:]]*};/p
		/^union [^[:space:]].*{/,/^[[:space:]]*};/p
		/^typedef .*;/p
		/^#define .*\\$/,/[^\]$/p
		/^#define .*\\$/!{/^[[:space:]]*#/p}
		/^typedef\|^struct\|^union/!s/^\([A-Za-z][^{]*\)=.*/extern \1;/p
		/^typedef\|^struct\|^union/!s/^\([A-Za-z][^{]*[^ {]\)[[:space:]]*{$/\1;/gp
		/^typedef\|^struct\|^union/!{
			/^\([A-Za-z][^{]*[^ {]\)[[:space:]]*,$/,/.*{$/{ s/[[:space:]]*{$/;/g; p } }
	' <"$file" >"$outname"
done
