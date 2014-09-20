#!/bin/bash

################################################################################
#
# Copyright 2010-2014 Carlos Ramisch, Vitor De Araujo, Silvio Ricardo Cordeiro,
# Sandra Castellanos
#
# mweconsole.py is part of mwetoolkit
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

mweconsole_version=(0.0.7 2012-02-25)

ASSOC_MEASURES="mle:pmi:ll:t:dice"
CONTRAST_MEASURES="csmwe:simplediff:simplecsmwe"

_main() {
	for arg; do
		case "$arg" in
			-y) export assume_yes=1 ;;
			*) echo "Unknown option $arg" >&2; exit 1 ;;
		esac
	done

	if [[ $- == *i* ]]; then
		_start
	else
		"$BASH" --rcfile "$0" -i
	fi
}

_confirm() {
	if [[ $assume_yes ]]; then
		return 0
	else
		printf "$1 (y/n) " "${@:2}"
		local reply
		read -n 1 reply
		echo
		[[ $reply == [yY] ]]
	fi
}

setvar() {
	local __cmd
	printf -v __cmd "%s=(%q)" "$1" "$2"
	eval "$__cmd"
}

_elem() {
	local val="$1"; shift
	local i
	for i; do
		[[ $i = $val ]] && return 0
	done
	return 1
}

help() {
	printf "\n"

	printf "Project commands:\n"
	printf "  \e[1mcreate-project [<dirname> [-n]]\e[0m: Creates a new project.\n"
	printf "  \e[1mopen-project <dirname> [-n]\e[0m: Opens a project.\n"
	printf "  \e[1msave-project <dirname> [-n]\e[0m: Saves current project under a new directory.\n\n"
	printf "  \e[1m-n\e[0m option: do not enter into the project folder"
	printf "\n"

	printf "File commands:\n"
	printf "  \e[1mcorpus <filename>\e[0m: Select a corpus file.\n"
	printf "  \e[1mpattern <filename>\e[0m: Select a pattern file.\n"
	printf "  \e[1mreference <filename>\e[0m: Select a reference (gold standard) file.\n"
	printf "  \e[1mwc [type]\e[0m: Show statistics about the selected file.\n"
	printf "  \e[1mhead <n> [type]\e[0m: Keep first n entries in a file.\n"
	printf "  \e[1mtail <n> [type]\e[0m: Keep last n entries in a file.\n"
	printf "  \e[1mindex\e[0m: Index the corpus.\n"
	printf "  \e[1mextract\e[0m: Extract candidates from the corpus.\n"
	printf "  \e[1mcount <source>\e[0m: Count individual frequencies of candidate words in a corpus.\n"
	printf "  \e[1mfilter <source> <cmp> <n>\e[0m: Filter candidates by their frequency in a corpus.\n"
	printf "  \e[1massociation [measure...]\e[0m: Compute association measures for candidates.\n"
	printf "  \e[1msort [-a] <feature>\e[0m: Sort candidates by a feature.\n"
	printf "  \e[1mfeatures\e[0m: Show all meta-features in a candidates file.\n"
	printf "  \e[1mannotate\e[0m: Annotate candidates according to the reference.\n"
	printf "  \e[1mcontrast [-a] <source> [measure...]\e[0m: Compute contrast measures for candidates.\n"
	printf "  \e[1mmap\e[0m: Calculate Mean Average Precision for candidates.\n"
	printf "\n"
	printf "\e[1m<type>\e[0m is one of \e[1mcorpus\e[0m, \e[1mpatterns\e[0m or \e[1mcandidates\e[0m.\n"
	printf "When not specified, the last file used is implicitly selected.\n"
	printf "\e[1m<source>\e[0m is one of \e[1mcorpus\e[0m, \e[1mgoogle\e[0m, or \e[1myahoo\e[0m.\n"
	printf "\e[1m<cmp>\e[0m is a comparison operator (eq, ne, lt, le, gt, ge).\n"
	printf "\n"
}

_load_metadata() {
	[[ -f "$PROJMETADATA" ]] && . "$PROJMETADATA"
}

_save_metadata() {
	for var in CORPUS_SRC PATTERNS_SRC REFERENCE_SRC CORPUS_INDEXED; do
		printf "%s=%q\n" "$var" "${!var}"
	done >"$PROJMETADATA"
}

