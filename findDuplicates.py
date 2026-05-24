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
        "-y",
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt (requires --reallydelete to actually delete)",
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


_DUPLICATE_SUFFIX_RE = re.compile(r"( 1| [(]1[)]|)\.[^.]+$")
_RENAME_RE = re.compile(r"( 1| \(1\))$")


def make_common_name(file):
    """
    Given a MusicFile, return the full path name minus the extension and any iTunes/Picard
    first-duplicate suffix. Only " 1" and " (1)" are treated as duplicate markers — higher
    numbers (e.g. "Episode 2") are assumed to be legitimately distinct files.
    """
    return _DUPLICATE_SUFFIX_RE.sub("", file.full_path_name)


def _rename_target(file):
    """
    If file has a ' 1' or ' (1)' suffix, return the Path it should be renamed to after its
    duplicate is deleted. Returns None when no rename is needed.
    """
    new_stem = _RENAME_RE.sub("", file.path.stem)
    if new_stem != file.path.stem:
        return file.path.parent / (new_stem + file.path.suffix)
    return None


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


def delete_tracks(tracks, rename_pairs=None, delete_the_files=False):
    rename_pairs = rename_pairs or []

    if not tracks:
        output("No tracks to delete")
        return

    total = len(tracks) + len(rename_pairs)
    message = f"Deleting {len(tracks)} file(s)"
    with _progress_bar() as progress:
        task = progress.add_task(message, total=total)
        for track in tracks:
            progress.console.print(f"  [dim]{track}[/dim]", end="")
            if delete_the_files:
                track.path.unlink()
                progress.console.print(" [green]deleted[/green]")
            else:
                progress.console.print(" [yellow]skipped (test mode)[/yellow]")
            progress.advance(task)
        for keep_file, new_path in rename_pairs:
            progress.console.print(
                f"  [dim]{keep_file.path.name}[/dim] → [dim]{new_path.name}[/dim]", end=""
            )
            if delete_the_files:
                if new_path.exists():
                    progress.console.print(" [red]rename skipped (target exists)[/red]")
                else:
                    keep_file.path.rename(new_path)
                    progress.console.print(" [green]renamed[/green]")
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

    rename_pairs = [
        (keep, _rename_target(keep))
        for keep, _ in delete_pairs
        if _rename_target(keep) is not None
    ]
    _print_duplicate_summary(delete_pairs, rename_pairs)
    return [delete for _, delete in delete_pairs], rename_pairs


def _print_duplicate_summary(delete_pairs, rename_pairs):
    if not delete_pairs:
        console.print("\n[green]No duplicates found.[/green]")
        return

    rename_map = {keep: new_path for keep, new_path in rename_pairs}

    table = Table(
        title=f"Found {len(delete_pairs)} duplicate pair(s)",
        show_lines=True,
    )
    table.add_column("Keep", style="green", no_wrap=False)
    table.add_column("Delete", style="red", no_wrap=False)

    for keep, delete in delete_pairs:
        keep_path = Path(keep.full_path_name)
        delete_path = Path(delete.full_path_name)
        rename = rename_map.get(keep)
        keep_label = keep_path.name
        if rename:
            keep_label += f"\n[dim]→ {rename.name}[/dim]"
        if keep_path.parent == delete_path.parent:
            dir_prefix = f"[dim]{keep_path.parent}/[/dim]\n"
            table.add_row(dir_prefix + keep_label, dir_prefix + delete_path.name)
        else:
            table.add_row(keep.full_path_name + (f"\n→ {rename}" if rename else ""), delete.full_path_name)

    console.print(table)


def main(cli_arguments):
    parsed = cli_parser(cli_arguments)
    global VERBOSE
    VERBOSE = parsed.verbose or 0

    delete_list, rename_pairs = find_tracks_to_delete_at_path(
        starting_path=parsed.path, file_type=parsed.type
    )

    if not delete_list:
        return

    if not parsed.yes:
        answer = console.input("\nProceed? (y/[bold]N[/bold]): ").strip().lower()
        if answer != "y":
            console.print("[yellow]Aborted.[/yellow]")
            return

    if not parsed.reallydelete:
        console.print(
            f"[yellow]Test mode — add --reallydelete to delete {len(delete_list)} file(s)"
            + (f" and rename {len(rename_pairs)}" if rename_pairs else "")
            + ".[/yellow]"
        )
        return

    delete_tracks(delete_list, rename_pairs, delete_the_files=True)


if __name__ == "__main__":
    main(sys.argv[1:])
