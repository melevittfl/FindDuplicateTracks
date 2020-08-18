import pytest
from pathlib import Path
from collections import namedtuple
from musicfile import MusicFile
import shutil


@pytest.fixture
def music_file():
    best_file = Path("tests/resources/amazing_track.m4a")
    return {"class": MusicFile(filename=best_file), "track": best_file}


@pytest.fixture
def test_tracks():
    best_file = Path("tests/resources/amazing_track.m4a")
    worst_file = Path("tests/resources/amazing_track 1.m4a")
    another_worst = Path("tests/resources/amazing_track 2.m4a")
    short_low_bitrate = Path("tests/resources/128bits.m4a")

    first_equal = Path("tests/resources/Equal 1.m4a")
    second_equal = Path("tests/resources/Equal.m4a")
    third_equal = Path("tests/resources/Equal (2).m4a")

    BetterWorse = namedtuple("BetterWorse", ["better", "worse"])
    Equal = namedtuple("Equal", ["longer", "shorter", "longest"])

    return {
        "better_worse": BetterWorse(MusicFile(best_file), MusicFile(worst_file)),
        "equal": Equal(MusicFile(first_equal), MusicFile(second_equal), MusicFile(third_equal)),
        "short128bit": MusicFile(short_low_bitrate),
        "worst2": MusicFile(another_worst),
    }


@pytest.fixture(scope="session")
def test_tree(tmpdir_factory):
    best_file = Path("tests/resources/amazing_track.m4a")
    worst_file = Path("tests/resources/amazing_track 1.m4a")
    another_worst = Path("tests/resources/amazing_track 2.m4a")
    short_low_bitrate = Path("tests/resources/128bits.m4a")

    first_equal = Path("tests/resources/Equal 1.m4a")
    second_equal = Path("tests/resources/Equal.m4a")
    third_equal = Path("tests/resources/Equal (2).m4a")

    tmpdir = tmpdir_factory.mktemp("music_files")

    for file in Path("tests/resources").glob("*.m4a"):
        shutil.copy(file, tmpdir)

    return {
        "best": best_file,
        "worst": worst_file,
        "short": short_low_bitrate,
        "equal1": first_equal,
        "equal": second_equal,
        "equal2": third_equal,
        "worst2": another_worst,
        "path": tmpdir,
    }
