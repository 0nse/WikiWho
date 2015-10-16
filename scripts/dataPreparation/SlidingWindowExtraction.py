#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Usage: python SlidingWindowExtraction.py
       or manually call merge(Bool, PathAsString)

The relevant entry point method is merge(). Currently, BLOCK_TIME is hardcoded.
Add an argparser if you need to.

This script requires a sorted input file. You can sort WikiWho's output
deletionRevisions.csv using:
sort -t$'\t' -k3,3 -k1,1n deletionRevisions.csv -o userSortedDeletionRevisions.csv
The file is then sorted by username as first and post creation timestamp as second
sort criterion.
'''

import csv
# Time between a contribution and a later blocking of the author in which the
# contribution is assumed to have led to the blocking:
BLOCK_TIME = 172800
blockedCount = notBlockedCount = 0

def merge(shouldBeSlidingWindow=True, postsFile='../../processed/run9/userSortedDeletionRevisions.csv'):
  ''' This is the entry point method for mergeRecentPostsOfSameUser and
  mergeSlidingWindow. See their documentation for information in how they
  differ. '''
  with open(postsFile, 'r') as inputFile, \
       open('../data/blocked_sliding.txt', 'a') as bFile, \
       open('../data/notBlocked_sliding.txt', 'a') as nbFile:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')

    io = [blockLogReader,
          bFile,
          nbFile]

    if shouldBeSlidingWindow:
      mergeSlidingWindow(*io)
    else:
      mergeRecentPostsOfSameUser(*io)

    printStatistics()

def preprocessLine(line):
  ''' type conversion from string and other preprocessing '''
  timestamp = int(line[0])
  user = line[2]
  post = line[4].strip()
  secondsToBlock = int(line[5])
  return [timestamp,
          user,
          post,
          secondsToBlock]


def mergeRecentPostsOfSameUser(reader, bFile, nbFile):
  ''' This function merges posts of the same user within a BLOCK_TIME time frame.
  There is no sliding window. Thus, posts in the same time frame will be grouped
  but without overlap. Naturally, many combinations of successive posts are left
  out. Use mergeSlidingWindow instead if that is a concern for you.

  The first post will be considered of the same user and all her posts afterwards
  in the time frame. When this time frame ends or when there is a block in
  between, the posts are merged and written to disk. The algorithm will then
  continue from the first entry after the last already processed post.
  '''
  previousUser = None
  previousSecondsToBlock = 0
  firstTimestamp = 0
  for line in reader:
    [timestamp, user, post, secondsToBlock] = preprocessLine(line)

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

def mergeSlidingWindow(reader, bFile, nbFile):
  ''' Merge posts of the same user within a BLOCK_TIME time frame. First, all
  posts by the same user are gathered and then all posts within the time frame
  will be merged into one post which will be written to disk. Next, the first
  post will be removed and thus the window slides to later posts which remain
  apart from each other in the same time frame.

  A window will not slide over a blocking but will end there and a new window
  will be created after the new blocking:
  [xB],[xxx],[xx],[x] instead of [xBxxx],[Bxxx],[xxx],[xx],[x] and so on.
  Where B is a blocked post, x is a regular one, [] indicates the window.

  As the code does not use the block log, the window can slide over two
  successive blockings: [xBBx],[BBx],[Bx],[x] if the time until a block of the
  first blocking is greater than that of the second (the second was blocked
  sooner after posting).

  If a merged post contains a post that resulted in a blocking, the whole merged
  window will be considered as blocked.

  Be aware that this function will create many posts: The files can easily grow
  into many GB. '''
  import sys
  previousUser = None
  previousSecondsToBlock = 0
  postsData = []
  for line in reader:
    [timestamp, user, post, secondsToBlock] = preprocessLine(line)

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
             or timeDelta > BLOCK_TIME): # or (previousSecondsToBlock != -1 and secondsToBlock == -1)
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

def write(recentPosts, secondsToBlock, bFile, nbFile):
  ''' Writes recentPosts to disk. Depending on secondsToBlock and BLOCK_TIME, in
  which a post must have appeared to be considered a block, the blocked file
  (bFile) or not blocked file (nbFile) is used. '''
  mergedPost = '<BOP> %s <EOP>\n' % ' '.join(recentPosts)
  if (secondsToBlock != -1 \
     and secondsToBlock < BLOCK_TIME):
    bFile.write(mergedPost)

    global blockedCount
    blockedCount += len(recentPosts)
  else:
    nbFile.write(mergedPost)

    global notBlockedCount
    notBlockedCount += len(recentPosts)

def printStatistics():
    global blockedCount
    global notBlockedCount
    print('[I] Blocked posts:\t%i\n[I] Not blocked posts:\t%i' % (blockedCount, notBlockedCount))

if __name__ == '__main__':
  merge()
