#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This script requires a sorted input file. You can sort WikiWho's output
deletionRevisions.csv using:
sort -t$'\t' -k3 -k1 deletionRevisions.csv -o userSortedDeletionRevisions.csv
The file is then sorted by username as first and post creation timestamp as second
sort criterion.
'''

import csv
BLOCK_TIME = 172800
blocked = 0
notBlocked = 0

def mergeRecentPostsOfSameUser(postsFile='../../processed/run8/userSortedDeletionRevisions.csv'):
  with open(postsFile, 'r') as inputFile, \
       open('../data/blocked_sliding.txt', 'a') as bFile, \
       open('../data/notBlocked_sliding.txt', 'a') as nbFile:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')

    previousUser = None
    previousSecondsToBlock = 0
    firstTimestamp = 0
    for [timestamp, _, user, _, post, secondsToBlock] in blockLogReader:
      # type conversion from string and other preprocessing:
      timestamp = int(timestamp)
      secondsToBlock = int(secondsToBlock)
      post = post.strip()

      timeDelta = timestamp - firstTimestamp
      if (previousUser != user \
         # the user was blocked in between the two posts:
         or secondsToBlock > previousSecondsToBlock \
         # posts too far apart:
         or timeDelta > BLOCK_TIME):

        # we are not in the first iteration so write to disk:
        if previousUser:
          write(recentPosts, secondsToBlock, bFile, nbFile)

        recentPosts = [post]
        firstTimestamp = timestamp
        previousUser = user
      else:
        recentPosts.append(post)

      previousSecondsToBlock = secondsToBlock
    # write last post(s) to disk:
    if previousUser:
      write(recentPosts, secondsToBlock, bFile, nbFile)

    printStatistics()

def mergeSlidingWindow(postsFile='../../processed/run8/userSortedDeletionRevisions.csv'):
  import sys
  with open(postsFile, 'r') as inputFile, \
       open('../data/blocked_sliding.txt', 'a') as bFile, \
       open('../data/notBlocked_sliding.txt', 'a') as nbFile:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')

    previousUser = None
    previousSecondsToBlock = 0
    postsData = []
    for [timestamp, _, user, _, post, secondsToBlock] in blockLogReader:
      # type conversion from string and other preprocessing:
      timestamp = int(timestamp)
      secondsToBlock = int(secondsToBlock)

      postData = (timestamp, post, secondsToBlock)
      if user == previousUser:
        postsData.append(postData)
      else:
        while postsData:
          (firstTimestamp, _, previousSecondsToBlock) = postsData[0]
          recentPosts = []
          smallestSecondsToBlock = sys.maxsize

          for (timestamp, post, secondsToBlock) in postsData:
            timeDelta = timestamp - firstTimestamp
            # out of blocked timeframe or blocked happened between the two posts,
            # thus break out of loop to write to disk:
            if (secondsToBlock > previousSecondsToBlock \
               or timeDelta > BLOCK_TIME):
              assert len(recentPosts), '[E] 0 posts should be written to disk. This should never happen.'
              break
            # all within the timeframe given in BLOCK_TIME:
            else:
              recentPosts.append(post)
              # if there is a block in recentPosts, we want to count it as
              # blocked:
              if (secondsToBlock != -1 and \
                 secondsToBlock < smallestSecondsToBlock):
                smallestSecondsToBlock = secondsToBlock

              previousSecondsToBlock = secondsToBlock

            # write all in BLOCK_TIME frame to disk:
            write(recentPosts, smallestSecondsToBlock, bFile, nbFile)
          # drop oldest:
          postsData = postsData[1:]
        # add postData of different user:
        postsData = [postData]
      previousUser = user

    # write last post(s) to disk:
    if previousUser:
      write(recentPosts, secondsToBlock, bFile, nbFile)

    printStatistics()

def write(recentPosts, secondsToBlock, bFile, nbFile):
  ''' Writes recentPosts to disk. Depending on secondsToBlock and BLOCK_TIME, in
  which a post must have appeared to be considered a block, the blocked file
  (bFile) or not blocked file (nbFile) is used. '''
  mergedPost = '<BOP> %s <EOP>\n' % ' '.join(recentPosts)
  if (secondsToBlock != -1 \
     and  secondsToBlock < BLOCK_TIME):
    bFile.write(mergedPost)

    global blocked
    blocked += len(recentPosts)
  else:
    nbFile.write(mergedPost)

    global notBlocked
    notBlocked += len(recentPosts)

def printStatistics():
    global blocked
    global notBlocked
    print('[I] Blocked posts:\t%i\n[I] Not blocked posts:\t%i' % (blocked, notBlocked))

if __name__ == '__main__':
  mergeSlidingWindow()
