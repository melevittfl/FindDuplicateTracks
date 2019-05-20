import pytest
from pathlib import Path
from collections import namedtuple

from musicfile import MusicFile

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