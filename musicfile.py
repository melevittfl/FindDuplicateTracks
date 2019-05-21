from tinytag import TinyTag
from pathlib import Path


class MusicFile(object):

    def __init__(self, filename):
        self.path = Path(filename)

    @property
    def bitrate(self):
        return TinyTag.get(self.path).bitrate

    @property
    def size(self):
        return Path.stat(self.path).st_size

    @property
    def full_path_name(self):
        return self.__str__()

    @property
    def name(self):
        return self.__repr__()

    @property
    def album(self):
        return self.path.parent.resolve()

    def __repr__(self):
        return self.path.name

    def __str__(self):
        return str(self.path.resolve())

    def __eq__(self, other):
        """Files are equal if they have the same size and bitrate"""
        if isinstance(other, MusicFile):
            return (self.bitrate == other.bitrate) and (self.size == other.size)
        else:
            return NotImplemented

    def __gt__(self, other):
        """One file is greater if it has a higher bitrate or, if equal, the shorter name"""
        if isinstance(other, MusicFile):
            return True if ((self.bitrate > other.bitrate) and (self.size > other.size)) else \
                   True if (((self.bitrate == other.bitrate) and (self.size == other.size))
                            and len(self.name) < len(other.name)) else False
        else:
            return NotImplemented

    def __hash__(self):
        return hash((self.bitrate, self.size))
