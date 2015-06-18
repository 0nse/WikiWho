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

from structures.Revision import Revision

from functions.determineAuthorship import determineAuthorship
from functions.print import *

from etc.Relation import Relation

import getopt
import os
import re
from sys import argv, exit

# Container of revisions.
revisions = {}
revision_order = []

# Hash tables.
spam = []

# SPAM detection variables.
CHANGE_PERCENTAGE = -0.40
PREVIOUS_LENGTH = 1000
CURR_LENGTH = 1000
FLAG = "move"

def sortRevisions(page):
    """ Iterates over all page revisions and sorts them ascendingly by their ID.
    Wikipedia dumps should have them already sorted in the first place. However,
    I stumbled upon one (rare?) export where this was not the case. As the order
    is crucial to the WikiWho algorithm, we are better safe than sorry.
    """
    sortedRevisions = []
    for revision in page:
        sortedRevisions.append(revision)
    sortedRevisions.sort(key = lambda x: x.id)
    return sortedRevisions

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

def processDeletionDiscussion(page, i):
    # Revisions to compare.
    revision_curr = Revision()
    revision_prev = Revision()
    text_curr = None

    print("Now processing: %s" % page.title)
    # Iterate over revisions of the article.
    sortedRevisions = sortRevisions(page)
    for revision in sortedRevisions:
        vandalism = False

        # Update the information about the previous revision.
        revision_prev = revision_curr

        if (revision.sha1 == None):
            revision.sha1 = Text.calculateHash(revision.text)

        if (revision.sha1 in spam):
            vandalism = True

        #TODO: SPAM detection: DELETION
        if (revision.comment!= None and revision.comment.find(FLAG) > 0):
            pass
        else:
            if (
                ( revision_prev.length > PREVIOUS_LENGTH )
                and ( len(revision.text) < CURR_LENGTH )
                and ( ( (len(revision.text) - revision_prev.length) / float(revision_prev.length) ) <= CHANGE_PERCENTAGE )
               ):
                vandalism = True
                revision_curr = revision_prev

        if (not vandalism):
            # Information about the current revision.
            revision_curr = Revision()
            revision_curr.id = i
            revision_curr.wikipedia_id = int(revision.id)
            revision_curr.length = len(revision.text)
            revision_curr.timestamp = revision.timestamp

            # Relation of the current relation.
            relation = Relation()
            relation.revision = int(revision.id)
            relation.length = len(revision.text)

            # Some revisions don't have contributor.
            if (revision.contributor != None):
                revision_curr.contributor_id = revision.contributor.id
                revision_curr.contributor_name = revision.contributor.user_text
                relation.author = revision.contributor.user_text
            else:
                revision_curr.contributor_id = 'Not Available ' + revision.id
                revision_curr.contribur_name = 'Not Available ' + revision.id
                relation.author = 'Not Available ' + revision.id

            # Content within the revision.
            text_curr = revision.text.lower()

            # Perform comparison.
            vandalism = determineAuthorship(revision_curr, revision_prev, text_curr, relation, revisions)


            if (not vandalism):
                # Add the current revision with all the information.
                revisions.update({revision_curr.wikipedia_id : revision_curr})
                revision_order.append((revision_curr.wikipedia_id, False))
                # Update the fake revision id.
                i = i+1

                # Calculate the number of tokens in the revision.
                total = 0
                for p in revision_curr.ordered_paragraphs:
                    for paragraph_curr in revision_curr.paragraphs[p]:
                        for hash_sentence_curr in paragraph_curr.sentences.keys():
                            for sentence_curr in paragraph_curr.sentences[hash_sentence_curr]:
                                total = total + len(sentence_curr.words)
                revision_curr.total_tokens = total
                relation.total_tokens = total

            else:
                revision_order.append((revision_curr.wikipedia_id, True))
                revision_curr = revision_prev
                spam.append(revision.sha1)


def analyseDumps(path):
    for fileName in extractFileNamesFromPath(path):
        # Access the file.
        dumpIterator = mwIterator.from_file(open_file(fileName))

        # Iterate over the pages.
        for page in dumpIterator:
            i = 0

            if page.namespace is 4 and page.title.startswith("Wikipedia:Articles for deletion"):
                i = processDeletionDiscussion(page, i)
    return (revisions, revision_order)

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

    return (inputfile,revision)

if __name__ == '__main__':

    (path, revision) = main(argv[1:])

    (revisions, order) = analyseDumps(path)

    print("revision", revision)
    if (not revision or revision == 'all'):
        printAllRevisions(order, revisions)
    else:
        printRevision(revisions[int(revision)])
