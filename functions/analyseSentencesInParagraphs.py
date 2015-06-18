from structures import Text
from structures.Sentence import Sentence

def analyseSentencesInParagraphs(unmatched_paragraphs_curr, unmatched_paragraphs_prev, revision_curr, revision_prev, relation, revisions):
    # Hash table.
    sentences_ht = {}

    # Containers for unmatched and matched sentences.
    unmatched_sentences_curr = []
    unmatched_sentences_prev = []
    matched_sentences_prev = []
    total_sentences = 0


    # Iterate over the unmatched paragraphs of the current revision.
    for paragraph_curr in unmatched_paragraphs_curr:

        # Split the current paragraph into sentences.
        sentences = Text.splitIntoSentences(paragraph_curr.value)

        # Iterate over the sentences of the current paragraph
        for sentence in sentences:

            # Create the Sentence structure.
            sentence = sentence.strip()
            sentence = ' '.join(Text.splitIntoWords(sentence))
            hash_curr = Text.calculateHash(sentence)
            matched_curr = False
            total_sentences = total_sentences + 1


            # Iterate over the unmatched paragraphs from the previous revision.
            for paragraph_prev in unmatched_paragraphs_prev:
                if (hash_curr in paragraph_prev.sentences.keys()):
                    for sentence_prev in paragraph_prev.sentences[hash_curr]:

                        if (not sentence_prev.matched):

                            matched_one = False
                            matched_all = True
                            for word_prev in sentence_prev.words:

                                if (word_prev.matched):
                                    matched_one = True
                                else:
                                    matched_all = False

                            if not(matched_one):
                                sentence_prev.matched = True
                                matched_curr = True
                                matched_sentences_prev.append(sentence_prev)

                                # TODO: CHECK this
                                for word_prev in sentence_prev.words:
                                    word_prev.matched = True
                                    word_prev.used.append(revision_curr.wikipedia_id)


                                # Add the sentence information to the paragraph.
                                if (hash_curr in paragraph_curr.sentences.keys()):
                                    paragraph_curr.sentences[hash_curr].append(sentence_prev)
                                    paragraph_curr.ordered_sentences.append(sentence_prev.hash_value)
                                else:
                                    paragraph_curr.sentences.update({sentence_prev.hash_value : [sentence_prev]})
                                    paragraph_curr.ordered_sentences.append(sentence_prev.hash_value)
                                break
                            elif (matched_all):

                                sentence_prev.matched = True
                                matched_sentences_prev.append(sentence_prev)

                    if (matched_curr):
                        break


            # Iterate over the hash table of sentences from old revisions.
            if ((not matched_curr) and (hash_curr in sentences_ht.keys())):
                for sentence_prev in sentences_ht[hash_curr]:
                    if (not sentence_prev.matched):
                        matched_one = False
                        matched_all = True
                        for word_prev in sentence_prev.words:
                            if (word_prev.matched):
                                matched_one = True
                            else:
                                matched_all = False

                        if not(matched_one):

                            sentence_prev.matched = True
                            matched_curr = True
                            matched_sentences_prev.append(sentence_prev)

                            # TODO: CHECK this
                            for word_prev in sentence_prev.words:
                                word_prev.matched = True
                                word_prev.used.append(revision_curr.wikipedia_id)

                                if (revision_prev.wikipedia_id not in word_prev.used):
                                    word_prev.freq.append(revision_curr.wikipedia_id)

                                # Revert: reintroducing something that somebody else deleted
                                if (revision_prev.wikipedia_id not in word_prev.used):
                                    for elem in word_prev.deleted:

                                        if (elem in revisions.keys()):
                                            if (revisions[elem].contributor_id != revision_curr.contributor_id):
                                                if (elem in relation.revert.keys()):
                                                    relation.revert.update({elem : relation.revert[elem] + 1})
                                                else:
                                                    relation.revert.update({elem : 1})
                                            else:
                                                if (elem in relation.self_revert.keys()):
                                                    relation.self_revert.update({elem : relation.self_revert[elem] + 1})
                                                else:
                                                    relation.self_revert.update({elem : 1})

                                if (revision_prev.wikipedia_id not in word_prev.used):
                                    if (elem in revisions.keys()):
                                        if (revisions[word_prev.revision].contributor_id != revision_curr.contributor_id):
                                            if (word_prev.revision in relation.reintroduced.keys()):
                                                relation.reintroduced.update({word_prev.revision : relation.reintroduced[word_prev.revision] + 1 })
                                            else:
                                                relation.reintroduced.update({word_prev.revision : 1 })
                                        else:
                                            if (word_prev.revision in relation.self_reintroduced.keys()):
                                                relation.self_reintroduced.update({word_prev.revision : relation.self_reintroduced[word_prev.revision] + 1})
                                            else:
                                                relation.self_reintroduced.update({word_prev.revision : 1})



                            # Add the sentence information to the paragraph.
                            if (hash_curr in paragraph_curr.sentences.keys()):
                                paragraph_curr.sentences[hash_curr].append(sentence_prev)
                                paragraph_curr.ordered_sentences.append(sentence_prev.hash_value)
                            else:
                                paragraph_curr.sentences.update({sentence_prev.hash_value : [sentence_prev]})
                                paragraph_curr.ordered_sentences.append(sentence_prev.hash_value)
                            break
                        elif (matched_all):
                            sentence_prev.matched = True
                            matched_sentences_prev.append(sentence_prev)


            # If the sentence did not match, then include in the container of unmatched sentences for further analysis.
            if (not matched_curr):
                sentence_curr = Sentence()
                sentence_curr.value = sentence
                sentence_curr.hash_value = hash_curr

                paragraph_curr.ordered_sentences.append(sentence_curr.hash_value)
                if (sentence_curr.hash_value in paragraph_curr.sentences.keys()):
                    paragraph_curr.sentences[sentence_curr.hash_value].append(sentence_curr)
                else:
                    paragraph_curr.sentences.update({sentence_curr.hash_value : [sentence_curr]})

                unmatched_sentences_curr.append(sentence_curr)


    # Identify the unmatched sentences in the previous paragraph revision.
    for paragraph_prev in unmatched_paragraphs_prev:
        for sentence_prev_hash in paragraph_prev.ordered_sentences:
            for sentence_prev in paragraph_prev.sentences[sentence_prev_hash]:
                if (not sentence_prev.matched):
                    unmatched_sentences_prev.append(sentence_prev)
                    sentence_prev.matched = True
                    matched_sentences_prev.append(sentence_prev)


    return (unmatched_sentences_curr, unmatched_sentences_prev, matched_sentences_prev, sentences_ht)
