# Find Duplicate Tracks

Re-encoding some CDs in iTunes left me with albums where each track was there twice. 
The original track and a second track with a space and a 1 at the end of the name. I.e.:

`Track.m4a` and `Track 1.m4a`.

This utility will find all tracks that are almost the same except for the " 1.m4a" part 
and delete the lower bitrate one. 

Sometimes, iTunes seems to just duplicate the files and you and up with duplicate
size and bitrate files, just with slightly different names. In that case, the one with the shortest name is deleted. 


## Usage

<pre>
usage: findDuplicates.py [-h] [-t {mp3,ogg,opus,mp4,m4a,flac,wma,wav}]
                         [--reallydelete] [-v]
                         path

Find music files that iTunes has duplicated. (c) Mark Levitt 2019

positional arguments:
  path                  The path to the root of your Music files

optional arguments:
  -h, --help            show this help message and exit
  -t {mp3,ogg,opus,mp4,m4a,flac,wma,wav}, --type {mp3,ogg,opus,mp4,m4a,flac,wma,wav}
                        Files extension to scan. Defaults to 'm4a'
  --reallydelete        Actually delete the duplicate files on disk
  -v, --verbose         Increase output verbosity
</pre

## Dependencies

It uses the TinyTag library from https://pypi.org/project/tinytag/ to read the bitrate from the track. 

