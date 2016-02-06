#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Requirements: Numpy, Matplotlib

Determine how many posts were made by the most active users and plot this. As a
result, a distribution close to a pareto distribution can be illustrated on
Wikipedia AfD discussions.
'''

def plotContributionFrequencyDistribution(postsFile='../../processed/run9/userSortedDeletionRevisions.csv'):
  import csv
  from collections import Counter
  from matplotlib import pyplot as plt
  import numpy as np

  with open(postsFile, 'r') as inputFile:
    print('[I] starting to process "%s".' % postsFile)
    blockLogReader = csv.reader(inputFile, delimiter='\t', quoting=csv.QUOTE_NONE)
    contributionAuthors = []

    for [_, _, user, _, _, _] in blockLogReader:
      contributionAuthors.append(user)

  # how often was each user active? [(user : #contributions),]
  userActivity = Counter(contributionAuthors)

  mostActiveUser, mostActiveUserContributions = userActivity.most_common(1)[0]
  print('[I] %i users made %i contributions with %s being the most active user. He/she contributed %i times.' % (len(userActivity), len(contributionAuthors), mostActiveUser, mostActiveUserContributions))

  activity = list(userActivity.values())
  # most active user's contribution amount first:
  activity.sort(reverse=True)
  # start from 0.0:
  valuesY = [0]
  valuesY.extend(activity)
  valuesY = np.cumsum(valuesY)

  valuesX = range(len(valuesY))

  plt.xlabel('Number of most active editors')
  plt.ylabel('Number of total contributions')

  plt.scatter(valuesX, valuesY)

  for i in valuesX:
    y = valuesY[i]
    if y >= len(contributionAuthors) / 2:
      plt.annotate('Half of all considered contributions were\nmade by the %i most active users.' % i, xy=(valuesX[i], valuesY[i]), xytext=(200,20),
                   textcoords='offset points', ha='center', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.2', fc='yellow', alpha=0.3),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5',
                                   color='red'))
      break

  # Start the plot at (0.0) and end it at the highest x-value. These calls must
  # be made AFTER plt.scatter.
  plt.axes().set_xlim(0)
  plt.axes().set_ylim(0)

  plt.savefig('../data/contributionFrequencyDistribution.png', dpi=300)

if __name__ == '__main__':
  plotContributionFrequencyDistribution()
