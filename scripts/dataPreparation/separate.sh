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
#
# Exits with 1 if the balanced files do not have the same length.
# Exits with 2 if one of the balanced files is missing.

# set this directory as current working directory:
cd "$(dirname "$0")"

# load getLength method:
source ../helpers.sh


#################################################################################
# Expects a name like 'blocked' or 'notBlocked' for which there is a
# 'blocked.txt' or 'notBlocked.txt' respectively in the same directory as this
# script.
# Returns the number of lines of the file divided by k rounded down.
function splitKFold {
  name="$1"
  fileName=../data/${name}.txt
  k=$2
  if [ -z $3 ]; then # $3 is unset
    lines=`getLength "${fileName}"`
    linesByK=$((lines / k)) # floor
  else
    linesByK=$3
  fi

  directory=../data/${name}
  rm -r "${directory}" > /dev/null 2>&1
  mkdir "${directory}"
  currentLine=1

  for ((i=1; i <= ${k}; i++)); do
    lastLine=$((linesByK + currentLine - 1))
    sed -n ${currentLine},${lastLine}p "${fileName}" > ${directory}/${name}_${i}.txt
    currentLine=$((lastLine + 1))
  done

  # return the used amount of lines:
  echo ${linesByK}
}
#################################################################################

fileName="$1"
# 172800 are two days. If it is unset, it will be assumed that blocked.txt and
# notBlocked_full.txt already exist. In this case, those are being split.
secondsToBlock=$2
isSlidingWindow="$3"
if  [ -z "${isSlidingWindow}" ]; then
  folder=regular
else
  folder=sw
fi

# If this is given, it is assumed that blocked.txt/notBlocked.txt do not exist
# yet. Thus, they are created, split and balanced. When this script is called by
# classify_lm.sh, secondsToBlock will only be given for lm_all but not lm_fw.
# Thus, it is ensured that no additional extraction/balancing is done.
if [ -n "${secondsToBlock}" ]; then
  # only create full files, if the directory does not exist yet and with it
  # these files created by Balancing.py:
  if [ ! -f ../data/regular/blocked_full.txt ]; then
    # blocked:
    awk -F $'\t' '{ seconds=int($6);
                    if (seconds > -1 && seconds < int("'"$secondsToBlock"'")) {
                      gsub(/^ +| +$/, "", $5); # trim string
                      print "<BOP> " $5 " <EOP>"
                    }
                  }' "${fileName}" > ../data/regular/blocked_full.txt
    echo "[I] Wrote blocked_full.txt to disk."
  fi

  if [ ! -f ../data/regular/notBlocked_full.txt ]; then
    # not blocked:
    awk -F $'\t' '{ seconds=int($6);
                    if (seconds < 0 || seconds >= int("'"$secondsToBlock"'")) {
                      gsub(/^ +| +$/, "", $5); # trim string
                      print "<BOP> " $5 " <EOP>"
                    }
                  }' "${fileName}" > ../data/regular/notBlocked_full.txt
    echo "[I] Wrote notBlocked_full.txt to disk."
  fi

  if [ -n "${isSlidingWindow}" ]; then
    # Assuming this script was called by classify_lm.sh, it starts with the lowest
    # timeframe and ends with the biggest. Thus, the amount of blocked contributions
    # will increase. To make the classifier results comparable, all have to be
    # trained on the same sample size. Hence, in the first run, all blocked
    # contributions are considered. The later will all use as many blocked
    # contributions as the first run, but randomly sampled.
    # If this script is called manually, the ${linesFile} can be removed.
    linesFile=../data/lines_temporary_file_DO_NOT_DELETE
    if [ -f ../data/"${folder}"/blocked.txt ] && [ -f ../data/"${folder}"/notBlocked.txt ]; then
      # Balancing.py creates blocked.txt and notBlocked.txt
      numberOfContributions=`head -n 1 "${linesFile}"`
      python Balancing.py -sw --lines ${numberOfContributions}
    else
      python Balancing.py -sw > "${linesFile}"
    fi
  fi
fi
# copy files for processing:
# In the first run, notBlocked.txt will be of the same length as
# blocked_full.txt. Therefore, no sampling is applied to the blocked posts and
# we can copy it fully to become blocked.txt:
cp ../data/"${folder}"/blocked_full.txt ../data/blocked.txt
cp ../data/"${folder}"/blocked.txt ../data/. # not existing when there was no linesFile
cp ../data/"${folder}"/notBlocked.txt ../data/.

# assert that both files are of same length:
echo "[I] Asserting that the generated files are of same length."
statusCode=0
blockedLength=`getLength "../data/blocked.txt"`
statusCode=$(( statusCode + $? ))
notBlockedLength=`getLength "../data/notBlocked.txt"`
statusCode=$(( statusCode + $? ))

if [ ${statusCode} -ne 0 ]; then
  echo "[E] One or both balanced files were missing. Aborting."
  exit 2
fi
if [ "${blockedLength}" -ne "${notBlockedLength}" ]; then
  echo "[E] The files are not of same length. Aborting."
  exit 1
fi

# splitting:
lines=`splitKFold "blocked" 10`
echo "[I] Split blocked."
splitKFold "notBlocked" 10 ${lines}
echo "[I] Split not blocked."
