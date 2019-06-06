from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict
from tqdm import tqdm
import argparse
import re


VERBOSE = 0


def cli_parser(command_line):
    parser = argparse.ArgumentParser(description="Find music files that iTunes has duplicated. (c) Mark Levitt 2019")
    parser.add_argument('path', help="The path to the root of your Music files")
    parser.add_argument('-t', '--type', default="m4a", help="Files extension to scan. Defaults to 'm4a'",
                        choices=['mp3', 'ogg', 'opus', 'mp4', 'm4a', 'flac', 'wma', 'wav'])
    parser.add_argument('--reallydelete', action="store_true", help="Actually delete the duplicate files on disk")
    parser.add_argument('-v', '--verbose', action="count", help="Increase output verbosity")
    return parser.parse_args(command_line)


def output(text=None, level=0, end="\n", flush=False):
    if level <= VERBOSE:
        print(text, end=end, flush=flush)


def search_pattern(file_type):
    return '*.' + file_type


def make_common_name(file, file_type):
    """
    Given a MusicFile, return the full path name minus the extension and any extra sequence characters
    For example. /some/path/file.m4a, /some/path/file 1.m4a, and /some/path/file 2.m4a should all return
    /some/path/file
    """
    return re.compile(f'( [\\d]|).{file_type}$').sub('', file.full_path_name)


def get_tree_list(starting_path, file_type):
    """Return a list of tracks for the given file type"""
    pattern = search_pattern(file_type)
    total = 0
    track_list = []
    for track_path in Path(starting_path).rglob(pattern):
        if track_path.is_file() and not track_path.name.startswith("._"):
            if total % 500 == 0:
                output(".", end="", flush=True)
            track_list.append(track_path)
            total += 1
    output("Done.")
    return track_list


def delete_tracks(tracks, delete_the_files=False):
    if delete_the_files:
        message = f"Deleting {len(tracks)} files"
    else:
        message = "Test mode - skipping delete"

    if not tracks:
        output("No tracks to delete")
    else:
        with tqdm(desc=message, total=len(tracks),
                  bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
                  unit="files") as pbar:
            for track in tqdm(tracks):
                tqdm.write(f"Deleting {track}...", end="")
                if delete_the_files:
                    track.path.unlink()
                    tqdm.write("Deleted")
                else:
                    tqdm.write("Test mode. Track not deleted")
                    pass
                pbar.update(1)


def best_track(first_file=None, second_file=None):
    """
    Compare two MusicFiles and return a tuple of two files, the first being the one to keep, the second being the one
    to delete. Pick the one to keep that is present if it is the only one, lexically the shortest name (if the two
    files have the same size and bitrate), or the one with the highest bitrate)
    """
    return (first_file, second_file) if not second_file \
        else (second_file, first_file) if not first_file \
        else (first_file, second_file) if first_file > second_file else (second_file, first_file)


def find_tracks_to_delete_at_path(starting_path=".", file_type="m4a"):
    output(f"Examining directory: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    tracks_to_delete = []
    file_list = get_tree_list(starting_path, file_type)
    output(f"{len(file_list)} tracks found.", level=2)
    with tqdm(desc="Finding duplicates", total=len(file_list),
              bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
              unit="files") as pbar:
        for track in (MusicFile(x) for x in file_list):
            if VERBOSE > 0:
                tqdm.write(f"Checking: {track.name}")
            common_name = make_common_name(track, file_type)
            tracks_to_keep[common_name], delete_candidate = best_track(tracks_to_keep[common_name], track)
            if delete_candidate is not None:
                tracks_to_delete.append(delete_candidate)
            pbar.update(1)
    output(f"Done. Found {len(tracks_to_delete)} duplicate tracks")

    return tracks_to_delete


def main(cli_arguments):
    parsed = cli_parser(cli_arguments)
    path = parsed.path
    delete = parsed.reallydelete
    f_type = parsed.type
    global VERBOSE
    VERBOSE = parsed.verbose
    if not VERBOSE:
        VERBOSE = 0

    delete_tracks(find_tracks_to_delete_at_path(starting_path=path, file_type=f_type), delete_the_files=delete)


if __name__ == '__main__':
    main(sys.argv[1:])

