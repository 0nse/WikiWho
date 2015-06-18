# WikiWho
An algorithm to identify authorship and editor interactions in Wiki revisioned content.

## Installation Requirements
WikiWho has been tested on Arch Linux running Python 3.4.3.

WikiWho utilizes the MediaWiki Utilities library to process the revisioned content extracted from Wikipedia.
These functions can be downloaded from the official MediaWiki Utilities repository (under the MIT license) at the
following link:
* https://github.com/halfak/Mediawiki-Utilities

## Running WikiWho

`python WikiWho.py`

**Parameters**:
* `-i [source_file_name or directory]` (complete history dump of articles, either as XML, bzip2, gzip, LZMA or 7zip. Alternatively, if a directory is specified, all files residing in it, matching one of the supported file types, will be processed.)
* `-r [<revid> | all]` (what revision to show. revID or "all". If this parameter is missing, `-r all` will be assumed.)


**Example**:
* `python WikiwhoRelationships.py -i Randomarticle.xml -r 5`
Returns the edit interactions produced at every revision up to revision number 5 (has to be an actual revision id) of `Randomarticle.xml`.

## Licence
This work is released under a GPLv3 licence. It is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **without any warranty**; without even the implied warranty of **merchantability** or **fitness for a particular purpose**.

For more information, please refer to the LICENSE file which you should have received with your copy of the program. If this is not the case, please refer to http://www.gnu.org/licenses/.
