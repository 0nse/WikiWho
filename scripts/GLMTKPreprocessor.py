#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Initial program developed by René Pickhardt (@renepickhardt).
# It was then modified to accept a file input parameter and to use a dedicated
# method for word extraction from the wordLists.

def split(textLines):
  # If a string was passed instead of a file, wrap it inside a list so that
  # iterating over it will return just this string instead of the individiual
  # characters:
  if type(textLines) == str:
    textLines = [textLines]

  with open('ngram-1', 'w') as funi, \
       open('ngram-2', 'w') as fbi,  \
       open('ngram-3', 'w') as ftri, \
       open('ngram-4', 'w') as ffour:
    for line in textLines:
        wordList = line.rstrip('\n').split(' ')
        index = 1

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

  parser.add_argument('inputFile', type=argparse.FileType('r'), nargs='?',
                      help='The path to the text file to process.')
  parser.add_argument('--post', dest="text", type=str, nargs='?',
                      help='The text to preprocess.')
  args = parser.parse_args()
  if args.inputFile:
    split(args.inputFile)
  elif args.text:
    split(args.text)
  else:
    raise Exception("You must either specify a path to a file or pass a string by using the --post parameter.")
