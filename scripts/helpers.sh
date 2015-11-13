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
