#!/bin/bash
# This script will train on blocked/not blocked data and test with not blocked/
# blocked data respectively. High perplexities would indicate a measurable
# difference between the language of blocked and not blocked posts.

# Adapt the path to the GLMTK binary according to your setup:
glmtk=~/glmt/glmtk

function testAgainstOppositeData {
  name=$1
  k=$2
  trainingFile=${name}/merged_${name}.txt
  queriesPath=${trainingFile}.glmtk/queries/
  logFile=${name}_evaluation.log
  globalPerplexity=0

  # test data will be of the opposite type:
  if [[ ${name} == "blocked" ]]; then
    testName="notBlocked"
  else
    testName="blocked"
  fi

  # better safe than sorry: remove earlier training and ngram files:
  rm ngram-* > /dev/null 2>&1
  rm ${trainingFile} > /dev/null 2>&1

  # concatenate all data of type ${testName}:
  for ((i=0; i < ${k}; i++)); do
    cat ${name}/${name}_${i}.txt >> ${trainingFile}
  done
  # train on ${output}:
  echo "Training." | tee -a ${logFile}
  ${glmtk} ${trainingFile} -n 4 -e MKN

  for ((i=0; i < ${k}; i++)); do
    # create ngram files:
    echo "Training." | tee -a ${logFile}
    python GLMTKPreprocessor.py ${testName}/${testName}_${i}.txt

    globalSum=0
    wordsAmount=0
    # test on all ngrams and sum up their logarithmic results:
    for ((j=1; j < 5; j++)); do
      echo "Testing ${testName}_${i} against model of opposite type." | tee -a ${logFile}
      ${glmtk} ${trainingFile}.glmtk -n ${j} -e MKN -q cond${j} ngram-${j}

      # the sed command extracts the filename of the last modified file:
      resultFile=`ls -rtl ${queriesPath} | tail -n 1 | sed -E 's/.*[0-9]{1,2} [0-9]{2}:[0-9]{2} (.*)$/\1/'`
      # all values for all grams are being added up:
      sum=`head -n -5 "${queriesPath}${resultFile}" | awk '{ if ($NF > 0) {
                                                                 sum+=log($NF)
                                                              }
                                                            }
                                                            END  { print sum }'`
      globalSum=`python -c "print(${globalSum} + ${sum})"`
    done

    wordsAmount=`wc -w ${testName}/${testName}_${i}.txt | cut -d ' ' -f1`
    perplexity=`python -c "import math; fraction = -${sum} / ${wordsAmount}.; print(math.pow(math.e, fraction))"` # Python 2/3 floating point division
    globalPerplexity=`python -c "print(${globalPerplexity} + ${perplexity})"`

    echo "Perplexity for ${testName}_${i} (opposite type): " ${perplexity} "  Sum: " ${sum} " Word amount: " ${wordsAmount} | tee -a ${logFile}
    python -c "print(-$globalSum / $wordsAmount.)"

    # remove training data from this evaluation
    rm ${trainingFile}
    # remove ngram files from previous iteration:
    rm ngram-*
  done

  globalPerplexity=`python -c "print(${globalPerplexity} / 10.)"`
  echo "Global perplexity: " ${globalPerplexity} | tee -a ${logFile}
}
#################################################################################


echo "Starting 10-fold crossvalidation by building LMs on blocked posts."
testAgainstOppositeData "blocked" 10
echo "Starting 10-fold crossvalidation by building LMs on posts, which have not been blocked."
testAgainstOppositeData "notBlocked" 10
