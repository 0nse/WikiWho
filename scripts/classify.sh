#!/bin/bash
#
# Start classification by calling all relevant scripts.
#
# Usage: ./classify.sh

./classify_lm.sh
dataPreparation/createRapidMinerFiles.sh
./classify_rm.sh
