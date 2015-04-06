#! /bin/bash
HERE="$(cd "$(dirname "$0")" && pwd)"

set -o nounset    # Using "$UNDEF" var raises error
set -o errexit    # Exit on error, do not continue quietly

usage_exit() { {
    echo "Usage: $(basename "$0") [-h]"
    echo "Compare files in 'reference-output' with the ones in 'output'."
    echo ""
    echo "If the REPLACE_REFERENCES environment variable is set,"
    echo "will also replace the references by the corresponding outputs."
    exit 1
} 1>&2;
}

test "$#" -ne 0  && usage_exit


########################################

find -type d | while read dir; do
    if test -d "$dir/output" && test -d "$dir/reference-output"; then
        (cd "$dir/reference-output" && find -type f) | while read name; do
            ref_path="$dir/reference-output/$name"
            out_path="$dir/output/$name"
            if test -f "$out_path"; then
                if ! cmp -s "$out_path" "$ref_path"; then
                    if test "${REPLACE_REFERENCES+set}"; then
                        echo -e "Replacing bad reference in $dir: $name"
                        cp "$out_path" "$ref_path"
                    else
                        echo -e "Bad match in $dir: $name"
                    fi
                fi
            fi
        done
    fi
done
