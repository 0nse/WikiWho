#!/bin/bash

function pick {
  fileName=$1
  outputFileName=$2
  amount=$3

  length=`wc -l ${fileName} | cut -f1 -d ' '`
  line=0
  usedRandom=(0)

  for ((i=0; i < ${amount}; i++)); do
    # duplicate free random line generation:
    while (contains ${line} ${usedRandom[@]}); do
      # generate a new random line number:
      bytes=$[1 + $[RANDOM % 4]]
      line=`od -A n -t d -N ${bytes} /dev/urandom`
      line=$((line % length))

      # ensure it's positive:
      if [[ ${line} -lt 0 ]]; then
        line=$((line * -1))
      fi
    done
    usedRandom[${i}]=${line}
    if [[ -z $4 ]]; then
      echo -n $line":" >> ${outputFileName}
    fi
    sed ${line}'q;d' ${fileName} >> ${outputFileName}
  done
}

function contains {
  # Usage: contains "value" "array"
  # Returns true, when the value is in the array.
  local e
  for e in "${@:2}"; do
    if [[ "$e" == "$1" ]]; then
      return 0;
    fi
  done
  return 1
}

function extractRandomSamples {
  # Draw 30 samples (15 each) of blocked and not blocked posts. Print them
  # together with their line number so that it becomes clear where the post
  # originated from.
  tmpFileName="postsForManualEvaluation_tmp.txt"
  pick "run7/blocked.txt" ${tmpFileName} 15
  pick "run7/notBlocked.txt" ${tmpFileName} 15
  sort ${tmpFileName} > postsForManualEvaluation.txt
  rm ${tmpFileName}
}

function createRandomNotBlockedFile {
  # Create a notBlocked file which contains as many entries as blocked.txt.
  # Thus, the result is a balanced, randomly sampled notBlocked file.
  length=`wc -l "run7/blocked.txt" | cut -f1 -d ' '`
  pick "run7/notBlocked.txt" "notBlocked_randomlyBalanced.txt" ${length} "don't print line numbers"
}

case "$1" in
  (sample)
    extractRandomSamples
    exit 0
    ;;
  (balance)
    createRandomNotBlockedFile
    exit 0
    ;;
  (*)
    echo "Usage: $0 {sample|balance}"
    exit 1
    ;;
esac
