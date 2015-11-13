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
#
# A parameter (seconds) can be parsed (e.g. 86400) if only one timeframe should
# be tested. It must be known to this script (see timeframeMnemonic). The size
# of blocked.txt and notBlocked.txt will be set to |blocked_full.txt| in this
# case.

function process {
  seconds=$1
  classifier=$2
  timeframeMnemonic=$3
  path=processed/run9/${seconds}
  mkdir -p ${path}/{lm,nb,svm}_all

  dataPreparation/separate.sh ../../processed/run9/deletionRevisions.csv ${seconds}
  if [ $? -ne 0 ]; then
    # This will be 1 if the balancing did not work. set -e is not an option for
    # this script, because, e.g. rm will return 1 when a file to delete does not
    # exist.
    rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1
    exit 1
  fi
  # start language model on data. The parameter is used for later LaTeX table
  # genration:
  lm/evaluate_posts.sh "${timeframeMnemonic}"
  # move data files:
  mv data/{blocked,notBlocked}{,_full}.txt ${path}/
  # move LM output:
  mv data/output_{n,}b.csv ${path}/${classifier}/
  # move LM log:
  mv lm/evaluation.log ${path}/${classifier}/
  # move LM confusion matrix:
  mv postprocessing/confusionMatrix.tex ${path}/${classifier}/
  # move LM AUC data:
  mv AUC/auc*.png ${path}/${classifier}/
}

# This file is used by separate.sh to make sure that we have the same sample
# size in all runs and thus comparable results:
rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1

source helpers.sh
timeframes=(`returnTimeFrames "$1"`)
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
  process ${timeframe} lm_all "${timeframesMnemonic[${timeframe}]}"
done

rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1
