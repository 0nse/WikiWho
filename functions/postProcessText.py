from sys import path

path.append("../WikiCodeCleaner")
from WikiCodeCleaner.clean import clean as cleanWikiCode

def cleanText(textList):
    """WikiCode and other symbols are being removed using
    0nse/WikiCodeCleaner."""
    text = mergeText(textList)

    return cleanWikiCode(text)

def mergeText(textList):
    """Merges the list of words so that all words are separated
    by a space except for symbols which are padded together with
    their previous and next."""
    if not textList:
        return ""

    word = textList[0]
    text = word if doesWordContainSymbols(word) else word + " "

    for word in textList[1:]:
        if doesWordContainSymbols(word):
            text = text.strip()
            text += word
        else:
            text += word + " "

    return text.strip()

def doesWordContainSymbols(word):
    # this is string.punctuation without ' and " and `:
    punctuation = "!#$%&()*+,-./:;<=>?@[\\]^_{|}~"
    return any(c in word for c in punctuation)
