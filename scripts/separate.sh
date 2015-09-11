#!/bin/bash
# Launch this script with the first parameter being the path to the
# deletionDiscussion.csv file and the second the number of seconds until a block
# may have appeared so that it will be counted as a block.
# The awk statements will not only add the prefix <BOP> and suffix <EOP> but also
# trim the post.

#################################################################################
# Expects a name like 'blocked' or 'notBlocked' for which there is a
# 'blocked.txt' or 'notBlocked.txt' respectively in the same directory as this
# script.
# Returns the number of lines of the file divided by k rounded down.
function splitKFold {
  name=$1
  fileName=$1.txt
  k=$2
  echo $3
  if [ -z $3 ]; then # $3 is unset
    lines=`wc -l ${fileName} | cut -f1 -d ' '`
    linesByK=$((${lines} / $k)) # floor
  else
    linesByK=$3
  fi

  mkdir ${name}
  currentLine=1

  for ((i=0; i < $k; i++)); do
    sed -n ${currentLine},$((${linesByK}+${currentLine}))p ${fileName} > ${name}/${name}_${i}.txt
    currentLine=$((${linesByK} + ${currentLine}))
  done

  echo ${linesByK}
}
#################################################################################


fileName=$1
secondsToBlock=$2

rm -r blocked notBlocked

# blocked:
awk -F $'\t' '{ seconds=int($6);
                if (seconds > -1 && seconds < "'"$secondsToBlock"'") {
                  gsub(/^ +| +$/, "", $5); # trim string
                  print "<BOP> " $5 " <EOP>"
                }
              }' $fileName > blocked.txt
echo "Wrote blocked to disk, now splitting."
lines=`splitKFold "blocked" 10`
echo "Split. Continuing with not blocked."

# not blocked:
awk -F $'\t' '{ seconds=int($6);
                if (seconds < 0 || seconds >= "'"$secondsToBlock"'") {
                  gsub(/^ +| +$/, "", $5); # trim string
                  print "<BOP> " $5 " <EOP>"
                }
              }' $fileName > notBlocked.txt
splitKFold "notBlocked" 10 ${lines}
