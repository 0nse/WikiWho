#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Usage: python TimeframeCalculations.py

Requirements: Numpy, Matplotlib

This script requires a sorted input file. You can sort WikiWho's output
deletionRevisions.csv using:
sort -t$'\t' -k3,3 -k1,1n deletionRevisions.csv -o userSortedDeletionRevisions.csv
The file is then sorted by username as first and post creation timestamp as second
sort criterion.
'''

def extractLastPostToBlockDeltas(postsFile='../../processed/run9/userSortedDeletionRevisions.csv'):
  ''' Extracts the time between the last post by a user and its (probably)
  corresponding blocking. If a user was blocked several times, multiple values
  will be returned for her. '''
  import csv
  with open(postsFile, 'r') as inputFile, \
       open('../data/smallestDeltas.txt', 'a') as output:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')
    deltas = []

    previousSecondsToBlock = -1
    previousTimestamp = 0
    previousUser = None
    for [timestamp, _, user, _, _, secondsToBlock] in blockLogReader:
      # type conversion from string and other preprocessing:
      secondsToBlock = int(secondsToBlock)
      timestamp = int(timestamp)
      areDifferentUsers = previousUser != user

      timeDelta = timestamp - previousTimestamp
      # timeDelta can be 0 if the timestamps are incomplete and missing seconds:
      assert areDifferentUsers or (timeDelta >= 0), '[E] Time delta for one user can never be less than zero. Is the list sorted?'

      secondsToBlockDelta = previousSecondsToBlock - secondsToBlock
      wasLastBlock = (previousSecondsToBlock > -1) and (secondsToBlock == -1)
      # Determine whether the current post was blocked later than former and
      # thus belongs to another blocking. We use some tolerance of two minutes
      # assuming that no block would ever be this short.
      if (previousSecondsToBlock != -1 \
         and ( \
           secondsToBlockDelta < 0 \
           # the difference between blocks was small but the two posts are a long
           # time apart. Thus, these must be two different blockings:
           or (timeDelta - secondsToBlockDelta) > 120 \
           or wasLastBlock \
           or areDifferentUsers) \
         ):
           output.write('%i\n' % previousSecondsToBlock)
           deltas.append(previousSecondsToBlock)

      # we expect the input data to be sorted chronologically (oldest to newest
      # post by same author):
      previousSecondsToBlock = secondsToBlock
      previousUser = user
      previousTimestamp = timestamp

    # last block, if any:
    if previousSecondsToBlock != -1:
       output.write('%i\n' % previousSecondsToBlock)
       deltas.append(previousSecondsToBlock)

    return deltas

def countDeltaDistribution(deltas):
  ''' Scatter plot of the time passed (in seconds) after the last post before a
  blocking until the actual blocking was issued.
  '''
  from matplotlib import pyplot as plt
  from collections import Counter
  import numpy as np

  counter = Counter(deltas)
  counter = sorted(counter.items())
  valuesX = [keyValue[0] for keyValue in counter]
  valuesY = [keyValue[1] for keyValue in counter]
  valuesY = np.cumsum(valuesY)

  fig = plt.figure(figsize=(30,10))
  plt.scatter(valuesX, valuesY, marker='x')

  plt.xlabel('Time in seconds')
  plt.ylabel('Number of last posts prior to blocking')
  plt.title('Number of last posts before their author was blocked in time frame')

  plt.savefig('../data/deltasDistribution.png', dpi=300)
  plt.gca().set_yscale('log')
  plt.savefig('../data/deltasDistribution_logy.png', dpi=300)

if __name__ == '__main__':
  deltas = extractLastPostToBlockDeltas()
  countDeltaDistribution(deltas)
