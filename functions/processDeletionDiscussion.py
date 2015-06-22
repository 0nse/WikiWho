import re

from etc.Relation import Relation

from functions.determineAuthorship import determineAuthorship

from structures.Revision import Revision

# Spam detection variables.
CHANGE_PERCENTAGE = -0.40
PREVIOUS_LENGTH = 1000
CURR_LENGTH = 1000
FLAG = "move"

def processDeletionDiscussion(page, revisions):
    # Hash table.
    spam = []

    # Revisions to compare.
    revision_curr = Revision()
    revision_prev = Revision()
    text_curr = None

    # Container of current revision order.
    revisions_order = []

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
            text_curr = removeAfDText(revision.text)
            text_curr = text_curr.lower()

            # Perform comparison.
            vandalism = determineAuthorship(revision_curr, revision_prev, text_curr, relation, revisions)


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
                relation.total_tokens = total

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

def removeAfDText(text):
    afdHeader = """:\'\'The following discussion is an archived debate of the proposed deletion of the article below. <span style="color:red">\'\'\'Please do not modify it.\'\'\'</span>  Subsequent comments should be made on the appropriate discussion page (such as the article\'s [[Help:Using talk pages|talk page]] or in a [[Wikipedia:Deletion review|deletion review]]).  No further edits should be made to this page.\'\'"""
    afdFooter = """:\'\'The above discussion is preserved as an archive of the debate.  <span style="color:red">\'\'\'Please do not modify it.\'\'\'</span> Subsequent comments should be made on the appropriate discussion page (such as the article\'s [[Help:Using talk pages|talk page]] or in a [[Wikipedia:Deletion review|deletion review]]). No further edits should be made to this page."""
    resultRe = re.compile("The result was '''[^']+'''.")

    text = text.replace(afdHeader, "")
    text = text.replace(afdFooter, "")
    text = resultRe.sub("", text)

    return text
