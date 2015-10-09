#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import subprocess

with open('../data/notBlocked.txt', 'r') as notBlocked, \
     open('../data/blocked.txt', 'r') as blocked, \
     open('../data/notBlocked_randomlyBalanced.txt', 'a') as output:
  length = sum(1 for line in blocked)
  lines = notBlocked.readlines() # make sure you have the available memory
  print('Randomly sampling %i lines' % length)
  sample = random.sample(lines, length)

  for post in sample:
    output.write(post)