from structures import Text
from structures.Word import Word
from difflib import Differ

# Spam detection.
WORD_DENSITY = 10

def analyseWordsInSentences(unmatched_sentences_curr, unmatched_sentences_prev, revision_curr, possible_vandalism, revisions):

    matched_words_prev = []
    unmatched_words_prev = []

    # Split sentences into words.
    text_prev = []
    for sentence_prev in unmatched_sentences_prev:
        for word_prev in sentence_prev.words:
            if (not word_prev.matched):
                text_prev.append(word_prev.value)
                unmatched_words_prev.append(word_prev)

    text_curr = []
    for sentence_curr in unmatched_sentences_curr:
        splitted = Text.splitIntoWords(sentence_curr.value)
        text_curr.extend(splitted)
        sentence_curr.splitted.extend(splitted)

    # Edit consists of removing sentences, not adding new content.
    if (len(text_curr) == 0):
        return (matched_words_prev, False)

    # SPAM detection.
    if (possible_vandalism):

        density = Text.computeAvgWordFreq(text_curr, revision_curr.wikipedia_id)

        if (density > WORD_DENSITY):
            return (matched_words_prev, possible_vandalism)
        else:
            possible_vandalism = False

    if (len(text_prev) == 0):
        for sentence_curr in unmatched_sentences_curr:
            for word in sentence_curr.splitted:
                word_curr = Word()
                word_curr.author_id = revision_curr.contributor_id
                word_curr.author_name = revision_curr.contributor_name
                word_curr.revision = revision_curr.wikipedia_id
                word_curr.value = word
                sentence_curr.words.append(word_curr)
                word_curr.used.append(revision_curr.wikipedia_id)

        return (matched_words_prev, possible_vandalism)

    d = Differ()
    diff = list(d.compare(text_prev, text_curr))


    for sentence_curr in unmatched_sentences_curr:

        for word in sentence_curr.splitted:
            curr_matched = False
            pos = 0

            while (pos < len(diff)):

                word_diff = diff[pos]

                if (word == word_diff[2:]):

                    if (word_diff[0] == ' '):
                        for word_prev in unmatched_words_prev:
                            if ((not word_prev.matched) and (word_prev.value == word)):
                                word_prev.used.append(revision_curr.wikipedia_id)
                                word_prev.matched = True
                                curr_matched = True
                                sentence_curr.words.append(word_prev)
                                matched_words_prev.append(word_prev)
                                diff[pos] = ''
                                pos = len(diff)+1

                                break

                    elif (word_diff[0] == '-'):
                        for word_prev in unmatched_words_prev:
                            if ((not word_prev.matched) and (word_prev.value == word)):
                                word_prev.matched = True
                                matched_words_prev.append(word_prev)
                                diff[pos] = ''
                                word_prev.deleted.append(revision_curr.wikipedia_id)
                                break

                    elif (word_diff[0] == '+'):
                        curr_matched = True
                        word_curr = Word()
                        word_curr.value = word
                        word_curr.author_id = revision_curr.contributor_id
                        word_curr.author_name = revision_curr.contributor_name
                        word_curr.revision = revision_curr.wikipedia_id
                        word_curr.used.append(revision_curr.wikipedia_id)
                        sentence_curr.words.append(word_curr)

                        diff[pos] = ''
                        pos = len(diff)+1

                pos = pos + 1

            if not(curr_matched):
                word_curr = Word()
                word_curr.value = word
                word_curr.author_id = revision_curr.contributor_id
                word_curr.author_name = revision_curr.contributor_name
                word_curr.revision = revision_curr.wikipedia_id
                word_curr.used.append(revision_curr.wikipedia_id)
                sentence_curr.words.append(word_curr)

    return (matched_words_prev, possible_vandalism)
