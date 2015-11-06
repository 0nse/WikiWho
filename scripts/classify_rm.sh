#!/bin/bash
#
# Executes the SVM and NB classifier on all timeframes. The classifiers are set
# to work on full text. A confusion matrix is built and moved to the designated
# folder. This is a separate script because the RapidMiner tasks still need some
# data and configuration set up by hand.
#
# Usage: ./classify_rm.sh

#!/bin/bash
function process {
  seconds=$1
  classifier=$2
  path=processed/run9/${seconds}
  mkdir -p ${path}/{{lm,nb,svm}_{all,fw}}

  ~/RapidMiner/scripts/rapidminer '//Local Repository/processes/timeframes/${seconds}/${classifier}'

  truePositives=`extractByLineNumber 52 ${classifier}`
  falsePositives=`extractByLineNumber 53 ${classifier}`
  falseNegatives=`extractByLineNumber 56 ${classifier}`
  trueNegatives=`extractByLineNumber 57 ${classifier}`

  auc_opt=`extractByPattern "AUC (optimistic)" ${classifier}`
  auc=`extractByPattern "AUC" ${classifier}`
  auc_pess=`extractByPattern "AUC (pessimistic)" ${classifier}`

  # create confusion matrix:
  postprocessing/confusionMatrix.sh ${truePositives} ${falsePositives} ${falseNegatives} ${trueNegatives} ${auc_opt} ${auc} ${auc_pess}

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

#             13h,    1d,   1.5d,     2d,   2.5d,     3d,     4d,     5d,     6d
timeframes=(46800, 86400, 129600, 172800, 216000, 259200, 345600, 432000, 518400)

for timeframe in "${timeframes[@]}"; do
  process ${timeframe} svm_all
  process ${timeframe} nb_all
done