create-project() {
	local usage="Usage: create-project [<directory> [-n]]\n  \e[1m-n\e[0m option: do not enter into the project folder\n"

	local dir opts=()
	[[ $# -eq 2 && $2 == -n ]] && {
		opts+=(-n)
		set -- "$1"
	}

	if [[ $# -eq 1 ]]; then
		dir="$1"
		if [[ -d $dir ]]; then
			printf "Project already exists; will open instead of creating.\n"
		else
			mkdir "$dir" || {
				printf "Could not create project directory \"%s\"!\n" "$dir"
				return 1
			}
		fi
	elif [[ $# -eq 0 ]]; then
		dir="$(mktemp -dt "mweconsole.XXXXXXXXXX")" || {
			printf "Could not create temporary project directory!\n"
			return 1
		}
		opts+=(-n)
	else
		printf "$usage"
		return 1
	fi

	open-project "$dir" "${opts[@]}"
}


open-project() {
	local usage="Usage: open-project <directory> [-n]\n  \e[1m-n\e[0m option: do not enter into the project folder\n"

	[[ $# -eq 1 || ( $# -eq 2 && $2 == -n ) ]] || {
		printf "$usage"
		return 1
	}

	local dir="$1"
	[[ -d $dir ]] || {
		_confirm "Directory \"%s\" does not exist. Create?" "$dir" || return 1
		create-project "$@"
		return
	}

	PROJDIR="$(readlink -e "$dir")"

	[[ $2 == -n ]] || {
		cd "$dir" || {
			printf "Error entering project directory!\n"
			return 1
		}
	}

	[[ -e "$PROJDIR/dtd" ]] || ln -s "$MWETOOLKITDIR/dtd" "$PROJDIR/dtd" || return 1
	[[ -d "$PROJDIR/index" ]] || mkdir "$PROJDIR/index" || return 1
	
	CORPUS_SRC=()
	PATTERNS_SRC=()
	REFERENCE_SRC=()
	# CANDIDATES_SRC=()

	CORPUS="$PROJDIR/corpus.xml"
	PATTERNS="$PROJDIR/patterns.xml"
	CANDIDATES="$PROJDIR/candidates.xml"
	REFERENCE="$PROJDIR/reference.xml"
	TMPFILE="$PROJDIR/tmpfile"
	INDEXBASE="$PROJDIR/index/corpus"
	PROJMETADATA="$PROJDIR/mweconsole.rc"

	CORPUS_INDEXED=
	LAST_TOUCHED=

	_load_metadata
	_readfeatures
	return 0
}

save-project() {
	local usage="Usage: save-project <directory> [-n]\n  \e[1m-n\e[0m option: do not enter into the project folder\n"

	[[ $# -eq 1 || ( $# -eq 2 && $2 == -n ) ]] || {
		printf "$usage"
		return 1
	}

	local dir="$1"
	if [[ -d $dir ]]; then
		_confirm "Directory \"%s\" already exists. Overwrite?" || return 1
	else
		mkdir "$dir" || return 1
	fi

	cp -R "$PROJDIR"/* "$dir"
	open-project "$@"
}

_start() {
	PS1="(mwe) \W> "

	PRG="$(readlink -e "$BASH_SOURCE")"
	[[ $PRG == */* ]] || PRG="./$PRG"
	PRGDIR="$(dirname "$PRG")"

	printf "Looking for mwetoolkit:\n"
	for MWETOOLKITDIR in "$PRGDIR" "$PRGDIR/.." "$PRGDIR/../.." ""; do
		[[ $MWETOOLKITDIR ]] || {
			printf "Could not find mwetoolkit!\n"
			exit 1
		}

		MWETOOLKITDIR="$(readlink -e "$MWETOOLKITDIR")"

		printf "  $MWETOOLKITDIR... "
		if [[ -d $MWETOOLKITDIR/bin ]]; then
			printf "ok!\n"
			break
		else
			printf "no\n"
		fi
	done
	BIN="$MWETOOLKITDIR/bin"

	#printf "Creating temporary project folder... "
	#PROJDIR="$(mktemp -dt "mweconsole.XXXXXXXXXX")" || {
	#	printf "failed!\n"
	#	exit 1
	#}
	#printf "ok!\n"
	#ln -s "$MWETOOLKITDIR/dtd" "$PROJDIR/dtd"
	#mkdir "$PROJDIR/index"

	create-project || exit 1

	printf "\n"
	printf "mweconsole %s, %s\n" "${mweconsole_version[@]}"
	printf "This is a bash prompt augmented with mweconsole-specific commands.\n"
	printf "Type \e[1mhelp\e[0m for help on usage.\n"
	#printf "Type \e[1mguess\e[0m to make mweconsole try to guess what to do\n"
	#printf "based on the files it finds on current directory.\n"
	printf "Type \e[1mexit\e[0m to exit mweconsole.\n"
	printf "\n"
}

_loadfile() {
	local srcvar="$1" dest="$2" typename="$3" dtd="$4" command="$5"
	shift 5

	if [[ $# -eq 0 ]]; then
		if [[ ${!srcvar} ]]; then
			local srcvar_all="$srcvar[*]"
			printf "Current $typename: %s\n" "${!srcvar_all}"
		else
			printf "No $typename selected. Use \e[1m$command <filename>\e[0m to select one.\n"
		fi
	elif [[ $# -eq 1 ]]; then
		[[ -f $1 ]] || {
			printf "File \"%s\" does not exist!\n" "$1"
			return 1
		}

		grep -q "<!DOCTYPE.*mwetoolkit-$dtd\.dtd" -- "$1" || {
			_confirm "\e[1mWarning:\e[0m File \"%s\" seems not to contain a $typename DOCTYPE. Continue?" "$1" || return 1
		}

		cp "$1" "$dest" || {
			printf "Error copying $typename file!\n"
			return 1;
		}

		setvar "$srcvar" "$1"
		_save_metadata
		return 0
	else
		printf "Usage: corpus [filename]\n"
	fi
	return 2
}

corpus() {
	LAST_TOUCHED="corpus"
	CORPUS_INDEXED=
	_loadfile CORPUS_SRC "$CORPUS" "corpus" "corpus" "corpus" "$@" || return
	printf "Corpus file \"%s\" selected. Use \e[1mindex\e[0m to index it.\n" "$CORPUS_SRC"
}

pattern() {
	LAST_TOUCHED="pattern"
	_loadfile PATTERNS_SRC "$PATTERNS" "pattern file" "patterns" "pattern" "$@" || return
	printf "Pattern file \"%s\" selected.\n" "$PATTERNS_SRC"
}

patterns() { pattern "$@"; }

candidates() {
	LAST_TOUCHED="candidates"
	printf "Nothing happens!\n"
}

reference() {
	# LAST_TOUCHED="reference"
	_loadfile REFERENCE_SRC "$REFERENCE" "reference file" "dict" "reference" "$@" || return
	printf "Reference file \"%s\" selected.\n" "$REFERENCE_SRC"
}

_selectfile() {
	type="$1"
	[[ $type ]] || type="$LAST_TOUCHED"
	
	case "$type" in
		corp*) file="$CORPUS"; type="corpus" ;;
		cand*) file="$CANDIDATES"; type="candidate file" ;;
		pat*) file="$PATTERNS"; type="pattern file" ;;
		"") printf "No file specified and none selected!\n"; return 1 ;;
		*) printf "$usage"; return 1 ;;  ## Assume $usage leaked from caller?
	esac

	[[ -f $file ]] || {
		printf "Selected file does not exist!\n"
		return 2
	}
}	

_headtail() {
	local operation="$1"; shift
	local first_or_last
	case "$operation" in
		head) first_or_last="first" ;;
		tail) first_or_last="last" ;;
		*) printf "_headtail: Invalid operation \"$operation\"!\n"; return 1 ;;
	esac

	local type file num
	local usage="Usage: $operation <number-of-entries> [corpus|pattern|candidates]\n"
	if [[ $# -eq 0 || $# -ge 3 || $1 == *[^0-9]* ]]; then
		printf "$usage"
		return 1
	fi

	num="$1"; shift
	_selectfile "$@" || return

	mv "$file" "$TMPFILE"
	python "$BIN/$operation.py" -n "$num" "$TMPFILE" >"$file" || {
		printf "Error filtering file!\n"
		mv "$TMPFILE" "$file"
		return 1
	}
	printf "Kept only $first_or_last $num entries of $type.\n"
}

head() { _headtail head "$@"; }
tail() { _headtail tail "$@"; }

wc() {
	local type file
	_selectfile "$@" || return

	python "$BIN/wc.py" "$file"
}

index() {
	python "$BIN/index.py" -v -i "$INDEXBASE" "$CORPUS" || {
		printf "Error indexing corpus!\n"
		return 1
	}
	printf "Corpus file indexed. Now you can use \e[1mextract\e[0m to extract candidates.\n"
	CORPUS_INDEXED=yes
	_save_metadata
}

extract() {
	local opts=()

	[[ $CORPUS ]] || {
		printf "No corpus file selected! Use \e[1mcorpus <filename>\e[0m to select one.\n"
		return 1
	}
	[[ $PATTERNS ]] || {
		printf "No pattern file selected! Use \e[1mpettern <filename>\e[0m to select one.\n"
		return 1
	}

	# Change working directory so that the pathname does not appear in corpus name.
	(
		cd "$(dirname "$CORPUS")" || return 1
		if [[ $CORPUS_INDEXED ]]; then
			opts+=(-i "$INDEXBASE")
		else
			printf "Corpus not indexed; extracting directly from XML instead.\n"
			printf "You can use \e[1mindex\e[0m to index it.\n"
			opts+=("${CORPUS##*/}")
		fi
		python "$BIN/candidates.py" -v -p "$PATTERNS" "$@" "${opts[@]}" >"$CANDIDATES" || {
			printf "Error extracting candidates!\n"
			return 1
		}
	)

	LAST_TOUCHED="candidates"
	printf "Candidates extracted.\n"
}

count() {
	local countopts=()
	local usage="Usage: count {corpus|google|yahoo}\n"

	[[ $# -le 1 ]] || {
		printf "$usage"
		return 1
	}
	[[ $# -eq 0 ]] && printf "No source specified; assuming \"corpus\".\n"

	case "$1" in
		corpus|"") countopts+=(-i "$INDEXBASE") ;;
		google) countopts+=(-w) ;;
		yahoo) countopts+=(-y) ;;
		# *) countopts+=(-i "$1") ;;
		*) printf "$usage"; return 1 ;;
	esac

	python "$BIN/counter.py" -v "${countopts[@]}" "$CANDIDATES" >"$TMPFILE" || {
		printf "Error counting word frequencies!\n"
		return 1
	}
	mv "$TMPFILE" "$CANDIDATES"

	printf "Individual word frequencies counted.\n"
}

filter() {
	local usage="Usage: filter <source> {eq|ne|lt|le|gt|ge} <value>\n"
	usage+="<source> is one of \e[1mcorpus\e[0m, \e[1mgoogle\e[0m or \e[1myahoo\e[0m.\n"
	usage+="You must use \e[1mcount <source>\e[0m before using \e[1mfilter\e[0m.\n"
	local opts=()
	local source="$1" op="$2" value="$3"

	[[ $# -ne 3 || $3 == *[^0-9]* ]] && {
		printf "$usage"
		return 1
	}

	case "$2" in
		eq) op="=="; opts+=(-e "$1:$3") ;;
		ne) op="!="; opts+=(-e "$1:$3" -r) ;;
		ge) op=">="; opts+=(-t "$1:$3") ;;
		lt) op="<" ; opts+=(-t "$1:$3" -r) ;;
		gt) op=">" ; opts+=(-t "$1:$(($3+1))") ;;
		le) op="<="; opts+=(-t "$1:$(($3+1))" -r) ;;
		*) printf "$usage"; return 1 ;;
	esac

	_readfeatures
	_elem "$1" "${corpus_names[@]}" || {
		printf "Source \"%s\" not present in candidate file. You might have to use \e[1mcount <source>\e[0m first.\n" "$1"
		return 1
	}

	python "$BIN/filter.py" "${opts[@]}" "$CANDIDATES" >"$TMPFILE" || {
		printf "Error filtering candidates!\n"
		return 1
	}
	mv "$TMPFILE" "$CANDIDATES"

	printf "Kept only candidates with frequency in $1 $op $3.\n"
}

