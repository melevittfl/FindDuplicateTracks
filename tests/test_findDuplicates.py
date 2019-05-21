import pytest
import shutil
from findDuplicates import *


def test_all_files():
    expected = list(Path(".").rglob(".py"))
    actual = list(all_files(".", ".py"))
    assert expected == actual


def test_files_are_equal(test_tracks):
    assert test_tracks["equal"].longer == test_tracks["equal"].shorter


def test_files_are_not_equal(test_tracks):
    assert test_tracks["equal"].longer != test_tracks["better_worse"].worse


def test_best_track(test_tracks):
    # Different bitrate files should return the higher one
    assert best_track(test_tracks["better_worse"].better,
                      test_tracks["better_worse"].worse) == (test_tracks["better_worse"].better,
                                                             test_tracks["better_worse"].worse)

    # Equal size and bitrate files should return the shorter name
    assert best_track(test_tracks["equal"].longer,
                      test_tracks["equal"].shorter) == (test_tracks["equal"].shorter, test_tracks["equal"].longer)

    # Comparing the first file with None should return the first file
    assert best_track(test_tracks["equal"].shorter, None) == (test_tracks["equal"].shorter, None)

    # Comparing the None with the second file should return the second file
    assert best_track(None, test_tracks["equal"].shorter) == (test_tracks["equal"].shorter, None)

    # Comparing a MusicFile with a non MusicFile should return TypeError
    with pytest.raises(TypeError):
        best_track(test_tracks["equal"].longer, "Not A File")


def test_find_tracks_to_delete_at_path(test_tracks):
    complete = [test_tracks["better_worse"].better,
                test_tracks["better_worse"].worse,
                test_tracks["equal"].shorter,
                test_tracks["equal"].longer,
                test_tracks["short128bit"]]

    tracks_to_keep = [test_tracks["better_worse"].better,
                      test_tracks["equal"].shorter,
                      test_tracks["short128bit"]]

    list_to_delete = set(complete) - set(tracks_to_keep)
    result = find_tracks_to_delete_at_path("resources")
    assert isinstance(result[0], MusicFile)
    assert set(result) == set(list_to_delete)


def test_delete_tracks(tmpdir):
    delete_list = []
    keep_list = []
    for i in range(0, 6):
        path = Path(tmpdir / f"test_file{i:03d}.tmp")
        shutil.copy("resources/128bits.m4a", path)
        if i % 2:
            delete_list.append(MusicFile(path))
        else:
            keep_list.append(path)

    temp_dir = Path(tmpdir)
    delete_list_paths = [Path(p.full_path_name) for p in delete_list]
    all_the_tracks = delete_list_paths + keep_list

    delete_tracks(delete_list, actually_delete=False)
    remaining_tracks = temp_dir.glob("*.tmp")
    assert set(all_the_tracks) == set(remaining_tracks)

    delete_tracks(delete_list, actually_delete=True)

    remaining_tracks = temp_dir.glob("*.tmp")
    assert set(keep_list) == set(remaining_tracks)
    assert len(set(delete_list_paths).intersection(remaining_tracks)) == 0


def test_delete_duplicate_music_files(test_tree):
    complete = [test_tree["best"],
                test_tree["worst"],
                test_tree["equal"],
                test_tree["equal1"],
                test_tree["short"]]

    tracks_to_keep = [test_tree["best"],
                      test_tree["equal"],
                      test_tree["short"]]

    temp_dir = test_tree["path"]
    temp_dir_string = temp_dir.strpath
    complete = [n.name for n in complete]
    keep = [n.name for n in tracks_to_keep]

    delete_duplicate_music_files(temp_dir_string, actually_delete=False)
    remaining_tracks = [n.name for n in Path(temp_dir.strpath).glob("*.m4a")]
    assert set(complete) == set(remaining_tracks)

    delete_duplicate_music_files(temp_dir_string, actually_delete=True)
    remaining_tracks = [n.name for n in Path(temp_dir.strpath).glob("*.m4a")]
    assert set(remaining_tracks) == set(keep)


    


