#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Initial program developed by René Pickhardt (@renepickhardt).
# It was then modified to accept a file input parameter and to use a dedicated
# method for word extraction from the wordLists.

def split(inputFile):
  with open('ngram-1', 'w') as funi, \
       open('ngram-2', 'w') as fbi,  \
       open('ngram-3', 'w') as ftri, \
       open('ngram-4', 'w') as ffour:
    for line in inputFile:
        wordList = line.rstrip('\n').split(' ')
        index = 0

        funi.write( mergeWordsToLine(wordList, index) )
        index += 1
        if (index >= len(wordList)):
            continue

        fbi.write( mergeWordsToLine(wordList, index, 1) )
        index += 1

        if (index >= len(wordList)):
            continue
        ftri.write( mergeWordsToLine(wordList, index, 2) )
        index += 1

        while (index < len(wordList)):
            ffour.write( mergeWordsToLine(wordList, index, 3) )
            index += 1

def mergeWordsToLine(wordList, index, grams=0):
  ''' Merges all as many words into one line separated by spaces and suffixed by
  a newline, as specified in grams. '''
  l = []
  for i in range(-grams, 1):
    l.append( wordList[index + i] )

  return ' '.join(l) + '\n'


if __name__ == '__main__':
  import argparse
  parser = argparse.ArgumentParser(description='Prepare a text file to be processed by GLMTK.',
                                   epilog='GLMTKPreprocessor comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.')

  parser.add_argument('inputFile', type=argparse.FileType('r'),
                      help='The path to the text file to process.')
  args = parser.parse_args()
  split(args.inputFile)
