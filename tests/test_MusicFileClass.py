from pathlib import Path

from musicfile import MusicFile


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


def test_files_are_equal(test_tracks):
    assert test_tracks["equal"].longer == test_tracks["equal"].shorter


def test_files_are_not_equal(test_tracks):
    assert test_tracks["equal"].longer != test_tracks["better_worse"].worse


def test_should_return_false_if_not_equal_is_false(test_tracks):
    assert (test_tracks["equal"].longer != test_tracks["equal"].shorter) is False


def test_higher_bitrate_file_greater_than_lower_bitrate_file(test_tracks):
    assert test_tracks["better_worse"].better > test_tracks["better_worse"].worse


def test_lower_bitrate_file_less_than_higher_bitrate_file(test_tracks):
    assert test_tracks["better_worse"].worse < test_tracks["better_worse"].better


def test_shorter_name_file_greater_than_longer_name_file(test_tracks):
    assert test_tracks["equal"].shorter > test_tracks["equal"].longer


def test_longer_name_file_less_than_shorter_name_file(test_tracks):
    assert test_tracks["equal"].longer < test_tracks["equal"].shorter


def test_higher_bitrate_file_greater_than_shorter_name_file(test_tracks):
    assert test_tracks["better_worse"].better > test_tracks["short128bit"]


def test_shorter_name_file_less_than_higher_bitrate_file(test_tracks):
    assert test_tracks["short128bit"] < test_tracks["better_worse"].better


def test_should_return_false_if_greater_than_is_false(test_tracks):
    assert (test_tracks["short128bit"] > test_tracks["better_worse"].better) is False
