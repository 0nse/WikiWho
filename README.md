# WikiWho
An algorithm to identify authorship and editor interactions in Wiki revisioned content.

## Installation Requirements
WikiWho has been tested on Arch Linux running Python 3.4.3.

WikiWho utilizes the MediaWiki Utilities library to process the revisioned content extracted from Wikipedia.
These functions can be downloaded from the official MediaWiki Utilities repository (under the MIT license) at the
following link:
* https://github.com/halfak/Mediawiki-Utilities

## Running WikiWho

python WikiwhoRelationships.py

parameters:

-i \[source_file_name.xml\] (complete history dump XML of one article. If this parameter identifies a directory, all XML-files in said directory will be processed.)

-o [a | r] --> what type of output to produce --> a=authorship for all tokens of a revision | r= interactions for every revision with each other revision in the past. I.e., this will list you all revisions and for each type of interaction we defined (delete, undelete, reintro, ..) the revisions that were target of that interaction and the number of tokens that interaction included. We will soon provide code that will spit put a more aggregated version of this as an editor-editor network. Yet, from the output available right now, you can already construct such a network yourself by summing up the positive and/or negative interactions between two editors over the whole revision history or a part of it.

-r [\<revid\> | all] --> what revision to show. revID or "all" for -o a, revID only for -o r


example A:

python WikiwhoRelationships.py -i Randomarticle.xml -o a -r 5

gives authorship for all tokens of revision 5 (has to be an actual revision id) of Randomarticle

example B:

python WikiwhoRelationships.py -i Randomarticle.xml -o r -r 5

gives the edit interactions produced at every revision to other revisions, up to revision number 5 (has to be an actual revision id) of Randomarticle

## Licence
This work is released under a GPLv3 licence. It is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**.

For more information, please refer to the LICENSE file which you should have received with your copy of the program. If this is not the case, please refer to http://www.gnu.org/licenses/.
