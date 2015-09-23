#!/usr/bin/python
# -*- coding: utf-8 -*-

def calculateAUC(outputDirectory='.', positiveFile='output_b.csv', negativeFile='output_nb.csv'):
  # true positives:  output_b: True
  #                  tested on blocked, predicted as blocks
  # false positives: output_nb: False
  #                  tested on not blocked, predicted as blocks
  values = []

  with open(positiveFile, 'r') as positivesFile:
    for line in positivesFile:
      difference = float(line.split('\t')[0])
      if difference >= 0: # true positive
        values.append( (difference, True) )
  tp = len(values)

  with open(negativeFile, 'r') as negativesFile:
    for line in negativesFile:
      difference = float(line.split('\t')[0])
      if difference < 0: # false positive
        # multiplying the value with -1 ensures that we end up with a positive
        # confidence value:
        values.append( (difference * -1, False) )
  fp = len(values) - tp
  if not fp:
    import pdb; pdb.set_trace()

  print('True positives:\t%i\nFalse positives:\t%i\nRatio:\t%f' % (tp, fp, tp / fp))

  values.sort(reverse=True)
  y = [0]
  currentY = 0
  for (_, prediction) in values:
    if prediction:
      currentY += 1
    else:
      y.append(currentY)

  # normalise to the scale of x=y=[0,1]
  y = [value / y[-1] for value in y]
  dx = 1 / len(y)
  x = [dx * i for i in range(len(y))]

  import numpy
  area = numpy.trapz(y, dx=dx)
  print('AUC:\t%f' % area)

  from matplotlib import pyplot as plt
  fig = plt.figure()
  plt.plot(x, y)
  plt.savefig('%s/auc.png' % outputDirectory)

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Calculates and plots the AUC from the data provided through the variables positiveFile and negativeFile.',
                                   epilog='GLMTKPostprocessor comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')
  parser.add_argument('--dir', dest='outputDirectory', type=str, nargs='?',
                      help='The directory under which the plotted graph should be saved as auc.png.')
  parser.add_argument('--positive', dest='positiveFile', type=str, nargs='?',
                      help='The path to the CSV data of the evaluation results on post-level tested on blocked entries.')
  parser.add_argument('--negative', dest='negativeFile', type=str, nargs='?',
                      help='The path to the CSV data of the evaluation results on post-level tested on not blocked entries.')
  args = parser.parse_args()

  # “There has to be an easier way!” — sure but this was quicker for now:
  if args.outputDirectory:
    if args.positiveFile:
      if args.negativeFile:
        calculateAUC(args.outputDirectory, args.positiveFile, args.negativeFile)
      else:
        calculateAUC(args.outputDirectory, args.positiveFile)
    elif args.negativeFile:
      calculateAUC(args.outputDirectory, args.negativeFile)
    else:
      calculateAUC(args.outputDirectory)
  elif args.positiveFile:
    if args.negativeFile:
      calculateAUC(args.positiveFile, args.negativeFile)
    else:
      calculateAUC(args.positiveFile)
  elif args.negativeFile:
    calculateAUC(args.negativeFile)
  else:
    calculateAUC()
