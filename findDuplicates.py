from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict
from typing import Tuple, Optional
from tqdm import tqdm
import argparse


VERBOSE = 1


def cli_parser(commnad_line):
    parser = argparse.ArgumentParser(description="Find music files that iTunes has duplicated. (c) Mark Levitt 2019")
    parser.add_argument('path', help="The path to the root of your Music files")
    parser.add_argument('-t', '--type', default="m4a", help="Files extension to scan. Defaults to 'm4a'",
                        choices=['mp3', 'ogg', 'opus', 'mp4', 'm4a', 'flac', 'wma', 'wav'])
    parser.add_argument('--reallydelete', action="store_true", help="Actually delete the duplicate files on disk")
    parser.add_argument('-v', '--verbose', action="count", help="Increase output verbosity")
    return parser.parse_args(commnad_line)


def search_pattern(file_type):
    return '*.' + file_type


def get_tree_size(starting_path, file_type):
    """Return total number of files in given path and subdirs."""
    pattern = search_pattern(file_type)
    total = 0
    for path in Path(starting_path).rglob(pattern):
        if path.is_file() and not path.name.startswith("._"):
            if VERBOSE:
                if total % 500 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()
            total += 1
    return total


def all_files(starting_path=".", file_type="*"):
    for path in Path(starting_path).rglob(search_pattern(file_type)):
        if path.is_file() and not path.name.startswith("._"):
            yield MusicFile(path)


def delete_tracks(tracks, delete_the_files=False):

    if delete_the_files:
        message = f"Deleting {len(tracks)} files"
    else:
        message = "Test mode - skipping delete"

    if not tracks:
        print("No tracks to delete")
    else:
        with tqdm(desc=message, total=len(tracks),
                  bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as pbar:
            for track in tqdm(tracks):
                if VERBOSE > 0:
                    tqdm.write(f"Deleting {track}...", end="")
                if delete_the_files:
                    track.path.unlink()
                    if VERBOSE > 0:
                        tqdm.write("Deleted")
                else:
                    if VERBOSE > 0:
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


def find_tracks_to_delete_at_path(starting_path: str = ".", file_type: str = "m4a") -> list:
    print(f"Examining directory: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    tracks_to_delete = []

    with tqdm(desc="Finding duplicates", total=get_tree_size(starting_path, file_type),
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
              unit="files") as pbar:
        for file in all_files(starting_path, file_type):
            if VERBOSE > 1:
                tqdm.write(f"Checking: {file.name}")
            common_name = file.full_path_name.rstrip(f' 1.{file_type}')
            tracks_to_keep[common_name], delete_candidate = best_track(tracks_to_keep[common_name], file)
            if delete_candidate is not None:
                tracks_to_delete.append(delete_candidate)
            pbar.update(1)
    print(f"Done. Found {len(tracks_to_delete)} duplicate tracks")

    return tracks_to_delete


def delete_duplicate_music_files(starting_path=".", file_type="m4a", do_delete=False):
    delete_tracks(find_tracks_to_delete_at_path(starting_path=starting_path, file_type=file_type), do_delete)


if __name__ == '__main__':
    parsed = cli_parser(sys.argv[1:])
    path = parsed.path
    delete = parsed.reallydelete
    type = parsed.type
    VERBOSE = parsed.verbose
    if not VERBOSE:
        VERBOSE = 1

    delete_duplicate_music_files(starting_path=path, do_delete=delete, file_type=type)
