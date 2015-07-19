#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 19, 2015

@author: Michael Ruster
'''

from mw.xml_dump import Iterator as mwIterator
from mw.xml_dump.functions import EXTENSIONS as mwExtensions
from mw.xml_dump.functions import open_file

from functions.processDeletionDiscussion import sortRevisions

from WikiWho import extractFileNamesFromPath

import xml.etree.cElementTree as ET

from codecs import encode, decode

from sys import argv, exit

def generateOutputFile(fileName):
    """ Generate an output file name by replacing fileName's extension
    with 'xml' or appending '.xml' if no known was found. """
    fileNameLower = fileName.lower()
    for extension in mwExtensions:
        extension = '.' + extension
        if fileNameLower.endswith(extension):
            extensionPosition = fileNameLower.rfind(extension)
            outputFileName = fileName[:extensionPosition]

    if not outputFileName:
        print('[W] No known file extension was found for "%s". This should never happen.' % fileName)

    return open(outputFileName + '_filtered.xml', 'ab')

def writePage(pageObj, outputFile):
    page = ET.Element('page')
    createSubElement(page, 'title', pageObj)
    createSubElement(page, 'ns', pageObj, 'namespace')
    createSubElement(page, 'id', pageObj)

    sortedRevisions = sortRevisions(pageObj)
    for revisionObj in sortedRevisions:
        revision = createSubElement(page, 'revision', pageObj)
        createSubElement(revision, 'id', revisionObj)
        createSubElement(revision, 'timestamp', revisionObj)

        contributor = createSubElement(revision, 'contributor')
        contributorObj = revisionObj.contributor
        if contributorObj is not None:
            createSubElement(contributor, 'username', contributorObj, 'user_text')
            createSubElement(contributor, 'id', contributorObj)

        createSubElement(revision, 'comment', revisionObj)
        createSubElement(revision, 'model', revisionObj)
        createSubElement(revision, 'format', revisionObj)
        createSubElement(revision, 'text', revisionObj)

    tree = ET.ElementTree(page)
    print("Writing page %s to disk." % pageObj.title)
    tree.write(outputFile, encoding="UTF-8")

def createSubElement(parent, elementName, obj=None, objAttrName=None):
    """ Add a new child to parent with elementName as its name. If obj
    is set, its attribute with the name of the element will be written
    into the element's content if such an attribute exist.
    If the element's name and the attribute to read differ, objAttrName
    can be used. """
    if not objAttrName:
        objAttrName = elementName
    element = ET.SubElement(parent, elementName)
    try:
        element.text = (str(getattr(obj, objAttrName)))
    except AttributeError: # write an empty element:
        pass
    return element

def filterForDeletionDiscussions(path):
    """ Load dump file(s) from path and iterate over their pages and their
    revisions. All revisions will be matched against the blocks dict to
    calculate how many seconds after the creation of the revision, the
    author was blocked (if s/he was blocked at all afterwards).
    """
    for fileName in extractFileNamesFromPath(path):
        print('Now processing the file "%s".' % fileName)

        outputFile = generateOutputFile(fileName)
        copyXMLDumpHeadToFile(fileName, outputFile)

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

                writePage(page, outputFile)

        outputFile.write(encode('</mediawiki>'))
        outputFile.close()

def copyXMLDumpHeadToFile(fileName, outputFile):
    """ Copies the XML dump's head into the new file. If the XML file was
    properly generated, this includes the opening mediawiki-tag as well
    as the siteinfo-element. """
    with open_file(fileName) as currentFile:
        while True:
            line = currentFile.readline()
            outputFile.write(line)
            if '</siteinfo>' in decode(line).lower():
                break

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="WikiWho DiscussionParser DeletionDiscussionFilter: This program will extract all deletion discussions from the dumps and write them to disk.",
                                     epilog="""
                                     WikiWho DiscussionParser, Copyright (C) 2015 Fabian Flöck, Maribel Acosta, Michael Ruster (based on wikiwho by Fabian Flöck, Maribel Acosta).
                                     WikiWho DiscussionParser comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.
                                     """)

    parser.add_argument('pageDumpPath', help='Path to the Wikipedia page(s) dump (XML, 7z, bz2…).')

    args = parser.parse_args()

    filterForDeletionDiscussions(args.pageDumpPath)
