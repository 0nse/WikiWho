import csv

from functions.postProcessText import cleanText

def writeAllRevisions(order, revisions):
    for (revision, vandalism) in order:
        if not(vandalism):
            writeRevision(revisions[revision])

def writeRevision(revision):
    """This method writes a revision to a CSV file. This features the
    author and timestamp but most importantly the text introduced in
    this revision. Said text will be cleaned so that markup is removed.
    It will append to this directory's "deletionRevisions.csv". Make
    sure, this script has writing access.
    """
    textList = []
    for hash_paragraph in revision.ordered_paragraphs:
        para = revision.paragraphs[hash_paragraph]
        paragraph = para[-1]

        for hash_sentence in paragraph.ordered_sentences:
            sentence = paragraph.sentences[hash_sentence][-1]

            textList.extend( [word.value for word in sentence.words if word.revision is revision.wikipedia_id] )

    text = cleanText(textList, revision.contributor_name)

    # only print a line when this revision introduced new text
    if text.strip():
        print("Writing authorhship for revision %s to disk." % revision.wikipedia_id)
        with open('deletionRevisions.csv', 'a', newline='') as csvFile:
            spamwriter = csv.writer(csvFile, delimiter='\t',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([revision.timestamp,
                                 revision.contributor_id,
                                 revision.contributor_name,
                                 revision.wikipedia_id,
                                 text])
