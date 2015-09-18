#!/usr/bin/python
# -*- coding: utf-8 -*-

def calculateAUC():
  # true positives:  output_b: True
  #                  tested on blocked, predicted as blocks
  # false positives: output_nb: False
  #                  tested on not blocked, predicted as blocks
  values = []

  with open('output_b.csv', 'r') as positivesFile:
    for line in positivesFile:
      difference = float(line.split('\t')[0])
      if difference >= 0: # true positive
        values.append( (difference, True) )

  with open('output_nb.csv', 'r') as negativesFile:
    for line in negativesFile:
      difference = float(line.split('\t')[0])
      if difference < 0: # false positive
        # multiplying the value with -1 ensures that we end up with a positive
        # confidence value:
        values.append( (difference * -1, False) )

  values.sort(reverse=True)
  y = [0]
  currentY = 0
  for (_, prediction) in values:
    if prediction:
      currentY += 1
    else:
      y.append(currentY)

  print(len(y))
  # normalise to the scale of x=y=[0,1]
  y = [value / y[-1] for value in y]
  dx = 1 / len(y)
  x = [dx * i for i in range(len(y))]

  import numpy
  area = numpy.trapz(y, dx=dx)
  print(area)

  from matplotlib import pyplot as plt
  fig = plt.figure()
  plt.plot(x, y)
  plt.savefig('auc.png')

if __name__ == '__main__':
  calculateAUC()
