#!/bin/bash
#
# Start classification by calling all relevant scripts.
#
# Usage: ./classify.sh
#        will help you determine the best performing timeframe
#        ./classify.sh 86400
#        will evaluate the performance for the amount of seconds specified
#
# The seconds parameter must be known to the scripts (see timeframesMnemonic).

path=processed/run9/

echo "To start the classification process, all files in  ${path} will be deleted."
echo "Moreover, the data and processes in RapidMiner's repository/{processes,data}/timeframes will be overwritten."
read -p "Are you sure, you want to continue? [y/N] " -r

if [[ $REPLY =~ ^[Yy]$ ]]; then
  rm -r ${path} > /dev/null 2>&1
  # This file can exist, if classify_lm.sh or separate.sh was aborted.
  rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1

  echo "[I] Preparing files and doing LM classifcation."
  ./classify_lm.sh $1
  if [ $? -ne 0 ]; then
    # This will be 1 if the balancing did not work. set -e is not an option for
    # this script, because, e.g. rm will return 1 when a file to delete does not
    # exist.
    exit 1
  fi
  # cleanup data from last run:
  rm -r data/{notB,b}locked

  echo "[I] Converting data for RapidMiner and creating RapidMiner processes."
  dataPreparation/createRapidMinerFiles.sh $1

  echo "[I] Classifying using SVM and NB classifier."
  ./classify_rm.sh $1

  echo "[I] Transforming results into LaTeX tables."
  postprocessing/embedConfusionMatrices.sh $1
  python postprocessing/TimeframeResultsExtraction.py $1

  mv postprocessing/comparison.tex processed/run9/.
  mv data/relativePerformance_*.png processed/run9/.

  echo "[I] Classifcations executed successfully."
fi
