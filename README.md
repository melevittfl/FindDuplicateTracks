# Find Duplicate Tracks

Re-encoding some CDs in iTunes left me with albums where each track was there twice. 
The original track and a second track with a space and a 1 at the end of the name. I.e.:

`Track.m4a` and `Track 1.m4a`.

This utility will find all tracks that are almost the same except for the " 1.m4a" part 
and delete the lower bitrate one. 

Sometimes, iTunes seems to just duplicate the files and you and up with duplicate
size and bitrate files, just with slightly different names. In that case, the one with the shortest name is deleted. 


## Usage

<pre>python3 findDuplicates.py <i>/path/to/music/tracks</i></pre>

Out of the box, the utity won't actually delete any files. 

To actually delete change line 57 to True:
`actually_delete=True`

## Dependencies

It uses the TinyTag library from https://pypi.org/project/tinytag/ to read the bitrate from the track. 
