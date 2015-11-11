#!/bin/bash
#
# Start classification by calling all relevant scripts.
#
# Usage: ./classify.sh

path=processed/run9/

echo "To start the classification process, all files in  ${path} will be deleted."
echo "Moreover, the data and processes in RapidMiner's repository/{processes,data}/timeframes will be overwritten."
read -p "Are you sure, you want to continue? [y/N] " -r

if [[ $REPLY =~ ^[Yy]$ ]]; then
  rm -r ${path} > /dev/null 2>&1
  # This file can exist, if classify_lm.sh or separate.sh was aborted.
  rm data/lines_temporary_file_DO_NOT_DELETE > /dev/null 2>&1

  echo "[I] Preparing files and doing LM classifcation."
  ./classify_lm.sh
  if [ $? -ne 0 ]; then
    # This will be 1 if the balancing did not work. set -e is not an option for
    # this script, because, e.g. rm will return 1 when a file to delete does not
    # exist.
    exit 1
  fi

  echo "[I] Converting data for RapidMiner and creating RapidMiner processes."
  dataPreparation/createRapidMinerFiles.sh

  echo "[I] Classifying using SVM and NB classifier."
  ./classify_rm.sh

  echo "[I] Transforming results into LaTeX tables."
  postprocessing/embedConfusionMatrices.sh
  python postprocessing/TimeframeResultsExtraction.py

  echo "[I] Classifcations executed successfully."
fi
