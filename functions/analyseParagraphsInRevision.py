from structures import Text
from structures.Paragraph import Paragraph

def analyseParagraphsInRevision(revision_curr, revision_prev, text_curr, revisions):
    # Hash table.
    paragraphs_ht = {}

    # Containers for unmatched and matched paragraphs.
    unmatched_paragraphs_curr = []
    unmatched_paragraphs_prev = []
    matched_paragraphs_prev = []

    # Split the text of the current into paragraphs.
    paragraphs = Text.splitIntoParagraphs(text_curr)

    # Iterate over the paragraphs of the current version.
    for paragraph in paragraphs:

        # Build Paragraph structure and calculate hash value.
        paragraph = paragraph.strip()
        hash_curr = Text.calculateHash(paragraph)
        matched_curr = False

        # If the paragraph is in the previous revision,
        # update the authorship information and mark both paragraphs as matched (also in HT).
        if (hash_curr in revision_prev.ordered_paragraphs):

            for paragraph_prev in revision_prev.paragraphs[hash_curr]:
                if (not paragraph_prev.matched):
                    matched_curr = True
                    paragraph_prev.matched = True
                    matched_paragraphs_prev.append(paragraph_prev)

                    # TODO: added this (CHECK).
                    for hash_sentence_prev in paragraph_prev.sentences.keys():
                        for sentence_prev in paragraph_prev.sentences[hash_sentence_prev]:
                            sentence_prev.matched = True
                            for word_prev in sentence_prev.words:
                                word_prev.matched = True
                                word_prev.used.append(revision_curr.wikipedia_id)

                    addParagraphs(revision_curr, revision_prev, hash_curr, paragraph_prev)
                    break


        # If the paragraph is not in the previous revision, but it is in an older revision
        # update the authorship information and mark both paragraphs as matched.
        if ((not matched_curr) and (hash_curr in paragraphs_ht)):
            for paragraph_prev in paragraphs_ht[hash_curr]:
                if (not paragraph_prev.matched):
                    matched_curr = True
                    paragraph_prev.matched = True
                    matched_paragraphs_prev.append(paragraph_prev)

                    # TODO: added this (CHECK).
                    for hash_sentence_prev in paragraph_prev.sentences.keys():
                        for sentence_prev in paragraph_prev.sentences[hash_sentence_prev]:
                            sentence_prev.matched = True
                            for word_prev in sentence_prev.words:
                                word_prev.matched = True
                                word_prev.used.append(revision_curr.wikipedia_id)

                                if (revision_prev.wikipedia_id not in word_prev.used):
                                    word_prev.freq.append(revision_curr.wikipedia_id)

                    addParagraphs(revision_curr, revision_prev, hash_curr, paragraph_prev)
                    break

        # If the paragraph did not match with previous revisions,
        # add to container of unmatched paragraphs for further analysis.
        if (not matched_curr):
            paragraph_curr = Paragraph()
            paragraph_curr.hash_value = Text.calculateHash(paragraph)
            paragraph_curr.value = paragraph

            revision_curr.ordered_paragraphs.append(paragraph_curr.hash_value)

            if (paragraph_curr.hash_value in revision_curr.paragraphs.keys()):
                revision_curr.paragraphs[paragraph_curr.hash_value].append(paragraph_curr)
            else:
                revision_curr.paragraphs.update({paragraph_curr.hash_value : [paragraph_curr]})

            unmatched_paragraphs_curr.append(paragraph_curr)


    # Identify unmatched paragraphs in previous revision for further analysis.
    for paragraph_prev_hash in revision_prev.ordered_paragraphs:
        for paragraph_prev in revision_prev.paragraphs[paragraph_prev_hash]:
            if (not paragraph_prev.matched):
                unmatched_paragraphs_prev.append(paragraph_prev)

    return (unmatched_paragraphs_curr, unmatched_paragraphs_prev, matched_paragraphs_prev, paragraphs_ht)

def addParagraphs(revision_curr, revision_prev, hash_curr, paragraph_prev):
    # Add paragraph to current revision.
    if (hash_curr in revision_curr.paragraphs.keys()):
        revision_curr.paragraphs[paragraph_prev.hash_value].append(paragraph_prev)
        revision_curr.ordered_paragraphs.append(paragraph_prev.hash_value)
    else:
        revision_curr.paragraphs.update({paragraph_prev.hash_value : [paragraph_prev]})
        revision_curr.ordered_paragraphs.append(paragraph_prev.hash_value)
