#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Aug 13, 2015

@author: Michael Ruster
'''
import re

from mw.xml_dump import Iterator as mwIterator
from mw.xml_dump.functions import open_file

import WikiCodeCleaner.signature as Signature
import WikiCodeCleaner.dropNested as TemplateProcessor

removableTagsRe = re.compile('(?i)</?(includeonly)|(nowiki)>', re.DOTALL)
#                           \__/
#                    case insensitive
noIncludeRe = re.compile('(?i)<noinclude>.*?</noinclude>', re.DOTALL)
#                         \__/           \_/
#                 case insensitive     non-greedy
boxBeginningRe = re.compile('(?i)(.*?){{[a-z]*box[ \n]*\|.*?(small)?text *=(.*)', re.DOTALL)
#                            \__/        \___/   \____/
#            case insensitive_/        mbox etc.   spaces or newlines
templateValuesRe = re.compile('.*?}}(.*)')
#                              \_/   \/
#     any text before template end   any text after the template
signature = '%s %s' % (Signature.userRe.pattern, Signature.timestampRe.pattern)

def extractMessageBoxText(text):
    ''' Extract the text given in the (small)text attribute of a message box
    template: https://en.wikipedia.org/wiki/Module:Message_box '''
    boxBeginning = boxBeginningRe.search(text)
    while boxBeginning:
        # extract the actual text:
        if boxBeginning.group(1):
            text = boxBeginning.group(1)
        if boxBeginning.group(3):
            text += boxBeginning.group(3)
        assert boxBeginning.group(3), '[E] There was no text following the box template.'

        previousSymbol = None
        nestingLevel = 2
        position = 0

        for symbol in text:
            if symbol == '{':
                nestingLevel += 1
            elif symbol == '}':
                nestingLevel -= 1

            # update the values:
            previousSymbol = symbol
            position += 1

            if (nestingLevel == 0 or
                (nestingLevel == 2 and symbol == '|')):
                break

        if previousSymbol == '|':
            appendedText = templateValuesRe.search(text).group(1)
            # -2 due to '|'
            text = text[:position - 1] + appendedText
        else:
            # -2 due to '}}'
            text = text[:position - 2] + text[position:]

        # are there any more boxes?
        boxBeginning = boxBeginningRe.search(text)

    return text


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

            if not text:
                continue

            text = extractMessageBoxText(text)

            # remove includeonly tags because they will be left out in subst and
            # nowiki. See https://en.wikipedia.org/wiki/Template:Nowiki
            # https://en.wikipedia.org/wiki/Template:Includeonly:
            text = removableTagsRe.sub('', text)

            # remove noinclude parts:
            text = noIncludeRe.sub('', text)

            # replace templates for later optional characters:
            text = TemplateProcessor.dropNested(text, r'{{', r'}}', TemplateProcessor.replaceSpansWithRePattern)

            # If there is no alphabetical letter in the text there are also no
            # words and we better skip:
            if not re.compile('[A-Z,a-z]+').search(text):
                continue

            text = re.escape(text.strip())

            # substitute signatures:
            text = text.replace('\\~'*4, signature)

            # if we have a wildcard in the beginning or the end, we must mark
            # beginning and end to not match too much:
            if text.startswith(TemplateProcessor.regexSubstitutionPlaceholderString):
                text = '^' + text
            if text.endswith(TemplateProcessor.regexSubstitutionPlaceholderString):
                text += '$'

            text = text.replace(TemplateProcessor.regexSubstitutionPlaceholderString, '.*?')

            textRe = re.compile(text)
            revisions.append(textRe)

        templates[template.title] = revisions
    return templates

if __name__ == '__main__':
    extractTemplateRevisions('xmls/afd_templates.xml')
