#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Usage: python NonFunctionWordsFilter.py input.txt output.txt

Removes all words that are not function words from the input and saves as a new
file.
'''

# The list of function words selected from a compiled list by Leah Gilner and
# Franc Morales: http://www.sequencepublishing.com/academic.html
FUNCTION_WORDS = ['i', 'a', 'aboard', 'about', 'above', 'absent', 'according', 'accordingly', 'across', 'after', 'against', 'ahead', 'albeit', 'all', 'along', 'alongside', 'although', 'amid', 'amidst', 'among', 'amongst', 'an', 'and', 'another', 'anti', 'any', 'anybody', 'anyone', 'anything', 'around', 'as', 'aside', 'astraddle', 'astride', 'at', 'away', 'bar', 'barring', 'be', 'because', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'bit', 'both', 'but', 'by', 'can', 'certain', 'circa', 'concerning', 'consequently', 'considering', 'could', 'dare', 'deal', 'despite', 'down', 'during', 'each', 'either', 'enough', 'every', 'everybody', 'everyone', 'everything', 'except', 'excepting', 'excluding', 'failing', 'few', 'fewer', 'following', 'for', 'four', 'from', 'given', 'great', 'had', 'he', 'heaps', 'hence', 'her', 'hers', 'herself', 'him', 'himself', 'his', 'however', 'if', 'in', 'including', 'inside', 'instead', 'into', 'it', 'its', 'itself', 'less', 'like', 'little', 'loads', 'lots', 'many', 'may', 'me', 'might', 'mine', 'minus', 'more', 'most', 'much', 'must', 'my', 'myself', 'near', 'neither', 'nevertheless', 'no', 'nobody', 'none', 'nor', 'nothing', 'notwithstanding', 'of', 'off', 'on', 'once', 'one', 'onto', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'past', 'pending', 'per', 'plenty', 'plus', 'regarding', 'respecting', 'round', 'save', 'saving', 'several', 'shall', 'she', 'should', 'since', 'so', 'some', 'somebody', 'someone', 'something', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'therefore', 'these', 'they', 'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'till', 'to', 'toward', 'towards', 'two', 'under', 'underneath', 'unless', 'unlike', 'until', 'unto', 'up', 'upon', 'us', 'various', 'versus', 'via', 'wanting', 'we', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereas', 'wherever', 'whether', 'which', 'whichever', 'while', 'whilst', 'who', 'whoever', 'whom', 'whomever', 'whose', 'will', 'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves']

def filterForFunctionWords(inputFile, outputFile):
  ''' This is the entry point method for mergeRecentPostsOfSameUser and
  mergeSlidingWindow. See their documentation for information in how they
  differ. '''
  for line in inputFile:
    words = []
    for word in line.split(' '):
      if word in FUNCTION_WORDS:
        words.append(word)

    if len(words):
      outputFile.write('<BOP> %s <EOP>\n' % ' '.join(words))

if __name__ == '__main__':
  import argparse
  import os
  parser = argparse.ArgumentParser(description='Filter all words but function words from input file and write it as output file. The files may not be identical.',
                                   epilog='This program (NonFunctionWordsFilter) comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')

  parser.add_argument('inputFile', type=argparse.FileType('r'),
                      default=None, help='Path to the file which should be used as input')
  parser.add_argument('outputFile', type=argparse.FileType('a'),
                      default=None, help='Path to the file which should be used as output')
  args = parser.parse_args()
  if args.inputFile == args.outputFile:
    raise ValueError('Input and output file may not be identical.')

  filterForFunctionWords(args.inputFile, args.outputFile)
