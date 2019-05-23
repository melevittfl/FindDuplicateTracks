from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict
from typing import Tuple, Optional
from tqdm import tqdm
import time

verbose = 1


def get_tree_size(starting_path, pattern):
    """Return total number of files in given path and subdirs."""
    total = 0
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            if verbose:
                if total % 500 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()
            total += 1
    return total


def all_files(starting_path=".", pattern="*"):
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            yield MusicFile(path)


def delete_tracks(tracks, delete=False):
    if delete:
        message = f"Deleting {len(tracks)} files"
    else:
        message = "Test mode - skipping delete"
    with tqdm(desc=message, total=len(tracks),
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as pbar:
        for track in tqdm(tracks):
            if verbose > 1:
                tqdm.write(f"Deleting {track}...", end="")
            if delete:
                track.path.unlink()
                if verbose > 1:
                    tqdm.write("Deleted")
            else:
                if verbose > 1:
                    tqdm.write("Test mode. Track not deleted")
                pass
            pbar.update(1)


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
    print(f"Examining directory: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    tracks_to_delete = []

    with tqdm(desc="Finding duplicates", total=get_tree_size(starting_path, tail),
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
              unit="files") as pbar:
        for file in all_files(starting_path, tail):
            if verbose > 1:
                tqdm.write(f"Checking: {file.name}")
            common_name = file.full_path_name.rstrip(' 1.m4a')
            tracks_to_keep[common_name], delete = best_track(tracks_to_keep[common_name], file)
            if delete is not None:
                tracks_to_delete.append(delete)
            pbar.update(1)
    print(f"Done. Found {len(tracks_to_delete)} duplicate tracks")

    return tracks_to_delete


def delete_duplicate_music_files(starting_path=".", type="*.m4a", delete=False):
    delete_tracks(find_tracks_to_delete_at_path(starting_path, type), delete)


if __name__ == '__main__':
    actually_delete = False

    delete_duplicate_music_files(sys.argv[1], delete=actually_delete)







