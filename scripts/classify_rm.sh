#!/bin/bash
#
# Usage: ./classify_rm.sh
#
# Requirements: Data and processes created by
#               dataPreparation/createRapidMinerFiles.sh
#               at least Bash 4 for associative arrays
#
# Executes the SVM and NB classifier on all timeframes. The classifiers are set
# to work on full text. A confusion matrix is built and moved to the designated
# folder. This is a separate script because the RapidMiner tasks still need some
# data and configuration which can be created by running
# dataPreparation/createRapidMinerFiles.sh

#!/bin/bash
function process {
  seconds=$1
  classifier=$2
  timeframesMnemonic=$3
  path=processed/run9/${seconds}
  mkdir -p ${path}/{lm,nb,svm}_all

  ~/RapidMiner/scripts/rapidminer "//Local Repository/processes/timeframes/${seconds}/${classifier}"

  truePositives=`extractByLineNumber 52 ${classifier}`
  falseNegatives=`extractByLineNumber 53 ${classifier}`
  falsePositives=`extractByLineNumber 56 ${classifier}`
  trueNegatives=`extractByLineNumber 57 ${classifier}`

  auc_opt=`extractByPattern "AUC (optimistic)" ${classifier}`
  auc=`extractByPattern "AUC" ${classifier}`
  auc_pess=`extractByPattern "AUC (pessimistic)" ${classifier}`

  case "${classifier}" in
    "nb_all" )
      classifierMnemonic="full text na\\\"{i}ve Bayes";;
    "nb_fw" )
      classifierMnemonic="function words na\\\"{i}ve Bayes";;
    "svm_all" )
      classifierMnemonic="full text SVM";;
    "svm_fw" )
      classifierMnemonic="function words SVM";;
  esac
  # create confusion matrix:
  postprocessing/confusionMatrix.sh "${timeframesMnemonic}" "${classifierMnemonic}" "${truePositives}" "${falsePositives}" "${falseNegatives}" "${trueNegatives}" "${auc_opt}" "${auc}" "${auc_pess}"

  # move LM output:
  mv ~/${classifier}_{auc.per,model.mod,performance} ${path}/${classifier}/
  # move LM confusion matrix:
  mv postprocessing/confusionMatrix.tex ${path}/${classifier}/
}

function extractByLineNumber {
  line=$1
  classifier=$2
  # q;d is a lot faster than -n '${line}p':
  sed ${line}'q;d' ~/${classifier}_performance | sed -r 's/.*<double>(.*)\.0<\/double>$/\1/'
}

function extractByPattern {
  # Extracts the value appearing in an element after a line matching the pattern
  pattern=$1
  classifier=$2
  value=`grep '<string>'"${pattern}"'</string>' -A 1 ~/${classifier}_performance | tail -n 1 | sed -r 's/.*<double>(.*)<\/double>$/\1/'`
  value=`python -c "print(round(${value}, 2))"`
  echo ${value}
}

source helpers.sh
timeframes=(`returnTimeFrames "$1"`)

classifiers=(svm_all nb_all)
if [ -n "$1" ]; then
  classifiers=("${classifiers[0]}" "${classifiers[1]}" svm_fw nb_fw)
fi
# associative arrays are hashed so iterating over the keys will result in some
# (for us) unpredictable order:
timeframesMnemonic=([46800]="13 hours"
                    [86400]="1 day"
                    [129600]="1.5 days"
                    [172800]="2 days"
                    [216000]="2.5 days"
                    [259200]="3 days"
                    [345600]="4 days"
                    [432000]="5 days"
                    [518400]="6 days")

for timeframe in "${timeframes[@]}"; do
  for classifier in "${classifiers[@]}"; do
    process ${timeframe} "${classifier}" "${timeframesMnemonic[${timeframe}]}"
  done
done
