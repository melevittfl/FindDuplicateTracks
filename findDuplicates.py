from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict
from typing import Tuple, Optional


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


def best_track(first_file: MusicFile = None, second_file: MusicFile = None) -> Tuple[
    Optional[MusicFile], Optional[MusicFile]]:
    """
    Compare two MusicFiles and return the one that is present if the is only one,
    lexically the shortest name (if the two files have the same size and bitrate),
    or the one with the highest bitrate)
    """
    return (first_file, second_file) if not second_file \
        else (second_file, first_file) if not first_file \
        else (first_file, second_file) if first_file > second_file else (second_file, first_file)


def find_tracks_to_delete_at_path(starting_path: str =".", tail: str ="*.m4a") -> list:
    print(f"Evaluating starting path: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    tracks_to_delete = []

    for file in all_files(starting_path, tail):
        print(f"Checking: {file.name}")
        common_name = file.full_path_name.rstrip(' 1.m4a')
        tracks_to_keep[common_name], delete = best_track(tracks_to_keep[common_name], file)
        if delete is not None:
            tracks_to_delete.append(delete)

    return tracks_to_delete


def delete_duplicate_music_files(starting_path=".", type="*.m4a", actually_delete=False):
    delete_tracks(find_tracks_to_delete_at_path(starting_path, type), actually_delete)


if __name__ == '__main__':

    #find_extra_tracks(sys.argv[1])

    delete_duplicate_music_files(sys.argv[1])







