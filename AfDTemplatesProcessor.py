#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Aug 13, 2015

@author: Michael Ruster
'''
import re

from mw.xml_dump import Iterator as mwIterator
from mw.xml_dump.functions import open_file

import WikiCodeCleaner.clean as Cleaner
import WikiCodeCleaner.dropNested as TemplateProcessor

def extractTemplateRevisions(fileName):
    ''' Used to build regular expressions of a set of templates as given via an
    XML dump (raw or 7z, bz2 etc.) through fileName. The result will be a
    dictionary with the template name as title and a list of its revisions as re
    as values.
    For the list of Articles of Deletion templates, see:
    https://en.wikipedia.org/w/index.php?title=Category:Articles_for_deletion_templates&oldid=547048916
    For exporting them to XML, see:
    https://en.wikipedia.org/wiki/Special:Export '''

    dumpIterator = mwIterator.from_file(open_file(fileName))
    templates = {}

    # Iterate over the templates.
    for template in dumpIterator:
        if template.title == 'Template:Afd3':
            # This template is too general to be detected as it only consists of
            # another template that it substitutes.
            continue

        revisions = []
        notice = 0
        for revision in template:
            text = revision.text

            # mark templates for later wildcard replacement:
            text = TemplateProcessor.dropNested(text, r'{{', r'}}', TemplateProcessor.replaceSpansWithRePattern)

            text = Cleaner.clean(text)

            # If there is no alphabetical letter in the text there are also no
            # words and we better skip. Ignore our placeholder as it allows any
            # text:
            textPlaceholderFree = text.replace(TemplateProcessor.regexSubstitutionPlaceholderString, '')
            if not re.compile('[A-Z,a-z]+').search(textPlaceholderFree):
                continue

            text = re.escape(text.strip())
            # If text hardly contains any words, we better ignore it as being
            # too generic:
            if text.count(' ') < 4:
                continue

            # if we have a wildcard in the beginning or the end, we must mark
            # beginning and end to not match too much:
            if text.startswith(TemplateProcessor.regexSubstitutionPlaceholderString):
                text = '^' + text
            if text.endswith(TemplateProcessor.regexSubstitutionPlaceholderString):
                text += '$'

            text = text.replace(TemplateProcessor.regexSubstitutionPlaceholderString, '.*?')

            textRe = re.compile(text)
            revisionTuple = (revision.timestamp, textRe)

            revisions.append(revisionTuple)

        # Sort descendingly so that the newest revision is the first:
        revisions.sort(reverse=True)
        templates[template.title] = revisions

    return templates

if __name__ == '__main__':
    extractTemplateRevisions('xmls/afd_templates.xml')
