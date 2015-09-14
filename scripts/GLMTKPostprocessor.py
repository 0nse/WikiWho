#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import math

ngramSum = 0
post = []

def retrieveLatestFiles(path):
  """ Given a path, the paths to the four latest files is returned. This is
  determined by last modification time."""
  files = [os.path.join(path, name) for name in os.listdir(path)]
  # sort by modification time:
  files.sort(key=os.path.getmtime)

  return files[-4:]

def calculatePerplexityForNextPost(unigrams, bigrams, trigrams, fourgrams):
  global ngramSum, post
  ngramSum = 0
  post = []

  if not step(unigrams):
    if not step(bigrams):
      if not step(trigrams):
        while not step(fourgrams):
          pass

  # perplexity e^-(sum(log(P(w))) / N) — only works in Python 3:
  return math.pow(math.e, -(ngramSum / len(post)))

def step(iterator):
  """ Return a boolean value expressing whether this line marked the end of a
  post. Updates the ngramSum and adds the current word to post.
  Next() will be called on the iterator. Thus, a StopIteration exception may be
  raised. """
  global ngramSum, post

  line = next(iterator)
  wordsList = line.split(' ')

  try:
    (newWord, value) = wordsList[-1].split('\t')
  except ValueError:
    # file ended as we have reached the summary part of the file:
    raise StopIteration
  post.append(newWord)

  # the last word of the list is the value computed by GLMTK:
  value = float(value)
  ngramSum += math.log(value) if (value > 0) else 0

  return newWord == '<EOP>'

def calculatePerplexities(positivePath, negativePath, fileNameSuffix=None):
  """ Calculates the actual perplexities. No checks are done on fileNameSuffix.
  Thus, you can most likely break this code.
  All output is appended to a file. Therefore, you might want to remove files
  from any prior runs.
  The file is created as follows: difference	pos. perpl.	neg. perpl.	post
  The difference is calculated as the positive minus the negative perplexity. As
  absolute value, it can be seen as a confidence measurement in the implicit
  classification. Said classification is encoded in the difference being positive
  or negative. A positive difference value means that the classification predicted
  the correct class. """
  global post

  if fileNameSuffix:
    fileName = 'output_%s.csv' % fileNameSuffix
  else:
    fileName = 'output.csv'

  positiveNGrams = retrieveLatestFiles(positivePath)
  negativeNGrams = retrieveLatestFiles(negativePath)

  with open(positiveNGrams[0], 'r') as bUni,   \
       open(positiveNGrams[1], 'r') as bBi,    \
       open(positiveNGrams[2], 'r') as bTri,   \
       open(positiveNGrams[3], 'r') as bFour,  \
       open(negativeNGrams[0], 'r') as nbUni,  \
       open(negativeNGrams[1], 'r') as nbBi,   \
       open(negativeNGrams[2], 'r') as nbTri,  \
       open(negativeNGrams[3], 'r') as nbFour, \
       open(fileName, 'a') as output:
    while True:
      try:
        pPerplexity = calculatePerplexityForNextPost(bUni, bBi, bTri, bFour)
        nPerplexity = calculatePerplexityForNextPost(nbUni, nbBi, nbTri, nbFour)
      except StopIteration:
        # the file end has been reached. As the negative data  should have
        # originated from the same file (thus it should have the same length), we
        # can already break.
        break

      # if this value is negative, the predicted class is wrong:
      difference = nPerplexity - pPerplexity
      output.write('%f	%f	%f	%s\n' % (difference,
                                         pPerplexity,
                                         nPerplexity,
                                         ' '.join(post)))

if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Postprocess the results created by GLMTK.',
                                   epilog='GLMTKPostprocessor comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')

  parser.add_argument('positivePath', type=str,
                      help='The path to the queries folder of the positive training data.')
  parser.add_argument('negativePath', type=str,
                      help='The path to the queries folder of the not positive training data.')
  parser.add_argument('fileNameSuffix', type=str, nargs='?',
                      help='An option file name suffix.')
  args = parser.parse_args()

  calculatePerplexities(args.positivePath, args.negativePath, args.fileNameSuffix)
