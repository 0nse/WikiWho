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

import socket

from sys import argv

def isDeletionDiscussion(page):
    """ A deletion discussion (AfD) is set in the Wikipedia namespace 4. It
    starts with 'Wikipedia:Articles for deletion/' with a few exceptions. These
    exceptions are AfD collections using templates to link to the original
    discussions. """
    if (page.namespace is 4 \
       and page.title.startswith('Wikipedia:Articles for deletion/') \
       # Old links to old discussions:
       and not page.title.startswith('Wikipedia:Articles for deletion/Old/') \
       and page.title != 'Wikipedia:Articles for deletion/Old' \
       # Log collects discussions by including them through a template:
       and not page.title.startswith('Wikipedia:Articles for deletion/Log/') \
       and page.title != 'Wikipedia:Articles for deletion/Log'):
        return True

    return False

def isRegisteredUser(page):
    """ A user must be a page of namespace 2:User and the page must start with
    'User:'. Furthermore, an IP address may not follow as we are looking for
    registered accounts only. This test requires the socket module which is
    imported in filterDumps."""
    if (page.namespace is 2 \
       and page.title.startswith('User:')):
        userName = page.title[5:]

        if '/' in userName:
            return False

        try: # test for IPv4 address:
            socket.inet_pton(socket.AF_INET, userName)
        except OSError:
            try: # test for IPv6 address:
                socket.inet_pton(socket.AF_INET6, userName)
            except OSError:
                return True

    # not user page or IP address:
    return False

def generateOutputFile(fileName):
    """ Generate an output file name by replacing fileName's extension with
    'xml' or appending '.xml' if no known was found. """
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
    """ Write the pageObj into outputFile as XML. """
    page = ET.Element('page')
    createSubElement(page, 'title', pageObj)
    createSubElement(page, 'ns', pageObj, 'namespace')
    createSubElement(page, 'id', pageObj)

    sortedRevisions = sortRevisions(pageObj)
    for revisionObj in sortedRevisions:
        revision = createSubElement(page, 'revision', pageObj)
        createSubElement(revision, 'comment', revisionObj)
        createSubElement(revision, 'format', revisionObj)
        createSubElement(revision, 'id', revisionObj)
        createSubElement(revision, 'minor', revisionObj)
        createSubElement(revision, 'model', revisionObj)
        createSubElement(revision, 'parentid', revisionObj)
        createSubElement(revision, 'sha1', revisionObj)
        createSubElement(revision, 'text', revisionObj)
        createSubElement(revision, 'timestamp', revisionObj)

        contributor = createSubElement(revision, 'contributor')
        contributorObj = revisionObj.contributor
        if contributorObj is not None:
            createSubElement(contributor, 'id', contributorObj)
            createSubElement(contributor, 'username', contributorObj, 'user_text')

    tree = ET.ElementTree(page)
    print("[I] Writing page %s to disk." % pageObj.title)
    tree.write(outputFile, encoding="UTF-8")

def createSubElement(parent, elementName, obj=None, objAttrName=None):
    """ Add a new child to parent with elementName as its name. If obj is set,
    its attribute with the name of the element will be written into the
    element's content if such an attribute exist.
    If the element's name and the attribute to read differ, objAttrName can be
    used.
    Special treatment is applied to the 'minor' attribute as it is a boolean
    value. Just like in the dumps, the element is only written if it is True. In
    the case of minor being false, None will be returned!
    """
    if not objAttrName:
        objAttrName = elementName

    if objAttrName == 'minor':
        isMinor = getattr(obj, objAttrName)
        if isMinor:
            return ET.SubElement(parent, elementName)
        else:
            return None

    element = ET.SubElement(parent, elementName)
    try:
        element.text = (str(getattr(obj, objAttrName)))
    except AttributeError: # write an empty element:
        pass
    return element

def filterDumps(path, condition=isDeletionDiscussion):
    """ Load dump file(s) from path and iterate over their pages and their
    revisions. All revisions will be matched against condition. Positive matches
    will be written into the output file as XML.
    condition is a method that returns a boolean value and analyses a Page
    object.
    """
    for fileName in extractFileNamesFromPath(path):
        print('[I] Now processing the file "%s".' % fileName)

        outputFile = generateOutputFile(fileName)
        copyXMLDumpHeadToFile(fileName, outputFile)

        # Access the file.
        dumpIterator = mwIterator.from_file(open_file(fileName))
        # Iterate over the pages.
        for page in dumpIterator:
            if condition(page):
                writePage(page, outputFile)

        outputFile.write(encode('</mediawiki>'))
        outputFile.close()

def copyXMLDumpHeadToFile(fileName, outputFile):
    """ Copies the XML dump's head into the new file. If the XML file was
    properly generated, this includes the opening mediawiki-tag as well as the
    siteinfo-element. """
    with open_file(fileName) as currentFile:
        while True:
            line = currentFile.readline()
            outputFile.write(line)
            if '</siteinfo>' in decode(line).lower():
                break

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="WikiWho DiscussionParser DumpFilter: This program will extract all pages from the dumps matching a condition and write them to disk.",
                                     epilog="""
                                     WikiWho DiscussionParser, Copyright (C) 2015 Fabian Flöck, Maribel Acosta, Michael Ruster (based on wikiwho by Fabian Flöck, Maribel Acosta).
                                     WikiWho DiscussionParser comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. For more information, see the LICENSE and README.md files this program should have been distributed with.
                                     """)

    parser.add_argument('pageDumpPath', help='Path to the Wikipedia page(s) dump (XML, 7z, bz2…).')
    parser.add_argument('-c', nargs='?', default=isDeletionDiscussion,
                        dest='condition', type=str,
                        help='A boolean method that returns True or False when given a Page object. Available options are "isDeletionDiscussion" and "isRegisteredUser". Default: "isDeletionDiscussion".')

    args = parser.parse_args()

    if args.condition in ['isDeletionDiscussion', 'isRegisteredUser']:
        filterDumps(args.pageDumpPath, eval(args.condition))
    else:
        print('[E] Only "isDeletionDiscussion" and "isRegisteredUser" are valid conditions.')
        import sys
        sys.exit(1)
