#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Requirements: Numpy, Matplotlib
'''

def plotContributionFrequencyDistribution(postsFile='../../processed/run9/userSortedDeletionRevisions.csv'):
  import csv
  from collections import Counter
  from matplotlib import pyplot as plt

  with open(postsFile, 'r') as inputFile:
    print('[I] starting to process "%s".' % postsFile)
    blockLogReader = csv.reader(inputFile, delimiter='\t', quoting=csv.QUOTE_NONE)
    users = []

    for [_, _, user, _, _, _] in blockLogReader:
      users.append(user)

  # how often was each user active? [(user : #contributions),]
  userActivity = Counter(users)
  # how often did users make n many contributions? [(#contributions : frequency),]
  contributionsFrequency = Counter(userActivity.values())
  # convert to list  for zip:
  contributionsFrequency = list(contributionsFrequency.items())
  contributionsFrequency.sort(reverse=True)
  # x = contrib frequency, y number of users that contributed that frequently
  valuesY, valuesX = zip(*contributionsFrequency)

  plt.xscale('log')
  plt.yscale('log')
  plt.scatter(range(1, len(valuesY)+1), valuesY)

  # Start the plot at (0.0) and end it at the highest x-value. These calls must
  # be made AFTER plt.scatter.
  plt.axes().set_xlim(0)
  plt.axes().set_ylim(0)

  plt.savefig('../data/contributionFrequencyDistribution.png', dpi=300)

if __name__ == '__main__':
  plotContributionFrequencyDistribution()
