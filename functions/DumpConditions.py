#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 30, 2015

@author: Michael Ruster
'''

import socket

def isStringAnIpAddress(s):
    """ Returns True if string s is an IPv4 or IPv6 address. """
    try: # test for IPv4 address:
        socket.inet_pton(socket.AF_INET, s)
    # Python < 3.3 will raise a socket.error whereas >= 3.3 raises OSError:
    except (OSError, socket.error):
        try: # test for IPv6 address:
            socket.inet_pton(socket.AF_INET6, s)
        except (OSError, socket.error):
            return False
    return True

def isRegisteredUser(page):
    """ A user must be a page of namespace 2:User and the page must start with
    'User:'. Furthermore, an IP address may not follow as we are looking for
    registered accounts only. This test requires the socket module which is
    imported in filterDumps."""
    if (page.namespace is 2 \
       and page.title.startswith('User:')):
        userName = page.title[5:]

        if '/' in userName: # some users create subpages in their namespace:
            return False

        if not isStringAnIpAddress(userName):
            return True
    # not user page or IP address:
    return False

def isRegisteredUserTalk(page):
    """ A user talk page must be a page of namespace 3:User Talk and the page
    must start with 'User Talk:'. Furthermore, an IP address may not follow as
    we are looking for registered accounts only. This test requires the socket
    module which is imported in filterDumps."""
    title = page.title.lower()
    if (page.namespace is 3 \
       and title.startswith('user talk:')):
        userName = title[10:]

        if '/' in userName: # ignore potential sub pages:
            return False

        if not isStringAnIpAddress(userName):
            return True
    # not user page or IP address:
    return False

def isDeletionDiscussion(page):
    """ A deletion discussion (AfD) is set in the Wikipedia namespace 4. It
    starts with 'Wikipedia:Articles for deletion/' with a few exceptions. These
    exceptions are AfD collections using templates to link to the original
    discussions. """
    if (page.namespace is 4 \
       and page.title.startswith('Wikipedia:Articles for deletion/') \
       # Old links to old discussions:
       and not page.title.startswith('Wikipedia:Articles for deletion/Old/') \
       and page.title != 'Wikipedia:Articles for deletion/Old' \
       # Log collects discussions by including them through a template:
       and not page.title.startswith('Wikipedia:Articles for deletion/Log/') \
       and page.title != 'Wikipedia:Articles for deletion/Log'):
        return True

    return False

def parse(conditionString):
    """ Return the condition method by evaluating the string if it is of known
    a known value. Else, exit. This method could be made more dynamic by
    iterating over methods and comparing with their names. """
    if conditionString in ['isDeletionDiscussion', 'isRegisteredUser', 'isRegisteredUserTalk']:
        return eval(conditionString)
    else:
        print('[E] Only "isDeletionDiscussion", "isRegisteredUser" and "isRegisteredUserTalk" are valid conditions. Defaulting to "isDeletionDiscussion".')
        return isDeletionDiscussion
