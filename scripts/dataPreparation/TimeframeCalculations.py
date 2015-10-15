#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This script requires a sorted input file. You can sort WikiWho's output
deletionRevisions.csv using:
sort -t$'\t' -k3,3 -k1,1n deletionRevisions.csv -o userSortedDeletionRevisions.csv
The file is then sorted by username as first and post creation timestamp as second
sort criterion.
'''

import csv

def extractLastPostToBlockDeltas(postsFile='../../processed/run9/userSortedDeletionRevisions.csv'):
  ''' Extracts the time between the last post by a user and its (probably)
  corresponding blocking. If a user was blocked several times, multiple values
  will be returned for her. '''
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
      try:
        assert areDifferentUsers or (timeDelta >= 0), '[E] Time delta for one user can never be less than zero. Is the list sorted?'
      except:
        import pdb; pdb.set_trace()

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

if __name__ == '__main__':
  extractLastPostToBlockDeltas()
