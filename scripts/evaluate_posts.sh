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
  rm ${trainingFile}          > /dev/null 2>&1
  rm perplexityByPost_*_*.txt > /dev/null 2>&1

  for ((i=0; i < ${k}; i++)); do
    for ((j=0; j < ${k}; j++)); do
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
    test ${b}  ${i} ${b}  # blocked    + blocked
    test ${b}  ${i} ${nb} # blocked    + notBlocked
    test ${nb} ${i} ${nb} # notBlocked + blocked
    test ${nb} ${i} ${b}  # notBlocked + notBlocked

    # remove training data from this evaluation
    rm ${bTrainingFile}
    rm ${nbTrainingFile}
  done
}

function test {
  # Test on the input data as follows:
  # First parameter: will be used as truth. Its test data will be used.
  # Second parameter: the k-th file which is currently left out for testing.
  # Third parameter: will be used for testing together with the 2nd parameter.
  #
  # This method will create the needed n-grams and initiates tests on a per post
  # basis. Actual testing is done in testNGrams.
  name=$1
  i=$2
  testName=$3

  trainingFile=${name}/merged_${name}.txt
  testFile=${testName}/${testName}_${i}.txt
  perplexityFile=perplexityByPost_${name}_${testName}.txt

  wordsAmount=`wc -w ${testName} | cut -d ' ' -f1`
  # create ngrams for current sentence:
  python GLMTKPreprocessor.py ${testFile}

  testNGrams ${trainingFile} ${perplexityFile} ${wordsAmount}

  # remove ngram files from this iteration:
  rm ngram-*
}

function testNGrams {
  trainingFile=$1
  perplexityFile=$2
  wordsAmount=$3
  queriesPath=${trainingFile}.glmtk/queries/

  # sum of log values returned by glmtk for all ngrams:
  globalSum=0
  # test on all ngrams and sum up their logarithmic results:
  for ((j=1; j < 5; j++)); do
    echo "Testing ${name}_${i}." | tee -a ${logFile}
    ${glmtk} ${trainingFile}.glmtk -n ${j} -e MKN -q cond${j} ngram-${j}

    # the sed command extracts the filename of the last modified file:
    resultFile=`ls -rtl ${queriesPath} | tail -n 1 | sed -E 's/.*[0-9]{1,2} [0-9]{2}:[0-9]{2} (.*)$/\1/'`
    # take the natural logarithm of the result or return 0 if the value was <= 0:
    sum=`head -n -5 "${queriesPath}${resultFile}" | awk '{ ($NF > 0) ? sum+=log($NF) : sum=0; }
                                                         END { print sum }'`
    globalSum=`python -c "print(${globalSum} + ${sum})"`
  done
  perplexity=`python -c "import math; fraction = -${globalSum} / ${wordsAmount}.; print(math.pow(math.e, fraction))"` # Python 2/3 floating point division

  echo ${perplexity} ${line} >> ${perplexityFile}
}
#################################################################################

echo "Starting 10-fold crossvalidation."
kFoldXValidation 10
