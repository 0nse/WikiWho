#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Usage: python FilterResultsPlotting.py PathToLogFile

Requirements: Matplotlib, execute after AUC.py

Notes: Usually, you would not call this script but filterPostEvaluationResults.sh
       instead.

Plots AUC and tp/fp ratio for a given AUC.log. The files are stored as
ratio_development.png and auc_development.png.
This script is usually called by filterPostEvaluationResults.sh. '''

def plot(logFile):
  import os
  outputDirectory = os.path.dirname(logFile.name)

  accuracyValues = []
  aucValues = []

  accuracyString = 'Accuracy'
  aucString = 'AUC'

  for line in logFile:
    if line.startswith(accuracyString):
      accuracyValues.append(extractValue(line, accuracyString))
    elif line.startswith(aucString):
      # make it a percentage:
      aucValues.append(extractValue(line, aucString) * 100)

  from matplotlib import pyplot as plt
  fig = plt.figure()
  plt.axes().set_xlim(1)
  plt.plot(range(2, len(accuracyValues) + 2), accuracyValues, color='b', label=accuracyString)
  plt.xlabel('Minimum number of words per post')
  plt.ylabel('Accuracy')

  plt.plot(range(2, len(aucValues) + 2), aucValues, color='r', label=aucString)
  plt.xlabel('Minimum number of words per post')
  plt.ylabel('AUC')

  plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
                 ncol=2, mode="expand", borderaxespad=0.)
  plt.savefig('%s/development.png' % outputDirectory, dpi=300, bbox_inches='tight')

def extractValue(s, desc):
  value = s.replace('%s:	' % desc, '')
  return float(value)

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Plots the effect of post word amounts and the true positive/false positive-ratio from the AUC.py log.',
                                   epilog='GLMTKPostprocessor comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument('filePath', type=argparse.FileType('r'),
                      help='The directory under which the log is stored.')
  args = parser.parse_args()
  plot(args.filePath)
