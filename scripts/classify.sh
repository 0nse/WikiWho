#!/bin/bash
#
# Start classification by calling all relevant scripts.
#
# Usage: ./classify.sh
#        will help you determine the best performing timeframe
#        ./classify.sh 86400
#        will evaluate the performance for the amount of seconds specified
#        ./classify.sh 86400 somethingSomething
#        will evaluate the performance for the amount of seconds specified using
#        the sliding window approach. The parameter value is ignored.
#
# The seconds parameter must be known to the scripts (see timeframesMnemonic).

function classify {
  seconds=$1
  isSlidingWindow="$2"

  echo "[I] Preparing files and doing LM classifcation."
  ./classify_lm.sh ${seconds} "${isSlidingWindow}"
  if [ $? -ne 0 ]; then
    # This will be 1 if the balancing did not work. set -e is not an option for
    # this script, because, e.g. rm will return 1 when a file to delete does not
    # exist.
    exit 1
  fi
  # cleanup data from last run:
  rm -r data/{notB,b}locked

  echo "[I] Converting data for RapidMiner and creating RapidMiner processes."
  dataPreparation/createRapidMinerFiles.sh ${seconds}

  echo "[I] Classifying using SVM and NB classifier."
  ./classify_rm.sh ${seconds}

  echo "[I] Transforming results into LaTeX tables and creating performance charts"
  if [ -n "${seconds}" ]; then
    ../venv/bin/python postprocessing/TimeframeResultsExtraction.py ${seconds}

    mv data/relativePerformance_*.png processed/run9/${seconds}/.
    mv data/performanceComparison_*.png processed/run9/${seconds}/.
  fi

  postprocessing/embedConfusionMatrices.sh ${seconds}
  mv postprocessing/comparison.tex processed/run9/.

  echo "[I] Classifcations executed successfully."
}

path=processed/run9/

echo "To start the classification process, all files in  ${path} will be deleted."
echo "Moreover, the data and processes in RapidMiner's repository/{processes,data}/timeframes will be overwritten."
read -p "Are you sure, you want to continue? [y/N] " -r

seconds=$1
isSlidingWindow="$2"

if [[ $REPLY =~ ^[Yy]$ ]]; then
  rm -r ${path} > /dev/null 2>&1
  # This file can exist, if classify_lm.sh or separate.sh was aborted.
  rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1
  # Remove leftover data files:
  rm -r data/{regular,sw}/{b,notB}locked.txt > /dev/null 2>&1

  if [ -n "${isSlidingWindow}" ]; then
    echo "[I] Starting sliding window classification."
    classify ${seconds} "${isSlidingWindow}"
  fi
  echo "[I] Starting sliding window classification."
  classify ${seconds}
fi
