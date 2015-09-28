#!/bin/bash
# This script will do k-fold cross validation on blocked/not blocked data on
# post=level.
# High perplexity would indicate similarities in the language used for blocked/
# not blocked data respectively.

# Adapt the path to the GLMTK binary according to your setup:
glmtk=~/glmt/glmtk
function kFoldXValidation {
  k=$1

  b="blocked"
  nb="notBlocked"

  bTrainingFile=${b}/merged_${b}.txt
  nbTrainingFile=$nb/merged_${nb}.txt

  bQueriesPath=${bTrainingFile}.glmtk/queries/
  nbQueriesPath=${nbTrainingFile}.glmtk/queries/

  logFile=evaluation.log

  # better safe than sorry: remove earlier training and ngram files:
  rm ngram-*                  > /dev/null 2>&1
  rm ${bTrainingFile}         > /dev/null 2>&1
  rm ${nbTrainingFile}        > /dev/null 2>&1
  rm -r ${bQueriesPath}       > /dev/null 2>&1
  rm -r ${nbQueriesPath}      > /dev/null 2>&1

  for ((i=1; i <= ${k}; i++)); do
    for ((j=1; j <= ${k}; j++)); do
      if [[ ${j} == ${i} ]]; then # this will be used for testing
        continue
      fi
      cat ${b}/${b}_${j}.txt   >> ${bTrainingFile}
      cat ${nb}/${nb}_${j}.txt >> ${nbTrainingFile}
    done
    # train:
    echo "[${i}] Training."
    ${glmtk} ${bTrainingFile}  -n 4 -e MKN
    ${glmtk} ${nbTrainingFile} -n 4 -e MKN

    echo "[${i}] Testing"
    # create ngram files for every post and test on them:
                          # trained      testing
    test ${b}  ${i} ${b}  # blocked    + blocked    = true
    test ${nb} ${i} ${b}  # notBlocked + blocked    = false
    ../venv/bin/python3 GLMTKPostprocessor.py "${bQueriesPath}" "${nbQueriesPath}" "b"
                          # trained      testing
    test ${nb} ${i} ${nb} # notBlocked + notBlocked = true
    test ${b}  ${i} ${nb} # blocked    + notBlocked = false
    ../venv/bin/python3 GLMTKPostprocessor.py "${nbQueriesPath}" "${bQueriesPath}" "nb"

    # remove training data from this evaluation
    rm ${bTrainingFile}
    rm ${nbTrainingFile}
  done
  truePositives=`grep ^[0-9] output_b.csv | wc -l`
  falseNegatives=`grep ^- output_b.csv | wc -l`
  echo "[Training:b]  true positives: ${truePositives} false negatives: ${falseNegatives}" | tee -a ${logFile}
  trueNegatives=`grep ^[0-9] output_nb.csv | wc -l`
  falsePositives=`grep ^- output_nb.csv | wc -l`
  echo "[Training:nb] true negatives: ${trueNegatives} false positives: ${falsePositives}" | tee -a ${logFile}
}

function test {
  # Test on the input data as follows:
  # First parameter: will be used as truth. Its test data will be used.
  # Second parameter: the k-th file which is currently left out for testing.
  # Third parameter: will be used for testing together with the 2nd parameter.
  #
  # This method will create the needed n-grams and initiates tests on a per post
  # basis. Actual testing is done in testNGrams.
  trainingFile=$1/merged_$1.txt
  i=$2
  testFile=$3/$3_${i}.txt

  # create ngrams for current sentence:
  python GLMTKPreprocessor.py ${testFile}

  echo "Testing ${testFile}" | tee -a ${logFile}
  for ((j=1; j <= 4; j++)); do
    ${glmtk} ${trainingFile}.glmtk -n ${j} -e MKN -q cond${j} ngram-${j}
  done

  # remove ngram files from this iteration:
  rm ngram-*
}
#################################################################################

echo "Starting 10-fold crossvalidation."
kFoldXValidation 10
