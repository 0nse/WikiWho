#!/bin/bash
# WARNING: The "shortened" folder will be deleted with all its contents!
#
# Usage: ./filterEvaluationResultsMin <ANYTHING>
# If ANYTHING is set, AUCs will be calculated respecting 2 to 500 words per
# post maximum Else, AUCs for posts minimum containing 2 to 500 words per
# post are considered.
# We start with 2, because an empty post would still contain "<EOP>".
function filterEvaluationResultsMin {
  fileName=$1
  wordsAmount=$2
  output=${3}/${fileName/..\//}
  echo $output

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
  }' ${fileName} > ${output}
}

function filterEvaluationResultsMax {
  fileName=$1
  wordsAmount=$2
  output=${3}/${fileName/..\//}

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
  }' ${fileName} > ${output}
}
#################################################################################

if [[ -z $1 ]]; then
  echo "Filtering for minimum post length"
else
  echo "Filtering for maximum post length"
fi

outputDir=shortened
b=output_b.csv
nb=output_nb.csv
log=${outputDir}/AUC.log

rm -r ${outputDir}
mkdir ${outputDir}

for ((i=2; i < 500; i++)); do
  if [[ -z $1 ]]; then
    filterEvaluationResultsMin ../${b}  ${i} ${outputDir}
    filterEvaluationResultsMin ../${nb} ${i} ${outputDir}
    echo "[At least ${i} words]" | tee -a ${log}
  else
    filterEvaluationResultsMax ../${b}  ${i} ${outputDir}
    filterEvaluationResultsMax ../${nb} ${i} ${outputDir}
    echo "[At most ${i} words]" | tee -a ${log}
  fi

  ../../venv/bin/python3 AUC.py --dir ${outputDir} --positive ${outputDir}/${b} --negative ${outputDir}/${nb} | tee -a ${log}
done

../../venv/bin/python3 filterResultsPlotter.py ${log}

# delete temporary files:
rm ${outputDir}/${b}
rm ${outputDir}/${nb}