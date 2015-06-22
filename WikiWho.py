#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 20, 2013

@author: Maribel Acosta
@author: Fabian Floeck
'''

from mw.xml_dump import Iterator as mwIterator
from mw.xml_dump.functions import EXTENSIONS as mwExtensions
from mw.xml_dump.functions import open_file

from functions.print import *
from functions.processDeletionDiscussion import processDeletionDiscussion

import getopt
import os
from sys import argv, exit

def extractFileNamesFromPath(path):
    """ Returns a list of file names that are identified under path.
    If path is a directory, its contents will be returned non-recursively. Thus,
    all non-directories with the suffix of a supported datatype will be returned.
    The list will be sorted alphabetically in ascending manner.
    If path identifies a file, it will be returned as a list.
    When path does neither, a FileNotFoundError is thrown.
    """
    if os.path.isdir(path):
        directoryContents = os.listdir(path)
        fileNames = []
        # filter for XML files only.
        for supportedFiletype in mwExtensions.keys():
            fileNames.extend(os.path.join(path, f)
                               for f in directoryContents
                               if f.lower().endswith("." + supportedFiletype)
                            )
        fileNames.sort()
    elif os.path.isfile(path):
        fileNames = [path]
    else:
        raise FileNotFoundError('No file or directory could be found in "%s"' % path)
    return fileNames

def analyseDumps(path, revision):
    for fileName in extractFileNamesFromPath(path):
        # Access the file.
        dumpIterator = mwIterator.from_file(open_file(fileName))

        # Iterate over the pages.
        for page in dumpIterator:

            if page.namespace is 4 \
               and page.title.startswith("Wikipedia:Articles for deletion/") \
               and not page.title.startswith("Wikipedia:Articles for deletion/Old/") \
               and page.title != "Wikipedia:Articles for deletion/Old":
                (revisions_order, revisions) = processDeletionDiscussion(page)

                if (not revision or revision == 'all'):
                    printAllRevisions(revisions_order, revisions)
                else:
                    try:
                        printRevision(revisions[int(revision)])
                    except:
                        pass

def main(my_argv):
    inputfile = ''
    revision = None

    try:
        if (len(my_argv) <= 2):
            opts, _ = getopt.getopt(my_argv,"i:",["ifile="])
        else:
            opts, _ = getopt.getopt(my_argv,"i:r:",["ifile=","revision="])
    except getopt.GetoptError:
        print('Usage: Wikiwho.py -i <inputfile> [-r <revision_id>]')
        exit(2)

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print("WikiWho DiscussionParser: An algorithm for extracting posts on Wikipedia page deletion discussions.")
            print()
            print('Usage: WikiWho.py -i <inputfile> [-rev <revision_id>]')
            print("-i --ifile File or directory to analyse")
            print("-h --help This help.")
            exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-r", "--revision"):
            revision = arg

    return (inputfile, revision)

if __name__ == '__main__':

    (path, revision) = main(argv[1:])

    analyseDumps(path, revision)
