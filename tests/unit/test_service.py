import tempfile
from pathlib import Path

import pytest

from raspi_music_button.domain.model import PlaybackCard
from raspi_music_button.services.service import Service

from .. import FakeAPlayAdapter, FakeAMixerAdapter, FakeMPG321Adapter


@pytest.fixture
def fake_service():
    FakeAMixerAdapter.COMMANDS = []
    FakeMPG321Adapter.COMMANDS = []
    return Service(FakeAPlayAdapter, FakeAMixerAdapter, FakeMPG321Adapter)


def test_list_of_devices(fake_service):
    expected = [
        PlaybackCard(
            card=0,
            name="Headphones [bcm2835 Headphones]",
        ),
        PlaybackCard(
            card=1,
            name="USB [Jabra SPEAK 510 USB]",
        ),
        PlaybackCard(
            card=2,
            name="vc4hdmi [vc4-hdmi]",
        ),
    ]

    assert fake_service.get_list_of_devices() == expected


def test_set_volume(fake_service):

    fake_service.set_volume(card_id=0, volume_prct=20)
    assert FakeAMixerAdapter.COMMANDS == [("set_content", 0, "'Headphone',0", "20%")]
    fake_service.set_volume(card_id=1, volume_prct=100)
    assert FakeAMixerAdapter.COMMANDS[-1] == ("set_content", 1, "'PCM',0", "100%")


def test_play_songs(fake_service):

    song = Path("my/fake/folder/song.mp3")
    fake_service.play_songs(card_id=0, songs=[song])

    assert len(FakeMPG321Adapter.COMMANDS) == 1
    assert FakeMPG321Adapter.COMMANDS[0] == ("play_song", 0, str(song))

    fake_service.play_songs(card_id=0, songs=[song.absolute()])

    assert len(FakeMPG321Adapter.COMMANDS) == 2
    assert FakeMPG321Adapter.COMMANDS[1] == ("play_song", 0, str(song.absolute()))


def test_play_folder(fake_service):

    folder = Path(tempfile.mkdtemp())
    song1 = folder.joinpath("song1.mp3")
    song1.open(mode="w").write("")
    folder.joinpath("other_file.csv").open(mode="w").write("")
    song2 = folder.joinpath("song2.mp3")
    song2.open(mode="w").write("")
    song3 = folder.joinpath("song3.mp3")
    song3.open(mode="w").write("")

    fake_service.play_folder(card_id=1, folder=folder)

    assert len(FakeMPG321Adapter.COMMANDS) == 1
    assert FakeMPG321Adapter.COMMANDS[0] == (
        "play_song",
        1,
        " ".join([str(song1), str(song2), str(song3)]),
    )
