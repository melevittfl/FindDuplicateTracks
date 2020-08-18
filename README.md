# Find Duplicate Tracks

Re-encoding some CDs in iTunes left me with albums where each track was there twice. 
The original track and a second track with a space and a 1 at the end of the name. I.e.:

`Track.m4a` and `Track 1.m4a`.

Some music taggers eg. MusicBrainz Picard behave similarly when saving tagged files and finding a file with the same name. Picard puts the number in parenthesis though, so if it finds `Track.m4a` it will name its file `Track (1).m4a`.

This utility will find all tracks that are almost the same except for the " 1.m4a" part (or a " (1).m4a" part)
and delete the lower bitrate one. It can (and will by default) search out the same music in multiple formats eg. flac and mp3.

Sometimes, iTunes seems to just duplicate the files and you and up with duplicate
size and bitrate files, just with slightly different names. In that case, the one with the shortest name is deleted. 


## Usage

<pre>
usage: findDuplicates.py [-h] [-t {mp3,ogg,opus,mp4,m4a,flac,wma,wav} ... --]
                         [--reallydelete] [-v]
                         path

Find music files that iTunes has duplicated. (c) Mark Levitt 2019

positional arguments:
  path                  The path to the root of your Music files

optional arguments:
  -h, --help            show this help message and exit
  -t {mp3,ogg,opus,mp4,m4a,flac,wma,wav} [{mp3,ogg,opus,mp4,m4a,flac,wma,wav} ...], --type {mp3,ogg,opus,mp4,m4a,flac,wma,wav} [{mp3,ogg,opus,mp4,m4a,flac,wma,wav} ...]
                        Files extension(s) to scan. Defaults to all choices.
                        End list with -- or another option.
  --reallydelete        Actually delete the duplicate files on disk
  -v, --verbose         Increase output verbosity
</pre>

## Dependencies

Python3 is required; findDuplicates is not compatible with Python 2

It uses the TinyTag library from https://pypi.org/project/tinytag/ to read the bitrate from the track. 

tqdm is used for printing progress indications. See https://pypi.org/project/tqdm/

pytest is the testing framework for running the test scripts. See https://pypi.org/project/pytest/ 

pip isn't actually needed but is the best tool for locating and installing the other Python dependencies.
