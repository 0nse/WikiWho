#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Jul 08, 2015

@author: Michael Ruster
'''
from datetime import datetime
from mw.types.timestamp import Timestamp as mwTimestamp

def createBlockedUsersDict(inputFile):
    """ Reads a block log CSV, cleans the comment, reorders the output and writes
    it to disk according to outputFile.
    This method naïvely parses the date in ISO 8601 format. It refrains from
    using python-dateutil. However, this has no impact on the data processing as
    the time differences between block and revision timestamps do not change.
    """
    import csv

    blocks = {}
    with inputFile:
        blockLogReader = csv.reader(inputFile, delimiter='\t', quotechar='"')

        for [timestamp, blockedUserName, _, _, _] in blockLogReader:
            try: # missing seconds:
                datetime.strptime(timestamp, '%Y-%m-%dT%H:%MZ')
                # add missing seconds, needed for mwTimestamp:
                timestamp = timestamp.replace('Z', ':00Z')
            except:
                # seconds exist, conversion to timestamp is possible
                pass
            # We use mwTimestamp because our dump iterator uses them as well.
            # This way, we can ensure that both use the correct timezone (which
            # adds two hours to the provided timestamp.
            timestamp = mwTimestamp(timestamp)
            try: # exists:
                timestamps = blocks[blockedUserName]
                timestamps.append(timestamp)
            except KeyError: # create new:
                blocks[blockedUserName] = [timestamp]

    for timestamps in blocks.values():
        # Sorted so that later time differences must only be computed with the
        # closest posterior timestamp (if any).
        timestamps.sort()

    return blocks

def labelRevisions(blocks, inputFile, outputFile):
    """ Writes outputFile with an additional column, which contains a time
    difference in seconds between when this revision was created and when the
    author was next blocked.
    Please be aware that, if writing permissions are given for outputFile, it
    will blindly overwrite everything you love.

    @see calculateSecondsUntilNextBlock(blocks, userName, timestamp) """
    import csv

    revisionReader = csv.reader(inputFile, delimiter='\t', quotechar='"')
    revisionWriter = csv.writer(outputFile, delimiter='\t',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)

    with inputFile:
        for [timestamp, userId, userName, revisionId, text] in revisionReader:

            secondsToBlock = calculateSecondsUntilNextBlock(blocks, userName, timestamp)

            revisionWriter.writerow([timestamp,
                                userId,
                                userName,
                                revisionId,
                                text,
                                secondsToBlock])

def calculateSecondsUntilNextBlock(blocks, userName, revisionTimestamp):
    """ Determine when the next block of a user happened after her/his post,
    which happened at timestamp.
    If the author has not been blocked at all (or only at times earlier than the
    current revision, the value will be -1.
    Important: [timestamps, userName] = blocks, blocks' timestamps must be
    sorted in ascending order (oldest timestamp first).
    Also, provided timestamp MUST be of type mw.types.timestamp.Timestamp!
    """
    deltaInSeconds = -1

    if userName in blocks:
        blockTimestamps = blocks[userName]

        # Find the timestamp closest to the user posting time
        # with the blockTimestamp being more recent than the
        # revision's timestamp.
        for blockTimestamp in blockTimestamps:
            if blockTimestamp > revisionTimestamp:
                deltaInSeconds = blockTimestamp - revisionTimestamp
                break

    return deltaInSeconds

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Takes a block log output file produced with 0nse/WikiParser and matches it against a revision log file produced with 0nse/WikiWho (Branch: DiscussionParser). As result, a revision log file will be written to disk with an extra column that contains the time of this revision until the user was next blocked.',
                                     epilog="""
                                     RevisionLabeller, Copyright (C) 2015 Michael Ruster.
                                     RevisionLabeller comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions. See the LICENCE file that should have been distributed with this program for more information.
                                     """)
    parser.add_argument('blockLogFile',  type=argparse.FileType('r'),
                        help='The path to the block log file to process (CSV).')
    parser.add_argument('revLogFile',  type=argparse.FileType('r'),
                        help='The path to the revision log file to process (CSV).')
    parser.add_argument('outputFile',  type=argparse.FileType('w'),
                        help='The path to the file to which the processed output should be written to. Please be aware that the file will be overwritten if it already exists.')

    args = parser.parse_args()
    if not (args.revLogFile != args.blockLogFile and args.revLogFile != args.outputFile):
        raise ValueError("All parameters must identify a unique file!")
    blocks = createBlockedUsersDict(args.blockLogFile)
    labelRevisions(blocks, args.revLogFile, args.outputFile)
