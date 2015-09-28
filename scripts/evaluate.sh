#!/bin/bash
# This script will do k-fold cross validation on blocked/not blocked data. Low
# perplexity would indicate similarities in the language used for blocked/not
# blocked data respectively.

# Adapt the path to the GLMTK binary according to your setup:
glmtk=~/glmt/glmtk

function kFoldXValidation {
  name=$1
  k=$2
  trainingFile=${name}/merged_${name}.txt
  queriesPath=${trainingFile}.glmtk/queries/
  logFile=${name}_evaluation.log
  globalPerplexity=0

  # better safe than sorry: remove earlier training and ngram files:
  rm ngram-* > /dev/null 2>&1
  rm ${trainingFile} > /dev/null 2>&1

  for ((i=1; i <= ${k}; i++)); do
    for ((j=1; j <= ${k}; j++)); do
      if [[ ${j} == ${i} ]]; then # this will be used for testing
        continue
      fi
      cat ${name}/${name}_${j}.txt >> ${trainingFile}
    done
    # train on ${output}:
    echo "Training." | tee -a ${logFile}
    ${glmtk} ${trainingFile} -n 4 -e MKN

    # create ngram files:
    python GLMTKPreprocessor.py ${name}/${name}_${i}.txt

    globalSum=0
    # test on all ngrams and sum up their logarithmic results:
    for ((j=1; j < 5; j++)); do
      echo "Testing ${name}_${i}." | tee -a ${logFile}
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

    wordsAmount=`wc -w ${name}/${name}_${i}.txt | cut -d ' ' -f1`
    perplexity=`python -c "import math; fraction = -${globalSum} / ${wordsAmount}.; print(math.pow(math.e, fraction))"` # Python 2/3 floating point division
    globalPerplexity=`python -c "print(${globalPerplexity} + ${perplexity})"`

    echo "Perplexity for ${name}_${i}: " ${perplexity} "  Sum: " ${globalSum} " Word amount: " ${wordsAmount} | tee -a ${logFile}

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
kFoldXValidation "blocked" 10
echo "Starting 10-fold crossvalidation by building LMs on posts, which have not been blocked."
kFoldXValidation "notBlocked" 10
