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
import numpy as np

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
  from datetime import datetime
  with open(postsFile, 'r') as inputFile:
    print('[I] starting to process "%s".' % postsFile)
    blockLogReader = csv.reader(inputFile, delimiter='\t', quoting=csv.QUOTE_NONE)
    deltas = []
    users = set()

    previousSecondsToBlock = -1
    previousTimestamp = None
    previousUser = None
    for [timestamp, _, user, _, _, secondsToBlock] in blockLogReader:
      # type conversion from string and other preprocessing:
      secondsToBlock = int(secondsToBlock)
      try:
        timestamp = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
      except ValueError:
        raise ValueError('[E] The timestamp format was unknown.', timestamp)
      areDifferentUsers = previousUser != user

      if previousTimestamp:
        timeDelta = (timestamp - previousTimestamp).total_seconds()
      else: # only happens in first iteration
        timeDelta = 0
      # timeDelta can be 0 if the timestamps are incomplete and missing seconds:
      assert areDifferentUsers or (timeDelta >= 0), '[E] Time delta for one user can never be less than zero. Is the list sorted?'

      secondsToBlockDelta = previousSecondsToBlock - secondsToBlock

      # Determine whether the current post was blocked later than the former
      # post and thus belongs to another blocking. We use some tolerance of two
      # minutes assuming that no block would ever be this short.
      if (previousSecondsToBlock != -1 \
         # same users and the last post had some time up to the block
         and ( not areDifferentUsers
           and (
             # If the same user's new block time is greater than the old, there
             # was a block in between. They can however be equal to zero if a
             # user made multiple contributions within the same second. For
             # example User:° did three (!) contributions on 19th July 2006,
             # 18:04:37.
             secondsToBlockDelta < 0 \
             # the difference between blocks was small but the two posts are a long
             # time apart. Thus, these must be two different blockings:
             or (timeDelta - secondsToBlockDelta) > 120 \
             # This user was blocked in the last iteration and then never again:
             or secondsToBlock == -1 \
           )
           or areDifferentUsers) \
         ):
           deltas.append(previousSecondsToBlock)
           users.add(previousUser)

      # we expect the input data to be sorted chronologically (oldest to newest
      # post by same author):
      previousSecondsToBlock = secondsToBlock
      previousUser = user
      previousTimestamp = timestamp

    # last block, if any:
    if previousSecondsToBlock != -1:
       deltas.append(secondsToBlock)
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

  print('[I] Number of blocks happening after a user contributed to an AfD: %i.' % len(deltas))
  print('[I] Users blocked multiple times: %i.' % (len(deltas) - len(users)))
  return deltas

def countDeltaDistribution(deltas):
  ''' Counts the occurences of deltas, sorts them from lowest to highest and
  returns a cumulative sum. E.g. [1, 5, 3, 1, 1, 5, 8] would be transformed
  to {'1' : 3, '3' : 1, '5' : 2, '8' : 1} and returned as
  ([3, 4, 6, 7], [1, 3, 5, 8]). '''
  from collections import Counter

  # the counter is used for grouping by timestamp frequency and sorting:
  counter = Counter(deltas)
  counter = sorted(counter.items())
  # convert from seconds to days:
  valuesX = [keyValue[0]/60/60/24 for keyValue in counter]
  # extract the actual value:
  valuesY = [keyValue[1] for keyValue in counter]
  valuesY = np.cumsum(valuesY)

  return (valuesX, valuesY)

hasLegendBeenPrinted = False
def plot(suffix, values):
  ''' Scatter plot of the time passed (in days) after the last post before a
  blocking until the actual blocking was issued.
  Values is a dictionary of values to plot with the key being the label and
  the value being a tuple of X and Y values.'''
  from matplotlib import pyplot as plt
  import itertools

  plt.subplot()
  # Add a title if you need one. I've disabled it, because the image will be
  # embedded into a figure with a caption.
  # plt.title('Number of last posts before their author was blocked in timeframe')
  plt.xlabel('Time in days')
  plt.ylabel('Number of last posts prior to a block')

  # see http://matplotlib.org/api/markers_api.html for available markers
  markers = itertools.cycle(['+', '.', 'o', 'x'])
  # see http://matplotlib.org/api/colors_api.html for available colours
  colours = itertools.cycle(['b', 'r', 'g', 'm'])
  highestXValues = []
  highestYValues = []
  for (label, (x, y)) in values.items():
    plt.scatter(x, y, marker=next(markers), color=next(colours), label=label)

    highestXValues.append(x[-1])
    highestYValues.append(y[-1])

  # Start the plot at (0.0) and end it at the highest x-value. These calls must
  # be made AFTER plt.scatter.
  plt.axes().set_xlim(0, max(highestXValues))
  plt.axes().set_ylim(0, max(highestYValues) + 250)

  global hasLegendBeenPrinted
  if not hasLegendBeenPrinted:
    # position lower right:
    plt.legend(loc=4)
    hasLegendBeenPrinted=True

  plt.savefig('../data/deltasDistribution_%s.png' % str(suffix), dpi=300)

def shortenValuesToDays(values, days):
  ''' A helper method so that the code is better readable. Shortens both values
  according to the amount of days given. If days is greater than all days in
  values, values is returned as-is.'''
  assert len(values) == 2, '[E] Values did not contain exactly two arguments (values for X and Y axis).'
  for i in range(len(values[0])):
    if values[0][i] >= days:
      return (values[0][:i], values[1][:i])
  return values

def areaBetweenTwoCurves(valuesA, valuesB):
  ''' Calculates the area between the two curves. The input order is irrelevant.
  '''
  areaA = np.trapz(valuesA[0], x=valuesA[1])
  areaB = np.trapz(valuesB[0], x=valuesB[1])

  return max(areaA, areaB) - min(areaA, areaB)

if __name__ == '__main__':
  afdDeltas = extractLastPostToBlockDeltas()
  afdValues = countDeltaDistribution(afdDeltas)
  # This file has been created by executing BlockedAfDUserExtraction.py and
  # sorting it afterwards as described in extractLastPostToBlockDeltas().
  globalDeltas = extractLastPostToBlockDeltas('../processed/dump/afdContributions.csv')
  globalValues = countDeltaDistribution(globalDeltas)
  print('[I] There are %i blocks in AfD discussions, %i on Wikipedia in general. That\'s a difference of %i users.' % (len(afdDeltas), len(globalDeltas), len(globalDeltas) - len(afdDeltas)))

  assert len(afdValues) <= len(globalValues), '[E] The global values cannot be less than the AfD values as the former contain the later.'

  subplotLengths = ('full', 30, 7)
  for days in subplotLengths:
    if type(days) is int or type(days) is float:
      afdValues = shortenValuesToDays(afdValues, days)
      globalValues = shortenValuesToDays(globalValues, days)

    plot(days, {'Only AfD discussions' : afdValues, 'Complete Wikipedia' : globalValues})

    area = areaBetweenTwoCurves(afdValues, globalValues)
    # we know that globalValues is >= afdValues:
    relativeArea  = area / np.trapz(globalValues[0], x=globalValues[1]) * 100
    print('[I] The area for the subplot of "%s" days is %.3f. Thus, the relation is %.3f%%.' % (str(days), area, relativeArea))
