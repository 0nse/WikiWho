#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Plots AUC and tp/fp ratio for a given AUC.log. The files are stored as
ratio_development.png and auc_development.png.
This script is usually called by filterPostEvaluationResults.sh. """

def plot(logFile):
  import os
  outputDirectory = os.path.dirname(logFile.name)

  ratioValues = []
  aucValues = []

  ratioString = 'Ratio'
  aucString = 'AUC'

  for line in logFile:
    if line.startswith(ratioString):
      ratioValues.append(extractValue(line, ratioString))
    elif line.startswith(aucString):
      aucValues.append(extractValue(line, aucString))

  from matplotlib import pyplot as plt
  fig = plt.figure()
  plt.plot(range(2, len(ratioValues) + 2), ratioValues)
  plt.xlabel('Minimum number of words per post')
  plt.ylabel('TP/FP ratio')
  plt.savefig('%s/ratio_development.png' % outputDirectory, dpi=300)

  fig = plt.figure()
  plt.plot(range(2, len(aucValues) + 2), aucValues)
  plt.xlabel('Minimum number of words per post')
  plt.ylabel('AUC (optimistic)')
  plt.savefig('%s/auc_development.png' % outputDirectory, dpi=300)

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
