from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict

actually_delete = False




def all_files(starting_path=".", pattern="*"):
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            yield MusicFile(path)


def find_matches_by_partial_name(starting_path=".",tail="*.m4a"):
    partial_name_matches = {}
    for file in all_files(starting_path, tail):
        partial_name = file.full_path_name.rstrip(' 1.m4a')

        duplicate = partial_name_matches.get(partial_name)

        if not duplicate:
            partial_name_matches[partial_name] = []

        partial_name_matches[partial_name].append(file)

    return partial_name_matches


def highest_bitrate(track_list):
    return sorted(track_list, key=lambda x: x.bitrate, reverse=True)[0]


def largest_size(track_list):
    return sorted(track_list, key=lambda x: x.size, reverse=True)[0]


def shortest_name(track_list):
    return sorted(track_list, key=lambda x: len(x.path.name), reverse=True)[0]


def best_track(first_file: MusicFile = None, second_file: MusicFile = None) -> MusicFile:
    """
    Compare two MusicFiles and return the one that is present if the is only one,
    lexically the shortest name (if the two files have the same size and bitrate),
    or the one with the highest bitrate)
    """
    return first_file if not second_file \
        else second_file if not first_file \
        else first_file if first_file > second_file else second_file


def generate_delete_list(complete, tracks_to_keep):
    return set(complete).difference(set(tracks_to_keep))



def evaluate_tracks_at_path(starting_path=".", tail="*.m4a"):
    print(f"Evaluating starting path: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    all_tracks = []

    for file in all_files(starting_path, tail):
        print(f"Checking: {file.name}")
        common_name = file.full_path_name.rstrip(' 1.m4a')
        tracks_to_keep[common_name] = best_track(tracks_to_keep[common_name], file)
        all_tracks.append(file)

    return {"keep": [v for v in tracks_to_keep.values()], "all": all_tracks}






def find_extra_tracks(starting_path=".", tail="*.m4a"):
    matches = find_matches_by_partial_name(starting_path, tail)

    for __, tracks in matches.items():
        if len(tracks) > 1:
            print(tracks[0].album)
            for track in tracks:
                print(f"{track} - VBR: {track.bitrate} Size: {track.size}")

            if all(track == tracks[0] for track in tracks):
                print("Tracks are equal, will keep the shortest named one")
                tracks.remove(shortest_name(tracks))
            else:
                print("Tracks are not the same, will keep the one with the highest bitrate")
                tracks.remove(highest_bitrate(tracks))

            for track in tracks:
                print(f"Deleting {track}...", end="")
                if actually_delete:
                    track.path.unlink()
                    print("Deleted")
                else:
                    print("Test mode. Track not deleted")


if __name__ == '__main__':
    pass
    #find_extra_tracks(sys.argv[1])

    #print(find_list_to_delete())







