import pytest
from pathlib import Path

from findDuplicates import *

test_file = Path("resources/amazing_track.m4a")
second_file = Path("resources/amazing_track 1.m4a")

@pytest.fixture
def music_file():
    return MusicFile(filename=test_file)


@pytest.fixture
def track_list():
    return [MusicFile(test_file), MusicFile(second_file)]

@pytest.fixture
def equal_tracks():
    first = Path("resources/Equal 1.m4a")
    second = Path("resources/Equal.m4a")
    return [MusicFile(first), MusicFile(second)]


def test_musicfile_class(music_file):
    assert isinstance(music_file, MusicFile)


def test_musicfile_returns_bitrate(music_file):
    assert music_file.bitrate == 256
    assert type(music_file.bitrate) == float


def test_musicfile_returns_size(music_file):
    assert music_file.size == 798880
    assert type(music_file.size) == int


def test_musicfile_returns_path(music_file):
    assert music_file.path == test_file
    assert isinstance(music_file.path, Path)


def test_all_files():
    expected = list(Path(".").rglob(".py"))
    actual = list(all_files(".", ".py"))
    assert expected == actual


def test_highest_bitrate(track_list):
    assert highest_bitrate(track_list) == track_list[0]  # Aria is 320VBR vs 256VBR


def test_largest_size(track_list):
    assert largest_size(track_list) == track_list[0]  # Aria is larger


def test_files_are_equal(equal_tracks):
    assert equal_tracks[0] == equal_tracks[1]


def test_shortest_name(equal_tracks):
    assert shortest_name(equal_tracks) == equal_tracks[1]




