from functions.analyseParagraphsInRevision import analyseParagraphsInRevision
from functions.analyseSentencesInParagraphs import analyseSentencesInParagraphs
from functions.analyseWordsInSentences import analyseWordsInSentences

def determineAuthorship(revision_curr, revision_prev, text_curr, relation, revisions):
    matched_words_prev = []

    # Spam detection variable.
    UNMATCHED_PARAGRAPH = 0.0

    # Containers for unmatched paragraphs and sentences in both revisions.
    unmatched_sentences_curr = []
    unmatched_sentences_prev = []
    matched_sentences_prev = []
    possible_vandalism = False
    vandalism = False

    paragraphs_ht = {}

    # Analysis of the paragraphs in the current revision.
    (unmatched_paragraphs_curr, unmatched_paragraphs_prev, matched_paragraphs_prev, paragraphs_ht) = analyseParagraphsInRevision(revision_curr, revision_prev, text_curr, relation, revisions)

    # Analysis of the sentences in the unmatched paragraphs of the current revision.
    if (len(unmatched_paragraphs_curr)>0):
        (unmatched_sentences_curr, unmatched_sentences_prev, matched_sentences_prev, sentences_ht) = analyseSentencesInParagraphs(unmatched_paragraphs_curr, unmatched_paragraphs_prev, revision_curr, revision_prev, relation, revisions)

        #TODO: SPAM detection
        if (len(unmatched_paragraphs_curr)/float(len(revision_curr.ordered_paragraphs)) > UNMATCHED_PARAGRAPH):
            possible_vandalism = True

        # Analysis of words in unmatched sentences (diff of both texts).
        if (len(unmatched_sentences_curr)>0):
            (matched_words_prev, vandalism) = analyseWordsInSentences(unmatched_sentences_curr, unmatched_sentences_prev, revision_curr, possible_vandalism, relation, revisions)

    if (len(unmatched_paragraphs_curr) == 0):
        for paragraph in unmatched_paragraphs_prev:
            for sentence_key in paragraph.sentences.keys():
                for sentence in paragraph.sentences[sentence_key]:
                    if not(sentence.matched):
                        unmatched_sentences_prev.append(sentence)

    # Add the information of 'deletion' to words
    for unmatched_sentence in unmatched_sentences_prev:
        for word_prev in unmatched_sentence.words:
            if not(word_prev.matched):
                for elem in word_prev.deleted:
                    if (elem != revision_curr.wikipedia_id) and (elem in revisions.keys()):
                        if (revisions[elem].contributor_id != revision_curr.contributor_id):
                            if (elem in relation.redeleted.keys()):
                                relation.redeleted.update({elem : relation.redeleted[elem] + 1})
                            else:
                                relation.redeleted.update({elem : 1})
                        else:
                            if (elem in relation.self_redeleted.keys()):
                                relation.self_redeleted.update({elem : relation.self_redeleted[elem] + 1})
                            else:
                                relation.self_redeleted.update({elem : 1})

                # Revert: deleting something that somebody else reintroduced.
                for elem in word_prev.freq:
                    if (elem != revision_curr.wikipedia_id) and (elem in revisions.keys()):
                        if (revisions[elem].contributor_id != revision_curr.contributor_id):
                            if (elem in relation.revert.keys()):
                                relation.revert.update({elem: relation.revert[elem] +1})
                            else:
                                relation.revert.update({elem: 1})
                        else:
                            if (elem in relation.self_revert.keys()):
                                relation.self_revert.update({elem: relation.self_revert[elem] +1})
                            else:
                                relation.self_revert.update({elem: 1})

                word_prev.deleted.append(revision_curr.wikipedia_id)
                if (revisions[word_prev.revision].contributor_id != revision_curr.contributor_id):
                    if (word_prev.revision in relation.deleted.keys()):
                        relation.deleted.update({word_prev.revision : relation.deleted[word_prev.revision] + 1 })
                    else:
                        relation.deleted.update({word_prev.revision : 1 })
                else:
                    if (word_prev.revision in relation.self_deleted.keys()):
                        relation.self_deleted.update({word_prev.revision : relation.self_deleted[word_prev.revision] + 1 })
                    else:
                        relation.self_deleted.update({word_prev.revision : 1 })



    # Reset matched structures from old revisions.
    for matched_paragraph in matched_paragraphs_prev:
        matched_paragraph.matched = False
        for sentence_hash in matched_paragraph.sentences.keys():
            for sentence in matched_paragraph.sentences[sentence_hash]:
                sentence.matched = False
                for word in sentence.words:
                    word.matched = False

    for matched_sentence in matched_sentences_prev:
        matched_sentence.matched = False
        for word in matched_sentence.words:
            word.matched = False

    for matched_word in matched_words_prev:
        matched_word.matched = False


    if (not vandalism):
        # Add the new paragraphs to hash table of paragraphs.
        for unmatched_paragraph in unmatched_paragraphs_curr:
            if (unmatched_paragraph.hash_value in paragraphs_ht.keys()):
                paragraphs_ht[unmatched_paragraph.hash_value].append(unmatched_paragraph)
            else:
                paragraphs_ht.update({unmatched_paragraph.hash_value : [unmatched_paragraph]})

            # Add the new sentences to hash table of sentences.
        for unmatched_sentence in unmatched_sentences_curr:
            if (unmatched_sentence.hash_value in sentences_ht.keys()):
                sentences_ht[unmatched_sentence.hash_value].append(unmatched_sentence)
            else:
                sentences_ht.update({unmatched_sentence.hash_value : [unmatched_sentence]})


    return vandalism
