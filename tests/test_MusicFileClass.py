import pytest
from collections import namedtuple
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
