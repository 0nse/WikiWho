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

class OutputWrapper:
  import os
  # script parent directory:
  fileDir = os.path.dirname(os.path.abspath(__file__)).split('/')
  parentDir = '/'.join(fileDir[:-1])
  wikiWhoDir = '/'.join(fileDir[:-2])

  blockedCount = notBlockedCount = mergedBlockedCount = mergedNotBlockedCount= 0

  def __init__(self, time):
    ''' Initialise class by deleting existing files and then opening them anew
    for appending mode. BLOCK_TIME is set.
    The paths are obviously hard-coded. '''
    self.blockedFilePath = '%s/data/blocked_full.txt' % self.parentDir
    self.notBlockedFilePath = '%s/data/notBlocked_full.txt' % self.parentDir

    # We append to a file. So better safe than sorry and try removing it first:
    self.deleteFile(self.blockedFilePath)
    self.deleteFile(self.notBlockedFilePath)

    self.bFile = open(self.blockedFilePath, 'a')
    self.nbFile = open(self.notBlockedFilePath, 'a')

    self.BLOCK_TIME = time

  def deleteFile(self, path):
    ''' Try deleting file located under path. If it does not exist, continue.
    Returns True on success, False else.
    '''
    try:
      os.remove(path)
      return True
    except OSError:
      return False

  def write(self, recentPosts, secondsToBlock):
    ''' Writes recentPosts to disk. Depending on secondsToBlock and BLOCK_TIME, in
    which a post must have appeared to be considered a block, the blocked file
    (bFile) or not blocked file (nbFile) is used. '''
    mergedPost = '<BOP> %s <EOP>\n' % ' '.join(recentPosts)
    if (secondsToBlock != -1 \
       and secondsToBlock < self.BLOCK_TIME):
      self.bFile.write(mergedPost)

      self.mergedBlockedCount += len(recentPosts)
      self.blockedCount += 1
    else:
      self.nbFile.write(mergedPost)

      self.mergedNotBlockedCount += len(recentPosts)
      self.notBlockedCount += 1

  def printStatistics(self):
      print('[I] Merged blocked posts:\t%i\n[I] Merged not blocked posts:\t%i' % (self.mergedBlockedCount, self.mergedNotBlockedCount))
      print('[I] Blocked posts:\t%i\n[I] Not blocked posts:\t%i' % (self.blockedCount, self.notBlockedCount))

  def close(self):
    self.bFile.close()
    self.nbFile.close()

###############
# Script code #
###############
import sys
import csv
# Time between a contribution and a later blocking of the author in which the
# contribution is assumed to have led to the blocking:
BLOCK_TIME = 86400

import os
# script parent directory:
fileDir = os.path.dirname(os.path.abspath(__file__)).split('/')
wikiWhoDir = '/'.join(fileDir[:-2])

def merge(shouldBeSlidingWindow=True, postsFile='%s/processed/run9/userSortedDeletionRevisions.csv' % wikiWhoDir):
  ''' This is the entry point method for mergeRecentPostsOfSameUser and
  mergeSlidingWindow. See their documentation for information in how they
  differ. '''

  with open(postsFile, 'r') as inputFile:
    blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')

    outputWrapper = OutputWrapper(BLOCK_TIME)

    if shouldBeSlidingWindow:
      mergeSlidingWindow(blockLogReader, outputWrapper)
    else:
      mergeRecentPostsOfSameUser(blockLogReader, outputWrapper)

    outputWrapper.close()
    outputWrapper.printStatistics()

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

