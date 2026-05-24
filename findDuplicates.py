#!/usr/bin/env python3

from musicfile import MusicFile
from pathlib import Path
import sys
from collections import defaultdict
from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    MofNCompleteColumn,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
import argparse
import re

VERBOSE = 0
console = Console(highlight=False)


def cli_parser(command_line):
    parser = argparse.ArgumentParser(
        description="Find music files that iTunes has duplicated. (c) Mark Levitt 2019"
    )
    parser.add_argument("path", help="The path to the root of your Music files")
    parser.add_argument(
        "-t",
        "--type",
        nargs="+",
        default=["mp3", "ogg", "opus", "mp4", "m4a", "flac", "wma", "wav"],
        help="Files extension(s) to scan. Defaults to all choices.\nEnd list with -- or another option.",
        choices=["mp3", "ogg", "opus", "mp4", "m4a", "flac", "wma", "wav"],
    )
    parser.add_argument(
        "--reallydelete",
        action="store_true",
        help="Actually delete the duplicate files on disk",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="Increase output verbosity"
    )
    return parser.parse_args(command_line)


def output(text=None, level=0, end="\n"):
    if level <= VERBOSE:
        console.print(text, end=end)


def search_pattern(file_types):
    pattern = "([^.].*)[.](" + file_types[0]
    for file_type in file_types[1:]:
        pattern += "|" + file_type
    pattern += ")"
    output("Search pattern: " + pattern, 2)
    return re.compile(pattern, re.IGNORECASE)


def make_common_name(file):
    """
    Given a MusicFile, return the full path name minus the extension and any extra sequence characters
    For example. /some/path/file.m4a, /some/path/file 1.m4a, and /some/path/file (2).m4a should all return
    /some/path/file
    """
    return re.compile(r"( \d+| [(]\d+[)]|)\.[^.]+$").sub("", file.full_path_name)


def get_tree_list(starting_path, file_type):
    """Return a list of tracks for the given file type"""
    pattern = search_pattern(file_type)
    seen = set()
    track_list = []
    with console.status("[bold green]Scanning for music files...") as status:
        for total, track_path in enumerate(Path(starting_path).rglob("*")):
            if track_path.is_file() and pattern.fullmatch(track_path.name):
                resolved = str(track_path.resolve())
                if resolved not in seen:
                    seen.add(resolved)
                    track_list.append(resolved)
                    status.update(
                        f"[bold green]Scanning...[/bold green] {len(track_list):,} tracks found"
                    )
    console.print(f"[green]✓[/green] Found [bold]{len(track_list):,}[/bold] tracks\n")
    return track_list


def _progress_bar():
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )


def delete_tracks(tracks, delete_the_files=False):
    if delete_the_files:
        message = f"Deleting {len(tracks)} files"
    else:
        message = "Test mode - skipping delete"

    if not tracks:
        output("No tracks to delete")
    else:
        with _progress_bar() as progress:
            task = progress.add_task(message, total=len(tracks))
            for track in tracks:
                progress.console.print(f"  [dim]{track}[/dim]", end="")
                if delete_the_files:
                    track.path.unlink()
                    progress.console.print(" [green]deleted[/green]")
                else:
                    progress.console.print(" [yellow]skipped (test mode)[/yellow]")
                progress.advance(task)


def best_track(first_file=None, second_file=None):
    """
    Compare two MusicFiles and return a tuple of two files, the first being the one to keep, the second being the one
    to delete. Pick the one to keep that is present if it is the only one, lexically the shortest name (if the two
    files have the same size and bitrate), or the one with the highest bitrate)
    """
    return (
        (first_file, second_file)
        if not second_file
        else (second_file, first_file)
        if not first_file
        else (first_file, second_file)
        if first_file > second_file
        else (second_file, first_file)
    )


def find_tracks_to_delete_at_path(starting_path=".", file_type=None):
    if file_type is None:
        file_type = ["m4a"]
    output(f"Examining directory: {starting_path}")

    tracks_to_keep = defaultdict(lambda: None)
    delete_pairs = []
    file_list = get_tree_list(starting_path, file_type)
    output(f"{len(file_list)} tracks found.", level=2)
    with _progress_bar() as progress:
        task = progress.add_task("Finding duplicates...", total=len(file_list))
        for track in (MusicFile(x) for x in file_list):
            if VERBOSE > 1:
                progress.console.print(f"  Checking: [dim]{track.full_path_name}[/dim]")
            common_name = make_common_name(track)
            if VERBOSE > 2:
                progress.console.print(f"  Common name: [dim]{common_name}[/dim]")
            tracks_to_keep[common_name], delete_candidate = best_track(
                tracks_to_keep[common_name], track
            )
            if delete_candidate is not None:
                delete_pairs.append((tracks_to_keep[common_name], delete_candidate))
                if VERBOSE > 0:
                    progress.console.print(
                        f"  [green]Keep:[/green]   {tracks_to_keep[common_name].full_path_name}\n"
                        f"  [red]Delete:[/red] {delete_candidate.full_path_name}"
                    )
            progress.advance(task)

    _print_duplicate_summary(delete_pairs)
    return [delete for _, delete in delete_pairs]


def _print_duplicate_summary(delete_pairs):
    if not delete_pairs:
        console.print("\n[green]No duplicates found.[/green]")
        return

    table = Table(
        title=f"Found {len(delete_pairs)} duplicate pair(s)",
        show_lines=True,
    )
    table.add_column("Keep", style="green", no_wrap=False)
    table.add_column("Delete", style="red", no_wrap=False)

    for keep, delete in delete_pairs:
        keep_path = Path(keep.full_path_name)
        delete_path = Path(delete.full_path_name)
        if keep_path.parent == delete_path.parent:
            dir_prefix = f"[dim]{keep_path.parent}/[/dim]\n"
            table.add_row(dir_prefix + keep_path.name, dir_prefix + delete_path.name)
        else:
            table.add_row(keep.full_path_name, delete.full_path_name)

    console.print(table)


def main(cli_arguments):
    parsed = cli_parser(cli_arguments)
    path = parsed.path
    delete = parsed.reallydelete
    f_type = parsed.type
    global VERBOSE
    VERBOSE = parsed.verbose
    if not VERBOSE:
        VERBOSE = 0

    delete_tracks(
        find_tracks_to_delete_at_path(starting_path=path, file_type=f_type),
        delete_the_files=delete,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
