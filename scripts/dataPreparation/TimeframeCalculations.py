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

def extractLastPostToBlockDeltas(postsFile='../../processed/run9/userSortedDeletionRevisions.csv', outputFile=None, usersOutputFile=None):
  ''' Extracts the time between the last post by a user and its (probably)
  corresponding blocking. If a user was blocked several times, multiple values
  will be returned for her.

  If outputFile is set, a file will be created at the given path. If the file
  exists, contents will be appended. The written time deltas are sorted from
  smallest to highest seconds until a blocking. The path may not lead to a
  non-existent (parent-) directory.

  The same requirements hold for usersOutputFile. If it is set to a file via
  a path, pickle will be used to dump a set of users, who were blocked at
  least once and participated in an AfD at least once to disk.'''
  import csv
  with open(postsFile, 'r') as inputFile:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')
    deltas = []
    users = set()

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
           deltas.append(previousSecondsToBlock)
           users.add(user)

      # we expect the input data to be sorted chronologically (oldest to newest
      # post by same author):
      previousSecondsToBlock = secondsToBlock
      previousUser = user
      previousTimestamp = timestamp

    # last block, if any:
    if previousSecondsToBlock != -1:
       deltas.append(previousSecondsToBlock)
       users.add(user)

  if outputFile:
    deltas.sort()
    with open(outputFile, 'a') as output:
      for delta in deltas:
         output.write('%i\n' % delta)

  # Dump user set to disk for later use with other python scripts:
  if usersOutputFile:
    with open(usersOutputFile, 'wb') as output:
      import pickle
      pickle.dump(users, output)

  return deltas

def countDeltaDistribution(deltas):
  ''' Scatter plot of the time passed (in days) after the last post before a
  blocking until the actual blocking was issued.
  '''
  from collections import Counter
  import numpy as np

  counter = Counter(deltas)
  counter = sorted(counter.items())
  # convert from seconds to days:
  valuesX = [keyValue[0]/60/60/24 for keyValue in counter]
  valuesY = [keyValue[1] for keyValue in counter]
  valuesY = np.cumsum(valuesY)

  fig = plot(valuesX, valuesY, 'full')
  fig = plot(valuesX[:100000], valuesY[:100000], '100k')
  fig = plot(valuesX[:50000],  valuesY[:50000],  '50k')

def plot(x, y, suffix):
  from matplotlib import pyplot as plt

  fig = plt.figure()

  # Add a title if you need one. I've disabled it, because the image will be
  # embedded into a figure with a caption.
  # plt.title('Number of last posts before their author was blocked in timeframe')
  plt.xlabel('Time in days')
  plt.ylabel('Number of last posts prior to blocking')

  plt.scatter(x, y, marker='+')

  # Start the plot at (0.0) and end it at the highest x-value. These calls must
  # be made AFTER plt.scatter.
  plt.axes().set_xlim(0, x[-1])
  plt.axes().set_ylim(0)

  plt.savefig('../data/deltasDistribution_%s.png' % suffix, dpi=300)

if __name__ == '__main__':
  deltas = extractLastPostToBlockDeltas()
  countDeltaDistribution(deltas)
