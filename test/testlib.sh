#! /bin/bash

set -o nounset    # Using "$UNDEF" var raises error
set -o errexit    # Exit on error, do not continue quietly
exec </dev/null   # Don't hang if a script tries to read from stdin

t_TOOLKIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
t_BIN="$t_TOOLKIT/bin"
t_SHARED="$t_TOOLKIT/test/input-corpora"


# t_echo_bold txt
# Print $txt in bold.
t_echo_bold() { printf "\e[1m%s\e[0m\n" "$1"; }

# t_echo_rgb rgb txt
# Print $txt in colors (0 <= $rgb <= 7; r=1,g=2,b=4).
t_echo_rgb() { printf "\e[$((30+$1))m%s\e[0m\n" "$2"; }

# t_echo_bold_rgb rgb txt
# Print $txt in bold and in colors (See `t_echo_rgb`).
t_echo_bold_rgb() { t_echo_bold "$(t_echo_rgb "$@")"; }


# t_warn message
# Print "WARNING: $message"
t_warn() { t_echo_bold_rgb 1 "WARNING: $1"; }

# t_error message
# Print "ERROR: $message"
t_error() { t_echo_bold_rgb 1 "ERROR: $1"; }



# t_testname test_name
# Print "num: test_name" in bold
t_testname() {
    _THIS_TEST_NAME="$1"
    _THIS_TEST_NUM="$((${_THIS_TEST_NUM:-}+1))"
    t_echo_bold "$_THIS_TEST_NUM: $_THIS_TEST_NAME"
}


# t_run command_and_args
# Run command with given args.
# Also echoes the command on screen.
# Respects env-var `quiet`.
t_run() {
    if test "${quiet:-0}" -eq 0; then
        t_echo_bold_rgb 3 "$@"
    fi
    eval "$@"
}


# t_xml_to_sorted_txt xml_in txt_out
# Convert XML into TXT with sorted sentences.
t_xml_to_sorted_txt() {
    local _INPUT="$1"; local _OUTPUT="$2"
    t_run "python $t_BIN/xml2csv.py $_INPUT | cut -f 2 | tail -n +2 | sort >$_OUTPUT"
}


# t_diff [diff_args...] text_a text_b
# Diff between text_a and text_b.
# Uses wdiff if available.
t_diff() {
    if hash "wdiff" 2>/dev/null; then
        diff -u "$@" | wdiff -d --terminal
    else
        if ! test "${_WARNED_WDIFF+set}"; then
            t_warn "wdiff is not installed; using diff"
            _WARNED_WDIFF=1
        fi
        diff -u "$@"
    fi
}


# t_compare txt_ref txt_in
# Compare `txt_in` to reference `txt_ref` and output differences.
t_compare() {
    local txt_ref="$1"
    local txt_in="$2"

    if ! test -f "$txt_ref"; then
        t_warn "not found: $txt_ref"

    else
        local error=0
        t_diff "$txt_ref" "$txt_in" || error=1

        if test "$error" -ne 0; then
            t_backtrace
            t_echo_bold_rgb 1 "Test $_THIS_TEST_NUM: FAILED!"
        else
            t_echo_bold_rgb 2 "OK."
        fi

        return "$error"
    fi
}


# t_backtrace
# Print a stack backtrace of calling functions.
t_backtrace() {
    echo "------------------------------------"
    echo "Shell backtrace (most recent first):"
    if test "${BASH_VERSION+set}"; then
        local N="${#BASH_LINENO[@]}"
        for I in `seq 0 $((N-2))`; do
            echo "  In ${FUNCNAME[$((I+1))]} at" \
                "${BASH_SOURCE[$((I+1))]}:${BASH_LINENO[$I]}"
        done
    else
        echo "  Unable to get a backtrace (shell=$SHELL)"
        echo "  Use 'bash' for better output."
    fi
}
