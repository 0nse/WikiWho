#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jun 18, 2015

@author: Michael Ruster
'''
import re
from sys import path

path.append('./WikiCodeCleaner')
from WikiCodeCleaner.clean import clean as cleanWikiCode

def clean(text, userName):
    """WikiCode and other symbols are being removed using 0nse/WikiCodeCleaner.
    Prior to that though, user links to the author of this revision will be
    removed as they are most likely just part of her signature."""
    try:
        # Escape userName for users such as the 22 year old cocktail waitress
        # Janet from Texas; User:Hiall:)
        userName = re.escape(userName.lower())
        userSelfLink = re.compile("\[\[user:" + userName + "[^\]]+\]\]")
        text = userSelfLink.sub("", text)
    except AttributeError:
        # There exist pages with deleted users and therefore # there is no
        # username. Example: Articles for deletion/Jonathan Sadko (ID: 2665745)
        #
        # We clear the text so that it will not be printed:
        text = ''

    return cleanWikiCode(text)

def merge(textList):
    """Merges the list of words so that all words are separated by a space
    except for symbols which are padded together with their previous and next.
    """
    if not textList:
        return ''

    word = textList[0]
    text = word if doesWordContainSymbols(word) else word + ' '

    for word in textList[1:]:
        if doesWordContainSymbols(word):
            text = text.strip()
            text += word
        else:
            text += word + ' '

    return text.strip()

def doesWordContainSymbols(word):
    # this is string.punctuation without ' and " and `:
    punctuation = '!#$%&()*+,-./:;<=>?@[\\]^_{|}~§'
    return any(c in word for c in punctuation)
