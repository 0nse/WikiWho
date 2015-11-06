#!/bin/bash
#
# Usage: ./separate.sh ../../processed/run9/deletionRevisions.csv 172800
#        ./separate.sh
#
# Launch this script with the first parameter being the path to the
# deletionDiscussion.csv file and the second the number of seconds until a block
# may have appeared so that it will be counted as a block.
# The awk statements will not only add the prefix <BOP> and suffix <EOP> but also
# trim the post.
#
# All blocked posts will be stored as blocked.txt, all that were never blocked
# to notBlocked_full.txt. The file notBlocked.txt contains as many posts as there
# were blocked ones; randomly sampled from notBlocked_full.txt. These sampled
# posts are used for creating the ten splits.
#
# If no parameter is given, blocked.txt and notBlocked_full.txt are assumed to be
# existent from an earlier run and only random sampling and ten times splitting
# will be done.

# set this directory as current working directory:
cd "$(dirname "$0")"

#################################################################################
# Expects a name like 'blocked' or 'notBlocked' for which there is a
# 'blocked.txt' or 'notBlocked.txt' respectively in the same directory as this
# script.
# Returns the number of lines of the file divided by k rounded down.
function splitKFold {
  name=$1
  fileName=../data/$1.txt
  k=$2
  if [ -z $3 ]; then # $3 is unset
    lines=`wc -l ${fileName} | cut -f1 -d ' '`
    linesByK=$((lines / k)) # floor
  else
    linesByK=$3
  fi

  directory=../data/${name}
  mkdir ${directory}
  currentLine=1

  for ((i=1; i <= ${k}; i++)); do
    lastLine=$((linesByK + currentLine - 1))
    sed -n ${currentLine},${lastLine}p ${fileName} > ${directory}/${name}_${i}.txt
    currentLine=$((lastLine + 1))
  done

  # return the used amount of lines:
  echo $3
  echo ${linesByK}
}
#################################################################################


fileName=$1
# 172800 are two days. If it is unset, it will be assumed that blocked.txt and
# notBlocked_full.txt already exist. In this case, those are being split.
secondsToBlock=$2

rm -r ../data/blocked ../data/notBlocked > /dev/null 2>&1

# blocked:
if [ -n "${secondsToBlock}" ]; then
  awk -F $'\t' '{ seconds=int($6);
                  if (seconds > -1 && seconds < int("'"$secondsToBlock"'")) {
                    gsub(/^ +| +$/, "", $5); # trim string
                    print "<BOP> " $5 " <EOP>"
                  }
                }' ${fileName} > ../data/blocked_full.txt
fi
echo "Wrote blocked_full.txt to disk."

# not blocked:
if [ -n "${secondsToBlock}" ]; then
  awk -F $'\t' '{ seconds=int($6);
                  if (seconds < 0 || seconds >= int("'"$secondsToBlock"'")) {
                    gsub(/^ +| +$/, "", $5); # trim string
                    print "<BOP> " $5 " <EOP>"
                  }
                }' ${fileName} > ../data/notBlocked_full.txt
fi
echo "Wrote notBlocked_full.txt to disk."

# Assuming this script was called by classify_lm.sh, it starts with the lowest
# timeframe and ends with the biggest. Thus, the amount of blocked contributions
# will increase. To make the classifier results comparable, all have to be
# trained on the same sample size. Hence, in the first run, all blocked
# contributions are considered. The later will all use as many blocked
# contributions as the first run, but randomly sampled.
# If this script is called manually, the ${linesFile} can be removed.
linesFile=../data/lines_temporary_file_DO_NOT_DELETE
if [ -f "${linesFile}" ]; then
  numberOfContributions=`head -n 1 ${linesFile}`
  python Balancing.py --lines ${numberOfContributions}
else
  python Balancing.py > ${linesFile}
  # In the first run, notBlocked.txt will be of the same length as
  # blocked_full.txt. Therefore, no sampling is applied to the blocked posts and
  # we can copy it fully to become blocked.txt:
  cp ../data/blocked_full.txt ../data/blocked.txt
fi

lines=`splitKFold "blocked" 10`
echo "Split blocked."
splitKFold "notBlocked" 10 ${lines}
echo "Split not blocked."
