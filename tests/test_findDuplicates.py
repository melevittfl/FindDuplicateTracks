import pytest
import shutil
from findDuplicates import *


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
                test_tracks["short128bit"],
                test_tracks["worst2"]]

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

    delete_tracks(delete_list, delete_the_files=False)
    remaining_tracks = temp_dir.glob("*.tmp")
    assert set(all_the_tracks) == set(remaining_tracks)

    delete_tracks(delete_list, delete_the_files=True)

    remaining_tracks = temp_dir.glob("*.tmp")
    assert set(keep_list) == set(remaining_tracks)
    assert len(set(delete_list_paths).intersection(remaining_tracks)) == 0

    # assert no runtime excpetion occurs
    delete_tracks([], delete_the_files=False)


def test_delete_duplicate_music_files(test_tree):
    complete = [test_tree["best"],
                test_tree["worst"],
                test_tree["equal"],
                test_tree["equal1"],
                test_tree["short"],
                test_tree["worst2"]]

    tracks_to_keep = [test_tree["best"],
                      test_tree["equal"],
                      test_tree["short"]]

    temp_dir = test_tree["path"]
    temp_dir_string = temp_dir.strpath
    complete = [n.name for n in complete]
    keep = [n.name for n in tracks_to_keep]

    delete_duplicate_music_files(temp_dir_string, do_delete=False)
    remaining_tracks = [n.name for n in Path(temp_dir.strpath).glob("*.m4a")]
    assert set(complete) == set(remaining_tracks)

    delete_duplicate_music_files(temp_dir_string, do_delete=True)
    remaining_tracks = [n.name for n in Path(temp_dir.strpath).glob("*.m4a")]
    assert set(remaining_tracks) == set(keep)


def test_get_tree_list(tmpdir):
    for p in range(0, 5):
        d = Path(tmpdir / f"test_dir{p:03d}")
        d.mkdir()
        for i in range(0, 20):
            f = Path(d / f"test_file{i:03d}.tmp")

            f.touch()

    expected = list(Path(tmpdir).rglob(".tmp"))

    assert set(get_tree_list(tmpdir, ".tmp")) == set(expected)


def test_parse_args():
    parsed = cli_parser(['/Some/Path', '--reallydelete', '-vv', '-t', 'm4a'])
    assert parsed.path == '/Some/Path'
    assert parsed.reallydelete
    assert parsed.verbose == 2
    assert parsed.type == 'm4a'

    parsed = cli_parser(['/Some/Path'])
    assert not parsed.reallydelete

    with pytest.raises(SystemExit):
        parser = cli_parser([])

    with pytest.raises(SystemExit):
        parser = cli_parser(['-t doc'])


def test_search_pattern():
    assert search_pattern('m4a') == '*.m4a'


def test_make_common_name(test_tracks):
    c_name1 = test_tracks["better_worse"].better.full_path_name.rstrip('.m4a')
    result1 = make_common_name(test_tracks["better_worse"].better, 'm4a')
    assert result1 == c_name1

    c_name2 = test_tracks["better_worse"].worse.full_path_name.rstrip(' 1.m4a')
    result2 = make_common_name(test_tracks["better_worse"].worse, 'm4a')
    assert result2 == c_name2
