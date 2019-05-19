import pytest
from pathlib import Path
from collections import namedtuple

from findDuplicates import *

@pytest.fixture
def music_file():
    best_file = Path("resources/amazing_track.m4a")
    return {"class": MusicFile(filename=best_file),
            "track": best_file}


@pytest.fixture
def test_tracks():
    best_file = Path("resources/amazing_track.m4a")
    worst_file = Path("resources/amazing_track 1.m4a")

    first_equal = Path("resources/Equal 1.m4a")
    second_equal = Path("resources/Equal.m4a")

    BetterWorse = namedtuple('BetterWorse', ['better', 'worse'])
    Equal = namedtuple('Equal', ['longer', 'shorter'])

    return {"better_worse": BetterWorse(MusicFile(best_file), MusicFile(worst_file)),
            "equal": Equal(MusicFile(first_equal), MusicFile(second_equal))}


def test_musicfile_class(music_file):
    assert isinstance(music_file["class"], MusicFile)


def test_musicfile_returns_bitrate(music_file):
    assert music_file["class"].bitrate == 256
    assert type(music_file["class"].bitrate) == float


def test_musicfile_returns_size(music_file):
    assert music_file["class"].size == 798880
    assert type(music_file["class"].size) == int


def test_musicfile_returns_path(music_file):
    assert music_file["class"].path == music_file["track"]
    assert isinstance(music_file["class"].path, Path)


def test_musicfile_returns_short_name(music_file):
    assert music_file["class"].name == music_file["track"].name


def test_musicfile_returns_full_path_name(music_file):
    assert music_file["class"].full_path_name == str(music_file["track"].resolve())


def test_musicfile_returns_parent_path(music_file):
    assert music_file["class"].album == music_file["track"].parent.resolve()


def test_all_files():
    expected = list(Path(".").rglob(".py"))
    actual = list(all_files(".", ".py"))
    assert expected == actual


def test_highest_bitrate(test_tracks):
    assert highest_bitrate(test_tracks["better_worse"]) == test_tracks["better_worse"].better


def test_largest_size(test_tracks):
    assert largest_size(test_tracks["better_worse"]) == test_tracks["better_worse"].better


def test_files_are_equal(test_tracks):
    assert test_tracks["equal"].longer == test_tracks["equal"].shorter


def test_shortest_name(test_tracks):
    assert shortest_name(test_tracks["equal"]) == test_tracks["equal"].shorter


def test_best_track(test_tracks):
    assert best_track(test_tracks["better_worse"].better,
                      test_tracks["better_worse"].worse) == test_tracks["better_worse"].better
    assert best_track(test_tracks["equal"].longer,
                      test_tracks["equal"].shorter) == test_tracks["equal"].shorter
    assert best_track(test_tracks["equal"].longer, "Not A File") == NotImplemented


def test_find_list_to_delete():
    pass
