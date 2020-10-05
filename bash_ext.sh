# simple python cmd wrapper
function pcalc {
  python -c "print($1)"
}

# pass a file (1st arg), process (2nd arg) the file line by line
# e.g. to merge lines in a file to one line: batch_process <file> "LINES_TMP=\${LINES_TMP}\${LINE}" && echo ${LINES_TMP}
function batch_process {
  for LINE in $( cat $1 ); do eval "$2" ; done
}
