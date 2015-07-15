#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Feb 20, 2013

@author: Maribel Acosta
@author: Fabian Floeck
@author: Michael Ruster
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

def analyseDumpsAndOutputWriteToDisk(path, revision, blocks):
    """ Load dump file(s) from path and iterate over their pages and their
    revisions. All revisions will be matched against the blocks dict to
    calculate how many seconds after the creation of the revision, the
    author was blocked (if s/he was blocked at all afterwards).
    """
    for fileName in extractFileNamesFromPath(path):
        print('Now processing the file "%s".' % fileName)
        # Access the file.
        dumpIterator = mwIterator.from_file(open_file(fileName))

        # Iterate over the pages.
        for page in dumpIterator:

            if (page.namespace is 4 \
               and page.title.startswith("Wikipedia:Articles for deletion/") \
               # Old links to old discussions:
               and not page.title.startswith("Wikipedia:Articles for deletion/Old/") \
               and page.title != "Wikipedia:Articles for deletion/Old" \
               # Log collects discussions by including them through a template:
               and not page.title.startswith("Wikipedia:Articles for deletion/Log/") \
               and page.title != "Wikipedia:Articles for deletion/Log"):
                (revisions_order, revisions) = processDeletionDiscussion(page)

                if (not revision or revision == 'all'):
                    writeAllRevisions(revisions_order, revisions, blocks)
                else:
                    try:
                        writeRevision(revisions[int(revision)], blocks)
                    except:
                        pass

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="WikiWho DiscussionParser: An algorithm for extracting posts on Wikipedia page deletion discussions and checking when the post's author has last been blocked.",
                                     epilog="""
                                     WikiWho DiscussionParser, Copyright (C) 2015 Fabian Flöck, Maribel Acosta, Michael Ruster (based on wikiwho by Fabian Flöck, Maribel Acosta).
                                     WikiWho DiscussionParser comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.
                                     """)

    parser.add_argument('-i', dest='pageDumpPath', required=True,
                        help='Path to the Wikipedia page(s) dump (XML, 7z, bz2…).')
    parser.add_argument('-b', dest='blockLog',  type=argparse.FileType('r'), required=True,
                        help='Path to the block log file produced wit 0nse/WikiParser (CSV).'),
    parser.add_argument('-r', dest='revision', default='all', nargs='?',
                        help='Use this parameter if you are only interested in a subset of revisions (revision ID must exist in data).')

    args = parser.parse_args()

    print("Loading blocked users and the associated blocking timestamps into memory.", end=' ')
    import timeUntilBlocked
    blocks = timeUntilBlocked.createBlockedUsersDict(args.blockLog)
    print("Done.")

    analyseDumpsAndOutputWriteToDisk(args.pageDumpPath, args.revision, blocks)
