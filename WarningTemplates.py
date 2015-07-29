#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 28, 2015

@author: Michael Ruster

This file contains lists of template names that are used to issue warnings on
user pages. It was compiled from:
    https://en.wikipedia.org/w/index.php?title=Wikipedia:Template_messages/User_talk_namespace&oldid=671520213
The templates are used as follows:
 - {{subst:uw-TemplateName}} or
 - {{subst:uw-TemplateName|ReferenceToArticle}} or
 - {{subst:uw-TemplateName|ReferenceToArticle|Additional text}}
However, an untrained editor might forget about the substitution fuction. Thus
 - {{uw-TemplateName}},
 - {{uw-TemplateName|ReferenceToArticle}}
 - {{uw-TemplateName|ReferenceToArticle|Additional text}}
should also be taken into consideration.
Some warning templates are used multiple times. Thus, list addition should be
followed by duplicate removal.
'''

# Blatant vandalism
# # Vandalism
vandalism = ['vandalism1', 'vandalism2', 'vandalism3', 'vandalism4', 'vandalism4im']

# General disruptive editing not categorised elsewhere
# # Disruptive editing
disruptive = ['disruptive1', 'disruptive2', 'disruptive3', 'generic4']

# Behaviour in articles
# # Editing tests
test = ['test1', 'test2', 'test3', 'vandalism4']
# # Page blanking, removal of content
delete = ['delete1', 'delete2', 'delete3', 'delete4', 'delete4im']
# # Frequent or mass changes to genres without consensus or reference
genre = ['genre1', 'genre2', 'genre3', 'genre4']
# # Removing file deletion tags
idt = ['idt1', 'idt2', 'idt3', 'idt4']
# # Image-related vandalism
image = ['image1', 'image2', 'image3', 'image4', 'image4im']
# # Improper humour in articles
joke = ['joke1', 'joke2', 'joke3', 'joke4', 'joke4im']
# # Censorship of material
notcensored = ['notcensored1', 'notcensored2', 'notcensored3', 'generic4']
# # Ownership of articles
own = ['own1', 'own2', 'own3', 'generic4', 'own4im']
# # Inappropriate expansion of plot summaries
plotsum = ['plotsum1', 'plotsum2', 'plotsum3']
# # Removal of maintenance templates
tdel = ['tdel1', 'tdel2', 'tdel3', 'tdel4']
# # Uploading unencyclopedic images (image vandalism)
upload = ['upload1', 'upload2', 'upload3', 'upload4', 'upload4im']
# # Disrupting the taxonomy templates
taxonomy = ['taxonomy1', 'taxonomy2', 'taxonomy3', 'generic4']

# Behaviour towards editors
# # Not assuming good faith
agf = ['agf1', 'agf2', 'agf3']
# # Harassment of other users
harass = ['harass1', 'harass2', 'harass3', 'harass4', 'harass4im']
# # Personal attack directed at editors
npa = ['npa1', 'npa2', 'npa3', 'npa4', 'npa4im']
# # Improper use of warning or blocking template
tempabuse = ['tempabuse1', 'tempabuse2', 'disruptive3']

# Adding promotions of objects or ideologies (also spam)
# # Using Wikipedia for advertising or promotion
advert = ['advert1', 'advert2', 'advert3', 'advert4', 'advert4im']
# # Not adhering to neutral point of view
npov = ['npov1', 'npov2', 'npov3', 'npov4', 'npov4im']
# # Inserting fringe or undue weight content into article links
fringe = ['fringe1', 'fringe2', 'fringe3']
# # Adding spam links
spam = ['spam1', 'spam2', 'spam3', 'spam4', 'spam4im']

# Inserting factual inaccuracies and/or libel
# # Adding unreferenced controversial information about living persons
biog = ['biog1', 'biog2', 'biog3', 'biog4', 'biog4im']
# # Defamation regarding article subjects
defamatory = ['defamatory1', 'defamatory2', 'defamatory3', 'defamatory4', 'defamatory4im']
# # Introducing deliberate factual errors
error = ['error1', 'error2', 'error3', 'error4']
# # Adding original research, including unpublished syntheses of sourced material
nor = ['nor1', 'nor2', 'nor3', 'nor4', 'nor4im']
# # Addition of unsourced or improperly cited material
unsourced = ['unsourced1', 'unsourced2', 'unsourced3', 'unsourced4']

# Unaccepted practices, unilateral action against policies or guidelines
# # Triggering the abuse filter by attempting to vandalise
attempt = ['attempt2', 'attempt3', 'attempt4']
# # Removing {{afd}} templates / refactoring others' comments in AfD discussions
afd = ['afd1', 'afd2', 'afd3', 'afd4']
# # Removing {{cfd}} templates / refactoring others' comments in CfD discussions
cfd = ['cfd1', 'cfd2', 'cfd3', 'cfd4']
# # Using talk page as forum
chat = ['chat1', 'chat2', 'chat3', 'chat4']
# # Creating inappropriate pages
create = ['create1', 'create2', 'create3', 'create4', 'create4im']
# # Uploading files missing copyright status
ics = ['ics1', 'ics2', 'ics3', 'ics4']
# # Formatting, date, language, etc. (Manual of Style)
mos = ['mos1', 'mos2', 'mos3', 'mos4']
# # Malicious or bad page moves
move = ['move1', 'move2', 'move3', 'move4', 'move4im']
# # Creating malicious redirects
redirect = ['redirect1', 'redirect2', 'redirect3', 'redirect4', 'redirect4im']
# # Removing {{speedy deletion}} templates
speedy = ['speedy1', 'speedy2', 'speedy3', 'speedy4', 'speedy4im']
# # Editing, correcting, or deleting others' talk page comments
tpv = ['tpv1', 'tpv2', 'tpv3', 'tpv4']
# # Removing {{{Prod blp}} templates
blpprod = ['blpprod1', 'blpprod2', 'blpprod3', 'blpprod4']

def mergeTemplatesSimplified(*lists):
    """ Merges all provides lists into a set so that it is duplicate free. This
    method does not return regular expressions. It instead simplifies the
    problem at hand by assuming that e.g. '{{uw-TemplateName|' is unique enough
    for tasks such as determining whether  a template is contained in a text.
    """
    mergedSet = set()
    for l in lists:
        for templateName in l:
            mergedSet.update(['{{uw-%s}}' % templateName,
                              '{{uw-%s|'  % templateName])
    return mergedSet

def mergeTemplatesRe(*lists):
    """ Reuses mergeTemplatesSimplified to remove duplicates in the template
    lists. This method returns a list as regular expression cannot be members of
    a set. The list contains regular expressions to match the templates. For
    performance reasons, they are simplified, so e.g.
    '{{uw-TemplateName|Article|Text|Rubbish}}' will also be matched. """
    import re
    templatesRe = []

    templatesSet = mergeTemplatesSimplified(lists)
    for template in templatesSet:
        if template.endswith('|'):
            # match e.g. '{{uw-TemplateName|Article|Text}}' instead of just '{{uw-TemplateName|':
            template += '[^}]*}}'
        templatesRe.append(re.compile(template))
    return templatesRe
