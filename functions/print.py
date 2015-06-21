from copy import deepcopy, copy

from functions.postProcessText import cleanText

def printAllRevisions(order, revisions):

    for (revision, vandalism) in order:
        if not(vandalism):
            printRevision(revisions[revision])

def printRevision(revision):
    """Print all text that was introduced in this revision."""

    print("Printing authorhship for revision: ", revision.wikipedia_id)
    textList = []
    for hash_paragraph in revision.ordered_paragraphs:
        p_copy = deepcopy(revision.paragraphs[hash_paragraph])
        paragraph = p_copy.pop(0)

        for hash_sentence in paragraph.ordered_sentences:
            sentence = paragraph.sentences[hash_sentence].pop(0)

            for word in sentence.words:
                if word.revision is revision.wikipedia_id:
                    textList.append(word.value)
    print(cleanText(textList, revision.contributor_name))
