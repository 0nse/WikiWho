#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Maribel Acosta
@author: Fabian Floeck
@author: Michael Ruster
'''
import csv

import functions.TextPostProcessing as TextPostProcessing
import BlockTimeCalculation
import WarningTemplates

from datetime import datetime

def writeAllRevisions(order, revisions, blocks, pageName = None):
    """ Writes the revisions to disk. Don't pass a pageName if you want to
    process deletion discussions. The pageName is used for user warnings to
    determine the admonished user. """
    for (revisionId, vandalism) in order:
        if not(vandalism):
            revision = revisions[revisionId]
            text = extractCurrentRevisionsText(revision, blocks)

            if not pageName:
                writeDeletionDiscussion(text, revision, blocks)
            else:
                writeUserWarning(text, revision, pageName)

def extractCurrentRevisionsText(revision, blocks):
    """ Iterates over the revision's text and extracts all text that has been
    introduced in this revision as a list. """
    textList = []
    for hash_paragraph in revision.ordered_paragraphs:
        para = revision.paragraphs[hash_paragraph]
        paragraph = para[-1]

        for hash_sentence in paragraph.ordered_sentences:
            sentence = paragraph.sentences[hash_sentence][-1]

            textList.extend( [word.value for word in sentence.words if word.revision is revision.wikipedia_id] )

    return TextPostProcessing.merge(textList)


def writeDeletionDiscussion(text, revision, blocks):
    """ Writes this deletion discussion to disk. Text is this revision's text.
    Said text will be cleaned so that markup is removed. It will append to this
    directory's 'deletionRevisions.csv'. Make sure, this script has writing
    access. The CSV will have the following columns:
    timestamp | contrib ID | contrib name | rev ID | text | seconds to block
    Seconds to block is the time in seconds until the user who is author of this
    revision got blocked. """
    text = TextPostProcessing.clean(text, revision.contributor_name)

    # only print a line when this revision introduced new text
    if text.strip():
        secondsToBlock = BlockTimeCalculation.calculateSecondsUntilNextBlock(blocks, revision.contributor_name, revision.timestamp)
        print("[I] Writing authorhship for revision %s to disk." % revision.wikipedia_id)
        with open('deletionRevisions.csv', 'a', newline='') as csvFile:
            spamwriter = csv.writer(csvFile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([revision.timestamp,
                                 revision.contributor_id,
                                 revision.contributor_name,
                                 revision.wikipedia_id,
                                 text,
                                 secondsToBlock])

# calculate the templates once:
templatesRe = WarningTemplates.mergeTemplatesRe(WarningTemplates.vandalism,
                                                WarningTemplates.disruptive,
                                                WarningTemplates.agf,
                                                WarningTemplates.harass,
                                                WarningTemplates.npa,
                                                WarningTemplates.tempabuse)
def writeUserWarning(text, revision, pageName):
    """ Writes user warnings in a block log format into 'userWarnings.csv'. The
    columns look as follows:
    timestamp | blocked user name | warning | issuer ID | issuer name """
    assert revision.title.startsWith('User:'), '[E] Revision is not a user page:"%s"' % revision.title
    blockedUserName = revision.title[5:]

    for templateRe in templatesRe:
        if templateRe.search(text): # contains warning
            print('[I] Writing admonished user "%s" to disk.' % revision.contributor_name)
            with open('userWarnings.csv', 'a', newline='') as csvFile:
                spamwriter = csv.writer(csvFile, delimiter='\t',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

                spamwriter.writerow([revision.timestamp,
                                     blockedUserName,
                                     revision.wikipedia_id,
                                     text,
                                     revision.contributor_id,
                                     revision.contributor_name])
            break
