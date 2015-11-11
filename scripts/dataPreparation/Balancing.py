#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Usage: python NotBlockedBalancing.py

Randomly samples blocked/notBlocked files to be of same size. See the argparse
description for more information.

If the --lines argument is missing, this script will print the number of lines
in data/blocked_full.txt as used by dataPreparation/separate.sh.
'''

import random
import subprocess
import os

def balance(length=None):
  files = ['notBlocked']

  if not length:
    # assuming len(blocked) > len(notBlocked) and thus blocked needs to be
    # sampled to be of the same size:
    with open('../data/blocked_full.txt', 'r') as blocked:
      length = sum(1 for line in blocked)
      # The print statement is used so that dataPreparation/separate.sh can
      # store the amount of lines into a file. Naturally, this could be done in
      # Python as well but this way, a change to the file name does not involve
      # a change in two separate files.
      print(length)
  else:
    files.append('blocked')

  for fileName in files:
    write(fileName, length)

def write(fileName, length):
  ''' Randomly sample and write the file to disk. '''
  fullFile = '../data/%s_full.txt' % fileName
  outputFile = '../data/%s.txt' % fileName

  with open(fullFile, 'r') as fullInput:
    lines = fullInput.readlines() # make sure you have the available memory

  sample = random.sample(lines, length)

  os.remove(outputFile)
  with open(outputFile, 'a') as output:
    for post in sample:
      output.write(post)

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Randomly draw elements to create a subset of notBlocked_full.txt and blocked_full.txt. This algorithm is naïvely implemented and can easily consume a lot of memory (that is, as much as the file size is + the size of the file newly to create).',
                                   epilog='This program (Balancing) comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')

  parser.add_argument('--lines', type=int, nargs='?',
                      help='The number of lines to extract. If none are given, it is assumed that blocked is the smaller file and notBlocked will be sampled to the same length.')
  args = parser.parse_args()

  balance(args.lines)
