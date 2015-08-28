#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Maribel Acosta
@author: Fabian Floeck
@author: Michael Ruster
'''
import csv

import functions.TextPostProcessing as TextPostProcessing
import functions.WarningTemplates as WarningTemplates
import BlockTimeCalculation

import AfDTemplatesProcessor as AfDTemplates

from datetime import datetime

def writeAllRevisions(order, revisions, blocks, pageName = None):
    """ Writes the revisions to disk. Don't pass a pageName if you want to
    process deletion discussions. The pageName is used for user warnings to
    determine the admonished user. """
    assert (not pageName) ^ (not blocks), '[E] Illegal configuration. Both parameters pageName and blocks are set. One must be empty.'
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
    revision got blocked.
    Revisions of anonymous users will be ignored as IP addresses are not unique.
    Likewise, bots will be ignored as we are interested in human communication.

    The list of bots can be retrieved from running WikiWho w/o the Bot removal
    and executing the bash command (replacing the space delimiter with a tab):
    grep 'Bot	' deletionRevisions.csv | cut -f 3 -d '	' | sort | uniq
    For our dump, we detected 55 bots with SineBot being the most active. """
    # we will not process anonymous users or bots:
    if not revision.contributor_id or \
      revision.contributor_name.endswith('Bot'):
        return

    text = TextPostProcessing.clean(text, revision.contributor_name)

    text = removeAfDText(text, revision.timestamp)

    # only print a line when this revision introduced new text:
    if text.strip():
        secondsToBlock = BlockTimeCalculation.calculateSecondsUntilNextBlock(blocks, revision.contributor_name, revision.timestamp)
        print("[I] Writing authorship for revision %s to disk." % revision.wikipedia_id)
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
                                                WarningTemplates.npa)
def writeUserWarning(text, revision, pageName):
    """ Writes user warnings in a block log format into 'userWarnings.csv'. The
    columns look as follows:
    timestamp | blocked user name | warning | issuer ID | issuer name """
    assert pageName.startswith('User talk:'), '[E] Revision is not a user page:"%s"' % pageName
    blockedUserName = pageName[10:]

    for templateRe in templatesRe:
        matchedTemplate = templateRe.search(text)
        if matchedTemplate:
            matchedWarning = matchedTemplate.group(1)
            print('[I] Writing admonished user "%s" with warning "%s" to disk.' % (blockedUserName, matchedWarning))
            with open('userWarnings.csv', 'a', newline='') as csvFile:
                spamwriter = csv.writer(csvFile, delimiter='\t',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

                spamwriter.writerow([revision.timestamp,
                                     blockedUserName,
                                     revision.wikipedia_id,
                                     matchedWarning,
                                     revision.contributor_id,
                                     revision.contributor_name])
            break

#===============================================================================
# The following method uses regular expressions. The expression is compiled
# before the method definition so that it is only compiled once:
#===============================================================================
afdTemplates = AfDTemplates.extractTemplateRevisions('xmls/afd_templates.xml')

def removeAfDText(text, timestamp):
    """ Although AfD headers and footers are obviously templates, the dumps do
    not contain them as marked up template but as the text from them being
    resolved. Thus, the text has to be manually removed in a preprocessing step.
    """
    for templateTitle in afdTemplates:
        for (templateTimestamp, templateRe) in afdTemplates[templateTitle]:
            # with the templateTimestamps sorted descendingly, the template
            # revision younger than but closest to the timestamp will be the
            # only template that a subst: could have used.
            if timestamp > templateTimestamp:
                text = templateRe.sub("", text)
                break

    return text
