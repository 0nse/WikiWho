#!/bin/bash

function returnTimeFrames {
  # timeframes is used to keep an order—it is important that 46800 is evaluated
  # first when iterating over all. If a parameter is passed to this script, only
  # the passed parameter's seconds will be processed.
  singleTimeframe=$1
  if [ -n "${singleTimeframe}" ]; then
    timeframes=("${singleTimeframe}")
  else
    # ordered timeframes:
    #             13h,   1d,  1.5d,    2d,  2.5d,    3d,    4d,    5d,    6d
    timeframes=(46800 86400 129600 172800 216000 259200 345600 432000 518400)
  fi

  # return:
  for timeframe in "${timeframes[@]}"; do
    echo "${timeframe}";
  done
}

function getLength {
  # Returns file length and returns a non-zero exit code if the file did not
  # exist.
  fileName=$1
  lines=`wc -l "${fileName}"`
  if [ $? -ne 0 ]; then
    echo "-1"
    return 2
  fi
  echo `echo ${lines} | cut -f1 -d ' '`
}