_readfeatures() {
	corpus_names=()
	corpus_sizes=()
	feature_names=()
	feature_types=()


	[[ -f $CANDIDATES ]] || return 1
	eval "$(
		sed -n 's/.*<corpussize name="\([^"]*\)" value="\([^"]*\)".*/\1 \2/p' -- "$CANDIDATES" |
			while read name size; do
				printf "corpus_names+=(%q)\n" "$name"
				printf "corpus_sizes+=(%q)\n" "$size"
			done

		sed -n 's/.*<metafeat name="\([^"]*\)" type="\([^"]*\)".*/\1 \2/p' -- "$CANDIDATES" |
			while read name type; do
				printf "feature_names+=(%q)\n" "$name"
				printf "feature_types+=(%q)\n" "$type"
			done
	)"
}

features() {
	local corpus_format="%-20s %s\n"
	local feature_format="%-20s %s\n"
	local i

	_readfeatures
	printf "Corpora information present in candidates file:\n"
	printf "$corpus_format" "Corpus" "Size"
	for i in "${!corpus_names[@]}"; do
		printf "$corpus_format" "${corpus_names[i]}" "${corpus_sizes[i]}"
	done

	printf "\n"

	printf "Features present in candidates file:\n"
	printf "$feature_format" "Feature" "Type"
	for i in "${!feature_names[@]}"; do
		printf "$feature_format" "${feature_names[i]}" "${feature_types[i]}"
	done

}

