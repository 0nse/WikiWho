#!/bin/bash

function pick {
  fileName=$1

  length=`wc -l ${fileName} | cut -f1 -d ' '`
  line=0
  usedRandom=(0)

  for ((i=0; i < 15; i++)); do
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
    echo -n $line":" >> postsForManualEvaluation_tmp.txt
    sed -n ${line}' p' ${fileName} >> postsForManualEvaluation_tmp.txt
  done
}

function contains {
  local e
  for e in "${@:2}"; do
    [[ "$e" == "$1" ]] && return 0;
  done
  return 1
}

pick "run7/blocked.txt"
pick "run7/notBlocked.txt"
sort postsForManualEvaluation_tmp.txt > postsForManualEvaluation.txt
rm postsForManualEvaluation_tmp.txt
