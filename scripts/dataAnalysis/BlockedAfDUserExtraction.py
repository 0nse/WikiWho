#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Michael Ruster

Extract the timestamp and user of contributions which were authored before the
respecitve user had been blocked. The result can be further processed by
TimeframeCalculations.py.

Requirements: MediaWiki Utilities, WikiWho DiscussionParser

Usage: python BlockedAfDUserExtraction.py -i /path/to/dumps/ -b /path/to/WikiParser/blocks.csv
'''

from mw.xml_dump import Iterator as mwIterator
from mw.xml_dump.functions import open_file

# Our very own little dependency hell:
from sys import path
path.append('../..')
path.append('../../WikiCodeCleaner')
path.append('../../functions')
import WikiWho
import BlockTimeCalculation
import TimeframeCalculations

import csv
import os.path

def extract(path, users, blocks):
  output = '../data/blockedAfDUsers.csv'

  if os.path.isfile(output):
    raise IOError('[E] File "%s" already exists. Aborting.' % output)

  with open(output, 'a') as output:
    writer = csv.writer(output, delimiter='\t',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for fileName in WikiWho.extractFileNamesFromPath(path):
      print('[I] Now processing the file "%s".' % fileName)
      # Access the file.
      dumpIterator = mwIterator.from_file(open_file(fileName))

      for page in dumpIterator:
        for revision in page:
          if revision.contributor:
            # participated in AfD and was blocked:
            if revision.contributor.user_text in users:
              secondsToBlock = BlockTimeCalculation.calculateSecondsUntilNextBlock(blocks, revision.contributor.user_text, revision.timestamp)

              # If secondsToBlock is -1, the user was once blocked but this post
              # belongs to the time after, when she was never blocked again.
              if secondsToBlock != -1:
                writer.writerow([revision.timestamp,
                                revision.contributor.id,
                                revision.contributor.user_text,
                                int(revision.id),
                                page.title,
                                secondsToBlock])


if __name__ == '__main__':
  import argparse, pickle, os
  parser = argparse.ArgumentParser(description='A method for extracting timestamps of users that have been blocked at least once and have participated in an AfD at least once.',
                                   epilog='''
                                   WikiWho DiscussionParser, Copyright (C) 2015 Fabian Flöck, Maribel Acosta, Michael Ruster (based on wikiwho by Fabian Flöck, Maribel Acosta).
                                   WikiWho DiscussionParser comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.
                                   ''')

  parser.add_argument('-i', dest='pageDumpPath', required=True,
                      help='Path to the Wikipedia page(s) dump (XML, 7z, bz2…).')
  parser.add_argument('-b', dest='blockLog',  type=argparse.FileType('r'),
                      default=None, nargs='?',
                      help='Path to the block log file produced with 0nse/WikiParser (CSV).'),
  args = parser.parse_args()

  usersFile = '../data/blockedAfDUserNames_temp.pkl'
  TimeframeCalculations.extractLastPostToBlockDeltas(usersOutputFile=usersFile)
  # If you stumble upon this code and ask yourself: why pickle? Why not just a
  # return parameter? I wanted to try pickle for once. That's all.
  with open(usersFile, 'rb') as inputFile:
    users = pickle.load(inputFile)
  os.remove(usersFile)

  blocks = BlockTimeCalculation.createBlockedUsersDict(args.blockLog)

  extract(args.pageDumpPath, users, blocks)
