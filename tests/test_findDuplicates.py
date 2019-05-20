import pytest
from collections import namedtuple

from findDuplicates import *



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


def test_files_are_not_equal(test_tracks):
    assert test_tracks["equal"].longer != test_tracks["better_worse"].worse


def test_shortest_name(test_tracks):
    assert shortest_name(test_tracks["equal"]) == test_tracks["equal"].shorter


def test_best_track(test_tracks):
    # Different bitrate files should return the higher one
    assert best_track(test_tracks["better_worse"].better,
                      test_tracks["better_worse"].worse) == test_tracks["better_worse"].better

    # Equal size and bitrate files should return the shorter name
    assert best_track(test_tracks["equal"].longer,
                      test_tracks["equal"].shorter) == test_tracks["equal"].shorter

    # Comparing the first file with None should return the first file
    assert best_track(test_tracks["equal"].shorter, None) == test_tracks["equal"].shorter

    # Comparing the None with the second file should return the second file
    assert best_track(None, test_tracks["equal"].shorter) == test_tracks["equal"].shorter

    # Comparing a MusicFile with a non MusicFile should return NotImplimented
    assert best_track(test_tracks["equal"].longer, "Not A File") == NotImplemented


def test_find_list_to_delete(test_tracks):
    assert find_list_to_delete() == [test_tracks["better_worse"].worse,
                                     test_tracks["equal"].longer]
