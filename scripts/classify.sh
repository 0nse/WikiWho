#!/bin/bash
#
# Start classification by calling all relevant scripts.
#
# Usage: ./classify.sh

path=processed/run9/

echo "To start the classification process, all files in  ${path} will be deleted."
echo "Moreover, the data and processes in RapidMiner's repository/{processes,data}/timeframes will be overwritten."
read -p "Are you sure, you want to continue? [y/N] " -r

if [[ $REPLY =~ ^[Yy]$ ]]
then
  rm -r ${path} > /dev/null 2>&1
  ./classify_lm.sh
  dataPreparation/createRapidMinerFiles.sh
  ./classify_rm.sh
  # LaTeX stubs creation:
  postprocessing/embedConfusionMatrices.sh
  python postprocessing/TimeframeResultsExtraction.py
fi
