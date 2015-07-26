#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
@author: Maribel Acosta
@author: Fabian Floeck
@author: Michael Ruster
'''
import re

from functions.determineAuthorship import determineAuthorship

from structures.Revision import Revision

# Spam detection variables.
CHANGE_PERCENTAGE = -0.40
PREVIOUS_LENGTH = 1000
CURR_LENGTH = 1000
FLAG = "move"

def processDeletionDiscussion(page):
    # Hash table.
    spam = []

    # Revisions to compare.
    revision_curr = Revision()
    revision_prev = Revision()
    text_curr = None

    # Container of current revision (order).
    revisions_order = []
    revisions = {}

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
        if (revision.comment != None and revision.comment.find(FLAG) > 0):
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
            revision_curr.wikipedia_id = int(revision.id)
            revision_curr.length = len(revision.text)
            revision_curr.timestamp = revision.timestamp

            # Some revisions don't have contributor.
            if (revision.contributor != None):
                revision_curr.contributor_id = revision.contributor.id
                revision_curr.contributor_name = revision.contributor.user_text
            else:
                revision_curr.contributor_id = 'Not Available ' + revision.id
                revision_curr.contribur_name = 'Not Available ' + revision.id

            # Content within the revision.
            text_curr = removeAfDText(revision.text)
            text_curr = preprocessAbbreviations(text_curr)
            text_curr = useEnDashForParentheticalExpression(text_curr)
            text_curr = removeStandaloneLinks(text_curr)
            text_curr = text_curr.lower()
            revision_curr.content = text_curr

            # Perform comparison.
            vandalism = determineAuthorship(revision_curr, revision_prev, text_curr, revisions)


            if (not vandalism):
                # Add the current revision with all the information.
                revisions.update({revision_curr.wikipedia_id : revision_curr})
                revisions_order.append((revision_curr.wikipedia_id, False))

                # Calculate the number of tokens in the revision.
                total = 0
                for p in revision_curr.ordered_paragraphs:
                    for paragraph_curr in revision_curr.paragraphs[p]:
                        for hash_sentence_curr in paragraph_curr.sentences.keys():
                            for sentence_curr in paragraph_curr.sentences[hash_sentence_curr]:
                                total = total + len(sentence_curr.words)
                revision_curr.total_tokens = total

            else:
                revisions_order.append((revision_curr.wikipedia_id, True))
                revision_curr = revision_prev
                spam.append(revision.sha1)

    return (revisions_order, revisions)

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

def useEnDashForParentheticalExpression(text):
    """ structures.Text.splitIntoWords(text) will split regular dashes into a
    separate word. Thus a sentence "I like - dare I say love - you" would be
    split into ["I","like","-","dare","I","say","love","-","you"]. When
    merging the text later on, we would end up with "like-dare" and in the end
    with "likedare".
    To prevent this, we replace the dashes, which are used as parenthetical
    expressions with an en dash."""
    return text.replace(" - ", " – ")


#===============================================================================
# The following methods use regular expressions. These expressions are compiled
# before the method definition so that they are only compiled once:
#===============================================================================
afdHeader = """:\'\'The following discussion is an archived debate of the proposed deletion of the article below. <span style="color:red">\'\'\'Please do not modify it.\'\'\'</span>  Subsequent comments should be made on the appropriate discussion page (such as the article\'s [[Help:Using talk pages|talk page]] or in a [[Wikipedia:Deletion review|deletion review]]).  No further edits should be made to this page.\'\'"""
afdFooter = """:\'\'The above discussion is preserved as an archive of the debate.  <span style="color:red">\'\'\'Please do not modify it.\'\'\'</span> Subsequent comments should be made on the appropriate discussion page (such as the article\'s [[Help:Using talk pages|talk page]] or in a [[Wikipedia:Deletion review|deletion review]]). No further edits should be made to this page."""
resultRe = re.compile("The result was '''[^']+'''.")

def removeAfDText(text):
    """ Although AfD headers and footers are obviously templates, the dumps do
    not contain them as marked up template but as the text from them being
    resolved. Thus, the text has to be manually removed in a preprocessing step.
    """
    text = text.replace(afdHeader, "")
    text = text.replace(afdFooter, "")
    text = resultRe.sub("", text)

    return text


#===============================================================================
# %s may be surrounded by symbols and probably ends with a dot. However, it
# cannot be extracted in a re if no symbol separates it from an alphabetic
# letter. This is to prevent mismatches as part of real words.
abbreviationNotPartOfAWord = r"(?i)[^a-z,A-Z](%s\.{0,1})[^a-z,A-Z]"
# We allow a single space after the first dot because mobile phone keyboards
# often add them (e.g. SwiftKey) automatically.
ieRe = re.compile(abbreviationNotPartOfAWord % "i\. {0,1}e")
egRe = re.compile(abbreviationNotPartOfAWord % "e\. {0,1}g")
nbRe = re.compile(abbreviationNotPartOfAWord % "n\. {0,1}b")
psRe = re.compile(abbreviationNotPartOfAWord % "p\. {0,1}s")

def preprocessAbbreviations(text):
    """ This method replaces the commonly used abbreviations i.e., e.g., n.b.
    and PS. with "i-e", "e-g", "n-b" and "p-s" respectively to prevent later
    steps splitting them into the words "i", "e", "g", "n", "b", "p" and "s".
    At least for "i.e.", this is an important step, considering we want to
    inspect the influence the use of the word "i" (and "you") has.
    If these abbreviations are written without intermediate dot (e.g. "eg."),
    they will be already interpreted as one word.
    """
    # All substitutes are space-padded so that words are not merged together.
    text = ieRe.sub(" i-e ", text)
    text = egRe.sub(" e-g ", text)
    text = nbRe.sub(" n-b ", text)
    text = psRe.sub(" p-s ", text)

    return text


#===============================================================================
# Import the protocols as given by WikiCodeCleaner. Remove '//' as it does not
# identify a protocol. Add 'www.' because often links are posted without their
# protocol.
try:
    from WikiCodeCleaner.links import wgUrlProtocols
except:
    from sys import path
    path.append('../WikiCodeCleaner')
    from WikiCodeCleaner.links import wgUrlProtocols

try:
    wgUrlProtocols.remove('//')
except ValueError: # not in list
    pass
# 'www.' must not follow a slash or colon. Else, it would be matched in URIs
# that contain it as a subdomain but also start with a valid protocol. In these
# cases, the match should always happen starting with the protocol (because it
# appears earlier).
wgUrlProtocols.append('[^:,/]www.')
uriIndicatorsEscaped = [re.escape(indicator) for indicator in wgUrlProtocols]
# URIs may not begin with '[' because else they would probably be alread wrapped
# in markup.
# (?:^[^\[])
#    (?: )   is a non matching group.
#    ^       beginning of the line
#    |[^\[]  or something that is not an opening square bracket
#    This is needed because making [ not appearing optional would allow it
#    again. Therefore, the beginning must either be the beginning of the line or
#    anything but an opening square bracket.
# ((?i)(?:%s)[^ ]+)
#    (?i)    case insensitive
#    (?:%s)  replaces the regex escaped protocols (OR-concatenated) in an un-
#            matched group.
#    [^ ]+   symbols that aren't a space (URI symbols after the protocol/www-
#            subdomain).
urisRe = re.compile('(?:^|[^\[])((?i)(?:%s)[^ ]+)' % '|'.join(uriIndicatorsEscaped))

def removeStandaloneLinks(text):
    """ Remove links that were just pasted into the text without the use of
    WikiCode. Frequently, users dump a link into their reply without marking
    them as actual links.
    We cannot remove those links in a postprocessing step because we lose
    crucial information: 'http://ddg.gg/ great site' would have been merged into
    'http://ddg.gg/great site'. However, if the trailing space of the slash
    would not be removed, we would end up with 'http:/ / ddg.gg/ great site'.
    Thus we apply this before any splitting in words.
    """
    text = urisRe.sub('', text)

    return text
