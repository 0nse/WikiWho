#!/bin/bash
# Launch this script with the first parameter being the number of words to
# respect and the second being the output folder. WARNING: The folder will be
# deleted with all its contents!
# The amounts of words is used to filter for a minimum amount of words a post
# must contain.
#
# Usage: ./filterEvaluationResultsMin WORDS_AMOUNT <ANYTHING>
# WORDS_AMOUNT is the limit of number of words. If ANYTHING is set, WORDS_AMOUNT
# will be the maximum post length. Else, it will be the minimum length.
function filterEvaluationResultsMin {
  fileName=$1
  wordsAmount=$2
  outputDir=$3

  awk -F $'\t' '
  { count = 0;
    split($NF, words, " ");
    for (w in words) {
      count++;
      if ( count == "'"$wordsAmount"'" ) {
        print $0;
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
      if ( count > "'"$wordsAmount"'" ) {
        break;
      }
    }
    if ( count <= "'"$wordsAmount"'") {
      print $0;
    }
  }' ${fileName} > ${outputDir}/${fileName}
}
#################################################################################


wordsAmount=$1
outputDir="shortened"

rm -r ${outputDir}
mkdir ${outputDir}

if [[ -z $2 ]]; then
  filterEvaluationResultsMin output_b.csv  ${wordsAmount} ${outputDir}
  filterEvaluationResultsMin output_nb.csv ${wordsAmount} ${outputDir}
else
  filterEvaluationResultsMax output_b.csv  ${wordsAmount} ${outputDir}
  filterEvaluationResultsMax output_nb.csv ${wordsAmount} ${outputDir}
fi

../venv/bin/python3 AUC.py --dir ${outputDir} --positive ${outputDir}/output_b.csv --negative ${outputDir}/output_nb.csv
