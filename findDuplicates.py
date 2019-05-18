from tinytag import TinyTag
from pathlib import Path
import sys

actually_delete=False


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
        '''Files are equal is they have the same size and bitrate'''
        if isinstance(other, MusicFile):
            return (self.bitrate == other.bitrate) and (self.size == other.size)


def all_files(starting_path=".", pattern="*"):
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            yield MusicFile(path)


def find_matches_by_partial_name(starting_path=".",tail="*.m4a"):
    partial_name_matches = {}
    for file in all_files(starting_path, tail):
        partial_name = file.full_path_name.rstrip(' 1.m4a')

        duplicate = partial_name_matches.get(partial_name)

        if duplicate:
            partial_name_matches[partial_name].append(file)
        else:
            partial_name_matches[partial_name] = []
            partial_name_matches[partial_name].append(file)

    return partial_name_matches


def highest_bitrate(track_list):
    return sorted(track_list, key=lambda x: x.bitrate, reverse=True)[0]


def largest_size(track_list):
    return sorted(track_list, key=lambda x: x.size, reverse=True)[0]


def shortest_name(track_list):
    return sorted(track_list, key=lambda x: len(x.path.name), reverse=True)[0]


def find_extra_tracks(starting_path=".", tail="*.m4a"):
    matches = find_matches_by_partial_name(starting_path, tail)

    for __, tracks in matches.items():
        if len(tracks) > 1:
            print(tracks[0].album)
            for track in tracks:
                print(f"{track} - VBR: {track.bitrate} Size: {track.size}")

            if tracks[0] == tracks[1]:
                tracks.remove(shortest_name(tracks))
            else:
                tracks.remove(highest_bitrate(tracks))

            for track in tracks:
                print(f"Deleting {track}...", end="")
                if actually_delete:
                    track.path.unlink()
                    print("Deleted")
                else:
                    print("Test mode. Track not deleted")


if __name__ == '__main__':
    find_extra_tracks(sys.argv[1])






