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
boxBeginningRe = re.compile('(?i){{[a-z]*box[ \n]*\|.*?(small)?text *=(.*)', re.DOTALL)
#                            \__/        \___/   \____/
#            case insensitive_/        mbox etc.   spaces or newlines
templateValuesRe = re.compile('.*?}}(.*)')
#                              \_/   \/
#     any text before template end   any text after the template
signature = '%s %s' % (Signature.userRe.pattern, Signature.timestampRe.pattern)

def extractMessageBoxText(text):
    ''' Extract the text given in the (small)text attribute of a message box
    template: https://en.wikipedia.org/wiki/Module:Message_box
    Naïvely, we assume that there is no relevant context outside the box. This
    is a simplification which can easily lead to an incomplete representation of
    the template's content. However, it is the only option without to also
    processing the box template and substituting it with the text.
    If no message box is found in text, text is returned as is. '''
    boxBeginning = boxBeginningRe.search(text)

    if boxBeginning:
        assert boxBeginning.group(2), '[E] There was no text following the box template.'

        # extract the actual text:
        text = boxBeginning.group(2)

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
            # -2 due to '|'
            text = text[:position - 1]
        else:
            # -2 due to '}}'
            text = text[:position - 2]

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

            # If a message box was used (which happens frequently) extract its
            # text:
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
            # words and we better skip. Ignore our placeholder as it allows any
            # text:
            textPlaceholderFree = text.replace(TemplateProcessor.regexSubstitutionPlaceholderString, '')
            if not re.compile('[A-Z,a-z]+').search(textPlaceholderFree):
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
            revisionTuple = (revision.timestamp, textRe)

            revisions.append(revisionTuple)

        # Sort descendingly so that the newest revision is the first:
        revisions.sort(reverse=True)
        templates[template.title] = revisions

    return templates

if __name__ == '__main__':
    extractTemplateRevisions('xmls/afd_templates.xml')
