#!/bin/bash
#
# Requires: at least Bash 4 for associative arrays
#
# Executes the LM classifier on all timeframes. The classifier is set to work on
# full text. A confusion matrix is built and moved to the designated folder. AUCs
# are calculated and plotted. For the other classifiers using RapidMiner, see
# classify_rm.sh.
#
# Usage: ./classify_lm.sh
#        ./classify_lm.sh 86400
#        ./classify_lm.sh 86400 somethingSomething
#
# A parameter (seconds) can be parsed (e.g. 86400) if only one timeframe should
# be tested. It must be known to this script (see timeframeMnemonic). The size
# of blocked.txt and notBlocked.txt will be set to |blocked_full.txt| in this
# case.
# If a third parameter is passed, the sliding window approach  will be used.

# getLength and returnTimeFrames:
source helpers.sh
# set this directory as current working directory:
cd "$(dirname "$0")"

function process {
  seconds=$1
  classifier=$2
  timeframeMnemonic=$3
  isSlidingWindow="$4"
  path=processed/run9/${seconds}
  sourcePath=../processed/run9/

  if [ "${classifier}" = "lm_all" ]; then
    mkdir -p ${path}/{lm,nb,svm}_all
  else
    mkdir -p ${path}/{lm,nb,svm}_fw
  fi

  # Create blocked.txt and notBlocked.txt without anything other than function
  # words. This method only works, if this function has already run at least once
  # for this value of ${seconds}. That is: ${classifier} = lm_all must be
  # executed before lm_fw!
  if [ ${classifier} = "lm_fw" ]; then
    for class in {b,notB}locked; do
      fileFW=data/"${class}".txt
      fileFull="${path}"/"${class}".txt
      python dataPreparation/NonFunctionWordsFilter.py ${fileFull} ${fileFW}
    done
    # we drop empty lines (did not contain any function word). Thus, we need to
    # rebalance manually. We don't check for exit codes because separate.sh will
    # already fail if the lengths don't match.
    blockedLength=`getLength data/blocked.txt`
    notBlockedLength=`getLength data/notBlocked.txt`
    # Our rebalancing is naive and removes the last n lines of the longer file.
    # The files are most likely randomly sampled anyways, so that's fine.
    if [ ${blockedLength} -ge ${notBlockedLength} ]; then
      lastLine=$(( notBlockedLength + 1 ))
      sed -i ${lastLine},${blockedLength}d data/blocked.txt
    else
      lastLine=$(( blockedLength + 1 ))
      sed -i ${lastLine},${notBlockedLength}d data/notBlocked.txt
    fi
    # split with already existing blocked files:
    dataPreparation/separate.sh
  else # lm_all:
    if [ -n "${isSlidingWindow}" ]; then
      # call separate.sh only after the data has been prepared. This is done
      # only in the lm_all branch because lm_fw will reuse the files created in
      # this iteration.

      # sort by users if not done already:
      if [ ! -f "${sourcePath}"userSortedDeletionRevisions.csv ]; then
        sort -t$'\t' -k3,3 -k1,1n "${sourcePath}"deletionRevisions.csv -o "${sourcePath}"userSortedDeletionRevisions.csv
      fi
      ../venv/bin/python dataPreparation/SlidingWindowExtraction.py
    fi
    # Split into ten parts each for 10-fold cross validation:
    dataPreparation/separate.sh ../"${sourcePath}"deletionRevisions.csv ${seconds} "${isSlidingWindow}"
  fi

  if [ $? -ne 0 ]; then
    # This will be 1 if the balancing did not work. set -e is not an option for
    # this script, because, e.g. rm will return 1 when a file to delete does not
    # exist.
    rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1
    exit 1
  fi
  # start language model on data. The parameter is used for later LaTeX table
  # genration:
  echo "[I] Process ${classifier} (${seconds}s) starts."
  lm/evaluate_posts.sh "${timeframeMnemonic}"
  # move data files. Rename, when function words are also considered:
  if [ ${classifier} = "lm_fw" ]; then
    for class in {b,notB}locked; do
      # function words
      fileFW=data/"${class}".txt
      mv "${fileFW}" "${path}"/"${class}"_fw.txt
    done
  else
    mv data/{b,notB}locked{,_full}.txt "${path}"/
  fi
  # move LM output:
  mv data/output_{n,}b.csv "${path}"/${classifier}/
  # move LM log:
  mv lm/evaluation.log "${path}"/${classifier}/
  # move LM confusion matrix:
  mv postprocessing/confusionMatrix.tex "${path}"/${classifier}/
  # move LM AUC data:
  mv AUC/auc*.png "${path}"/${classifier}/
}

# This file is used by separate.sh to make sure that we have the same sample
# size in all runs and thus comparable results:
rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1

timeframes=(`returnTimeFrames "$1"`)
isSlidingWindow="$2"
classifiers=(lm_all)
# If a parameter was passed, we also want to check for function words.
if [ -n "$1" ]; then
  classifiers=("${classifiers[0]}" lm_fw)
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
    process ${timeframe} "${classifier}" "${timeframesMnemonic[${timeframe}]}" "${isSlidingWindow}"
    # store the lm n-gram results:
    for class in {b,notB}locked; do
      mv data/"${class}"/merged_"${class}".txt.glmtk/queries processed/run9/"${timeframe}"/"${classifier}"/"${class}"Queries
    done
  done
done

rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1
