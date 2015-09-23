#!/bin/bash
# WARNING: The "shortened" folder will be deleted with all its contents!
#
# Usage: ./filterEvaluationResultsMin <ANYTHING>
# If ANYTHING is set, AUCs will be calculated respecting 1 to 100 words per
# post maximum Else, AUCs for posts minimum containing 1 to 100 words per
# post are considered.
function filterEvaluationResultsMin {
  fileName=$1
  wordsAmount=$2
  outputDir=$3

  awk -F $'\t' '
  { count = 0;
    split($NF, words, " ");
    for (w in words) {
      count++;
      if ( count == int("'"$wordsAmount"'") ) {
        print $0;
        break;
      }
    }
  }' ${fileName} > ${outputDir}/${fileName}
}

function filterEvaluationResultsMax {
  fileName=$1
  wordsAmount=$2
  outputDir=$3

  awk -F $'\t' '
  { count = 0;
    split($NF, words, " ");
    for (w in words) {
      count++;
      if ( count > int("'"$wordsAmount"'") ) {
        break;
      }
    }
    if ( count <= int("'"$wordsAmount"'") ) {
      print $0;
    }
  }' ${fileName} > ${outputDir}/${fileName}
}
#################################################################################

if [[ -z $1 ]]; then
  echo "Filtering for minimum post length"
else
  echo "Filtering for maximum post length"
fi

outputDir="shortened"

rm -r ${outputDir}
mkdir ${outputDir}

for ((i=2; i < 500; i++)); do
  if [[ -z $1 ]]; then
    filterEvaluationResultsMin output_b.csv  ${i} ${outputDir}
    filterEvaluationResultsMin output_nb.csv ${i} ${outputDir}
  else
    filterEvaluationResultsMax output_b.csv  ${i} ${outputDir}
    filterEvaluationResultsMax output_nb.csv ${i} ${outputDir}
  fi

  ../venv/bin/python3 AUC.py --dir ${outputDir} --positive ${outputDir}/output_b.csv --negative ${outputDir}/output_nb.csv | tee -a ${outputDir}/AUC.log
done

../venv/bin/python3 filterResultsPlotter.py ${outputDir}/AUC.log
