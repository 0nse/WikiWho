#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Usage: python TimeframeResultsExtraction.py [timeframe,]
       python TimeframeResultsExtraction.py 86400

Requirements: Matplotlib

If no timeframe is specified, all timeframes (see timeframes variable) will be
considered.
'''
from matplotlib import pyplot as plt
import numpy as np

import os
# script parent directory:
fileDir = os.path.dirname(os.path.abspath(__file__)).split('/')
parentDir = '/'.join(fileDir[:-1])

timeframes = {'46800'  : '13 hours',
              '86400'  : '1 day',
              '129600' : '1.5 days',
              '172800' : '2 days',
              '216000' : '2.5 days',
              '259200' : '3 days',
              '345600' : '4 days',
              '432000' : '5 days',
              '518400' : '6 days'}
# Create a list of numerically sorted timeframe seconds. OrderedDict could
# be used as alternative.
orderedTimeframes = sorted(list(timeframes), key=lambda x:  int(x))

classifiers = ['svm', 'nb', 'lm']
measuresOrder = ['recallPlus', 'recallMinus', 'precisionPlus', 'precisionMinus', 'F1Plus', 'F1Minus', 'accuracy', 'AUC']
# beautify the measuresOrder for being displayed on a plot:
labels = [x.replace('Plus', '+').replace('Minus', '-').title() for x in measuresOrder]

variations = ['all', 'fw']

def retrieveValues():
  ''' Calculate the arithmetic mean of the performance measures from the
  timeframe tests featuring three classifiers. The output can be used as cells
  for a LaTeX table. '''
  import re

  firstRe = re.compile(r'.*?& ([0-9\.]*) & .*')
  secondRe = re.compile(r'.*& ([0-9\.]*) & .*')
  # the trailing ' ?' is just there for compatibility reasons with older output:
  lastRe = re.compile(r'.*{([0-9\.]*)} ?\\')
  retrieve = lambda x, y: float(y.findall(x)[0])

  values = {}
  for key in measuresOrder:
    values[key] = []

  for timeframe in orderedTimeframes:
    for classifier in classifiers:
      for variation in variations:
        with open('%s/processed/run9/%s/%s_%s/confusionMatrix.tex' % (parentDir, timeframe, classifier, variation), 'r') as matrix:
          for line in matrix:
            if 'Predicted positive' in line:
              value = retrieve(line, lastRe)
              values['precisionPlus'].append(value)

            if 'Predicted negative' in line:
              value = retrieve(line, lastRe)
              values['precisionMinus'].append(value)

            elif 'Recall' in line:
              value = retrieve(line, firstRe)
              values['recallPlus'].append(value)
              value = retrieve(line, secondRe)
              values['recallMinus'].append(value)

            elif 'F1' in line:
              value = retrieve(line, firstRe)
              values['F1Plus'].append(value)
              value = retrieve(line, secondRe)
              values['F1Minus'].append(value)

            elif 'Accuracy' in line:
              value = retrieve(line, firstRe)
              values['accuracy'].append(value)

            # the parantheses guarantees that we ignore optimistic and pessimistic:
            elif 'AUC}' in line:
              value = retrieve(line, firstRe)
              values['AUC'].append(value)
  return values

def createArithmeticMeanTable(values, considerFunctionWords=False):
  outputFile = '%s/postprocessing/comparison.tex' % parentDir
  try:
    os.remove(outputFile)
  except OSError:
    # The file did not exist in the first place. Continue:
    pass
  with open(outputFile, 'a') as output:
    separator = ' & '
    boldFont = '\\textbf{%s}'
    subscript = '$_{%s}$'

    # create head:
    output.write('\\begin{tabular}{' + ' c '*(len(measuresOrder)+1) + '}\n')
    output.write('\\hline\n')
    output.write(boldFont % 'time' + separator)
    for key in measuresOrder:
      key = key.replace('Plus', subscript % '+')
      key = key.replace('Minus', subscript % '-')
      if key == measuresOrder[-1]:
        output.write(boldFont % key + '\n')
      else:
        output.write(boldFont % key + separator)
    output.write(r'\\' + '\\hline\n')

    classifiersLength = len(classifiers)
    if considerFunctionWords:
      classifiersLength *= len(variations)

    i = classifiersLength - 1
    # iteration:
    j = 0
    # iterate over all timeframes:
    while j < len(timeframes):
      means = []
      # calculate arithmetic mean for one category (e.g. F1):
      for key in measuresOrder:
        results = values[key][i-classifiersLength + 1 : i + 1]
        assert len(results) == classifiersLength

        arithmeticMean = sum(results) / classifiersLength
        decimalPlaces = 2
        if key == 'AUC':
          decimalPlaces = 3
        mean = round(arithmeticMean, decimalPlaces)
        # write 0.500 instead of 0.5:
        mean = ('{:.%sf}' % decimalPlaces).format(mean)
        means.append(mean)
      i += classifiersLength

      currentTimeframe = timeframes[orderedTimeframes[j]]
      output.write(currentTimeframe + separator)
      output.write( separator.join(means) + r'\\' + '\n' )
      j += 1

    output.write('\\end{tabular}')

def createBarChart(values):
  # Each values[orderKey] is a list with values of the following:
  # [svm_all, svm_fw, nb_all, nb_fw, lm_all, lm_fw]
  assertPlottableValues(values)

  # graph colours:
  colours = ['b', 'r']
  barWidth = 0.2
  # X axis labels (-1 because we exclude AUC):
  axisX = range(0, len(measuresOrder) - 1)
  # offset by bar width:
  axisXOffset = [v + barWidth for v in axisX]

  # iterate over all classifiers + variations:
  i = 0
  while i < len(classifiers) * len(variations):
    plt.subplots()
    plt.axhline(0, color='black')
    valuesY_all = []
    valuesY_fw = []

    # append values of all words and function words:
    for axisY in (valuesY_all, valuesY_fw):
      # iterate over all measures except AUC:
      for key in measuresOrder[:-1]:
        # set the value into relation with a random decision:
        value = values[key][i] - 50
        axisY.append(value)
      if i % 2:
        plt.bar(axisXOffset, axisY, width=barWidth, color=colours[i % 2], label='Function words')
      else:
        plt.bar(axisX, axisY, width=barWidth, color=colours[i % 2], label='Full text')
      i += 1

    # i is multiplied by len(variations). Thus, we divide it by itself.
    currentClassifier = classifiers[int((i - 1) / len(variations)) % len(classifiers)]

    plt.legend()
    # Labels:
    plt.xticks(axisXOffset, labels)

    plt.tight_layout()
    plt.savefig('%s/data/relativePerformance_%s.png' % (parentDir, currentClassifier), dpi=300)

def assertPlottableValues(values):
  assert len(values) == len(measuresOrder), '[E] There must be as many keys as there are measures to be displayed. Mismatch: %i vs %i' % (len(values), len(measuresOrder))
  assert len(values[measuresOrder[0]]) == len(classifiers) * len(variations), '[E] There must be %i * %i classifiers per key for each classifier * variation.' % (len(classifiers), len(variations))

def createClassifierDifferencesBarCharts(values):
  assertPlottableValues(values)

  colours = ['r', 'g', 'b']
  barWidth = 0.2
  # X axis labels (-1 because we exclude AUC):
  axisX = range(0, len(measuresOrder) - 1)
  # offset by bar width:
  axisXLeftOffset = [v - barWidth for v in axisX]
  axisXRightOffset = [v + barWidth for v in axisX]

  offset = 0
  for currentVariation in variations:
    plt.subplots()
    # scale to 0 to 100 so that charts are easier visually comparable:
    plt.axes().set_ylim(0, 100)

    # start at offset up to e.g. 3 (SVM, NB, LM) and skip e.g. every second
    # (all, fw) value:
    for i in range(offset, len(classifiers) * len(variations), len(variations)):
      # this is SVM, NB, LM:
      axisY = []

      # skip AUC for now:
      for key in measuresOrder[:-1]:
        value = values[key][i]
        axisY.append(value)

      j =  i - offset
      variation = 'function words' if offset else 'full text'
      if j == 0:
        plt.bar(axisXLeftOffset, axisY, width=barWidth, color=colours[j % 3], label='SVM (%s)' % variation)
      elif j == 2:
        plt.bar(axisX, axisY, width=barWidth, color=colours[j % 3], label='NB (%s)' % variation)
      else:
        plt.bar(axisXRightOffset, axisY, width=barWidth, color=colours[j % 3], label='LM (%s)' % variation)

    offset += 1

    plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                   ncol=2, mode="expand", borderaxespad=0.)
    # Labels:
    plt.xticks(axisX, labels)

    # bbox_inches="tight" ensures that the legend will fit in the saved figure.
    plt.savefig('%s/data/performanceComparison_%s.png' % (parentDir, currentVariation), dpi=300, bbox_inches='tight')


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Calculates the average mean of the three classifiers and creates a LaTeX table from the results.',
                                   epilog='TimeframeResultsExtraction.py comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument('timeframe', type=str, nargs='?',
                      help='A positional number argument can be passed if only one timeframe should be averaged.')
  args = parser.parse_args()

  if args.timeframe: # reduce to single timeframe
    timeframes = {args.timeframe : timeframes[args.timeframe]}
    orderedTimeframes = [args.timeframe]

  values = retrieveValues()
  createArithmeticMeanTable(values, args.timeframe != None)

  if args.timeframe:
    createBarChart(values)
    createClassifierDifferencesBarCharts(values)
