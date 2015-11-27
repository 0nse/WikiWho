#!/usr/bin/python
# -*- coding: utf-8 -*-

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

classifiers = ('lm', 'svm', 'nb')
measuresOrder = ['recallPlus', 'recallMinus', 'precisionPlus', 'precisionMinus', 'F1Plus', 'F1Minus', 'accuracy', 'AUC']

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
      try:
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
      # file did not exist (e.g. no function words)
      except IOError:
        pass
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
    # iterate over all timeframes:
    while i < classifiersLength * len(timeframes):
      means = []
      # calculate arithmetic mean for one category (e.g. F1):
      for key in measuresOrder:
        results = values[key][i-classifiersLength + 1 : i + 1]
        assert(len(results) == classifiersLength)

        arithmeticMean = sum(results) / classifiersLength
        decimalPlaces = 2
        if key == 'AUC':
          decimalPlaces = 3
        mean = round(arithmeticMean, decimalPlaces)
        # write 0.500 instead of 0.5:
        mean = ('{:.%sf}' % decimalPlaces).format(mean)
        means.append(mean)
      i += classifiersLength

      # e.g. for |classifiers|=3 at i=8: index=(8-2) / 3 = 2nd iteration:
      timeframeIndex = (i - len(classifiers) - 1) / len(classifiers)
      if considerFunctionWords:
        timeframeIndex -= 1
        timeframeIndex /= len(variations)

      # e.g. orderedTimeframes[2] == '86400', timeframes['86400'] == '1 day':
      currentTimeframe = timeframes[orderedTimeframes[timeframeIndex]]
      output.write(currentTimeframe + separator)
      output.write( separator.join(means) + r'\\' + '\n' )

    output.write('\\end{tabular}')

def createBarChart(values):
  # Each values[orderKey] is a list with values of the following:
  # [lm_all, lm_fw, svm_all, svm_fw, nb_all, nb_fw]
  pass # for key in measuresOrder:


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Calculates the average mean of the three classifiers and creates a LaTeX table from the results.',
                                   epilog='TimeframeResultsExtraction.py comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument('timeframe', type=str, nargs='?',
                      help='A positional number argument can be passed if only one timeframe should be averaged.')
  args = parser.parse_args()

  if args.timeframe: # reduce to single timeframe
    timeframes = {args.timeframe : timeframes[args.timeframe]}

  values = retrieveValues()
  createArithmeticMeanTable(values, args.timeframe != None)

  if args.timeframe:
    createBarChart(values)
