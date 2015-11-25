#!/usr/bin/python
# -*- coding: utf-8 -*-

def createArithmeticMeanTable(timeframe=None):
  ''' Calculate the arithmetic mean of the performance measures from the
  timeframe tests featuring three classifiers. The output can be used as cells
  for a LaTeX table. '''
  import re
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
  if timeframe: # reduce to single timeframe
    timeframes = {timeframe : timeframes[timeframe]}

  classifiers = ('lm', 'svm', 'nb')
  order = ['recallPlus', 'recallMinus', 'precisionPlus', 'precisionMinus', 'F1Plus', 'F1Minus', 'accuracy', 'AUC']

  firstRe = re.compile(r'.*?& ([0-9\.]*) & .*')
  secondRe = re.compile(r'.*& ([0-9\.]*) & .*')
  # the trailing ' ?' is just there for compatibility reasons with older output:
  lastRe = re.compile(r'.*{([0-9\.]*)} ?\\')
  retrieve = lambda x, y: float(y.findall(x)[0])

  separator = ' & '

  values = {}
  for key in order:
    values[key] = []

  for timeframe in timeframes:
    try:
      for classifier in classifiers:
        with open('%s/processed/run9/%s/%s_all/confusionMatrix.tex' % (parentDir, timeframe, classifier), 'r') as matrix:
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
    except IOError:
      pass

  outputFile = '%s/postprocessing/comparison.tex' % parentDir
  try:
    os.remove(outputFile)
  except OSError:
    # The file did not exist in the first place. Continue:
    pass
  with open(outputFile, 'a') as output:
    boldFont = '\\textbf{%s}'
    subscript = '$_{%s}$'

    # create head:
    output.write('\\begin{tabular}{' + ' c '*(len(order)+1) + '}\n')
    output.write('\\hline\n')
    output.write(boldFont % 'time' + separator)
    for key in order:
      key = key.replace('Plus', subscript % '+')
      key = key.replace('Minus', subscript % '-')
      if key == order[-1]:
        output.write(boldFont % key + '\n')
      else:
        output.write(boldFont % key + separator)
    output.write(r'\\' + '\\hline\n')

    # Create a list of numerically sorted timeframe seconds. OrderedDict could
    # be used as alternative.
    orderedTimeframes = sorted(list(timeframes), key=lambda x:  int(x))

    i = len(classifiers) - 1
    # iterate over all values:
    while i < len(classifiers) * len(timeframes):
      means = []
      # calculate arithmetic mean for one category (e.g. F1):
      for key in order:
        results = values[key][i-len(classifiers) + 1 : i + 1]
        assert(len(results) == len(classifiers))

        arithmeticMean = sum(results) / len(classifiers)
        decimalPlaces = 2
        if key == 'AUC':
          decimalPlaces = 3
        means.append(str(round(arithmeticMean, decimalPlaces)))
      i += len(classifiers)

      # e.g. for |classifiers|=3 at i=8: index=(8-2) / 3 = 2nd iteration:
      timeframeIndex = (i - len(classifiers) - 1) / len(classifiers)
      # e.g. orderedTimeframes[2] == '86400', timeframes['86400'] == '1 day':
      currentTimeframe = timeframes[orderedTimeframes[timeframeIndex]]
      output.write(currentTimeframe + separator)
      output.write( separator.join(means) + r'\\' + '\n' )

    output.write('\\end{tabular}')

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Calculates the average mean of the three classifiers and creates a LaTeX table from the results.',
                                   epilog='TimeframeResultsExtraction.py comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument('timeframe', type=str, nargs='?',
                      help='A positional number argument can be passed if only one timeframe should be averaged.')
  args = parser.parse_args()

  createArithmeticMeanTable(args.timeframe)