def mergeRecentPostsOfSameUser(reader, outputWrapper):
  ''' This function merges posts of the same user within a BLOCK_TIME time frame.
  There is no sliding window. Thus, posts in the same time frame will be grouped
  but without overlap. Naturally, many combinations of successive posts are left
  out. Use mergeSlidingWindow instead if that is a concern for you.

  The first post will be considered of the same user and all her posts afterwards
  in the time frame. When this time frame ends or when there is a block in
  between, the posts are merged and written to disk. The algorithm will then
  continue from the first entry after the last already processed post.

  Essentially, this method is deprecated as the classifiers perform subpar on
  its results.

  THIS METHOD IS DEPRECATED AND MAY BEHAVE INCORRECTLY.
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
        outputWrapper.write(recentPosts, secondsToBlock)

      recentPosts = [post]
      firstTimestamp = timestamp
      previousUser = user
    else:
      recentPosts.append(post)

    previousSecondsToBlock = secondsToBlock
  # write last post(s) to disk:
  if previousUser:
    outputWrapper.write(recentPosts, secondsToBlock)

def mergeSlidingWindow(reader, outputWrapper):
  ''' Merge posts of the same user within a BLOCK_TIME time frame. First, all
  posts by the same user are gathered and then all posts within the time frame
  will be merged into one post which will be written to disk. Next, the first
  post will be removed and thus the window slides to later posts which remain
  apart from each other in the same time frame.

  A window will not slide over a blocking but will end there and a new window
  will be created after the new blocking:
  [xB]xx,x[B]xx,xB[xx],xBx[x] instead of [xBxx],x[Bxx],xB[xx],xBx[x] and so on.
  Where B is a blocked post, x is a regular one, [] indicates the window.

  As the code does not use the block log, the window can slide over two
  successive blockings: [xBB]x,x[BB]x,xB[B]x,xBB[x] if the time until a block of
  the first blocking is greater than that of the second (the second was blocked
  sooner after posting).
  However, this is a rather theoretical warning as this would either require a
  very high BLOCK_TIME (greater than multiple days) or very short blockings (12
  hours or less for example). If BLOCK_TIME is 1d and the average block is at
  least 24h long, it is unlikely that this would happen.

  If a merged post contains a post that resulted in a blocking, the whole merged
  window will be considered as blocked.

  Be aware that this function will create many posts: The files can easily grow
  into many GB. '''
  previousUser = None
  previousSecondsToBlock = 0
  postsData = []
  for line in reader:
    [timestamp, user, post, secondsToBlock] = preprocessLine(line)

    postData = (timestamp, post, secondsToBlock)
    # first collect all posts by the same user:
    if user == previousUser:
      postsData.append(postData)
    # then, start creating windows and write them to disk:
    else:
      processUser(postsData, outputWrapper)
      postsData = []
      previousUser = user
      # add postData of different user (which triggered this branch):
      postsData = [postData]

  # write last post(s) to disk:
  if previousUser:
    # The condition ensures that nothing is written if only one user existed. In
    # any other case, the posts by the last user in the input file have not been
    # written yet.
    processUser(postsData, outputWrapper)

def processUser(postsData, outputWrapper):
  ''' Actual sliding window process. Slide a window over all posts by the same
  user and write them to disk. '''
  while postsData:
    (firstTimestamp, _, previousSecondsToBlock) = postsData[0]
    recentPosts = []
    smallestSecondsToBlock = sys.maxsize

    # stretch sliding window as far as possible:
    for (timestamp, post, secondsToBlock) in postsData:
      timeDelta = timestamp - firstTimestamp
      # outside of BLOCK_TIME or block happened between the two posts,
      # thus break out of loop to write to disk:
      if (secondsToBlock > previousSecondsToBlock \
         or timeDelta > BLOCK_TIME): # or (previousSecondsToBlock != -1 and secondsToBlock == -1)
        assert len(recentPosts), '[E] 0 posts should be written to disk. This should never happen.'
        break
      # all within the timeframe given in BLOCK_TIME:
      else:
        recentPosts.append(post)
        # if there is a block in recentPosts, we want to count it as
        # blocked. Thus, we look for the lowest secondsToBlock:
        if (secondsToBlock != -1 and \
           secondsToBlock < smallestSecondsToBlock):
          smallestSecondsToBlock = secondsToBlock

        previousSecondsToBlock = secondsToBlock

    # write all in BLOCK_TIME frame to disk:
    outputWrapper.write(recentPosts, secondsToBlock)
    # drop oldest:
    postsData = postsData[1:]

if __name__ == '__main__':
  merge()
