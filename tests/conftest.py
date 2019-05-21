import pytest
from pathlib import Path
from collections import namedtuple

from musicfile import MusicFile
import shutil

@pytest.fixture
def music_file():
    best_file = Path("resources/amazing_track.m4a")
    return {"class": MusicFile(filename=best_file),
            "track": best_file}


@pytest.fixture
def test_tracks():
    best_file = Path("resources/amazing_track.m4a")
    worst_file = Path("resources/amazing_track 1.m4a")
    short_low_bitrate = Path("resources/128bits.m4a")

    first_equal = Path("resources/Equal 1.m4a")
    second_equal = Path("resources/Equal.m4a")

    BetterWorse = namedtuple('BetterWorse', ['better', 'worse'])
    Equal = namedtuple('Equal', ['longer', 'shorter'])

    return {"better_worse": BetterWorse(MusicFile(best_file), MusicFile(worst_file)),
            "equal": Equal(MusicFile(first_equal), MusicFile(second_equal)),
            "short128bit": MusicFile(short_low_bitrate)}


@pytest.fixture(scope="session")
def test_tree(tmpdir_factory):
    best_file = Path("resources/amazing_track.m4a")
    worst_file = Path("resources/amazing_track 1.m4a")
    short_low_bitrate = Path("resources/128bits.m4a")

    first_equal = Path("resources/Equal 1.m4a")
    second_equal = Path("resources/Equal.m4a")

    tmpdir = tmpdir_factory.mktemp("music_files")

    for file in Path('resources').glob("*.m4a"):
        shutil.copy(file, tmpdir)

    return {"best": best_file,
            "worst": worst_file,
            "short": short_low_bitrate,
            "equal1": first_equal,
            "equal": second_equal,
            "path": tmpdir}
