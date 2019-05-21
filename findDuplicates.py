from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict


def all_files(starting_path=".", pattern="*"):
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            yield MusicFile(path)


def delete_tracks(tracks, actually_delete=False):
    for track in tracks:
        print(f"Deleting {track}...", end="")
        if actually_delete:
            track.path.unlink()
            print("Deleted")
        else:
            print("Test mode. Track not deleted")


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
    print("Determing tracks to delete")
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


def delete_duplicate_music_files(starting_path=".", type="*.m4a", actually_delete=False):
    tracks = evaluate_tracks_at_path(starting_path, type)
    delete_tracks(generate_delete_list(complete=tracks["all"], tracks_to_keep=tracks["keep"]),
                  actually_delete)


if __name__ == '__main__':

    #find_extra_tracks(sys.argv[1])

    delete_duplicate_music_files(sys.argv[1])







