#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Usage: python NotBlockedBalancing.py

Randomly samples blocked/notBlocked files to be of same size. See the argparse
description for more information.

If the --lines argument is missing, this script will print the number of lines
in data/regular/blocked_full.txt as used by dataPreparation/separate.sh.
'''

import random
import subprocess
import os

def balance(isSlidingWindow, length=None):
  files = ['notBlocked']

  if not length:
    # assuming len(blocked) > len(notBlocked) and thus blocked needs to be
    # sampled to be of the same size:
    with open('../data/regular/blocked_full.txt', 'r') as blocked:
      length = sum(1 for line in blocked)
      # The print statement is used so that dataPreparation/separate.sh can
      # store the amount of lines into a file. Naturally, this could be done in
      # Python as well but this way, a change to the file name does not involve
      # a change in two separate files.
      print(length)
  else:
    files.append('blocked')

  for fileName in files:
    write(fileName, length, isSlidingWindow)

def write(fileName, length, isSlidingWindow=False):
  ''' Randomly sample and write the file to disk. '''
  fullFile = '../data/regular/%s_full.txt' % fileName
  outputFile = '../data/regular/%s.txt' % fileName

  with open(fullFile, 'r') as fullInput:
    lines = fullInput.readlines() # make sure you have the available memory

  if isSlidingWindow:
    sampledLines = random.sample(range(len(lines)), length)
  else:
    sample = random.sample(lines, length)

  try:
    os.remove(outputFile)
  except OSError:
    # The file did not exist. We can continue:
    pass
  with open(outputFile, 'a') as output:
    # Write both regular and sliding window output file:
    if isSlidingWindow:
      fullFileSW = '../data/sw/%s_full.txt' % fileName
      outputFileSW = '../data/sw/%s.txt' % fileName

      with open(fullFileSW, 'r') as fullInputSW:
        linesSW = fullInputSW.readlines() # this more than doubles the memory of this process

      with open(outputFileSW, 'a') as outputSW:
        for lineNo in sampledLines:
          output.write(lines[lineNo])
          outputSW.write(linesSW[lineNo])

    else:
      for post in sample:
        output.write(post)

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Randomly draw elements to create a subset of notBlocked_full.txt and blocked_full.txt. This algorithm is naïvely implemented and can easily consume a lot of memory (that is, as much as the file size is + the size of the file newly to create).',
                                   epilog='This program (Balancing) comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')

  parser.add_argument('--lines', type=int, nargs='?',
                      help='The number of lines to extract. If none are given, it is assumed that blocked is the smaller file and notBlocked will be sampled to the same length.')
  parser.add_argument('-sw', action='store_true',
      help='If this flag is set, the data will be prepared for the sliding window approach. That is, the data will be sampled as usual but at the same time, the same lines from the original corpus will be sampled as well. Therefore, two new subsets will be created: sliding window data and regular data, both from the same posts.')
  args = parser.parse_args()

  balance(args.sw, args.lines)
