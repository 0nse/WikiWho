#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Maribel Acosta
@author: Fabian Floeck
@author: Michael Ruster
'''
import csv
import re

import functions.TextPostProcessing as TextPostProcessing
import functions.WarningTemplates as WarningTemplates
import BlockTimeCalculation

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

    text = removeAfDText(text)

    # only print a line when this revision introduced new text:
    if text.strip():
        secondsToBlock = BlockTimeCalculation.calculateSecondsUntilNextBlock(blocks, revision.contributor_name, revision.timestamp)
        print("[I] Writing authorship for revision %s to disk." % revision.wikipedia_id)
        with open('deletionRevisions.csv', 'a', newline='') as csvFile:
            writer = csv.writer(csvFile, delimiter='\t',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([revision.timestamp,
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
                writer = csv.writer(csvFile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

                writer.writerow([revision.timestamp,
                                 blockedUserName,
                                 revision.wikipedia_id,
                                 matchedWarning,
                                 revision.contributor_id,
                                 revision.contributor_name])
            break

#===============================================================================
# The following method uses regular expressions. The expressions are compiled
# before the method definition so that they are compiled only once:
#===============================================================================
# The following list of regular expressions has been build by analysing the most
# frequently made posts in AfDs.
afdTemplates = [ re.compile('(wikipediadeletionprocess )?(relistingdiscussions )?((wp)?relist )?(this afd is being )?relisted to generate a (clearer consensus|more thorough discussion so (a clearer |that )?(consensus|a decision) may (usefully )?be reached)( br| emsp| please add new discussion below this notice thanks)?'),
                 re.compile('(was proposed for deletion )?this page is an archive of (the discussion (about |surrounding ))?the proposed deletion (of the (article below|page entitled( \w)*) )?this page is (no longer live|kept as an historic record)'),
                 re.compile('this page is now preserved as an archive of the debate and like (some )?other (delete |vfd )?(sub)?pages is no longer live subsequent comments on the issue the deletion or (on )?the decisionmaking process should be placed on the relevant live pages please do not edit this page'),
                 re.compile('this page is an archive of the proposed deletion of the article below further comments should be made on the (appropriate discussion page such as the )?articles talk page (if it exists )?or (on a votes for undeletion nomination|after the end of this archived section)'),
                 re.compile('note this debate has been added to the .*?deletion list of .*?deletions( ron)?'),
                 re.compile('preceding wikipediasignatures (unsigned|undated)? comment (was )?added( at ?)?( by)?'),
                 re.compile('remove this template when closing this afd'),
                 re.compile('this afd nomination was incomplete (missing step )?it is listed now'),
                 re.compile('this afd nomination was wikipediaarticlesfordeletion howtolistpagesfordeletion orphaned listing now'),
                 re.compile('further comments should be made on the articles talk page rather than here so that this page is preserved as an historic record (br )?'),
                 re.compile('no further edits should be made to (this )?page'),
                 re.compile('the result( of the debate)? was'),
                 re.compile('(the (above discussion|following discussion)|this page) is ((now )?preserved as an archive of the debate( and (like other delete pages )?is no longer live)?|an archived debate of the proposed deletion of the article( below)?)'),
                 re.compile('(please do not modify it )?subsequent comments (on the issue the deletion or on the decisionmaking process )?should be (made|placed) on the (appropriate|relevant) (discussion|live) page(s)?( such as the articles talk page or (o|i)n an?)?') ]
spacesRe = re.compile(r' {2,}')

def removeAfDText(text):
    """ Although templates can be put into text without them expanding, it is
    advised against doing so. Therefore, templates are not marked as such but
    instead the dumps contain the templates text next to actual content. We try
    our best to remove the most frequently used templates using regular
    expressions. These were build after sorting the AfD posts by frequency.
    """
    for templateRe in afdTemplates:
        text = templateRe.sub("", text)

    # Remove leftover consecutive spaces that could appear after applying res:
    text = spacesRe.sub(' ', text)
    return text
