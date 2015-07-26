# WikiWho
An algorithm for extracting posts on Wikipedia page deletion discussions.

## Installation Requirements
WikiWho has been tested on Arch Linux running Python 3.4.3.

WikiWho utilizes the MediaWiki Utilities library to process the revisioned content extracted from Wikipedia.
These functions can be downloaded from the official MediaWiki Utilities repository (under the MIT license) at the
following link:
* https://github.com/halfak/Mediawiki-Utilities

## Running WikiWho

### `WikiWho.py`
This file is the core of this project. It is used to extract deletion discussions from Wikipedia page dumps, attribute their authorship and write them to disk together with the amounts of seconds between the post creation and the author being blocked. `-1` expresses that the user has not been blocked afterwards.

#### Parameters
* `-i [source_file_name or directory]` (complete history dump of articles, either as XML, bzip2, gzip, LZMA or 7zip. Alternatively, if a directory is specified, all files residing in it, matching one of the supported file types, will be processed.)
* `-b [block log]` (the block log constructed from the Wikipedia data dumps' logging dump through [0nse/WikiParser](https://github.com/0nse/wikiparser).)
* `-r [<revid> | all]` (what revision to show. revID or "all". If this parameter is missing, `-r all` will be assumed.)

#### Example
* `python WikiwhoRelationships.py -i randomArticle.xml -b blockLog.csv -r 5`
Returns the edit interactions produced at every revision up to revision number 5 (has to be an actual revision id) of `randomArticle.xml`.

### `BlockTimeCalculation.py`
Calculates the time between the creation of a post and when the author of said post has been blocked. This data is written as an additional column to the `revision log`. This file is used by `WikiWho.py`. Its standalone purpose is to migrate CSV-files from former WikiWho DiscussionParser revisions.

#### Parameters
* `[block log]` (the block log constructed from the Wikipedia data dumps' logging dump through [0nse/WikiParser](https://github.com/0nse/wikiparser).)
* `[revision log file]` (processed revisions with authorship but without calculated time until the next block.)
* `[output file]` (the file to where the new CSV file should be written to.)

### `DumpFilter.py`
Reads Wikipedia dumps and writes uncompressed XML dumps that only contain Articles for Deletion (AfD) or user pages of registered users. With preprocessing AfD, the actual WikiWho DiscussionParser can run a lot faster as it neither has to decompress the dumps nor filter for the relevant articles.

#### Parameters
* `[page dump path]` (the path to the dumps. It can also be a concrete file. The filtered file will be generated with the suffix `_filtered.xml`.)
* `[<condition>] (optional. It can be `isDeletionDiscussion` for AfD or `isRegisteredUser` for users. The default is `isDeletionDiscussion`.

## Licence
This work is released under a GPLv3 licence. It is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**.

For more information, please refer to the LICENSE file which you should have received with your copy of the program. If this is not the case, please refer to http://www.gnu.org/licenses/.