association() {
	local usage="Usage: association [<measure>...]\n"
	usage+="\e[1m<measure>\e[0m is one of ${ASSOC_MEASURES//:/, }. Multiple measures can be specified.\n"
	usage+="If no measures are specified, all supported measures are computed.\n"

	local features
	local IFS=":"

	# 0.0.3: When all arguments were made optional, the usage message was never
	# shown. '-h' is asymmetric with other commands. What to do?
	[[ $1 == -h ]] && {
		printf "$usage"
		return 1
	}

	_readfeatures
	[[ ${#corpus_names[@]} -eq 0 ]] && {
		printf "No corpus count present in the candidate file! Use \e[1mcount <source>\e[0m first.\n"
		return 1
	}

	if [[ $# -eq 0 ]]; then
		features="$ASSOC_MEASURES"
	else
		features="$*"
	fi

	# feat_association.py is ill-behaved: it throws the user into Python debug mode
	# at some situation. The temporary solution is closing stdin...
	python "$BIN/feat_association.py" -v -m "$features" "$CANDIDATES" </dev/null >"$TMPFILE" || {
		printf "Error calculating association measures!\n"
		return 1
	}
	mv "$TMPFILE" "$CANDIDATES"

	printf "Association measures calculated.\n"
}

sort() {
	local usage="Usage: sort [-a] <feature>\n"
	usage+="For a list of features present in the candidate file, use \e[1mfeatures\e[0m.\n"

	local opts=()

	[[ $1 == -a ]] && {
		opts+=(-a)
		shift
	}

	[[ $# -eq 1 ]] || {
		printf "$usage"
		return 1
	}

	_readfeatures
	_elem "$1" "${feature_names[@]}" || {
		printf "Feature \"%s\" not present in candidates file! You might have to\n" "$1"
		printf "use \e[1massociation\e[0m first. Use \e[1mfeatures\e[0m to see the features present.\n"
		return 1
	}

	python "$BIN/sort.py" "${opts[@]}" -f "$1" "$CANDIDATES" >"$TMPFILE" || {
		printf "Error sorting candidates file!\n"
		return 1
	}
	mv "$TMPFILE" "$CANDIDATES"
	printf "Candidates file sorted.\n"
}

annotate() {
	[[ -f $REFERENCE ]] || {
		printf "No reference file selected. Use \e[1mreference <filename>\e[0m to select one.\n"
		return 1
	}

	python "$BIN/eval_automatic.py" -v -r "$REFERENCE" "$CANDIDATES" >"$TMPFILE" || {
		printf "Error annotating candidate file based on reference list!\n"
		return 1
	}
	mv "$TMPFILE" "$CANDIDATES"
	printf "Candidates annotated.\n"
}

map() {
	local feat features

	_readfeatures

	local IFS=":"

	[[ ${#feature_names[@]} -eq 0 ]] && {
		printf "No feature present in candidates file! You must use \e[1massociation\e[0m before \e[1mmap\e[0m.\n"
		return 1
	}

	if [[ $# -eq 0 ]]; then
		features="${feature_names[*]}"
	else
		for feat; do
			_elem "$feat" "${feature_names[@]}" || {
				printf "Feature \"%s\" not present in candidates file!\n" "$feat"
				printf "You might have to use \e[1massociation\e[0m first.\n"
				printf "Use \e[1mfeatures\e[0m to see the features present.\n"
				return 1
			}
		done
		features="$*"
	fi

	python "$BIN/map.py" -f "$features" "$CANDIDATES" || {
		printf "Error calculating Mean Average Precision for candidates file!\n"
		printf "You must annotate the file using \e[1mreference <filename>\e[0m\n"
		printf "and then \e[1mannotate\e[0m before using \e[1mmap\e[0m.\n"
	}
}

contrast() {
	local usage="Usage: contrast [-a] <original-source> [<measure>...]\n"
	usage+="\e[1m<measure>\e[0m is one of ${CONTRAST_MEASURES//:/, }. Multiple measures can be specified.\n"
	usage+="If no measures are specified, all supported measures are computed.\n"

	local IFS=":"
	local opts=() original measure measures
	[[ $1 == -a ]] && {
		opts+=(-a)
		shift
	}

	[[ $# -eq 0 ]] && {
		printf "$usage"
		return 1
	}

	original="$1"; shift
	[[ $# -gt 0 ]] && opts+=(-m "$*")

	python "$BIN/feat_contrast.py" -o "$original" "${opts[@]}" "$CANDIDATES" >"$TMPFILE" && [[ -s $TMPFILE ]] || {
		printf "Error calculating contrast measures! You might have to use \e[1mcount\e[0m first.\n"
		return 1
	}

	mv "$TMPFILE" "$CANDIDATES"
	printf "Contrast measures calculated.\n"
}

_main "$@"
