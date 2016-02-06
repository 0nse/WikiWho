#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Usage: python AUC.py [AUC, optimistic, pessimistic]
       python AUC.py AUC --dir='.' --positive='b.csv' --negative='nb.csv'

Requirements: Matplotlib, Numpy

Calculate the AUC drawn from output_b.csv and output_nb.csv (or whatever is
passed to calculateAUC()). An AUC plot is being saved into a given output
directory as AUC.png for the average AUC, else AUC_optimistic.png or
AUC_pessimistic.png.

See the argparse help texts for more information.

Changes to the print output must be reflected in
../postprocessing/confusionMatrix.sh '''

def calculateAUC(variation, outputDirectory=None, positiveFile=None, negativeFile=None):
  if not outputDirectory:
    outputDirectory = '.'
  if not positiveFile:
    positiveFile = '../data/output_b.csv'
  if not negativeFile:
    negativeFile = '../data/output_nb.csv'

  # true positives:  output_b: True
  #                  tested on blocked, predicted as blocks
  # false positives: output_nb: False
  #                  tested on not blocked, predicted as blocks
  values = []

  # counts for false and true negative:
  fn = tn = 0
  with open(positiveFile, 'r') as positivesFile:
    for line in positivesFile:
      difference = float(line.split('\t')[0])
      if difference >= 0: # true positive
        values.append( (difference, True) )
      else:
        fn += 1
  tp = len(values)

  with open(negativeFile, 'r') as negativesFile:
    for line in negativesFile:
      difference = float(line.split('\t')[0])
      if difference < 0: # false positive
        # multiplying the value with -1 ensures that we end up with a positive
        # confidence value:
        values.append( (difference * -1, False) )
      else:
        tp += 1
  fp = len(values) - tp
  # accuracy:
  accuracy = (tn + tp) / (tn + fn + fp + tp) * 100

  # ratio except for when the denominator is zero; then just zero:
  ratio = 0 if not fp else tp / fp
  print('True positives:\t%i\nFalse positives:\t%i\nRatio:\t%f\nAccuracy:\t%f' % (tp, fp, ratio, accuracy))

  sortedValues = sort(values, variation)
  if len(sortedValues) == 2:
    # AUC, calculate ROC Y valuesY values for both:
    optimisticY = calculateYAxis(sortedValues[0])
    pessimisticY = calculateYAxis(sortedValues[1])

    y = []
    # average both to obtain AUC:
    for i in range(len(optimisticY)):
      averageValue = (optimisticY[i] + pessimisticY[i]) / 2
      y.append(averageValue)
  else:
    # pessimistic or optimistic; calculate ROC Y values:
    y = calculateYAxis(sortedValues)

  # normalise to the scale of x=y=[0,1]
  y = [value / y[-1] for value in y]
  dx = 1 / len(y)
  x = [dx * i for i in range(len(y))]

  import numpy as np
  area = np.trapz(y, dx=dx)
  print('AUC:\t%f' % area)

  from matplotlib import pyplot as plt
  fig = plt.figure()
  plt.plot(x, y)

  suffix = ''
  if variation != 'AUC':
    suffix = '_' + variation
  plt.savefig('%s/auc%s.png' % (outputDirectory, suffix))

def sort(values, order):
  ''' Sort the values as needed for the different variations of AUC. Every order
  string other than 'optimistic' and 'pessimistic' will be treated as normalised
  AUC. '''
  values.sort(reverse=True)
  if order == 'optimistic':
    return values

  # [:] ensures that we copy the list instead of copying pointers:
  valuesPessimistic = values[:]
  # sort descending on confidence (higehst first) and ascending on value (False
  # first):
  sorted(valuesPessimistic, key = lambda x: (-x[0], x[1]))

  if order == 'pessimistic':
    return valuesPessimistic
  else:
    return (values, valuesPessimistic)

def calculateYAxis(values):
  ''' Calculates a ROC curve from the values. '''
  y = [0]
  currentY = 0
  for (_, prediction) in values:
    if prediction:
      currentY += 1
    else:
      y.append(currentY)
  return y

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Calculates and plots the AUC from the data provided through the variables positiveFile and negativeFile.',
                                   epilog='AUC.py comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument(dest='variation', type=str,
                      help='The variation of AUC to calculate. Valid options are "optimistic", "pessimistic" and "AUC" for the inbetween.')
  parser.add_argument('--dir', dest='outputDirectory', type=str, nargs='?',
                      help='The directory under which the plotted graph should be saved as auc.png. Default is the current directory.')
  parser.add_argument('--positive', dest='positiveFile', type=str, nargs='?',
                      help='The path to the CSV data of the evaluation results on post-level tested on blocked entries. Default is ../data/output_b.csv.')
  parser.add_argument('--negative', dest='negativeFile', type=str, nargs='?',
                      help='The path to the CSV data of the evaluation results on post-level tested on not blocked entries. Default is ../data/output_nb.csv.')
  args = parser.parse_args()

  if args.variation not in ['AUC', 'optimistic', 'pessimistic']:
    raise Exception('[E] Allowed values are "AUC", "optimistic" and "pessimistic".')
  calculateAUC(args.variation, args.outputDirectory, args.positiveFile, args.negativeFile)
